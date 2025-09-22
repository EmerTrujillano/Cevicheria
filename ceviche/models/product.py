from datetime import datetime
from config.extensions import db

class Product(db.Model):
    __tablename__ = 'product'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10,2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    brand = db.Column(db.String(50))
    sku = db.Column(db.String(20), unique=True)
    unit = db.Column(db.String(20))
    
    # Campos específicos para cevichería
    ingredients = db.Column(db.Text)  # Lista de ingredientes separados por comas
    tags = db.Column(db.String(200))  # "picante,recomendado,nuevo,mas_vendido" separados por comas
    image_url = db.Column(db.String(255))  # URL de la imagen principal
    image_gallery = db.Column(db.Text)  # URLs de galería separadas por comas
    is_available = db.Column(db.Boolean, default=True)  # Disponible o agotado
    station_type = db.Column(db.String(20), default='hot')  # cold, hot, drinks, desserts
    preparation_time = db.Column(db.Integer, default=15)  # Tiempo estimado en minutos
    spice_level = db.Column(db.String(10), default='mild')  # mild, medium, hot, very_hot
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    surveys = db.relationship('Survey', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    reviews = db.relationship('Review', backref='product', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Product {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'stock': self.stock,
            'brand': self.brand,
            'sku': self.sku,
            'unit': self.unit,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            # Campos específicos para cevichería
            'ingredients': self.ingredients.split(',') if self.ingredients else [],
            'tags': self.tags.split(',') if self.tags else [],
            'image_url': self.image_url,
            'image_gallery': self.image_gallery.split(',') if self.image_gallery else [],
            'is_available': self.is_available,
            'station_type': self.station_type,
            'preparation_time': self.preparation_time,
            'spice_level': self.spice_level,
            'average_rating': self.get_average_rating(),
            'reviews_count': len(self.reviews),
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }
    
    def get_average_rating(self):
        """Calcula el rating promedio de las reseñas aprobadas"""
        approved_reviews = [r for r in self.reviews if r.is_approved]
        if not approved_reviews:
            return 0
        return sum(r.rating for r in approved_reviews) / len(approved_reviews)
    
    def get_tags_list(self):
        """Retorna las etiquetas como lista"""
        return self.tags.split(',') if self.tags else []
    
    def has_tag(self, tag):
        """Verifica si el producto tiene una etiqueta específica"""
        return tag in self.get_tags_list()
