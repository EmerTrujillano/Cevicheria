"""
Decoradores para autenticación y autorización con JWT
"""
from functools import wraps
from flask import jsonify, current_app, redirect, url_for, request
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, get_jwt

# Sistema de permisos para cevichería
ROLE_PERMISSIONS = {
    'waiter': {
        'areas': ['mesas', 'pedidos', 'menu'],
        'description': 'Mozo - Gestión de mesas y pedidos'
    },
    'cocina': {
        'areas': ['cocina', 'pedidos'],
        'description': 'Cocina - Gestión de preparación de pedidos'
    },
    'cashier': {
        'areas': ['caja', 'pagos', 'ventas'],
        'description': 'Cajero - Procesamiento de pagos'
    },
    'admin': {
        'areas': ['mesas', 'pedidos', 'menu', 'cocina', 'caja', 'pagos', 'ventas', 'productos', 'usuarios', 'reportes', 'configuracion'],
        'description': 'Administrador - Acceso total al sistema'
    }
}

# Definición de áreas del sistema para cevichería
SYSTEM_AREAS = {
    'mesas': {
        'description': 'Gestión de mesas, zonas y pisos',
        'default_roles': ['waiter', 'admin']
    },
    'pedidos': {
        'description': 'Gestión de órdenes y comandas',
        'default_roles': ['waiter', 'cocina', 'admin']
    },
    'menu': {
        'description': 'Visualización del menú (público y staff)',
        'default_roles': ['waiter', 'admin']
    },
    'cocina': {
        'description': 'Gestión de preparación de platos',
        'default_roles': ['cocina', 'admin']
    },
    'caja': {
        'description': 'Procesamiento de pagos',
        'default_roles': ['cashier', 'admin']
    },
    'pagos': {
        'description': 'Gestión de transacciones',
        'default_roles': ['cashier', 'admin']
    },
    'ventas': {
        'description': 'Reportes de ventas',
        'default_roles': ['cashier', 'admin']
    },
    'productos': {
        'description': 'Gestión de productos del menú',
        'default_roles': ['admin']
    },
    'usuarios': {
        'description': 'Gestión de usuarios del sistema',
        'default_roles': ['admin']
    },
    'reportes': {
        'description': 'Reportes y estadísticas generales',
        'default_roles': ['admin']
    },
    'configuracion': {
        'description': 'Configuración del sistema',
        'default_roles': ['admin']
    }
}

def get_user_by_id(user_id):
    """Obtener usuario por ID de forma segura"""
    try:
        from models import User
        # Convertir string a int si es necesario
        if isinstance(user_id, str):
            user_id = int(user_id)
        return User.query.get(user_id)
    except Exception:
        return None

