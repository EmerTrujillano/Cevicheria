from datetime import datetime
from config.extensions import db

class TemporaryPermission(db.Model):
    __tablename__ = 'temporary_permission'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    granted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    area = db.Column(db.String(50), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    reason = db.Column(db.Text)

    def __repr__(self):
        return f'<TemporaryPermission {self.area} for User {self.user_id}>'

    def to_dict(self):
        # Importar aquí para evitar importación circular
        from models import User
        import pytz
        
        user = User.query.get(self.user_id)
        granter = User.query.get(self.granted_by)
        
        # Convertir tiempo UTC a hora de Lima
        lima_tz = pytz.timezone('America/Lima')
        expires_at_lima = pytz.UTC.localize(self.expires_at).astimezone(lima_tz)
        created_at_lima = pytz.UTC.localize(self.created_at).astimezone(lima_tz)
        
        # Calcular tiempo restante
        now_lima = datetime.now(lima_tz)
        time_remaining = str(expires_at_lima - now_lima).split('.')[0] if expires_at_lima > now_lima else 'Expirado'
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': user.username if user else None,
            'granted_by': self.granted_by,
            'granted_by_username': granter.username if granter else None,
            'area': self.area,
            'expires_at': expires_at_lima.isoformat(),
            'created_at': created_at_lima.isoformat(),
            'is_active': self.is_active,
            'reason': self.reason,
            'time_remaining': time_remaining
        }
