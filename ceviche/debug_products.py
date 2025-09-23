#!/usr/bin/env python3
"""Script para debug de productos y sus imágenes"""

import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import Product
from config.extensions import db

def debug_products():
    """Debug de productos y sus URLs de imagen"""
    try:
        # Obtener todos los productos
        products = Product.query.all()
        
        print(f"Total de productos encontrados: {len(products)}")
        print("=" * 50)
        
        for product in products:
            print(f"ID: {product.id}")
            print(f"Nombre: {product.name}")
            print(f"image_url: '{product.image_url}'")
            print(f"image_url es None: {product.image_url is None}")
            print(f"image_url está vacío: {product.image_url == ''}")
            
            # Mostrar el to_dict
            product_dict = product.to_dict()
            print(f"to_dict image_url: '{product_dict.get('image_url')}'")
            print("-" * 30)
        
        # Probar productos con imagen específicamente
        products_with_images = Product.query.filter(Product.image_url.isnot(None)).filter(Product.image_url != '').all()
        print(f"\nProductos con image_url no vacío: {len(products_with_images)}")
        
        for product in products_with_images:
            print(f"- {product.name}: {product.image_url}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Configurar la aplicación para usar la base de datos
    from app import create_app
    app = create_app('mysql')
    with app.app_context():
        debug_products()