def validate_session_required(f):
    """Decorador que valida que la sesión del usuario sea válida"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            claims = get_jwt()
            
            # Obtener token de sesión del JWT
            session_token = claims.get('session_token')
            
            if not session_token:
                # Si no hay session_token, es un token antiguo - invalidar
                print(f"[SESSION] Token sin session_token para usuario {current_user_id} - RECHAZADO")
                return jsonify({
                    'message': 'Sesión inválida. Por favor inicia sesión nuevamente.',
                    'error_type': 'invalid_session',
                    'redirect_to_login': True
                }), 401
            
            # Validar sesión
            from services.session_service import SessionService
            is_valid, message = SessionService.validate_session(current_user_id, session_token)
            
            if not is_valid:
                print(f"[SESSION] Sesión inválida para usuario {current_user_id}: {message}")
                return jsonify({
                    'message': message,
                    'error_type': 'session_expired' if 'expirada' in message else 'session_invalid',
                    'redirect_to_login': True
                }), 401
            
            print(f"[SESSION] Sesión válida para usuario {current_user_id}")
            return f(*args, **kwargs)
            
        except Exception as e:
            print(f"[SESSION_DECORATOR] Error crítico: {str(e)}")
            # En caso de error crítico, denegar acceso por seguridad
            return jsonify({
                'message': 'Error de validación de sesión. Por favor inicia sesión nuevamente.',
                'error_type': 'session_error',
                'redirect_to_login': True
            }), 401
    
    return decorated_function

def has_area_access(user, area):
    """Verificar si un usuario tiene acceso a un área específica"""
    if not user or not user.role:
        return False
    
    # Verificar acceso por defecto según el rol
    if area in SYSTEM_AREAS:
        if user.role in SYSTEM_AREAS[area]['default_roles']:
            return True
    
    # Verificar permisos temporales activos
    from datetime import datetime
    from models import TemporaryPermission
    import pytz
    
    # Usar zona horaria de Lima
    lima_tz = pytz.timezone('America/Lima')
    now_lima = datetime.now(lima_tz)
    now_utc = now_lima.astimezone(pytz.UTC).replace(tzinfo=None)
    
    temp_perm = TemporaryPermission.query.filter_by(
        user_id=user.id,
        area=area,
        is_active=True
    ).filter(TemporaryPermission.expires_at > now_utc).first()
    
    return temp_perm is not None

def area_required(area_name):
    """Decorador para verificar acceso a área específica"""
    def decorator(f):
        @wraps(f)
        @validate_session_required  # Validar sesión primero
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                
                if not current_user_id:
                    return jsonify({'message': 'Token JWT inválido'}), 401
                
                current_user = get_user_by_id(current_user_id)
                
                if not current_user:
                    return jsonify({
                        'message': 'Usuario no encontrado. Redirigiendo al login...',
                        'error_type': 'user_not_found',
                        'redirect_to_login': True
                    }), 404
                
                if not has_area_access(current_user, area_name):
                    # Verificar si tiene permiso temporal activo pero ya expirado
                    from datetime import datetime
                    from models import TemporaryPermission
                    import pytz
                    
                    lima_tz = pytz.timezone('America/Lima')
                    now_lima = datetime.now(lima_tz)
                    now_utc = now_lima.astimezone(pytz.UTC).replace(tzinfo=None)
                    
                    expired_perm = TemporaryPermission.query.filter_by(
                        user_id=current_user.id,
                        area=area_name,
                        is_active=True
                    ).filter(TemporaryPermission.expires_at <= now_utc).first()
                    
                    if expired_perm:
                        # Desactivar el permiso expirado
                        expired_perm.is_active = False
                        from config.extensions import db
                        db.session.commit()
                        
                        # Convertir a hora de Lima para mostrar
                        expires_at_lima = pytz.UTC.localize(expired_perm.expires_at).astimezone(lima_tz)
                        
                        return jsonify({
                            'message': f'❌ Acceso Denegado ⏰ Permiso Temporal: Otorgado por: {expired_perm.granted_by} Expira: {expires_at_lima.strftime("%d/%m/%Y, %I:%M:%S %p")}',
                            'user_role': current_user.role,
                            'expired_permission': True
                        }), 403
                    
                    return jsonify({
                        'message': f'Acceso denegado al área: {area_name}. Usuario: {current_user.username} (Rol: {current_user.role})',
                        'user_role': current_user.role,
                        'username': current_user.username,
                        'required_area': area_name,
                        'default_roles_for_area': SYSTEM_AREAS.get(area_name, {}).get('default_roles', [])
                    }), 403
                    
                return f(current_user, *args, **kwargs)
            except Exception as e:
                return jsonify({'message': f'Error de autenticación: {str(e)}'}), 401
                
        return decorated_function
    return decorator

def admin_required(f):
    """Decorador para requerir permisos de administrador"""
    @wraps(f)
    @validate_session_required  # Validar sesión primero
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            if not current_user_id:
                return jsonify({'message': 'Token JWT inválido'}), 401
            
            current_user = get_user_by_id(current_user_id)
            
            if not current_user:
                return jsonify({
                    'message': 'Usuario no encontrado. Redirigiendo al login...',
                    'error_type': 'user_not_found',
                    'redirect_to_login': True
                }), 404
            
            if current_user.role not in ['admin', 'superadmin']:
                return jsonify({
                    'message': 'Acceso denegado. Se requieren permisos de administrador',
                    'current_role': current_user.role
                }), 403
                
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'message': f'Error de autenticación: {str(e)}'}), 401
    return decorated_function

def superadmin_required(f):
    """Decorador para requerir permisos de superadministrador"""
    @wraps(f)
    @validate_session_required  # Validar sesión primero
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            if not current_user_id:
                return jsonify({'message': 'Token JWT inválido'}), 401
            
            current_user = get_user_by_id(current_user_id)
            
            if not current_user:
                return jsonify({
                    'message': 'Usuario no encontrado. Redirigiendo al login...',
                    'error_type': 'user_not_found',
                    'redirect_to_login': True
                }), 404
            
            if current_user.role != 'superadmin':
                return jsonify({
                    'message': 'Acceso denegado. Solo superadministradores',
                    'current_role': current_user.role,
                    'user_id': current_user_id
                }), 403
                
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'message': f'Error de autenticación: {str(e)}'}), 401
    return decorated_function

def user_or_higher(f):
    """Decorador para cualquier usuario autenticado"""
    @wraps(f)
    @validate_session_required  # Validar sesión primero
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            if not current_user_id:
                return jsonify({'message': 'Token JWT inválido'}), 401
            
            current_user = get_user_by_id(current_user_id)
            
            if not current_user:
                return jsonify({
                    'message': 'Usuario no encontrado. Redirigiendo al login...',
                    'error_type': 'user_not_found',
                    'redirect_to_login': True
                }), 404
                
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'message': f'Error de autenticación: {str(e)}'}), 401
    return decorated_function

def validate_user_exists(f):
    """Decorador para validar que el usuario autenticado aún existe en la base de datos"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Verificar si hay un token JWT válido
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            
            if not current_user_id:
                # Si no hay usuario autenticado, redirigir al login
                if request.is_json:
                    return jsonify({
                        'message': 'No autenticado. Redirigiendo al login...',
                        'error_type': 'not_authenticated',
                        'redirect_to_login': True
                    }), 401
                else:
                    return redirect(url_for('auth_routes.login'))
            
            # Verificar si el usuario existe en la base de datos
            current_user = get_user_by_id(current_user_id)
            
            if not current_user:
                # Si el usuario no existe, redirigir al login
                if request.is_json:
                    return jsonify({
                        'message': 'Usuario no encontrado en la base de datos. Redirigiendo al login...',
                        'error_type': 'user_not_found',
                        'redirect_to_login': True
                    }), 404
                else:
                    return redirect(url_for('auth_routes.login'))
            
            # Si el usuario existe, continuar con la función
            return f(*args, **kwargs)
            
        except Exception as e:
            print(f"[USER_VALIDATION] Error: {str(e)}")
            # En caso de error, redirigir al login por seguridad
            if request.is_json:
                return jsonify({
                    'message': 'Error de validación de usuario. Redirigiendo al login...',
                    'error_type': 'validation_error',
                    'redirect_to_login': True
                }), 500
            else:
                return redirect(url_for('auth_routes.login'))
    
    return decorated_function

