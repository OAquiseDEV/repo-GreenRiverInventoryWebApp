from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from api.models import db, Categoria
from api.utils.decorators import role_required
from api.utils.validators import validate_required_fields

bp = Blueprint('categorias', __name__)

@bp.route('', methods=['GET'])
@jwt_required()
def list_categories():
    """List all categories (accessible by all authenticated users)"""
    categorias = Categoria.query.order_by(Categoria.nombre.asc()).all()
    return jsonify([categoria.to_dict() for categoria in categorias]), 200

@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_category(id):
    """Get single category"""
    categoria = Categoria.query.get(id)
    if not categoria:
        return jsonify({"error": "Categoría no encontrada"}), 404

    return jsonify(categoria.to_dict()), 200

@bp.route('', methods=['POST'])
@jwt_required()
@role_required(1, 2)  # Administrador, Oficina
def create_category():
    """Create new category"""
    data = request.get_json()

    # Validate required fields
    is_valid, error = validate_required_fields(data, ['nombre'])
    if not is_valid:
        return jsonify({"error": error}), 400

    # Check if category already exists
    existing = Categoria.query.filter_by(nombre=data['nombre']).first()
    if existing:
        return jsonify({"error": "La categoría ya existe"}), 400

    try:
        categoria = Categoria(
            nombre=data['nombre'],
            descripcion=data.get('descripcion')
        )
        db.session.add(categoria)
        db.session.commit()

        return jsonify({
            "message": "Categoría creada exitosamente",
            "categoria": categoria.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@role_required(1, 2)  # Administrador, Oficina
def update_category(id):
    """Update category"""
    categoria = Categoria.query.get(id)
    if not categoria:
        return jsonify({"error": "Categoría no encontrada"}), 404

    data = request.get_json()

    try:
        if 'nombre' in data:
            # Check if new name already exists
            existing = Categoria.query.filter_by(nombre=data['nombre']).first()
            if existing and existing.id != id:
                return jsonify({"error": "La categoría ya existe"}), 400
            categoria.nombre = data['nombre']

        if 'descripcion' in data:
            categoria.descripcion = data['descripcion']

        db.session.commit()

        return jsonify({
            "message": "Categoría actualizada exitosamente",
            "categoria": categoria.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
