#!/usr/bin/env python3
"""Script para limpiar los valores 'None' en image_url"""

import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import Product
from config.extensions import db

def fix_image_urls():
    """Limpiar los valores 'None' en image_url"""
    try:
        # Buscar productos con 'None' como string
        products_with_none_string = Product.query.filter(Product.image_url == 'None').all()
        
        print(f"Productos con image_url = 'None': {len(products_with_none_string)}")
        
        for product in products_with_none_string:
            print(f"Limpiando producto: {product.name}")
            product.image_url = None
        
        # Buscar productos con strings vacíos
        products_with_empty_string = Product.query.filter(Product.image_url == '').all()
        
        print(f"Productos con image_url vacío: {len(products_with_empty_string)}")
        
        for product in products_with_empty_string:
            print(f"Limpiando producto: {product.name}")
            product.image_url = None
        
        # Guardar cambios
        db.session.commit()
        print("✅ Base de datos actualizada exitosamente")
        
        # Verificar resultados
        products_with_images = Product.query.filter(Product.image_url.isnot(None)).all()
        print(f"\nProductos con imágenes válidas después de la limpieza: {len(products_with_images)}")
        
        for product in products_with_images:
            print(f"- {product.name}: {product.image_url}")
            
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()

if __name__ == "__main__":
    # Configurar la aplicación para usar la base de datos
    from app import create_app
    app = create_app('mysql')
    with app.app_context():
        fix_image_urls()