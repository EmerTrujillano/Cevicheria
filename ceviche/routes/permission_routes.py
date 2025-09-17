from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import timedelta
from models import User, TemporaryPermission
from services.permission_service import PermissionService
from utils.decorators import superadmin_required, SYSTEM_AREAS
from utils.validators import validate_duration_unit

permissions_bp = Blueprint('permissions', __name__)

@permissions_bp.route('/temporary-permissions', methods=['GET'])
@superadmin_required
def get_temporary_permissions(current_user):
    """Obtener permisos temporales - Solo superadmin (compatibilidad)"""
    try:
        # Por compatibilidad con templates antiguos
        return jsonify({
            'temporary_permissions': [],
            'message': 'Sistema de permisos temporales deshabilitado en la nueva versión'
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@permissions_bp.route('/areas', methods=['GET'])
@jwt_required()
def get_system_areas():
    """Obtener todas las áreas del sistema y permisos del usuario actual"""
    try:
        current_user_id = get_jwt_identity()
        areas_info, error = PermissionService.get_user_permissions(current_user_id)
        
        if error:
            return jsonify({'message': error}), 404
        
        current_user = User.query.get(current_user_id)
        
        return jsonify({
            'user': current_user.to_dict(),
            'areas': areas_info
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@permissions_bp.route('/grant', methods=['POST'])
@superadmin_required
def grant_temporary_permission(current_user):
    """Otorgar permiso temporal"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Datos requeridos'}), 400
        
        required_fields = ['user_id', 'area', 'hours']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({'message': f'Campos requeridos faltantes: {", ".join(missing_fields)}'}), 400
        
        user_id = data['user_id']
        area = data['area']
        hours = data['hours']
        reason = data.get('reason')
        
        # Validaciones
        try:
            user_id = int(user_id)
            hours = float(hours)
        except ValueError:
            return jsonify({'message': 'user_id y hours deben ser números'}), 400
        
        if hours <= 0:
            return jsonify({'message': 'Las horas deben ser un número positivo'}), 400
        
        temp_permission, error = PermissionService.grant_temporary_permission(
            user_id, area, hours, current_user.id, reason
        )
        
        if error:
            return jsonify({'message': error}), 400
        
        return jsonify({
            'message': f'Permiso temporal otorgado exitosamente',
            'permission': temp_permission.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@permissions_bp.route('/grant-multiple', methods=['POST'])
@superadmin_required
def grant_multiple_temporary_permissions(current_user):
    """Otorgar permisos temporales a múltiples áreas"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Datos requeridos'}), 400
        
        required_fields = ['user_id', 'areas', 'hours']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({'message': f'Campos requeridos faltantes: {", ".join(missing_fields)}'}), 400
        
        user_id = data['user_id']
        areas = data['areas']
        hours = data['hours']
        reason = data.get('reason')
        
        # Validaciones
        try:
            user_id = int(user_id)
            hours = float(hours)
        except ValueError:
            return jsonify({'message': 'user_id y hours deben ser números'}), 400
        
        if not isinstance(areas, list) or not areas:
            return jsonify({'message': 'areas debe ser una lista no vacía'}), 400
        
        if hours <= 0:
            return jsonify({'message': 'Las horas deben ser un número positivo'}), 400
        
        permissions, error = PermissionService.grant_multiple_temporary_permissions(
            user_id, areas, hours, current_user.id, reason
        )
        
        if error and not permissions:
            return jsonify({'message': error}), 400
        
        return jsonify({
            'message': f'Permisos temporales otorgados exitosamente',
            'details': error if permissions else None,
            'permissions': [perm.to_dict() for perm in permissions] if permissions else [],
            'areas_granted': areas,
            'count': len(permissions) if permissions else 0
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@permissions_bp.route('/revoke', methods=['POST'])
@superadmin_required
def revoke_temporary_permission(current_user):
    """Revocar permiso temporal"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Datos requeridos'}), 400
        
        user_id = data.get('user_id')
        area = data.get('area')
        
        if not user_id or not area:
            return jsonify({'message': 'user_id y area son requeridos'}), 400
        
        try:
            user_id = int(user_id)
        except ValueError:
            return jsonify({'message': 'user_id debe ser un número'}), 400
        
        success, message = PermissionService.revoke_temporary_permission(user_id, area)
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'message': message}), 404
            
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@permissions_bp.route('/active', methods=['GET'])
@superadmin_required
def list_active_permissions(current_user):
    """Listar todos los permisos temporales activos"""
    try:
        permissions = PermissionService.get_active_permissions()
        return jsonify(permissions), 200
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@permissions_bp.route('/<int:permission_id>', methods=['DELETE'])
@superadmin_required
def remove_temporary_permission(current_user, permission_id):
    """Eliminar permiso temporal específico"""
    try:
        permission = TemporaryPermission.query.get(permission_id)
        if not permission:
            return jsonify({'message': 'Permiso no encontrado'}), 404
        
        permission.is_active = False
        from config.extensions import db
        db.session.commit()
        
        return jsonify({'message': 'Permiso revocado exitosamente'}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@permissions_bp.route('/user/<int:user_id>', methods=['GET'])
@superadmin_required
def get_user_permissions(current_user, user_id):
    """Obtener permisos de un usuario específico"""
    try:
        areas_info, error = PermissionService.get_user_permissions(user_id)
        
        if error:
            return jsonify({'message': error}), 404
        
        user = User.query.get(user_id)
        
        return jsonify({
            'user': user.to_dict(),
            'areas': areas_info
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@permissions_bp.route('/cleanup', methods=['POST'])
@superadmin_required
def cleanup_expired_permissions(current_user):
    """Limpiar permisos expirados"""
    try:
        expired_count = PermissionService.cleanup_expired_permissions()
        return jsonify({
            'message': f'Se limpiaron {expired_count} permisos expirados'
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500
