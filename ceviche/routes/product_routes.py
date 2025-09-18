from flask import Blueprint, request, jsonify
from utils.decorators import area_required, admin_required, user_or_higher
from services.product_service import ProductService
from models import Category
import os
from werkzeug.utils import secure_filename
from datetime import datetime

products_bp = Blueprint('products', __name__)

@products_bp.route('', methods=['GET'])
@area_required('inventario')
def get_products(current_user):
    """Ver productos - Accesible para USER, ADMIN y SUPERADMIN"""
    try:
        # Parámetros de búsqueda opcionales
        search_query = request.args.get('search')
        category_id = request.args.get('category_id')
        
        if search_query:
            products = ProductService.search_products(search_query)
        else:
            products = ProductService.get_all_products()
        
        # Filtrar por categoría si se especifica
        if category_id:
            try:
                category_id = int(category_id)
                products = [p for p in products if p['category_id'] == category_id]
            except ValueError:
                return jsonify({'message': 'ID de categoría inválido'}), 400
        
        return jsonify({
            'products': products,
            'user_role': current_user.role,
            'permissions': ['read']
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@products_bp.route('', methods=['POST'])
@admin_required
def create_product(current_user):
    """Crear productos - Solo ADMIN y SUPERADMIN"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Datos requeridos'}), 400
        
        product, error = ProductService.create_product(data)
        
        if error:
            return jsonify({'message': error}), 400
        
        return jsonify({
            'message': 'Producto creado exitosamente',
            'product': product.to_dict(),
            'created_by': current_user.username
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@products_bp.route('/<int:product_id>', methods=['GET'])
@area_required('inventario')
def get_product(current_user, product_id):
    """Ver producto específico - USER, ADMIN y SUPERADMIN"""
    try:
        product_dict = ProductService.get_product_by_id(product_id)
        
        if not product_dict:
            return jsonify({'message': 'Producto no encontrado'}), 404
        
        return jsonify({
            'id': product_dict['id'],
            'name': product_dict['name'],
            'description': product_dict['description'],
            'price': product_dict['price'],
            'stock': product_dict['stock'],
            'category_id': product_dict['category_id'],
            'user_role': current_user.role
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@products_bp.route('/<int:product_id>', methods=['PUT'])
@admin_required
def update_product(current_user, product_id):
    """Actualizar productos - Solo ADMIN y SUPERADMIN"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Datos requeridos'}), 400
        
        product, error = ProductService.update_product(product_id, data)
        
        if error:
            return jsonify({'message': error}), 400
        
        return jsonify({
            'message': 'Producto actualizado exitosamente',
            'product': product.to_dict(),
            'updated_by': current_user.username
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@products_bp.route('/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(current_user, product_id):
    """Eliminar productos - Solo ADMIN y SUPERADMIN"""
    try:
        success, message = ProductService.delete_product(product_id)
        
        if success:
            return jsonify({
                'message': message,
                'deleted_by': current_user.username
            }), 200
        else:
            return jsonify({'message': message}), 404
            
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@products_bp.route('/permissions', methods=['GET'])
@user_or_higher
def get_user_permissions(current_user):
    """Ver permisos del usuario en inventario"""
    from utils.decorators import get_user_permissions
    
    permissions = get_user_permissions(current_user)
    can_modify = current_user.role in ['admin', 'superadmin']
    
    return jsonify({
        'user': current_user.username,
        'role': current_user.role,
        'areas_allowed': permissions,
        'inventory_permissions': {
            'read': 'inventario' in permissions,
            'create': can_modify,
            'update': can_modify, 
            'delete': can_modify
        }
    }), 200

@products_bp.route('/upload-image', methods=['POST'])
@admin_required
def upload_product_image(current_user):
    """Subir imagen de producto - Solo ADMIN y SUPERADMIN"""
    try:
        if 'image' not in request.files:
            return jsonify({'message': 'No se encontró archivo de imagen'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'message': 'No se seleccionó archivo'}), 400
        
        # Validar tipo de archivo
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'message': 'Tipo de archivo no permitido'}), 400
        
        # Crear nombre de archivo seguro
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        secure_name = f"product_{timestamp}_{name}{ext}"
        
        # Crear directorio si no existe
        upload_folder = os.path.join('static', 'images', 'products')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Guardar archivo
        file_path = os.path.join(upload_folder, secure_name)
        file.save(file_path)
        
        # URL relativa para la base de datos
        image_url = f"/static/images/products/{secure_name}"
        
        return jsonify({
            'message': 'Imagen subida exitosamente',
            'image_url': image_url,
            'filename': secure_name,
            'uploaded_by': current_user.username
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error al subir imagen: {str(e)}'}), 500
