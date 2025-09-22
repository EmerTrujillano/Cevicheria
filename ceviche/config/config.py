import os
from datetime import timedelta
import pytz

class Config:
    """Configuración base de la aplicación"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'CONTRASENA_ADMIN_PAV_ERIK_WA'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'SKDJHSAKDjsJDSDJSJHSKJjfdflññdoodñflsf'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de zona horaria para Lima, Perú
    TIMEZONE = pytz.timezone('America/Lima')

class DevelopmentConfig(Config):
    """Configuración para desarrollo con SQLite"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///cevicheria_dev.db'

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:@localhost:3306/cevicheria_db'

class MySQLConfig(Config):
    """Configuración específica para MySQL"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/cevicheria_db'

# Configuración por defecto - Usar MySQL para desarrollo
config = {
    'development': MySQLConfig,  # MySQL para desarrollo
    'production': ProductionConfig,
    'mysql': MySQLConfig,
    'default': MySQLConfig  # MySQL por defecto
}
