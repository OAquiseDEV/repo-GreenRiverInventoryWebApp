from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from api.models import db, Usuario, Role
from api.utils.validators import validate_required_fields, validate_email
from api.utils.decorators import role_required

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint.
    Returns JWT token and user data on successful authentication.
    """
    data = request.get_json()

    # Validate required fields
    is_valid, error = validate_required_fields(data, ['email', 'password'])
    if not is_valid:
        return jsonify({"error": "Email y contraseña son requeridos"}), 400

    email = data['email']
    password = data['password']

    # Find active user by email
    usuario = Usuario.query.filter_by(email=email, activo=True).first()

    if not usuario:
        return jsonify({"error": "Credenciales inválidas"}), 401

    # Verify password
    if not usuario.check_password(password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    # Create JWT token with user_id and role_id as identity
    identity = {
        "user_id": usuario.id,
        "role_id": usuario.role_id
    }
    access_token = create_access_token(identity=identity)

    # Return token and user data
    return jsonify({
        "access_token": access_token,
        "user": usuario.to_dict(include_role=True)
    }), 200

@bp.route('/register', methods=['POST'])
@jwt_required()
@role_required(1)  # Only Administrador can register new users
def register():
    """
    Register new user endpoint.
    Only accessible by Administrador role.
    """
    data = request.get_json()

    # Validate required fields
    is_valid, error = validate_required_fields(data, ['nombre', 'email', 'password', 'role_id'])
    if not is_valid:
        return jsonify({"error": error}), 400

    # Validate email format
    if not validate_email(data['email']):
        return jsonify({"error": "Email inválido"}), 400

    # Check if email already exists
    existing_user = Usuario.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"error": "El email ya está registrado"}), 400

    # Validate role exists
    role = Role.query.get(data['role_id'])
    if not role:
        return jsonify({"error": "Rol no encontrado"}), 404

    # Create new user
    try:
        nuevo_usuario = Usuario(
            nombre=data['nombre'],
            email=data['email'],
            role_id=data['role_id'],
            activo=data.get('activo', True)
        )
        nuevo_usuario.set_password(data['password'])

        db.session.add(nuevo_usuario)
        db.session.commit()

        return jsonify({
            "message": "Usuario creado exitosamente",
            "user": nuevo_usuario.to_dict(include_role=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current user information from JWT token.
    """
    current_user_identity = get_jwt_identity()
    user_id = current_user_identity['user_id']

    usuario = Usuario.query.get(user_id)
    if not usuario or not usuario.activo:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify(usuario.to_dict(include_role=True)), 200

@bp.route('/roles', methods=['GET'])
@jwt_required()
@role_required(1)  # Only Administrador
def get_roles():
    """
    Get all roles.
    Only accessible by Administrador.
    """
    roles = Role.query.all()
    return jsonify([role.to_dict() for role in roles]), 200
