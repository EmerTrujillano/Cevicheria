from datetime import datetime
from config.extensions import db

class Review(db.Model):
    __tablename__ = 'review'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)  # Nombre del cliente que deja la reseña
    rating = db.Column(db.Integer, nullable=False)  # De 1 a 5 estrellas
    comment = db.Column(db.Text)
    is_approved = db.Column(db.Boolean, default=False)  # Moderación de reseñas
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Admin que aprobó
    
    def __repr__(self):
        return f'<Review {self.customer_name} - {self.rating} stars>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'customer_name': self.customer_name,
            'rating': self.rating,
            'comment': self.comment,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat(),
            'approved_at': self.approved_at.isoformat() if self.approved_at else None
        }

class Payment(db.Model):
    __tablename__ = 'payment'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)  # cash, card, transfer
    cashier_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ID del cajero
    transaction_id = db.Column(db.String(100))  # ID de transacción para tarjetas
    notes = db.Column(db.Text)  # Notas adicionales del pago
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Payment {self.amount} - {self.payment_method}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'order_number': self.order.order_number if self.order else None,
            'amount': float(self.amount),
            'payment_method': self.payment_method,
            'cashier_id': self.cashier_id,
            'cashier_name': self.cashier.username if self.cashier else None,
            'transaction_id': self.transaction_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }