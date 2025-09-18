from config.extensions import db
from models import Product, Category
from utils.validators import validate_required_fields, validate_positive_number

class ProductService:
    @staticmethod
    def get_all_products():
        """Obtener todos los productos"""
        products = Product.query.all()
        return [product.to_dict() for product in products]

    @staticmethod
    def get_product_by_id(product_id):
        """Obtener producto por ID"""
        product = Product.query.get(product_id)
        return product.to_dict() if product else None

    @staticmethod
    def create_product(data):
        """Crear nuevo producto"""
        required_fields = ['name', 'price', 'category_id']
        missing_fields = validate_required_fields(data, required_fields)
        
        if missing_fields:
            return None, f'Campos requeridos faltantes: {", ".join(missing_fields)}'
        
        # Validar precio
        if not validate_positive_number(data['price']):
            return None, 'El precio debe ser un número positivo'
        
        # Verificar que la categoría existe
        category = Category.query.get(data['category_id'])
        if not category:
            return None, 'Categoría no encontrada'
        
        # Verificar SKU único si se proporciona
        if 'sku' in data and data['sku']:
            existing_product = Product.query.filter_by(sku=data['sku']).first()
            if existing_product:
                return None, 'El SKU ya existe'
        
        product = Product(
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            stock=data.get('stock', 0),
            category_id=data['category_id'],
            brand=data.get('brand'),
            sku=data.get('sku'),
            unit=data.get('unit'),
            # Campos específicos para cevichería
            ingredients=data.get('ingredients'),
            tags=data.get('tags'),
            image_url=data.get('image_url'),
            image_gallery=data.get('image_gallery'),
            is_available=data.get('is_available', True),
            station_type=data.get('station_type', 'hot'),
            preparation_time=data.get('preparation_time', 15),
            spice_level=data.get('spice_level', 'mild')
        )
        
        db.session.add(product)
        db.session.commit()
        
        return product, None

    @staticmethod
    def update_product(product_id, data):
        """Actualizar producto existente"""
        product = Product.query.get(product_id)
        if not product:
            return None, 'Producto no encontrado'
        
        # Validar precio si se proporciona
        if 'price' in data and not validate_positive_number(data['price']):
            return None, 'El precio debe ser un número positivo'
        
        # Verificar categoría si se proporciona
        if 'category_id' in data:
            category = Category.query.get(data['category_id'])
            if not category:
                return None, 'Categoría no encontrada'
        
        # Verificar SKU único si se cambia
        if 'sku' in data and data['sku'] and data['sku'] != product.sku:
            existing_product = Product.query.filter_by(sku=data['sku']).first()
            if existing_product:
                return None, 'El SKU ya existe'
        
        # Actualizar campos
        updatable_fields = [
            'name', 'description', 'price', 'stock', 'category_id', 'brand', 'sku', 'unit',
            'ingredients', 'tags', 'image_url', 'image_gallery', 'is_available', 
            'station_type', 'preparation_time', 'spice_level'
        ]
        for field in updatable_fields:
            if field in data:
                setattr(product, field, data[field])
        
        db.session.commit()
        return product, None

    @staticmethod
    def delete_product(product_id):
        """Eliminar producto"""
        product = Product.query.get(product_id)
        if not product:
            return False, 'Producto no encontrado'
        
        db.session.delete(product)
        db.session.commit()
        return True, 'Producto eliminado exitosamente'

    @staticmethod
    def search_products(query):
        """Buscar productos por nombre o descripción"""
        products = Product.query.filter(
            Product.name.contains(query) | Product.description.contains(query)
        ).all()
        return [product.to_dict() for product in products]
