"""
Modelo para gestión de sesiones de usuario
"""
from config.extensions import db
from datetime import datetime, timedelta
from utils.timezone_utils import lima_datetime_naive
import uuid
import secrets

class UserSession(db.Model):
    """
    Modelo para gestionar sesiones de usuario de manera independiente
    Permite múltiples sesiones por usuario en diferentes dispositivos
    """
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Información de la sesión
    device_info = db.Column(db.String(500))  # User-Agent, IP, etc.
    ip_address = db.Column(db.String(45))    # IPv4 o IPv6
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lima_datetime_naive, nullable=False)
    last_activity = db.Column(db.DateTime, default=lima_datetime_naive, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    # Estado de la sesión
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    logout_reason = db.Column(db.String(100))  # 'manual', 'inactivity', 'forced', 'expired'
    
    # Relación con User
    user = db.relationship('User', backref=db.backref('sessions', lazy='dynamic'))
    
    def __init__(self, user_id, device_info=None, ip_address=None, duration_hours=8):
        """
        Crear nueva sesión para un usuario
        
        Args:
            user_id: ID del usuario
            device_info: Información del dispositivo/navegador
            ip_address: Dirección IP del usuario
            duration_hours: Duración de la sesión en horas (default: 8)
        """
        self.session_id = self.generate_session_id()
        self.user_id = user_id
        self.device_info = device_info
        self.ip_address = ip_address
        
        # Usar hora de Lima
        now_lima = lima_datetime_naive()
        self.created_at = now_lima
        self.last_activity = now_lima
        self.expires_at = now_lima + timedelta(hours=duration_hours)
    
    @staticmethod
    def generate_session_id():
        """Generar ID único para la sesión"""
        return f"sess_{secrets.token_urlsafe(32)}"
    
    def update_activity(self):
        """Actualizar timestamp de última actividad"""
        self.last_activity = lima_datetime_naive()
        db.session.commit()
    
    def extend_session(self, hours=2):
        """
        Extender duración de la sesión
        
        Args:
            hours: Horas adicionales a agregar
        """
        self.expires_at = max(
            self.expires_at,
            lima_datetime_naive() + timedelta(hours=hours)
        )
        self.update_activity()
    
    def invalidate(self, reason='manual'):
        """
        Invalidar la sesión
        
        Args:
            reason: Motivo de cierre ('manual', 'inactivity', 'forced', 'expired')
        """
        self.is_active = False
        self.logout_reason = reason
        db.session.commit()
    
    def is_valid(self):
        """Verificar si la sesión es válida"""
        return (
            self.is_active and 
            self.expires_at > lima_datetime_naive()
        )
    
    def is_expired(self):
        """Verificar si la sesión ha expirado"""
        return lima_datetime_naive() > self.expires_at
    
    def time_remaining(self):
        """Obtener tiempo restante de la sesión en segundos"""
        if self.is_expired():
            return 0
        return int((self.expires_at - lima_datetime_naive()).total_seconds())
    
    def time_inactive(self):
        """Obtener tiempo de inactividad en segundos"""
        return int((lima_datetime_naive() - self.last_activity).total_seconds())
    
    def to_dict(self):
        """Convertir sesión a diccionario"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'user_name': self.user.username if self.user else None,
            'user_role': self.user.role if self.user else None,
            'device_info': self.device_info,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'is_valid': self.is_valid(),
            'time_remaining': self.time_remaining(),
            'time_inactive': self.time_inactive(),
            'logout_reason': self.logout_reason
        }
    
    @classmethod
    def get_active_sessions(cls, user_id=None):
        """
        Obtener sesiones activas
        
        Args:
            user_id: Si se especifica, solo sesiones de ese usuario
        
        Returns:
            Query de sesiones activas
        """
        query = cls.query.filter(
            cls.is_active == True,
            cls.expires_at > lima_datetime_naive()
        )
        
        if user_id:
            query = query.filter(cls.user_id == user_id)
        
        return query.order_by(cls.last_activity.desc())
    
    @classmethod
    def cleanup_expired_sessions(cls):
        """Limpiar sesiones expiradas"""
        expired_sessions = cls.query.filter(
            cls.is_active == True,
            cls.expires_at <= lima_datetime_naive()
        ).all()
        
        count = 0
        for session in expired_sessions:
            session.invalidate('expired')
            count += 1
        
        return count
    
    @classmethod
    def get_user_sessions(cls, user_id, active_only=True):
        """
        Obtener todas las sesiones de un usuario
        
        Args:
            user_id: ID del usuario
            active_only: Solo sesiones activas (default: True)
        
        Returns:
            Lista de sesiones
        """
        query = cls.query.filter(cls.user_id == user_id)
        
        if active_only:
            query = query.filter(
                cls.is_active == True,
                cls.expires_at > lima_datetime_naive()
            )
        
        return query.order_by(cls.last_activity.desc()).all()
    
    def __repr__(self):
        return f'<UserSession {self.session_id} for user {self.user_id}>'