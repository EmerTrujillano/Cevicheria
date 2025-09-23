from datetime import datetime
from config.extensions import db

class Category(db.Model):
    __tablename__ = 'category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    estacion = db.Column(db.String(50), nullable=True)  # fríos, calientes, frituras, bebidas, postres, acompañamientos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    products = db.relationship('Product', backref='category', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Category {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'estacion': self.estacion,
            'created_at': self.created_at.isoformat(),
            'products_count': len(self.products)
        }
