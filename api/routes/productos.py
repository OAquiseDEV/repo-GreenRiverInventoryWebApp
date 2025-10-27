from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.models import db, Producto, Categoria, Cliente, Etiqueta, Movimiento, Transformacion
from api.utils.decorators import role_required
from api.utils.validators import validate_required_fields, validate_length, validate_non_negative_number, validate_positive_number
from api.services.qr_service import generate_codigo_qr, generate_product_qr

bp = Blueprint('productos', __name__)

@bp.route('', methods=['GET'])
@jwt_required()
@role_required(1, 2, 3)  # Administrador, Oficina, Operario
def list_products():
    """List all products with optional filtering"""
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(100, max(1, per_page))  # Limit between 1 and 100

    # Filters
    categoria_id = request.args.get('categoria_id', type=int)
    estado = request.args.get('estado')
    search = request.args.get('search')  # Search by name

    # Build query
    query = Producto.query

    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)

    if estado:
        query = query.filter_by(estado=estado)

    if search:
        query = query.filter(Producto.nombre.ilike(f'%{search}%'))

    # Order by most recent first
    query = query.order_by(Producto.created_at.desc())

    # Paginate
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "items": [producto.to_dict(include_relations=True) for producto in paginated.items],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": paginated.total,
            "pages": paginated.pages
        }
    }), 200

@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
@role_required(1, 2, 3)  # Administrador, Oficina, Operario
def get_product(id):
    """Get single product details"""
    producto = Producto.query.get(id)
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404

    return jsonify(producto.to_dict(include_relations=True)), 200

