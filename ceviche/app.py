from flask import Flask
from config.config import config
from config.extensions import init_extensions, db
import os

def create_app(config_name=None):
    """Factory para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG') or 'default'
    
    app.config.from_object(config[config_name])
   
    # Inicializar extensiones
    init_extensions(app)
    
    # Importar todos los modelos para crear las tablas
    from models import (User, Category, Product, Survey, TemporaryPermission,
                       Floor, Zone, Table, Order, OrderItem, Review, Payment)
    from models.user_session import UserSession
    
    # Registrar blueprints existentes
    from routes.main_routes import main_bp
    from routes.auth_routes import auth_bp
    from routes.product_routes import products_bp
    from routes.category_routes import categories_bp
    from routes.user_routes import users_bp
    from routes.permission_routes import permissions_bp
    from routes.menu_routes import menu_bp
    
    # Blueprints por rol (si existen)
    try:
        from routes.admin_routes import admin_bp
        from routes.mozo_routes import mozo_bp
        from routes.cocina_routes import cocina_bp
        from routes.caja_routes import caja_bp
    except ImportError as e:
        print(f"⚠️ Algunos blueprints no disponibles: {e}")
        admin_bp = mozo_bp = cocina_bp = caja_bp = None
    
    # Blueprint para QR único del restaurante (si existe)
    try:
        from routes.restaurant_qr_routes import restaurant_qr_bp
    except ImportError:
        restaurant_qr_bp = None
    
    # Blueprints principales
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Blueprints por rol (si están disponibles)
    if admin_bp:
        app.register_blueprint(admin_bp)
    if mozo_bp:
        app.register_blueprint(mozo_bp)
    if cocina_bp:
        app.register_blueprint(cocina_bp)
    if caja_bp:
        app.register_blueprint(caja_bp)
    
    # Blueprint para QR único del restaurante (si existe)
    if restaurant_qr_bp:
        app.register_blueprint(restaurant_qr_bp)
    
    # Blueprints existentes
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(permissions_bp, url_prefix='/api/permissions')
    app.register_blueprint(menu_bp)  # ¡IMPORTANTE! Blueprint del menú sin prefix adicional
    
    # Inicializar servicios solo si están disponibles
    try:
        from services.qr_session_service import qr_service
        from services.inactivity_service import inactivity_service
        
        def start_background_services():
            """Iniciar servicios en background"""
            qr_service.start_cleanup_service(app)
            inactivity_service.start(app)  # Iniciar servicio de auto-logout
            
        # Crear tablas si no existen
        with app.app_context():
            db.create_all()
            # Iniciar servicios después de crear las tablas
            start_background_services()
    except ImportError as e:
        print(f"⚠️ Servicios de background no disponibles: {e}")
        # Solo crear tablas
        with app.app_context():
            db.create_all()
    
    return app

# Para desarrollo directo
if __name__ == '__main__':
    app = create_app('mysql')  # Usar MySQL
    app.run(host='0.0.0.0', port=5000, debug=True)
