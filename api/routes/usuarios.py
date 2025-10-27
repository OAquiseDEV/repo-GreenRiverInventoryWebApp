from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from api.models import db, Usuario, Role
from api.utils.decorators import role_required

bp = Blueprint('usuarios', __name__)

@bp.route('', methods=['GET'])
@jwt_required()
@role_required(1)  # Only Administrador
def list_users():
    """List all users (admin only)"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(100, max(1, per_page))

    query = Usuario.query.order_by(Usuario.created_at.desc())

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "items": [user.to_dict(include_role=True) for user in paginated.items],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": paginated.total,
            "pages": paginated.pages
        }
    }), 200

@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@role_required(1)  # Only Administrador
def update_user(id):
    """Update user role or active status"""
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    data = request.get_json()

    try:
        if 'role_id' in data:
            role = Role.query.get(data['role_id'])
            if not role:
                return jsonify({"error": "Rol no encontrado"}), 404
            usuario.role_id = data['role_id']

        if 'activo' in data:
            usuario.activo = bool(data['activo'])

        if 'nombre' in data:
            usuario.nombre = data['nombre']

        db.session.commit()

        return jsonify({
            "message": "Usuario actualizado exitosamente",
            "user": usuario.to_dict(include_role=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