@bp.route('', methods=['POST'])
@jwt_required()
@role_required(1, 2)  # Administrador, Oficina
def create_product():
    """
    Create new product with QR code generation.
    Follows exact specification from planning.md
    """
    data = request.get_json()
    current_user = get_jwt_identity()
    user_id = current_user['user_id']

    # Validate required fields
    is_valid, error = validate_required_fields(data, ['nombre', 'categoria_id', 'cantidad'])
    if not is_valid:
        return jsonify({"error": error}), 400

    # Validate nombre length
    is_valid, error = validate_length(data['nombre'], min_length=3, max_length=200)
    if not is_valid:
        return jsonify({"error": f"Nombre: {error}"}), 400

    # Validate cantidad
    is_valid, error = validate_non_negative_number(data['cantidad'], "Cantidad")
    if not is_valid:
        return jsonify({"error": error}), 400

    # Verify categoria exists
    categoria = Categoria.query.get(data['categoria_id'])
    if not categoria:
        return jsonify({"error": "Categoría no encontrada"}), 404

    # Verify cliente exists if provided
    cliente_id = data.get('cliente_id')
    if cliente_id:
        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            return jsonify({"error": "Cliente no encontrado"}), 404

    # Default estado if not provided
    estado = data.get('estado', 'No terminado')

    try:
        # Generate unique codigo_qr
        codigo_qr = generate_codigo_qr(prefix="PROD")

        # Ensure uniqueness
        while Producto.query.filter_by(codigo_qr=codigo_qr).first():
            codigo_qr = generate_codigo_qr(prefix="PROD")

        # BEGIN TRANSACTION
        # Create product
        producto = Producto(
            nombre=data['nombre'],
            categoria_id=data['categoria_id'],
            medida=data.get('medida'),
            estado=estado,
            cantidad=data['cantidad'],
            cliente_id=cliente_id,
            codigo_qr=codigo_qr,
            created_by=user_id
        )
        db.session.add(producto)
        db.session.flush()  # Get producto.id

        # Generate QR code image
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:5173')
        success, qr_file_path = generate_product_qr(producto.id, codigo_qr, frontend_url)

        if not success:
            db.session.rollback()
            return jsonify({"error": "Error generando código QR"}), 500

        # Create etiqueta record
        etiqueta = Etiqueta(
            producto_id=producto.id,
            tipo='qr_producto',
            ruta_archivo=qr_file_path,
            formato='png'
        )
        db.session.add(etiqueta)

        # Create initial movimiento (entrada)
        movimiento = Movimiento(
            producto_id=producto.id,
            tipo='entrada',
            cantidad=data['cantidad'],
            observaciones='Stock inicial',
            usuario_id=user_id
        )
        db.session.add(movimiento)

        # COMMIT TRANSACTION
        db.session.commit()

        # Return product with all relations
        return jsonify({
            "message": "Producto creado exitosamente",
            "producto": producto.to_dict(include_relations=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@role_required(1, 2)  # Administrador, Oficina
def update_product(id):
    """Update product"""
    producto = Producto.query.get(id)
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404

    data = request.get_json()

    try:
        # Update fields if provided
        if 'nombre' in data:
            is_valid, error = validate_length(data['nombre'], min_length=3, max_length=200)
            if not is_valid:
                return jsonify({"error": f"Nombre: {error}"}), 400
            producto.nombre = data['nombre']

        if 'medida' in data:
            producto.medida = data['medida']

        if 'estado' in data:
            producto.estado = data['estado']

        if 'categoria_id' in data:
            categoria = Categoria.query.get(data['categoria_id'])
            if not categoria:
                return jsonify({"error": "Categoría no encontrada"}), 404
            producto.categoria_id = data['categoria_id']

        if 'cliente_id' in data:
            if data['cliente_id']:
                cliente = Cliente.query.get(data['cliente_id'])
                if not cliente:
                    return jsonify({"error": "Cliente no encontrado"}), 404
            producto.cliente_id = data['cliente_id']

        db.session.commit()

        return jsonify({
            "message": "Producto actualizado exitosamente",
            "producto": producto.to_dict(include_relations=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@role_required(1)  # Only Administrador
def delete_product(id):
    """Delete product"""
    producto = Producto.query.get(id)
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404

    try:
        db.session.delete(producto)
        db.session.commit()
        return jsonify({"message": "Producto eliminado exitosamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bp.route('/transformar', methods=['POST'])
@jwt_required()
@role_required(1, 3)  # Administrador, Operario
def transform_product():
    """
    Transform product state (e.g., Untreated → Treated).
    Implements atomic transaction with row locking.
    """
    data = request.get_json()
    current_user = get_jwt_identity()
    user_id = current_user['user_id']

    # Validate required fields
    is_valid, error = validate_required_fields(data, [
        'producto_origen_id', 'producto_destino_id', 'cantidad', 'tipo_transformacion'
    ])
    if not is_valid:
        return jsonify({"error": error}), 400

    # Validate cantidad
    is_valid, error = validate_positive_number(data['cantidad'], "Cantidad")
    if not is_valid:
        return jsonify({"error": error}), 400

    try:
        # Query products with row locks (FOR UPDATE)
        producto_origen = db.session.query(Producto).filter_by(
            id=data['producto_origen_id']
        ).with_for_update().first()

        if not producto_origen:
            return jsonify({"error": "Producto origen no encontrado"}), 404

        producto_destino = db.session.query(Producto).filter_by(
            id=data['producto_destino_id']
        ).with_for_update().first()

        if not producto_destino:
            return jsonify({"error": "Producto destino no encontrado"}), 404

        # Verify sufficient stock
        cantidad = float(data['cantidad'])
        if float(producto_origen.cantidad) < cantidad:
            return jsonify({
                "error": f"Stock insuficiente en producto origen (disponible: {producto_origen.cantidad}, requerido: {cantidad})"
            }), 409

        # BEGIN TRANSACTION (already started by with_for_update)
        # Update producto origen
        producto_origen.cantidad = float(producto_origen.cantidad) - cantidad

        # Update producto destino
        producto_destino.cantidad = float(producto_destino.cantidad) + cantidad

        # Create transformacion record
        transformacion = Transformacion(
            producto_origen_id=producto_origen.id,
            producto_destino_id=producto_destino.id,
            cantidad=cantidad,
            tipo_transformacion=data['tipo_transformacion'],
            observaciones=data.get('observaciones'),
            usuario_id=user_id
        )
        db.session.add(transformacion)

        # COMMIT TRANSACTION
        db.session.commit()

        # Return transformation with updated products
        return jsonify({
            "message": "Transformación realizada exitosamente",
            "transformacion": transformacion.to_dict(include_relations=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
