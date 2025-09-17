import uuid
from datetime import datetime, timedelta
from config.extensions import db
from models import User

class SessionService:
    @staticmethod
    def generate_session_token():
        """Generar un token único para la sesión"""
        return str(uuid.uuid4())
    
    @staticmethod
    def start_session(user_id, token_expiry_hours=1):
        """Iniciar una nueva sesión para el usuario - Sistema de 'primera sesión gana'"""
        print(f"[SESSION_SERVICE] Verificando disponibilidad de sesión para usuario ID: {user_id}")
        
        user = User.query.get(user_id)
        if not user:
            print(f"[SESSION_SERVICE] Usuario no encontrado: {user_id}")
            return None, "Usuario no encontrado"
        
        # Verificar si ya existe una sesión activa
        if user.current_session_token and user.session_expires_at:
            # Verificar si la sesión actual no ha expirado
            if user.session_expires_at > datetime.utcnow():
                print(f"[SESSION_SERVICE] Usuario {user.username} ya tiene una sesión activa")
                print(f"[SESSION_SERVICE] Sesión iniciada: {user.last_login}")
                print(f"[SESSION_SERVICE] Sesión expira: {user.session_expires_at}")
                
                # Calcular tiempo restante
                tiempo_restante = user.session_expires_at - datetime.utcnow()
                horas_restantes = int(tiempo_restante.total_seconds() // 3600)
                minutos_restantes = int((tiempo_restante.total_seconds() % 3600) // 60)
                
                error_message = f"Otra máquina está usando la sesión. Sesión activa desde: {user.last_login.strftime('%d/%m/%Y %H:%M:%S')}. Tiempo restante: {horas_restantes}h {minutos_restantes}m"
                print(f"[SESSION_SERVICE] Rechazando nuevo login: {error_message}")
                return None, error_message
            else:
                print(f"[SESSION_SERVICE] Sesión anterior expirada, limpiando...")
                user.current_session_token = None
                user.session_expires_at = None
        
        # Generar nuevo token de sesión
        session_token = SessionService.generate_session_token()
        
        # Calcular tiempo de expiración
        expires_at = datetime.utcnow() + timedelta(hours=token_expiry_hours)
        
        # Crear nueva sesión
        user.current_session_token = session_token
        user.last_login = datetime.utcnow()
        user.session_expires_at = expires_at
        
        try:
            db.session.commit()
            print(f"[SESSION_SERVICE] Nueva sesión iniciada para usuario: {user.username}")
            print(f"[SESSION_SERVICE] Sesión expira en: {token_expiry_hours} horas")
            return session_token, None
        except Exception as e:
            print(f"[SESSION_SERVICE] Error al iniciar sesión: {str(e)}")
            db.session.rollback()
            return None, f"Error al iniciar sesión: {str(e)}"
    
    @staticmethod
    def validate_session(user_id, session_token):
        """Validar si la sesión del usuario es válida"""
        print(f"[SESSION_SERVICE] Validando sesión para usuario ID: {user_id}")
        print(f"[SESSION_SERVICE] Token recibido: {session_token[:20]}...")
        
        user = User.query.get(user_id)
        if not user:
            print(f"[SESSION_SERVICE] Usuario {user_id} no encontrado")
            return False, "Usuario no encontrado"
        
        print(f"[SESSION_SERVICE] Token almacenado: {user.current_session_token[:20] if user.current_session_token else 'None'}...")
        
        # Verificar si el token coincide
        if user.current_session_token != session_token:
            print(f"[SESSION_SERVICE] Token NO coincide para usuario {user.username}")
            print(f"[SESSION_SERVICE] Posible intento de acceso no autorizado")
            return False, "Sesión inválida. Token de autenticación no válido."
        
        # Verificar si la sesión no ha expirado
        if user.session_expires_at and user.session_expires_at < datetime.utcnow():
            print(f"[SESSION_SERVICE] Sesión expirada para usuario {user.username}")
            # Limpiar sesión expirada
            user.current_session_token = None
            user.session_expires_at = None
            db.session.commit()
            return False, "Sesión expirada"
        
        print(f"[SESSION_SERVICE] Sesión válida para usuario {user.username}")
        return True, "Sesión válida"
    
    @staticmethod
    def end_session(user_id):
        """Terminar la sesión actual del usuario"""
        print(f"[SESSION_SERVICE] Terminando sesión para usuario ID: {user_id}")
        
        user = User.query.get(user_id)
        if not user:
            print(f"[SESSION_SERVICE] Usuario no encontrado: {user_id}")
            return False
        
        # Limpiar todos los campos relacionados con la sesión
        user.current_session_token = None
        user.session_expires_at = None
        user.last_login = None  # Limpiar también el último login
        
        try:
            db.session.commit()
            print(f"[SESSION_SERVICE] Sesión completamente terminada para usuario: {user.username}")
            print(f"[SESSION_SERVICE] Campos limpiados: current_session_token, session_expires_at, last_login")
            return True
        except Exception as e:
            print(f"[SESSION_SERVICE] Error al terminar sesión: {str(e)}")
            db.session.rollback()
            return False

    @staticmethod
    def force_logout_user(user_id, reason="Forzado por administrador"):
        """Forzar el logout de un usuario (solo para administradores)"""
        print(f"[SESSION_SERVICE] Forzando logout para usuario ID: {user_id}, razón: {reason}")
        
        user = User.query.get(user_id)
        if not user:
            return False, "Usuario no encontrado"
        
        if not user.current_session_token:
            return False, "El usuario no tiene sesión activa"
        
        # Limpiar todos los campos relacionados con la sesión
        user.current_session_token = None
        user.session_expires_at = None
        user.last_login = None  # Limpiar también el último login
        
        try:
            db.session.commit()
            print(f"[SESSION_SERVICE] Logout forzado exitoso para usuario: {user.username}")
            print(f"[SESSION_SERVICE] Campos limpiados: current_session_token, session_expires_at, last_login")
            return True, f"Sesión terminada para {user.username}"
        except Exception as e:
            print(f"[SESSION_SERVICE] Error al forzar logout: {str(e)}")
            db.session.rollback()
            return False, f"Error al terminar sesión: {str(e)}"

    @staticmethod
    def get_session_info(user_id):
        """Obtener información de la sesión actual del usuario"""
        user = User.query.get(user_id)
        if not user:
            return None
        
        if not user.current_session_token:
            return {
                'has_session': False,
                'username': user.username,
                'message': 'Sin sesión activa'
            }
        
        # Verificar si la sesión está expirada
        if user.session_expires_at and user.session_expires_at < datetime.utcnow():
            return {
                'has_session': False,
                'username': user.username,
                'message': 'Sesión expirada'
            }
        
        tiempo_restante = user.session_expires_at - datetime.utcnow()
        horas_restantes = int(tiempo_restante.total_seconds() // 3600)
        minutos_restantes = int((tiempo_restante.total_seconds() % 3600) // 60)
        
        return {
            'has_session': True,
            'username': user.username,
            'login_time': user.last_login.isoformat() if user.last_login else None,
            'expires_at': user.session_expires_at.isoformat(),
            'time_remaining': f"{horas_restantes}h {minutos_restantes}m",
            'session_token_preview': user.current_session_token[:8] + '...' if user.current_session_token else None
        }

    @staticmethod
    def get_active_sessions():
        """Obtener todas las sesiones activas (para administradores)"""
        active_users = User.query.filter(
            User.current_session_token.isnot(None),
            User.session_expires_at > datetime.utcnow()
        ).all()
        
        sessions = []
        for user in active_users:
            tiempo_restante = user.session_expires_at - datetime.utcnow()
            horas_restantes = int(tiempo_restante.total_seconds() // 3600)
            minutos_restantes = int((tiempo_restante.total_seconds() % 3600) // 60)
            
            sessions.append({
                'user_id': user.id,
                'username': user.username,
                'role': user.role,
                'login_time': user.last_login.isoformat() if user.last_login else None,
                'expires_at': user.session_expires_at.isoformat(),
                'time_remaining': f"{horas_restantes}h {minutos_restantes}m"
            })
        
        return sessions

    @staticmethod
    def cleanup_expired_sessions():
        """Limpiar sesiones expiradas (ejecutar periódicamente)"""
        expired_users = User.query.filter(
            User.session_expires_at < datetime.utcnow(),
            User.current_session_token.isnot(None)
        ).all()
        
        for user in expired_users:
            user.current_session_token = None
            user.session_expires_at = None
            print(f"[SESSION_SERVICE] Sesión expirada limpiada para usuario: {user.username}")
        
        if expired_users:
            db.session.commit()
            print(f"[SESSION_SERVICE] {len(expired_users)} sesiones expiradas limpiadas")
