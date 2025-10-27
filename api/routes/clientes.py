from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from api.models import db, Cliente
from api.utils.decorators import role_required
from api.utils.validators import validate_required_fields, validate_email

bp = Blueprint('clientes', __name__)

@bp.route('', methods=['GET'])
@jwt_required()
@role_required(1, 2, 4)  # Administrador, Oficina, Delivery
def list_clients():
    """List all clients with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(100, max(1, per_page))

    search = request.args.get('search')

    query = Cliente.query

    if search:
        query = query.filter(Cliente.nombre.ilike(f'%{search}%'))

    query = query.order_by(Cliente.nombre.asc())

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "items": [cliente.to_dict() for cliente in paginated.items],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": paginated.total,
            "pages": paginated.pages
        }
    }), 200

@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
@role_required(1, 2, 4)  # Administrador, Oficina, Delivery
def get_client(id):
    """Get single client details"""
    cliente = Cliente.query.get(id)
    if not cliente:
        return jsonify({"error": "Cliente no encontrado"}), 404

    return jsonify(cliente.to_dict()), 200

@bp.route('', methods=['POST'])
@jwt_required()
@role_required(1, 2)  # Administrador, Oficina
def create_client():
    """Create new client"""
    data = request.get_json()

    # Validate required fields
    is_valid, error = validate_required_fields(data, ['nombre'])
    if not is_valid:
        return jsonify({"error": error}), 400

    # Validate email if provided
    if data.get('email') and not validate_email(data['email']):
        return jsonify({"error": "Email inválido"}), 400

    # Check if email already exists
    if data.get('email'):
        existing = Cliente.query.filter_by(email=data['email']).first()
        if existing:
            return jsonify({"error": "El email ya está registrado"}), 400

    try:
        cliente = Cliente(
            nombre=data['nombre'],
            email=data.get('email'),
            telefono=data.get('telefono'),
            direccion=data.get('direccion'),
            ruc_dni=data.get('ruc_dni')
        )
        db.session.add(cliente)
        db.session.commit()

        return jsonify({
            "message": "Cliente creado exitosamente",
            "cliente": cliente.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@role_required(1, 2)  # Administrador, Oficina
def update_client(id):
    """Update client"""
    cliente = Cliente.query.get(id)
    if not cliente:
        return jsonify({"error": "Cliente no encontrado"}), 404

    data = request.get_json()

    try:
        if 'nombre' in data:
            cliente.nombre = data['nombre']

        if 'email' in data:
            if data['email'] and not validate_email(data['email']):
                return jsonify({"error": "Email inválido"}), 400
            # Check if email already exists for another client
            if data['email']:
                existing = Cliente.query.filter_by(email=data['email']).first()
                if existing and existing.id != id:
                    return jsonify({"error": "El email ya está registrado"}), 400
            cliente.email = data['email']

        if 'telefono' in data:
            cliente.telefono = data['telefono']

        if 'direccion' in data:
            cliente.direccion = data['direccion']

        if 'ruc_dni' in data:
            cliente.ruc_dni = data['ruc_dni']

        db.session.commit()

        return jsonify({
            "message": "Cliente actualizado exitosamente",
            "cliente": cliente.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
