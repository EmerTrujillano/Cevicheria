from datetime import datetime
from config.extensions import db

class Order(db.Model):
    __tablename__ = 'order'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)  # COM-001, COM-002, etc.
    table_id = db.Column(db.Integer, db.ForeignKey('table.id'), nullable=True)  # Null para delivery/takeaway
    waiter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ID del mozo
    customer_name = db.Column(db.String(100))  # Opcional para identificar al cliente
    order_type = db.Column(db.String(20), nullable=False, default='dine_in')  # dine_in, takeaway, delivery, private_event
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, in_kitchen, ready, served, completed, cancelled
    
    # Campos de pago
    payment_status = db.Column(db.String(20), nullable=False, default='pending')  # pending, paid, refunded
    payment_method = db.Column(db.String(20))  # efectivo, tarjeta, yapeplin
    amount_received = db.Column(db.Numeric(10,2))  # Monto recibido
    change_given = db.Column(db.Numeric(10,2))  # Cambio entregado
    cashier_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # ID del cajero
    
    total_amount = db.Column(db.Numeric(10,2), nullable=False, default=0.00)
    special_instructions = db.Column(db.Text)  # Instrucciones especiales del cliente
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    served_at = db.Column(db.DateTime, nullable=True)
    paid_at = db.Column(db.DateTime, nullable=True)
    
    # Relaciones
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='order', lazy=True, cascade='all, delete-orphan')
    
    # No definir relaciones adicionales aquí para evitar conflictos con backref existentes
    
    def __repr__(self):
        return f'<Order {self.order_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'table_id': self.table_id,
            'table_number': self.table.number if self.table else None,
            'zone_name': self.table.zone.name if self.table and self.table.zone else None,
            'floor_name': self.table.zone.floor.name if self.table and self.table.zone and self.table.zone.floor else None,
            'waiter_id': self.waiter_id,
            'waiter_name': self.waiter.username if self.waiter else None,
            'customer_name': self.customer_name,
            'order_type': self.order_type,
            'status': self.status,
            'total_amount': float(self.total_amount),
            'special_instructions': self.special_instructions,
            'items_count': len(self.order_items),
            'created_at': self.created_at.isoformat(),
            'served_at': self.served_at.isoformat() if self.served_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None
        }

class OrderItem(db.Model):
    __tablename__ = 'order_item'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10,2), nullable=False)  # Precio al momento del pedido
    total_price = db.Column(db.Numeric(10,2), nullable=False)
    special_instructions = db.Column(db.Text)  # "Sin cebolla", "Extra picante", etc.
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, in_queue, preparing, ready, served, cancelled
    station_type = db.Column(db.String(20))  # cold, hot, drinks, desserts (heredado del producto)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)  # Cuando empezó la preparación
    ready_at = db.Column(db.DateTime, nullable=True)  # Cuando estuvo listo
    served_at = db.Column(db.DateTime, nullable=True)  # Cuando se entregó
    
    def __repr__(self):
        return f'<OrderItem {self.product.name if self.product else "Unknown"} x{self.quantity}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price),
            'total_price': float(self.total_price),
            'special_instructions': self.special_instructions,
            'status': self.status,
            'station_type': self.station_type,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ready_at': self.ready_at.isoformat() if self.ready_at else None,
            'served_at': self.served_at.isoformat() if self.served_at else None
        }