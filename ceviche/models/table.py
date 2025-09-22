from datetime import datetime, timedelta
from config.extensions import db

class Floor(db.Model):
    __tablename__ = 'floor'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # "Piso 1", "Piso 2", etc.
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    zones = db.relationship('Zone', backref='floor', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Floor {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'zones_count': len(self.zones),
            'created_at': self.created_at.isoformat()
        }

class Zone(db.Model):
    __tablename__ = 'zone'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # "Terraza", "Barra", "Niños", etc.
    description = db.Column(db.Text)
    floor_id = db.Column(db.Integer, db.ForeignKey('floor.id'), nullable=False)
    zone_type = db.Column(db.String(30), nullable=False, default='dining')  # dining, takeaway, delivery, private_event
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    tables = db.relationship('Table', backref='zone', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Zone {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'floor_id': self.floor_id,
            'floor_name': self.floor.name if self.floor else None,
            'zone_type': self.zone_type,
            'tables_count': len(self.tables),
            'available_tables': len([t for t in self.tables if t.status == 'available']),
            'created_at': self.created_at.isoformat()
        }

class Table(db.Model):
    __tablename__ = 'table'
    
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), nullable=False)  # "1", "2", "A1", "B3", etc.
    capacity = db.Column(db.Integer, nullable=False, default=4)
    zone_id = db.Column(db.Integer, db.ForeignKey('zone.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='available')  # available, occupied, reserved, cleaning, temp_occupied
    qr_code = db.Column(db.String(255), unique=True)  # URL del código QR
    
    # Campos para temporizador QR
    qr_scanned_at = db.Column(db.DateTime, nullable=True)  # Cuando se escaneó el QR
    qr_expires_at = db.Column(db.DateTime, nullable=True)  # Cuando expira el temporizador (10 min)
    qr_session_id = db.Column(db.String(100), nullable=True)  # ID único de sesión QR
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    orders = db.relationship('Order', backref='table', lazy=True)
    
    def __repr__(self):
        return f'<Table {self.number} - {self.zone.name if self.zone else "No Zone"}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'capacity': self.capacity,
            'zone_id': self.zone_id,
            'zone_name': self.zone.name if self.zone else None,
            'floor_name': self.zone.floor.name if self.zone and self.zone.floor else None,
            'status': self.status,
            'qr_code': self.qr_code,
            'qr_scanned_at': self.qr_scanned_at.isoformat() if self.qr_scanned_at else None,
            'qr_expires_at': self.qr_expires_at.isoformat() if self.qr_expires_at else None,
            'qr_session_id': self.qr_session_id,
            'is_qr_active': self.is_qr_session_active(),
            'qr_time_remaining': self.get_qr_time_remaining(),
            'created_at': self.created_at.isoformat()
        }
    
    def is_qr_session_active(self):
        """Verificar si la sesión QR está activa"""
        if not self.qr_expires_at:
            return False
        return datetime.utcnow() < self.qr_expires_at
    
    def get_qr_time_remaining(self):
        """Obtener tiempo restante de la sesión QR en segundos"""
        if not self.qr_expires_at:
            return 0
        
        remaining = self.qr_expires_at - datetime.utcnow()
        if remaining.total_seconds() <= 0:
            return 0
        
        return int(remaining.total_seconds())
    
    def start_qr_session(self, session_duration_minutes=10):
        """Iniciar sesión QR con temporizador"""
        import uuid
        
        self.qr_scanned_at = datetime.utcnow()
        self.qr_expires_at = datetime.utcnow() + timedelta(minutes=session_duration_minutes)
        self.qr_session_id = str(uuid.uuid4())
        self.status = 'temp_occupied'
        
        return self.qr_session_id
    
    def end_qr_session(self):
        """Finalizar sesión QR"""
        self.qr_scanned_at = None
        self.qr_expires_at = None
        self.qr_session_id = None
        if self.status == 'temp_occupied':
            self.status = 'available'