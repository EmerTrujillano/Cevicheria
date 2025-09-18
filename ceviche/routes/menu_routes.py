from flask import Blueprint, request, jsonify, render_template
from models import Product, Category, Review
from config.extensions import db
from sqlalchemy import and_, func

menu_bp = Blueprint('menu', __name__, url_prefix='/menu')

@menu_bp.route('/')
def virtual_menu():
    """Menú virtual para clientes (no requiere autenticación)"""
    table_id = request.args.get('table')
    return render_template('menu/virtual_menu_simple.html', table_id=table_id)

@menu_bp.route('/categories')
def get_categories():
    """Obtener todas las categorías con productos disponibles"""
    try:
        categories = Category.query.all()
        categories_data = []
        
        for category in categories:
            # Solo incluir categorías con productos disponibles
            available_products = [
                product for product in category.products 
                if product.is_available
            ]
            
            if available_products:
                category_data = category.to_dict()
                category_data['products_count'] = len(available_products)
                categories_data.append(category_data)
        
        return jsonify({
            'success': True,
            'data': categories_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener categorías: {str(e)}'
        }), 500

@menu_bp.route('/products')
def get_menu_products():
    """Obtener productos del menú organizados por categoría"""
    try:
        category_id = request.args.get('category_id', type=int)
        
        # Construir query base para productos disponibles
        query = Product.query.filter(Product.is_available == True)
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        products = query.all()
        
        # Organizar por categorías
        menu_data = {}
        for product in products:
            category_name = product.category.name if product.category else 'Sin categoría'
            
            if category_name not in menu_data:
                menu_data[category_name] = {
                    'category': product.category.to_dict() if product.category else None,
                    'products': []
                }
            
            product_data = product.to_dict()
            
            # Agregar reseñas aprobadas
            approved_reviews = [
                review.to_dict() for review in product.reviews 
                if review.is_approved
            ]
            product_data['reviews'] = approved_reviews[:3]  # Solo las primeras 3
            product_data['total_reviews'] = len(approved_reviews)
            
            menu_data[category_name]['products'].append(product_data)
        
        return jsonify({
            'success': True,
            'data': list(menu_data.values())
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener productos del menú: {str(e)}'
        }), 500

@menu_bp.route('/products/<int:product_id>')
def get_product_details(product_id):
    """Obtener detalles completos de un producto"""
    try:
        product = Product.query.filter(
            Product.id == product_id,
            Product.is_available == True
        ).first_or_404()
        
        product_data = product.to_dict()
        
        # Obtener todas las reseñas aprobadas
        approved_reviews = [
            review.to_dict() for review in product.reviews 
            if review.is_approved
        ]
        product_data['reviews'] = approved_reviews
        
        # Productos relacionados (misma categoría)
        related_products = Product.query.filter(
            Product.category_id == product.category_id,
            Product.id != product.id,
            Product.is_available == True
        ).limit(4).all()
        
        product_data['related_products'] = [
            {
                'id': p.id,
                'name': p.name,
                'price': float(p.price),
                'image_url': p.image_url,
                'average_rating': p.get_average_rating(),
                'tags': p.get_tags_list()
            }
            for p in related_products
        ]
        
        return jsonify({
            'success': True,
            'data': product_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener detalles del producto: {str(e)}'
        }), 500

@menu_bp.route('/products/<int:product_id>/reviews')
def get_product_reviews(product_id):
    """Obtener todas las reseñas de un producto"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        product = Product.query.get_or_404(product_id)
        
        # Obtener reseñas aprobadas paginadas
        reviews = Review.query.filter(
            Review.product_id == product_id,
            Review.is_approved == True
        ).order_by(Review.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        reviews_data = [review.to_dict() for review in reviews.items]
        
        # Estadísticas de reseñas
        rating_stats = db.session.query(
            Review.rating,
            func.count(Review.id).label('count')
        ).filter(
            Review.product_id == product_id,
            Review.is_approved == True
        ).group_by(Review.rating).all()
        
        stats = {rating: count for rating, count in rating_stats}
        
        return jsonify({
            'success': True,
            'data': {
                'reviews': reviews_data,
                'pagination': {
                    'page': reviews.page,
                    'pages': reviews.pages,
                    'per_page': reviews.per_page,
                    'total': reviews.total
                },
                'stats': {
                    'average_rating': product.get_average_rating(),
                    'total_reviews': reviews.total,
                    'rating_distribution': stats
                }
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener reseñas: {str(e)}'
        }), 500

@menu_bp.route('/search')
def search_products():
    """Buscar productos en el menú"""
    try:
        query_text = request.args.get('q', '').strip()
        category_id = request.args.get('category_id', type=int)
        tags = request.args.get('tags', '').split(',') if request.args.get('tags') else []
        spice_level = request.args.get('spice_level')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        
        if not query_text and not category_id and not tags and not spice_level:
            return jsonify({
                'success': False,
                'message': 'Se requiere al menos un criterio de búsqueda'
            }), 400
        
        # Construir query
        query = Product.query.filter(Product.is_available == True)
        
        if query_text:
            search_term = f'%{query_text}%'
            query = query.filter(
                db.or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.ingredients.ilike(search_term)
                )
            )
        
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if spice_level:
            query = query.filter(Product.spice_level == spice_level)
        
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        
        products = query.all()
        
        # Filtrar por tags si se especificaron
        if tags:
            filtered_products = []
            for product in products:
                product_tags = product.get_tags_list()
                if any(tag.strip() in product_tags for tag in tags if tag.strip()):
                    filtered_products.append(product)
            products = filtered_products
        
        products_data = []
        for product in products:
            product_data = product.to_dict()
            # Solo incluir datos básicos para la búsqueda
            product_data['reviews'] = []  # No incluir reseñas en búsqueda
            products_data.append(product_data)
        
        return jsonify({
            'success': True,
            'data': products_data,
            'total_results': len(products_data)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error en la búsqueda: {str(e)}'
        }), 500

@menu_bp.route('/featured')
def get_featured_products():
    """Obtener productos destacados"""
    try:
        # Productos con tags especiales
        featured_tags = ['recomendado', 'nuevo', 'mas_vendido']
        
        featured_products = []
        for tag in featured_tags:
            products = Product.query.filter(
                Product.is_available == True,
                Product.tags.contains(tag)
            ).limit(3).all()
            
            if products:
                featured_products.extend([
                    {
                        'tag': tag,
                        'products': [p.to_dict() for p in products]
                    }
                ])
        
        return jsonify({
            'success': True,
            'data': featured_products
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener productos destacados: {str(e)}'
        }), 500

# RUTAS QR ELIMINADAS - AHORA SE USA EL SISTEMA QR ÚNICO EN /restaurant/