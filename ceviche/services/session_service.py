"""
Servicio mejorado de gestión de sesiones
Maneja sesiones múltiples, duplicados y validaciones
"""
from flask import request, session as flask_session
from models.user_session import UserSession
from models import User
from config.extensions import db
from datetime import datetime, timedelta
from utils.timezone_utils import lima_datetime_naive, lima_now
import secrets

class SessionService:
    """Servicio para gestión avanzada de sesiones"""
    
    @staticmethod
    def create_session(user, force_new=False):
        """
        Crear nueva sesión para un usuario
        
        Args:
            user: Objeto User
            force_new: Forzar creación aunque existan sesiones activas
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Obtener información del dispositivo/navegador
            device_info = request.headers.get('User-Agent', 'Unknown')[:500]
            ip_address = SessionService.get_client_ip()
            
            # Verificar sesiones activas existentes
            existing_sessions = UserSession.get_user_sessions(user.id, active_only=True)
            
            # Política mejorada: Permitir múltiples usuarios diferentes simultáneamente
            # Solo invalidar sesiones existentes del MISMO usuario para evitar duplicados
            if existing_sessions:
                print(f"[SESSION_SERVICE] Usuario {user.username} ya tiene {len(existing_sessions)} sesión(es) activa(s)")
                print(f"[SESSION_SERVICE] Invalidando sesiones anteriores del mismo usuario para evitar duplicados")
                
                for session in existing_sessions:
                    session.invalidate('new_login_same_user')
                db.session.commit()
                
                print(f"[SESSION_SERVICE] Sesiones anteriores de {user.username} invalidadas. Diferentes usuarios pueden mantener sus sesiones activas.")
            
            # Crear nueva sesión
            new_session = UserSession(
                user_id=user.id,
                device_info=device_info,
                ip_address=ip_address,
                duration_hours=8  # 8 horas por defecto
            )
            
            db.session.add(new_session)
            
            # Actualizar campos en User (compatibilidad con sistema existente)
            user.current_session_token = new_session.session_id
            user.last_login = lima_datetime_naive()
            user.last_activity = lima_datetime_naive()
            user.session_expires_at = new_session.expires_at
            
            db.session.commit()
            
            # Establecer sesión Flask
            flask_session['session_id'] = new_session.session_id
            flask_session['user_id'] = user.id
            flask_session['username'] = user.username
            flask_session['role'] = user.role
            flask_session.permanent = True
            
            return {
                'success': True,
                'session': new_session.to_dict(),
                'message': 'Sesión creada exitosamente'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Error creando sesión: {str(e)}'
            }
    
    @staticmethod
    def validate_session(session_id=None):
        """
        Validar sesión actual
        
        Args:
            session_id: ID de sesión (si no se proporciona, se toma de Flask session)
            
        Returns:
            dict: Información de validación
        """
        try:
            # Obtener session_id de parámetro o Flask session
            if not session_id:
                session_id = flask_session.get('session_id')
            
            if not session_id:
                return {
                    'valid': False,
                    'reason': 'No session ID found'
                }
            
            # Buscar sesión en base de datos
            user_session = UserSession.query.filter_by(
                session_id=session_id,
                is_active=True
            ).first()
            
            if not user_session:
                return {
                    'valid': False,
                    'reason': 'Session not found or inactive'
                }
            
            # Verificar si la sesión no ha expirado
            if user_session.is_expired():
                user_session.invalidate('expired')
                return {
                    'valid': False,
                    'reason': 'Session expired'
                }
            
            # Actualizar actividad
            user_session.update_activity()
            
            return {
                'valid': True,
                'session': user_session.to_dict(),
                'user': user_session.user.to_dict() if user_session.user else None
            }
            
        except Exception as e:
            return {
                'valid': False,
                'reason': f'Error validating session: {str(e)}'
            }
    
    @staticmethod
    def invalidate_session(session_id, reason='manual'):
        """
        Invalidar una sesión específica
        
        Args:
            session_id: ID de la sesión a invalidar
            reason: Motivo de invalidación
            
        Returns:
            bool: Éxito de la operación
        """
        try:
            user_session = UserSession.query.filter_by(session_id=session_id).first()
            
            if user_session:
                user_session.invalidate(reason)
                
                # Limpiar campos del User si es la sesión principal
                if user_session.user.current_session_token == session_id:
                    user_session.user.current_session_token = None
                    user_session.user.session_expires_at = None
                    db.session.commit()
                
                return True
            
            return False
            
        except Exception as e:
            db.session.rollback()
            print(f"Error invalidating session: {str(e)}")
            return False
    
    @staticmethod
    def invalidate_user_sessions(user_id, except_session_id=None, reason='forced'):
        """
        Invalidar todas las sesiones de un usuario
        
        Args:
            user_id: ID del usuario
            except_session_id: Sesión a mantener activa (opcional)
            reason: Motivo de invalidación
            
        Returns:
            int: Número de sesiones invalidadas
        """
        try:
            query = UserSession.query.filter(
                UserSession.user_id == user_id,
                UserSession.is_active == True
            )
            
            if except_session_id:
                query = query.filter(UserSession.session_id != except_session_id)
            
            sessions = query.all()
            count = 0
            
            for session in sessions:
                session.invalidate(reason)
                count += 1
            
            db.session.commit()
            return count
            
        except Exception as e:
            db.session.rollback()
            print(f"Error invalidating user sessions: {str(e)}")
            return 0
    
    @staticmethod
    def get_active_sessions(include_user_info=True):
        """
        Obtener todas las sesiones activas del sistema
        
        Args:
            include_user_info: Incluir información del usuario
            
        Returns:
            list: Lista de sesiones activas
        """
        try:
            sessions = UserSession.get_active_sessions().all()
            result = []
            
            for session in sessions:
                session_dict = session.to_dict()
                if include_user_info and session.user:
                    session_dict['user_info'] = {
                        'username': session.user.username,
                        'role': session.user.role,
                        'estacion': session.user.estacion
                    }
                result.append(session_dict)
            
            return result
            
        except Exception as e:
            print(f"Error getting active sessions: {str(e)}")
            return []
    
    @staticmethod
    def cleanup_expired_sessions():
        """
        Limpiar sesiones expiradas del sistema
        
        Returns:
            int: Número de sesiones limpiadas
        """
        try:
            count = UserSession.cleanup_expired_sessions()
            
            # También limpiar campos de User para sesiones expiradas
            expired_users = User.query.filter(
                User.session_expires_at <= lima_datetime_naive(),
                User.current_session_token.isnot(None)
            ).all()
            
            for user in expired_users:
                user.current_session_token = None
                user.session_expires_at = None
            
            db.session.commit()
            return count
            
        except Exception as e:
            db.session.rollback()
            print(f"Error cleaning up sessions: {str(e)}")
            return 0
    
    @staticmethod
    def extend_session(session_id, hours=2):
        """
        Extender duración de una sesión
        
        Args:
            session_id: ID de la sesión
            hours: Horas adicionales
            
        Returns:
            bool: Éxito de la operación
        """
        try:
            user_session = UserSession.query.filter_by(session_id=session_id).first()
            
            if user_session and user_session.is_valid():
                user_session.extend_session(hours)
                
                # Actualizar User si es necesario
                if user_session.user.current_session_token == session_id:
                    user_session.user.session_expires_at = user_session.expires_at
                    db.session.commit()
                
                return True
            
            return False
            
        except Exception as e:
            db.session.rollback()
            print(f"Error extending session: {str(e)}")
            return False
    
    @staticmethod
    def get_client_ip():
        """Obtener IP del cliente considerando proxies"""
        # Headers en orden de prioridad
        headers_to_check = [
            'X-Forwarded-For',
            'X-Real-IP',
            'X-Forwarded-Proto',
            'HTTP_X_FORWARDED_FOR',
            'HTTP_X_REAL_IP',
        ]
        
        for header in headers_to_check:
            ip = request.headers.get(header)
            if ip:
                # X-Forwarded-For puede contener múltiples IPs separadas por coma
                return ip.split(',')[0].strip()
        
        # Fallback a remote_addr
        return request.environ.get('REMOTE_ADDR', 'unknown')
    
    @staticmethod
    def get_session_summary():
        """
        Obtener resumen del estado de sesiones
        
        Returns:
            dict: Resumen de sesiones
        """
        try:
            active_sessions = UserSession.get_active_sessions().all()
            
            # Agrupar por rol
            by_role = {}
            by_user = {}
            
            for session in active_sessions:
                if session.user:
                    role = session.user.role
                    username = session.user.username
                    
                    if role not in by_role:
                        by_role[role] = 0
                    by_role[role] += 1
                    
                    if username not in by_user:
                        by_user[username] = 0
                    by_user[username] += 1
            
            return {
                'total_active': len(active_sessions),
                'by_role': by_role,
                'by_user': by_user,
                'sessions': [s.to_dict() for s in active_sessions]
            }
            
        except Exception as e:
            print(f"Error getting session summary: {str(e)}")
            return {
                'total_active': 0,
                'by_role': {},
                'by_user': {},
                'sessions': []
            }

    # Métodos de compatibilidad con el sistema anterior
    @staticmethod
    def generate_session_token():
        """Compatibilidad: generar token de sesión"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def start_session(user_id, token_expiry_hours=8):
        """Compatibilidad: iniciar sesión usando el nuevo sistema"""
        try:
            user = User.query.get(user_id)
            if not user:
                return None, "Usuario no encontrado"
            
            # Verificar si ya existe una sesión activa usando el nuevo sistema
            existing_sessions = UserSession.get_user_sessions(user.id, active_only=True)
            
            if existing_sessions:
                # Invalidar solo sesiones anteriores del mismo usuario para evitar duplicados
                print(f"[SESSION_SERVICE] start_session: Usuario {user.username} tiene sesiones activas, invalidando duplicados")
                for session in existing_sessions:
                    session.invalidate('new_login_replacement')
                db.session.commit()
                print(f"[SESSION_SERVICE] start_session: Sesiones del usuario {user.username} invalidadas. Otros usuarios mantienen sus sesiones.")
            
            # Obtener información real de la request si está disponible
            device_info = 'Unknown Device'
            ip_address = '127.0.0.1'
            
            try:
                if request:
                    device_info = request.headers.get('User-Agent', 'Unknown')[:500]
                    ip_address = SessionService.get_client_ip()
            except:
                pass  # Si no hay request context, usar valores por defecto
            
            # Crear sesión directamente en la base de datos
            new_session = UserSession(
                user_id=user.id,
                device_info=device_info,
                ip_address=ip_address,
                duration_hours=token_expiry_hours
            )
            
            db.session.add(new_session)
            
            # Actualizar campos en User (compatibilidad)
            user.current_session_token = new_session.session_id
            user.last_login = lima_datetime_naive()
            user.last_activity = lima_datetime_naive()
            user.session_expires_at = new_session.expires_at
            
            db.session.commit()
            
            # IMPORTANTE: Establecer sesión Flask para permitir acceso a dashboards
            flask_session['session_id'] = new_session.session_id
            flask_session['user_id'] = user.id
            flask_session['username'] = user.username
            flask_session['role'] = user.role
            flask_session.permanent = True
            
            return new_session.session_id, None
                    
        except Exception as e:
            db.session.rollback()
            return None, f"Error creando sesión: {str(e)}"
    
    @staticmethod
    def validate_session_legacy(user_id, session_token):
        """Compatibilidad: validar sesión usando método anterior"""
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "Usuario no encontrado"
            
            # Verificar token en User model (sistema anterior)
            if user.current_session_token != session_token:
                return False, "Token de sesión inválido"
            
            # Verificar expiración
            if user.session_expires_at and user.session_expires_at < lima_datetime_naive():
                # Limpiar sesión expirada
                user.current_session_token = None
                user.session_expires_at = None
                db.session.commit()
                return False, "Sesión expirada"
            
            # Actualizar actividad
            user.last_activity = lima_datetime_naive()
            db.session.commit()
            
            return True, "Sesión válida"
            
        except Exception as e:
            return False, f"Error validando sesión: {str(e)}"
    
    @staticmethod
    def cleanup_inactive_sessions(inactivity_minutes=5):
        """Limpiar sesiones inactivas (para compatibilidad)"""
        return SessionService.cleanup_expired_sessions()
    
    @staticmethod
    def get_all_active_sessions():
        """
        Obtener todas las sesiones activas del sistema
        
        Returns:
            list: Lista de objetos UserSession activos con sus usuarios
        """
        try:
            sessions = UserSession.query.filter_by(is_active=True)\
                                      .join(User)\
                                      .order_by(UserSession.last_activity.desc())\
                                      .all()
            return sessions
        except Exception as e:
            print(f"[SESSION_SERVICE] Error obteniendo sesiones activas: {str(e)}")
            return []
    
    @staticmethod
    def close_user_sessions(user_id):
        """
        Cerrar todas las sesiones de un usuario específico
        
        Args:
            user_id: ID del usuario
            
        Returns:
            int: Número de sesiones cerradas
        """
        try:
            sessions = UserSession.query.filter_by(user_id=user_id, is_active=True).all()
            closed_count = 0
            
            for session in sessions:
                session.invalidate('admin_closed')
                closed_count += 1
            
            db.session.commit()
            return closed_count
            
        except Exception as e:
            db.session.rollback()
            print(f"[SESSION_SERVICE] Error cerrando sesiones del usuario {user_id}: {str(e)}")
            return 0

# Instancia global del servicio
session_service = SessionService()
