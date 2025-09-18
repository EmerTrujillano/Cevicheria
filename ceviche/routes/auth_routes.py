from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from config.extensions import blacklisted_tokens
from services.auth_service import AuthService
from services.session_service import SessionService
from models import User
from utils.decorators import role_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@jwt_required()
@role_required(['admin'])
def register():
    """
    Registro de usuarios - Solo disponible para administradores
    """
    try:
        data = request.get_json()
        print(f"[DEBUG] Datos recibidos en /register: {data}")
        
        if not data:
            print("[DEBUG] No se recibieron datos")
            return jsonify({'message': 'Datos requeridos'}), 400
        
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'waiter')  # Rol por defecto: mozo
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        
        print(f"[DEBUG] Username: {username}, Password presente: {bool(password)}, Role: {role}")
        
        if not username or not password:
            print("[DEBUG] Username o password faltante")
            return jsonify({'message': 'Usuario y contraseña son requeridos'}), 400
        
        # Validar que el rol sea válido
        valid_roles = ['admin', 'waiter', 'kitchen', 'cashier']
        if role not in valid_roles:
            return jsonify({'message': f'Rol inválido. Roles válidos: {valid_roles}'}), 400
        
        user, error = AuthService.register_user(
            username=username, 
            password=password,
            role=role,
            first_name=first_name,
            last_name=last_name
        )
        print(f"[DEBUG] Resultado del servicio - User: {user}, Error: {error}")
        
        if error:
            print(f"[DEBUG] Error del servicio: {error}")
            return jsonify({'message': error}), 400
        
        print(f"[DEBUG] Registro exitoso, devolviendo 201")
        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        print(f"[DEBUG] Excepción en /register: {str(e)}")
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        print(f"[DEBUG] Datos recibidos en /login: {data}")
        
        if not data:
            print("[DEBUG] No se recibieron datos en login")
            return jsonify({'message': 'Datos requeridos'}), 400
        
        username = data.get('username')
        password = data.get('password')
        force_new = data.get('force_new', False)  # Para cerrar sesiones remotas
        print(f"[DEBUG] Username: {username}, Password presente: {bool(password)}, Force new: {force_new}")
        
        if not username or not password:
            print("[DEBUG] Username o password faltante en login")
            return jsonify({'message': 'Usuario y contraseña son requeridos'}), 400
        
        # Primero autenticar credenciales
        user, access_token, error = AuthService.authenticate_user(username, password, force_new)
        if error:
            print(f"[DEBUG] Error de autenticación: {error}")
            return jsonify({'message': error}), 401
        
        # Si llegamos aquí, AuthService ya creó la sesión exitosamente
        print(f"[DEBUG] Login exitoso para usuario: {username}")
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict(),
            'session': {'status': 'active', 'created': True}
        }), 200
        
    except Exception as e:
        print(f"[DEBUG] Excepción en /login: {str(e)}")
        import traceback
        print(f"[DEBUG] Traceback completo: {traceback.format_exc()}")
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500
        
    except Exception as e:
        print(f"[DEBUG] Excepción en /login: {str(e)}")
        import traceback
        print(f"[DEBUG] Traceback completo: {traceback.format_exc()}")
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout del usuario - Terminar sesión y agregar token a blacklist"""
    try:
        from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
        verify_jwt_in_request()
        
        current_user_id = get_jwt_identity()
        jti = get_jwt()['jti']
        
        # Agregar token a blacklist
        blacklisted_tokens.add(jti)
        
        # Terminar sesión usando el nuevo sistema
        session_id = session.get('session_id')
        if session_id:
            SessionService.invalidate_session(session_id, 'manual_logout')
        
        # Limpiar sesión web
        session.clear()
        
        print(f"[AUTH] Logout exitoso para usuario ID: {current_user_id}")
        return jsonify({'message': 'Logout exitoso'}), 200
        
    except Exception as e:
        print(f"[AUTH] Error en logout: {str(e)}")
        return jsonify({'message': f'Error de autenticación: {str(e)}'}), 401

@auth_bp.route('/session-status', methods=['GET'])
def session_status():
    """Verificar el estado de la sesión actual"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({
                'valid': False,
                'message': 'No hay sesión activa'
            }), 200
        
        # Validar sesión usando el nuevo sistema
        validation_result = SessionService.validate_session(session_id)
        
        return jsonify({
            'valid': validation_result['valid'],
            'message': validation_result.get('reason', 'Sesión válida'),
            'session_info': validation_result.get('session'),
            'user_info': validation_result.get('user')
        }), 200
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'message': f'Error al verificar sesión: {str(e)}'
        }), 200

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Obtener perfil del usuario actual"""
    try:
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        
        return jsonify({
            'user': current_user.to_dict(),
            'permissions': {
                'can_manage_products': current_user.role in ['admin', 'superadmin'],
                'can_manage_categories': current_user.role in ['admin', 'superadmin'],
                'can_manage_users': current_user.role == 'superadmin'
            }
        }), 200
    except Exception as e:
        return jsonify({'message': f'Error de autenticación: {str(e)}'}), 401

@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """Cambiar contraseña del usuario actual"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Datos requeridos'}), 400
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({'message': 'Contraseña actual y nueva son requeridas'}), 400
        
        success, message = AuthService.change_password(current_user_id, old_password, new_password)
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'message': message}), 400
            
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@auth_bp.route('/sessions/active', methods=['GET'])
def get_active_sessions():
    """Ver todas las sesiones activas - Solo para administradores"""
    try:
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        from utils.decorators import get_user_by_id
        
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        current_user = get_user_by_id(current_user_id)
        
        if not current_user or current_user.role not in ['admin', 'superadmin']:
            return jsonify({'message': 'Acceso denegado. Se requieren permisos de administrador'}), 403
        
        from services.session_service import SessionService
        active_sessions = SessionService.get_active_sessions()
        
        return jsonify({
            'active_sessions': active_sessions,
            'total_sessions': len(active_sessions),
            'requested_by': current_user.username
        }), 200
        
    except Exception as e:
        print(f"[AUTH] Error al obtener sesiones activas: {str(e)}")
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@auth_bp.route('/sessions/force-logout/<int:user_id>', methods=['POST'])
def force_logout_user(user_id):
    """Forzar logout de un usuario - Solo para administradores"""
    try:
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        from utils.decorators import get_user_by_id
        
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        current_user = get_user_by_id(current_user_id)
        
        if not current_user or current_user.role not in ['admin', 'superadmin']:
            return jsonify({'message': 'Acceso denegado. Se requieren permisos de administrador'}), 403
        
        data = request.get_json() or {}
        reason = data.get('reason', f'Desconectado por {current_user.username}')
        
        from services.session_service import SessionService
        success, message = SessionService.force_logout_user(user_id, reason)
        
        if success:
            return jsonify({
                'message': message,
                'forced_by': current_user.username
            }), 200
        else:
            return jsonify({'message': message}), 400
        
    except Exception as e:
        print(f"[AUTH] Error al forzar logout: {str(e)}")
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@auth_bp.route('/session/info', methods=['GET'])
def get_session_info():
    """Obtener información de la sesión actual del usuario"""
    try:
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        from utils.decorators import get_user_by_id
        from services.session_service import SessionService
        
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        current_user = get_user_by_id(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'Usuario no encontrado'}), 404
        
        session_info = SessionService.get_session_info(current_user_id)
        
        if session_info:
            return jsonify({
                'session_info': session_info,
                'user_id': current_user_id
            }), 200
        else:
            return jsonify({'message': 'No se pudo obtener información de sesión'}), 500
        
    except Exception as e:
        print(f"[AUTH] Error al obtener info de sesión: {str(e)}")
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@auth_bp.route('/validate-user-existence', methods=['POST'])
def validate_user_existence():
    """Validar periódicamente si el usuario aún existe en la base de datos"""
    try:
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
        from utils.decorators import get_user_by_id
        from services.session_service import SessionService
        
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        session_token = claims.get('session_token')
        
        # Verificar si el usuario existe en la base de datos
        current_user = get_user_by_id(current_user_id)
        
        if not current_user:
            print(f"[AUTH] Usuario {current_user_id} no existe en la base de datos - expulsando sesión")
            
            # Si el usuario no existe, limpiamos cualquier sesión residual
            if session_token:
                try:
                    SessionService.end_session(current_user_id)
                except Exception as cleanup_error:
                    print(f"[AUTH] Error al limpiar sesión residual: {str(cleanup_error)}")
            
            return jsonify({
                'valid': False,
                'message': 'Usuario no encontrado en el sistema',
                'action': 'logout',
                'reason': 'user_not_exists'
            }), 200
        
        # Verificar que la sesión sea válida
        if session_token:
            is_valid, message = SessionService.validate_session(current_user_id, session_token)
            if not is_valid:
                return jsonify({
                    'valid': False,
                    'message': message,
                    'action': 'logout',
                    'reason': 'invalid_session'
                }), 200
        
        # Todo está bien - usuario existe y sesión válida
        return jsonify({
            'valid': True,
            'message': 'Usuario válido',
            'user_id': current_user_id,
            'username': current_user.username
        }), 200
        
    except Exception as e:
        print(f"[AUTH] Error en validación de existencia: {str(e)}")
        return jsonify({
            'valid': False,
            'message': f'Error de validación: {str(e)}',
            'action': 'logout',
            'reason': 'validation_error'
        }), 200

