from datetime import datetime
from config.extensions import db

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Control de sesiones
    current_session_token = db.Column(db.String(255), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    session_expires_at = db.Column(db.DateTime, nullable=True)

    # Relaciones
    temp_permissions = db.relationship('TemporaryPermission', 
                                     foreign_keys='TemporaryPermission.user_id',
                                     backref='user', lazy=True)
    granted_permissions = db.relationship('TemporaryPermission',
                                        foreign_keys='TemporaryPermission.granted_by',
                                        backref='granter', lazy=True)
    surveys = db.relationship('Survey', backref='user', lazy=True)
    
    # Nuevas relaciones para cevichería
    waiter_orders = db.relationship('Order', foreign_keys='Order.waiter_id', backref='waiter', lazy=True)
    cashier_payments = db.relationship('Payment', foreign_keys='Payment.cashier_id', backref='cashier', lazy=True)
    approved_reviews = db.relationship('Review', foreign_keys='Review.approved_by', backref='approver', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        result = {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }
        
        # Agregar campos de sesión solo si existen (para compatibilidad)
        try:
            if hasattr(self, 'last_login') and self.last_login:
                result['last_login'] = self.last_login.isoformat()
            else:
                result['last_login'] = None
                
            if hasattr(self, 'current_session_token'):
                result['has_active_session'] = self.current_session_token is not None
            else:
                result['has_active_session'] = False
        except:
            # Si hay error accediendo a los campos, ignorar
            result['last_login'] = None
            result['has_active_session'] = False
            
        return result
