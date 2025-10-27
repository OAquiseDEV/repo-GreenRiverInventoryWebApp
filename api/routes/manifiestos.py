from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.models import db, Manifiesto, DetalleManifiesto, Cliente, Producto, Movimiento
from api.utils.decorators import role_required
from api.utils.validators import validate_required_fields, validate_positive_number
from api.services.qr_service import generate_codigo_qr, generate_manifest_qr
from api.services.pdf_service import generate_manifest_pdf
from datetime import datetime

bp = Blueprint('manifiestos', __name__)

@bp.route('', methods=['GET'])
@jwt_required()
@role_required(1, 2, 3, 4)  # Administrador, Oficina, Operario, Delivery
def list_manifests():
    """List all manifests with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(100, max(1, per_page))

    # Filters
    estado = request.args.get('estado')
    cliente_id = request.args.get('cliente_id', type=int)
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')

    query = Manifiesto.query

    if estado:
        # Support multiple estados separated by comma
        if ',' in estado:
            estados = estado.split(',')
            query = query.filter(Manifiesto.estado.in_(estados))
        else:
            query = query.filter_by(estado=estado)

    if cliente_id:
        query = query.filter_by(cliente_id=cliente_id)

    if fecha_desde:
        query = query.filter(Manifiesto.fecha_creacion >= fecha_desde)

    if fecha_hasta:
        query = query.filter(Manifiesto.fecha_creacion <= fecha_hasta)

    query = query.order_by(Manifiesto.fecha_creacion.desc())

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "items": [m.to_dict(include_relations=True) for m in paginated.items],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": paginated.total,
            "pages": paginated.pages
        }
    }), 200

@bp.route('/<int:id>', methods=['GET'])
def get_manifest(id):
    """
    Get manifest details.
    Public endpoint if codigo_qr is provided, otherwise requires JWT.
    """
    codigo_qr = request.args.get('codigo_qr')

    manifiesto = Manifiesto.query.get(id)
    if not manifiesto:
        return jsonify({"error": "Manifiesto no encontrado"}), 404

    # If codigo_qr provided, verify it matches (public access)
    if codigo_qr:
        if manifiesto.codigo_qr != codigo_qr:
            return jsonify({"error": "Código QR inválido para este manifiesto"}), 400
    else:
        # Require JWT if no codigo_qr
        try:
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request()
        except:
            return jsonify({"error": "No autorizado"}), 401

    return jsonify(manifiesto.to_dict(include_relations=True)), 200

@bp.route('', methods=['POST'])
@jwt_required()
@role_required(1, 2)  # Administrador, Oficina
def create_manifest():
    """
    Create delivery manifest with PDF generation.
    Implements full specification from planning.md
    """
    data = request.get_json()
    current_user = get_jwt_identity()
    user_id = current_user['user_id']

    # Validate required fields
    is_valid, error = validate_required_fields(data, ['cliente_id', 'detalles'])
    if not is_valid:
        return jsonify({"error": error}), 400

    # Validate detalles array
    if not isinstance(data['detalles'], list) or len(data['detalles']) == 0:
        return jsonify({"error": "Debe incluir al menos un producto"}), 400

    # Validate each detalle
    for idx, detalle in enumerate(data['detalles']):
        is_valid, error = validate_required_fields(detalle, ['producto_id', 'cantidad'])
        if not is_valid:
            return jsonify({"error": f"Producto en detalle [{idx}]: {error}"}), 400

        is_valid, error = validate_positive_number(detalle['cantidad'], "cantidad")
        if not is_valid:
            return jsonify({"error": f"Producto en detalle [{idx}]: {error}"}), 400

    # Verify cliente exists
    cliente = Cliente.query.get(data['cliente_id'])
    if not cliente:
        return jsonify({"error": "Cliente no encontrado"}), 404

    # Verify all products exist and have sufficient stock
    stock_errors = []
    productos_data = []

    for detalle in data['detalles']:
        producto = Producto.query.get(detalle['producto_id'])
        if not producto:
            return jsonify({"error": f"Producto {detalle['producto_id']} no encontrado"}), 404

        cantidad = float(detalle['cantidad'])
        if float(producto.cantidad) < cantidad:
            stock_errors.append(
                f"{producto.nombre} (disponible: {producto.cantidad}, requerido: {cantidad})"
            )

        productos_data.append({
            'producto': producto,
            'cantidad': cantidad,
            'precio_unitario': detalle.get('precio_unitario'),
            'subtotal': detalle.get('subtotal')
        })

    if stock_errors:
        return jsonify({
            "error": f"Stock insuficiente para: {', '.join(stock_errors)}"
        }), 409

    try:
        # Generate numero_manifiesto (MAN-YYYYMMDD-XXXX)
        today = datetime.now().strftime('%Y%m%d')
        count_today = Manifiesto.query.filter(
            db.func.date(Manifiesto.fecha_creacion) == datetime.now().date()
        ).count()
        sequence = str(count_today + 1).zfill(4)
        numero_manifiesto = f"MAN-{today}-{sequence}"

        # Generate codigo_qr
        codigo_qr = generate_codigo_qr(prefix="MAN-QR")

        # BEGIN TRANSACTION
        # Create manifiesto
        manifiesto = Manifiesto(
            numero_manifiesto=numero_manifiesto,
            cliente_id=data['cliente_id'],
            estado='en_proceso',
            codigo_qr=codigo_qr,
            firma_operador=data.get('firma_operador'),
            usuario_creador_id=user_id
        )
        db.session.add(manifiesto)
        db.session.flush()  # Get manifiesto.id

        # Create detalles and update stock
        detalles_objs = []
        for prod_data in productos_data:
            producto = prod_data['producto']

            # Create detalle
            detalle = DetalleManifiesto(
                manifiesto_id=manifiesto.id,
                producto_id=producto.id,
                cantidad=prod_data['cantidad'],
                precio_unitario=prod_data['precio_unitario'],
                subtotal=prod_data['subtotal']
            )
            db.session.add(detalle)
            detalles_objs.append(detalle)

            # Decrease product stock
            producto.cantidad = float(producto.cantidad) - prod_data['cantidad']

            # Create movimiento
            movimiento = Movimiento(
                producto_id=producto.id,
                tipo='salida',
                cantidad=prod_data['cantidad'],
                observaciones=f"Manifiesto {numero_manifiesto}",
                usuario_id=user_id
            )
            db.session.add(movimiento)

        db.session.flush()  # Ensure all objects have IDs

        # Generate manifest QR code
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        success, qr_file_path = generate_manifest_qr(numero_manifiesto, codigo_qr, frontend_url)

        if not success:
            db.session.rollback()
            return jsonify({"error": "Error generando código QR del manifiesto"}), 500

        # Generate PDF
        pdf_path = f"/data/manifiestos/en_proceso/{numero_manifiesto}.pdf"
        pdf_success = generate_manifest_pdf(
            manifiesto=manifiesto,
            cliente=cliente,
            detalles=detalles_objs,
            qr_code_path=qr_file_path,
            output_path=pdf_path,
            is_final=False
        )

        if not pdf_success:
            db.session.rollback()
            return jsonify({"error": "Error generando PDF del manifiesto"}), 500

        # Update manifiesto with PDF path
        manifiesto.pdf_path_proceso = pdf_path

        # COMMIT TRANSACTION
        db.session.commit()

        # Return complete manifest
        return jsonify({
            "message": "Manifiesto creado exitosamente",
            "manifiesto": manifiesto.to_dict(include_relations=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@bp.route('/<int:id>/firma-cliente', methods=['PUT'])
def add_client_signature(id):
    """
    Client delivery confirmation - PUBLIC endpoint.
    Requires codigo_qr for verification instead of JWT.
    """
    codigo_qr = request.args.get('codigo_qr')
    data = request.get_json()

    # Validate codigo_qr
    if not codigo_qr:
        return jsonify({"error": "Código QR es requerido"}), 400

    # Validate firma_cliente
    if not data or 'firma_cliente' not in data or not data['firma_cliente']:
        return jsonify({"error": "Firma del cliente es requerida"}), 400

    # Get manifiesto
    manifiesto = Manifiesto.query.get(id)
    if not manifiesto:
        return jsonify({"error": "Manifiesto no encontrado"}), 404

    # Verify codigo_qr matches
    if manifiesto.codigo_qr != codigo_qr:
        return jsonify({"error": "Código QR inválido para este manifiesto"}), 400

    # Verify estado
    if manifiesto.estado == 'entregado':
        return jsonify({"error": "Este manifiesto ya fue entregado"}), 400

    if manifiesto.estado not in ['en_transito', 'en_proceso']:
        return jsonify({"error": "Solo se pueden firmar manifiestos en tránsito o en proceso"}), 400

    try:
        # Update manifiesto
        manifiesto.firma_cliente = data['firma_cliente']
        manifiesto.estado = 'entregado'
        manifiesto.fecha_entrega = datetime.utcnow()

        db.session.flush()

        # Generate final PDF with both signatures
        pdf_final_path = f"/data/manifiestos/finalizados/{manifiesto.numero_manifiesto}_final.pdf"

        # Get QR code path
        qr_path = f"/data/manifiestos/en_proceso/qr_{manifiesto.numero_manifiesto}.png"

        # Get cliente and detalles
        cliente = manifiesto.cliente
        detalles = manifiesto.detalles.all()

        pdf_success = generate_manifest_pdf(
            manifiesto=manifiesto,
            cliente=cliente,
            detalles=detalles,
            qr_code_path=qr_path,
            output_path=pdf_final_path,
            is_final=True
        )

        if not pdf_success:
            db.session.rollback()
            return jsonify({"error": "Error generando PDF final"}), 500

        # Update pdf_path_final
        manifiesto.pdf_path_final = pdf_final_path

        db.session.commit()

        return jsonify({
            "message": "Entrega confirmada exitosamente",
            "manifiesto": manifiesto.to_dict(include_relations=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@bp.route('/<int:id>/estado', methods=['PUT'])
@jwt_required()
@role_required(1, 2, 4)  # Administrador, Oficina, Delivery
def update_manifest_status(id):
    """Update manifest status (e.g., en_proceso -> en_transito)"""
    data = request.get_json()

    is_valid, error = validate_required_fields(data, ['estado'])
    if not is_valid:
        return jsonify({"error": error}), 400

    valid_estados = ['en_proceso', 'en_transito', 'entregado', 'cancelado']
    if data['estado'] not in valid_estados:
        return jsonify({"error": f"Estado inválido. Debe ser: {', '.join(valid_estados)}"}), 400

    manifiesto = Manifiesto.query.get(id)
    if not manifiesto:
        return jsonify({"error": "Manifiesto no encontrado"}), 404

    try:
        manifiesto.estado = data['estado']

        # If marking as en_transito, optionally set delivery user
        if data['estado'] == 'en_transito' and data.get('usuario_entrega_id'):
            manifiesto.usuario_entrega_id = data['usuario_entrega_id']

        db.session.commit()

        return jsonify({
            "message": "Estado actualizado exitosamente",
            "manifiesto": manifiesto.to_dict(include_relations=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
