from datetime import datetime
from config.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from utils.timezone_utils import lima_datetime_naive

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    estacion = db.Column(db.String(50), nullable=True)  # Para usuarios de cocina: 'frios', 'calientes', 'bebidas', 'postres'
    created_at = db.Column(db.DateTime, default=lima_datetime_naive)
    
    # Control de sesiones
    current_session_token = db.Column(db.String(255), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    last_activity = db.Column(db.DateTime, nullable=True)  # Nueva campo para auto-logout
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
    cashier_orders = db.relationship('Order', foreign_keys='Order.cashier_id', backref='cashier', lazy=True)
    cashier_payments = db.relationship('Payment', foreign_keys='Payment.cashier_id', backref='cashier_payments_rel', lazy=True)
    approved_reviews = db.relationship('Review', foreign_keys='Review.approved_by', backref='approver', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Establecer contraseña hasheada"""
        self.password = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Verificar contraseña - soporta tanto bcrypt como werkzeug.security"""
        try:
            # Primero intentar con werkzeug.security (pbkdf2)
            if self.password.startswith('pbkdf2:'):
                return check_password_hash(self.password, password)
            
            # Si no es pbkdf2, intentar con bcrypt
            elif self.password.startswith('$2b$'):
                from config.extensions import bcrypt
                return bcrypt.check_password_hash(self.password, password)
            
            # Si no es ninguno de los dos, intentar werkzeug por defecto
            else:
                return check_password_hash(self.password, password)
                
        except Exception as e:
            print(f"[USER_MODEL] Error verificando contraseña para {self.username}: {e}")
            return False

    @property
    def is_active(self):
        """Compatibilidad - usuarios siempre activos por defecto"""
        return True

    def to_dict(self):
        result = {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'estacion': self.estacion,
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