def get_user_permissions(user):
    """Obtener todas las áreas permitidas para un usuario"""
    if not user or not user.role:
        return []
    return ROLE_PERMISSIONS.get(user.role, {}).get('areas', [])

def role_required(*allowed_roles):
    """
    Decorador para verificar que el usuario tenga uno de los roles permitidos
    Uso: @role_required('admin', 'waiter')
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            try:
                # Obtener el usuario actual
                from models.user import User
                current_user_id = get_jwt_identity()
                current_user = User.query.get(current_user_id)
                
                if not current_user:
                    return jsonify({
                        'success': False,
                        'message': 'Usuario no encontrado',
                        'error_type': 'user_not_found'
                    }), 404
                
                # Verificar si el usuario tiene uno de los roles permitidos
                if current_user.role not in allowed_roles:
                    return jsonify({
                        'success': False,
                        'message': f'Acceso denegado. Se requiere uno de estos roles: {", ".join(allowed_roles)}',
                        'error_type': 'insufficient_permissions',
                        'required_roles': list(allowed_roles),
                        'user_role': current_user.role
                    }), 403
                
                # Si todo está bien, continuar con la función
                return f(*args, **kwargs)
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': 'Error de autenticación',
                    'error_type': 'auth_error',
                    'error': str(e)
                }), 500
        
        return decorated_function
    return decorator
