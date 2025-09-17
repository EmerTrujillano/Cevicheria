from flask import Blueprint, request, jsonify
from config.extensions import db
from models import User
from utils.decorators import superadmin_required, area_required
from utils.validators import validate_user_role
from flask_bcrypt import Bcrypt

users_bp = Blueprint('users', __name__)
bcrypt = Bcrypt()

@users_bp.route('', methods=['GET'])
@superadmin_required
def get_users(current_user):
    """Ver todos los usuarios - Solo SUPERADMIN (para panel admin) o con permiso temporal"""
    try:
        users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in users],
            'total': len(users),
            'managed_by': current_user.username
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@users_bp.route('/list', methods=['GET'])
@area_required('usuarios')
def list_users(current_user):
    """Ver todos los usuarios - Con permiso temporal o superadmin"""
    try:
        users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in users],
            'total': len(users),
            'managed_by': current_user.username
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
@area_required('usuarios')
def get_user(current_user, user_id):
    """Ver usuario específico - Solo SUPERADMIN o con permiso temporal"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        
        return jsonify({
            'user': user.to_dict(),
            'managed_by': current_user.username
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@users_bp.route('/<int:user_id>/role', methods=['PUT'])
@area_required('roles')
def change_user_role(current_user, user_id):
    """Cambiar rol de usuario - Solo SUPERADMIN o con permiso temporal para roles"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Datos requeridos'}), 400
        
        new_role = data.get('role')
        
        if not new_role:
            return jsonify({'message': 'Rol requerido'}), 400
        
        if not validate_user_role(new_role):
            return jsonify({'message': 'Rol inválido. Roles válidos: user, admin, superadmin'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        
        # No permitir cambiar el rol del propio superadmin
        if user.id == current_user.id:
            return jsonify({'message': 'No puedes cambiar tu propio rol'}), 403
        
        old_role = user.role
        user.role = new_role
        db.session.commit()
        
        return jsonify({
            'message': f'Rol cambiado de {old_role} a {new_role}',
            'user': user.to_dict(),
            'changed_by': current_user.username
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@users_bp.route('', methods=['POST'])
@area_required('usuarios')
def create_user(current_user):
    """Crear nuevo usuario - Solo SUPERADMIN o con permiso temporal"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Datos requeridos'}), 400
        
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'user')
        
        if not username or not password:
            return jsonify({'message': 'Usuario y contraseña son requeridos'}), 400
        
        if not validate_user_role(role):
            return jsonify({'message': 'Rol inválido. Roles válidos: user, admin, superadmin'}), 400
        
        # Verificar que el usuario no existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'message': 'El usuario ya existe'}), 409
        
        # Crear nuevo usuario
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            username=username,
            password=hashed_password,
            role=role
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'Usuario creado exitosamente',
            'user': new_user.to_dict(),
            'created_by': current_user.username
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@area_required('usuarios')
def delete_user(current_user, user_id):
    """Eliminar usuario - Solo SUPERADMIN o con permiso temporal"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        
        # No permitir eliminar el propio superadmin
        if user.id == current_user.id:
            return jsonify({'message': 'No puedes eliminar tu propia cuenta'}), 403
        
        # No permitir eliminar el último superadmin
        if user.role == 'superadmin':
            superadmin_count = User.query.filter_by(role='superadmin').count()
            if superadmin_count <= 1:
                return jsonify({'message': 'No se puede eliminar el último superadministrador'}), 403
        
        username_to_delete = user.username
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'message': f'Usuario {username_to_delete} eliminado exitosamente',
            'deleted_by': current_user.username
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@users_bp.route('/roles', methods=['GET'])
@area_required('roles')
def get_available_roles(current_user):
    """Ver roles disponibles - Solo SUPERADMIN o con permiso temporal para roles"""
    from utils.decorators import ROLE_PERMISSIONS
    
    return jsonify({
        'available_roles': list(ROLE_PERMISSIONS.keys()),
        'role_descriptions': {
            role: info['description'] 
            for role, info in ROLE_PERMISSIONS.items()
        }
    }), 200