@auth_bp.route('/validate-username-only', methods=['POST'])
def validate_username_only():
    """Validar solo si el usuario existe en la base de datos (sin verificar token de sesión)"""
    try:
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        from utils.decorators import get_user_by_id
        
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        
        # Solo verificar si el usuario existe en la base de datos
        current_user = get_user_by_id(current_user_id)
        
        if not current_user:
            print(f"[AUTH] Usuario {current_user_id} no existe en la base de datos")
            
            return jsonify({
                'valid': False,
                'message': 'Usuario no encontrado en el sistema',
                'action': 'logout',
                'reason': 'user_not_exists'
            }), 200
        
        # Usuario existe - respuesta exitosa
        return jsonify({
            'valid': True,
            'message': 'Usuario existe',
            'user_id': current_user_id,
            'username': current_user.username
        }), 200
        
    except Exception as e:
        print(f"[AUTH] Error en validación de usuario: {str(e)}")
        return jsonify({
            'valid': False,
            'message': f'Error de validación: {str(e)}',
            'action': 'logout',
            'reason': 'validation_error'
        }), 200

@auth_bp.route('/close-remote-sessions', methods=['POST'])
def close_remote_sessions():
    """Cerrar sesiones remotas y crear nueva sesión"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Datos requeridos'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'message': 'Usuario y contraseña son requeridos'}), 400
        
        # Primero autenticar credenciales
        user, access_token, error = AuthService.authenticate_user(username, password)
        if error:
            return jsonify({'message': error}), 401
        
        # Forzar cierre de sesiones remotas y crear nueva
        session_result = SessionService.create_session(user, force_new=True)
        
        if not session_result['success']:
            return jsonify({'message': session_result.get('error', 'Error creando sesión')}), 500
        
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict(),
            'session': session_result['session'],
            'message': 'Sesiones remotas cerradas exitosamente'
        }), 200
        
    except Exception as e:
        print(f"[AUTH] Error cerrando sesiones remotas: {str(e)}")
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@auth_bp.route('/active-sessions', methods=['GET'])
@jwt_required()
@role_required(['admin'])
def get_all_active_sessions():
    """Obtener todas las sesiones activas del sistema (solo admin)"""
    try:
        sessions = SessionService.get_active_sessions(include_user_info=True)
        
        return jsonify({
            'active_sessions': sessions,
            'total_sessions': len(sessions)
        }), 200
        
    except Exception as e:
        print(f"[AUTH] Error obteniendo sesiones activas: {str(e)}")
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@auth_bp.route('/extend-session', methods=['POST'])
def extend_current_session():
    """Extender la sesión actual (respuesta a ¿Sigues ahí?)"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'message': 'No hay sesión activa'}), 400
        
        data = request.get_json() or {}
        hours = data.get('hours', 2)  # Extender 2 horas por defecto
        
        success = SessionService.extend_session(session_id, hours)
        
        if success:
            return jsonify({
                'message': f'Sesión extendida por {hours} horas',
                'extended_hours': hours
            }), 200
        else:
            return jsonify({'message': 'Error extendiendo sesión'}), 500
            
    except Exception as e:
        print(f"[AUTH] Error extendiendo sesión: {str(e)}")
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500