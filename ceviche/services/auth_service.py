from datetime import datetime, timedelta
from config.extensions import db, bcrypt
from models import User
from models.user_session import UserSession
from flask_jwt_extended import create_access_token
from services.session_service import SessionService

class AuthService:
    @staticmethod
    def register_user(username, password, role='waiter', first_name='', last_name=''):
        """Registrar un nuevo usuario"""
        print(f"[AUTH_SERVICE] Registrando usuario: {username}, rol: {role}")
        
        try:
            # Verificar si el usuario ya existe
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"[AUTH_SERVICE] Usuario {username} ya existe")
                return None, 'El usuario ya existe'
            
            print(f"[AUTH_SERVICE] Usuario {username} no existe, creando nuevo usuario")
            
            # Crear usuario usando el método del modelo User
            user = User(
                username=username, 
                role=role,
                first_name=first_name,
                last_name=last_name,
                current_session_token=None,
                last_login=None,
                session_expires_at=None
            )
            
            # Usar el método set_password del modelo User (werkzeug.security)
            user.set_password(password)
            print(f"[AUTH_SERVICE] Password hasheado correctamente")
            
            print(f"[AUTH_SERVICE] Objeto User creado: {user}")
            
            print(f"[AUTH_SERVICE] Agregando usuario a la sesión de BD")
            db.session.add(user)
            
            print(f"[AUTH_SERVICE] Haciendo commit a la BD")
            db.session.commit()
            
            print(f"[AUTH_SERVICE] Usuario {username} registrado exitosamente con ID: {user.id}")
            
            # Verificar que el usuario realmente se guardó
            saved_user = User.query.filter_by(username=username).first()
            if saved_user:
                print(f"[AUTH_SERVICE] Verificación: Usuario {username} encontrado en BD con ID: {saved_user.id}")
            else:
                print(f"[AUTH_SERVICE] ERROR: Usuario {username} NO se encontró en BD después del commit")
                
            return user, None
            
        except Exception as e:
            print(f"[AUTH_SERVICE] ERROR en register_user: {str(e)}")
            db.session.rollback()
            return None, f'Error al registrar usuario: {str(e)}'

    @staticmethod
    def authenticate_user(username, password, force_new=False):
        """Autenticar usuario y generar token"""
        print(f"[AUTH_SERVICE] Intentando autenticar usuario: {username}, force_new: {force_new}")
        
        try:
            user = User.query.filter_by(username=username).first()
            print(f"[AUTH_SERVICE] Usuario encontrado: {user is not None}")
            
            if user:
                print(f"[AUTH_SERVICE] Usuario ID: {user.id}, Rol: {user.role}")
                
                # Verificar contraseña usando el método del modelo User
                password_valid = False
                try:
                    # Usar el método check_password del modelo User (werkzeug.security)
                    password_valid = user.check_password(password)
                    print(f"[AUTH_SERVICE] Contraseña válida: {password_valid}")
                except Exception as e:
                    print(f"[AUTH_SERVICE] Error verificando contraseña: {str(e)}")
                    print(f"[AUTH_SERVICE] Contraseña incorrecta para usuario: {username}")
                
                if password_valid:
                    print(f"[AUTH_SERVICE] Contraseña válida, verificando disponibilidad de sesión")
                    
                    # Verificar sesiones activas ANTES de intentar crear nueva
                    existing_sessions = UserSession.get_user_sessions(user.id, active_only=True)
                    
                    if existing_sessions and not force_new:
                        # Retornar información sobre sesiones existentes para que el frontend pueda manejarlas
                        print(f"[AUTH_SERVICE] Usuario {username} ya tiene sesiones activas y force_new=False")
                        return None, None, f"Ya tienes una sesión activa. ¿Quieres cerrar las sesiones remotas e iniciar nueva sesión?"
                    
                    # Intentar iniciar nueva sesión usando método de compatibilidad
                    session_token, session_error = SessionService.start_session(user.id, token_expiry_hours=24)
                    
                    if session_error:
                        # La sesión fue rechazada porque ya existe una activa
                        print(f"[AUTH_SERVICE] Login rechazado: {session_error}")
                        return None, None, session_error
                    
                    if not session_token:
                        print(f"[AUTH_SERVICE] Error: No se generó token de sesión")
                        return None, None, 'Error interno al generar sesión'
                    
                    print(f"[AUTH_SERVICE] Sesión iniciada exitosamente con token: {session_token[:20]}...")
                    
                    # Crear token JWT con información de sesión
                    access_token = create_access_token(
                        identity=str(user.id),  # Convertir a string
                        additional_claims={
                            'role': user.role, 
                            'username': user.username,
                            'session_token': session_token  # OBLIGATORIO incluir token de sesión
                        }
                    )
                    print(f"[AUTH_SERVICE] Token JWT generado exitosamente")
                    return user, access_token, None
                else:
                    print(f"[AUTH_SERVICE] Contraseña incorrecta para usuario: {username}")
                    return None, None, 'Credenciales inválidas'
            else:
                print(f"[AUTH_SERVICE] Usuario no encontrado: {username}")
                return None, None, 'Credenciales inválidas'
                
        except Exception as e:
            print(f"[AUTH_SERVICE] Excepción en authenticate_user: {str(e)}")
            import traceback
            print(f"[AUTH_SERVICE] Traceback: {traceback.format_exc()}")
            return None, None, f'Error interno: {str(e)}'

    @staticmethod
    def logout_user(user_id):
        """Cerrar sesión del usuario"""
        print(f"[AUTH_SERVICE] Cerrando sesión para usuario ID: {user_id}")
        return SessionService.end_session(user_id)

    @staticmethod
    def change_password(user_id, old_password, new_password):
        """Cambiar contraseña de usuario"""
        user = User.query.get(user_id)
        if not user:
            return False, 'Usuario no encontrado'
        
        if not bcrypt.check_password_hash(user.password, old_password):
            return False, 'Contraseña actual incorrecta'
        
        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        
        return True, 'Contraseña cambiada exitosamente'
