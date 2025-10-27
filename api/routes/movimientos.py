from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.models import db, Movimiento, Producto
from api.utils.decorators import role_required
from api.utils.validators import validate_required_fields, validate_positive_number

bp = Blueprint('movimientos', __name__)

@bp.route('', methods=['GET'])
@jwt_required()
@role_required(1, 2)  # Administrador, Oficina
def list_movements():
    """List all movements with filtering and pagination"""
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(100, max(1, per_page))

    # Filters
    producto_id = request.args.get('producto_id', type=int)
    tipo = request.args.get('tipo')  # entrada, salida, ajuste
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')

    # Build query
    query = Movimiento.query

    if producto_id:
        query = query.filter_by(producto_id=producto_id)

    if tipo:
        query = query.filter_by(tipo=tipo)

    if fecha_desde:
        query = query.filter(Movimiento.created_at >= fecha_desde)

    if fecha_hasta:
        query = query.filter(Movimiento.created_at <= fecha_hasta)

    # Order by most recent first
    query = query.order_by(Movimiento.created_at.desc())

    # Paginate
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "items": [mov.to_dict(include_relations=True) for mov in paginated.items],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": paginated.total,
            "pages": paginated.pages
        }
    }), 200

@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
@role_required(1, 2)  # Administrador, Oficina
def get_movement(id):
    """Get single movement details"""
    movimiento = Movimiento.query.get(id)
    if not movimiento:
        return jsonify({"error": "Movimiento no encontrado"}), 404

    return jsonify(movimiento.to_dict(include_relations=True)), 200

@bp.route('', methods=['POST'])
@jwt_required()
@role_required(1, 2)  # Administrador, Oficina
def create_movement():
    """
    Register manual movement (entrada, salida, ajuste).
    Updates product stock accordingly.
    """
    data = request.get_json()
    current_user = get_jwt_identity()
    user_id = current_user['user_id']

    # Validate required fields
    is_valid, error = validate_required_fields(data, ['producto_id', 'tipo', 'cantidad'])
    if not is_valid:
        return jsonify({"error": error}), 400

    # Validate tipo
    if data['tipo'] not in ['entrada', 'salida', 'ajuste']:
        return jsonify({"error": "Tipo debe ser: entrada, salida o ajuste"}), 400

    # Validate cantidad
    is_valid, error = validate_positive_number(data['cantidad'], "Cantidad")
    if not is_valid:
        return jsonify({"error": error}), 400

    # Verify producto exists
    producto = Producto.query.get(data['producto_id'])
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404

    # For salida, verify sufficient stock
    cantidad = float(data['cantidad'])
    if data['tipo'] == 'salida':
        if float(producto.cantidad) < cantidad:
            return jsonify({
                "error": f"Stock insuficiente (disponible: {producto.cantidad}, requerido: {cantidad})"
            }), 409

    try:
        # Create movimiento
        movimiento = Movimiento(
            producto_id=data['producto_id'],
            tipo=data['tipo'],
            cantidad=cantidad,
            observaciones=data.get('observaciones'),
            usuario_id=user_id
        )
        db.session.add(movimiento)

        # Update product stock
        if data['tipo'] == 'entrada':
            producto.cantidad = float(producto.cantidad) + cantidad
        elif data['tipo'] == 'salida':
            producto.cantidad = float(producto.cantidad) - cantidad
        elif data['tipo'] == 'ajuste':
            # For ajuste, cantidad represents the new stock level
            producto.cantidad = cantidad

        db.session.commit()

        return jsonify({
            "message": "Movimiento registrado exitosamente",
            "movimiento": movimiento.to_dict(include_relations=True),
            "producto": producto.to_dict(include_relations=False)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
