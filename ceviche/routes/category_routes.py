from flask import Blueprint, request, jsonify
from config.extensions import db
from models import Category, Product, User
from utils.decorators import area_required, admin_required, user_or_higher
from utils.validators import validate_required_fields

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('', methods=['GET'])
@area_required('categorias')
def get_categories(current_user):
    """Ver categorías - ADMIN y SUPERADMIN (usuarios no tienen acceso a categorías)"""
    try:
        categories = Category.query.all()
        return jsonify({
            'categories': [category.to_dict() for category in categories],
            'user_role': current_user.role,
            'permissions': ['read']
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@categories_bp.route('', methods=['POST'])
@admin_required
def create_category(current_user):
    """Crear categorías - Solo ADMIN y SUPERADMIN"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Datos requeridos'}), 400
        
        missing_fields = validate_required_fields(data, ['name'])
        if missing_fields:
            return jsonify({'message': f'Campos requeridos faltantes: {", ".join(missing_fields)}'}), 400
        
        # Verificar si la categoría ya existe
        existing_category = Category.query.filter_by(name=data['name']).first()
        if existing_category:
            return jsonify({'message': 'La categoría ya existe'}), 409
        
        category = Category(
            name=data['name'],
            description=data.get('description', '')
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Categoría creada exitosamente',
            'category': category.to_dict(),
            'created_by': current_user.username
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@categories_bp.route('/<int:category_id>', methods=['GET'])
@area_required('categorias')
def get_category(current_user, category_id):
    """Ver categoría específica - Solo ADMIN y SUPERADMIN"""
    try:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'message': 'Categoría no encontrada'}), 404
        
        return jsonify({
            'category': category.to_dict(),
            'user_role': current_user.role
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@categories_bp.route('/<int:category_id>', methods=['PUT'])
@admin_required
def update_category(current_user, category_id):
    """Actualizar categorías - Solo ADMIN y SUPERADMIN"""
    try:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'message': 'Categoría no encontrada'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Datos requeridos'}), 400
        
        # Verificar nombre único si se cambia
        if 'name' in data and data['name'] != category.name:
            existing_category = Category.query.filter_by(name=data['name']).first()
            if existing_category:
                return jsonify({'message': 'Ya existe una categoría con ese nombre'}), 409
        
        # Actualizar campos
        if 'name' in data:
            category.name = data['name']
        if 'description' in data:
            category.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Categoría actualizada exitosamente',
            'category': category.to_dict(),
            'updated_by': current_user.username
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@categories_bp.route('/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(current_user, category_id):
    """Eliminar categorías - Solo ADMIN y SUPERADMIN"""
    try:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'message': 'Categoría no encontrada'}), 404
        
        # Verificar si hay productos asociados
        products_count = Product.query.filter_by(category_id=category_id).count()
        if products_count > 0:
            return jsonify({'message': f'No se puede eliminar. Hay {products_count} producto(s) asociado(s)'}), 409
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Categoría eliminada exitosamente',
            'deleted_by': current_user.username
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500
