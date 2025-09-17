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
    
    # Registrar blueprints existentes
    from routes.main_routes import main_bp
    from routes.auth_routes import auth_bp
    from routes.product_routes import products_bp
    from routes.category_routes import categories_bp
    from routes.user_routes import users_bp
    from routes.permission_routes import permissions_bp
    from routes.dashboard_routes import dashboard_bp
    
    # Registrar nuevos blueprints para cevichería
    from routes.waiter_routes import waiter_bp
    from routes.kitchen_routes import kitchen_bp
    from routes.cashier_routes import cashier_bp
    from routes.menu_routes import menu_bp
    from routes.admin_routes import admin_bp
    
    # Blueprints principales
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Blueprints existentes
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(permissions_bp, url_prefix='/api/permissions')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    
    # Nuevos blueprints para cevichería
    app.register_blueprint(waiter_bp, url_prefix='/api/waiter')
    app.register_blueprint(kitchen_bp, url_prefix='/api/kitchen')
    app.register_blueprint(cashier_bp, url_prefix='/api/cashier')
    app.register_blueprint(menu_bp)  # Sin prefix adicional, ya tiene /menu en el blueprint
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Inicializar servicio de sesiones QR
    from services.qr_session_service import qr_service
    
    def start_background_services():
        """Iniciar servicios en background"""
        qr_service.start_cleanup_service(app)
    
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
        # Iniciar servicios después de crear las tablas
        start_background_services()
    
    return app

# Para desarrollo directo
if __name__ == '__main__':
    app = create_app('development')  # Volver a development (SQLite temporalmente)
    app.run(host='0.0.0.0', port=5000, debug=True)
