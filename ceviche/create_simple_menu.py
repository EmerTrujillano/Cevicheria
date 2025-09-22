#!/usr/bin/env python3
"""
Script para crear el menú simple del restaurante según especificaciones del usuario
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models.category import Category
from models.product import Product
from config.extensions import db

def limpiar_menu_actual(app):
    """Elimina todos los productos y categorías actuales"""
    print("🧹 Limpiando menú actual...")
    
    with app.app_context():
        # Eliminar todos los productos
        Product.query.delete()
        # Eliminar todas las categorías
        Category.query.delete()
        db.session.commit()
        print("✅ Menú actual eliminado")

def crear_menu_simple(app):
    """Crea el menú simple con los datos especificados"""
    print("🍽️ Creando menú simple...")
    
    # Datos del menú según especificaciones del usuario
    menu_data = {
        "fríos": [
            "Ceviche clásico",
            "Ceviche mixto", 
            "Ceviche nikkei",
            "Tiradito al ají amarillo",
            "Tiradito tres ajíes",
            "Leche de tigre",
            "Choritos a la chalaca",
            "Causa limeña (pollo / pulpo / cangrejo)",
            "Piqueo marino (frío)"
        ],
        "calientes": [
            "Arroz con mariscos",
            "Chaufa de mariscos",
            "Tacu tacu con mariscos",
            "Sudado de pescado",
            "Parihuela",
            "Pescado a lo macho",
            "Ají de gallina",
            "Piqueo marino (caliente)"
        ],
        "frituras": [
            "Jalea mixta",
            "Chicharrón de calamar",
            "Pulpo a la parrilla",
            "Lomo saltado"
        ],
        "bebidas": [
            "Chicha morada",
            "Chicha de jora",
            "Inca Kola",
            "Jugo de maracuyá",
            "Limonada",
            "Agua sin/con gas",
            "Pisco Sour",
            "Chilcano (clásico, maracuyá, jengibre)",
            "Sangría",
            "Cerveza (Pilsen, Cusqueña, artesanal)"
        ],
        "postres": [
            "Suspiro limeño",
            "Mazamorra morada",
            "Arroz con leche",
            "Tres leches",
            "Helado de maracuyá o chirimoya"
        ],
        "acompañamientos": [
            "Camote glaseado",
            "Choclo con queso",
            "Papa o yuca frita",
            "Ensalada criolla",
            "Pan al ajo"
        ]
    }
    
    # Precios base por categoría
    precios_base = {
        "fríos": 25.00,
        "calientes": 30.00,
        "frituras": 28.00,
        "bebidas": 8.00,
        "postres": 12.00,
        "acompañamientos": 10.00
    }
    
    with app.app_context():
        # Crear categorías y productos
        for categoria_nombre, platos in menu_data.items():
            print(f"📂 Creando categoría: {categoria_nombre}")
            
            # Crear categoría
            categoria = Category(
                name=categoria_nombre,
                description=f"Deliciosos platos {categoria_nombre} de la casa"
            )
            db.session.add(categoria)
            db.session.flush()  # Para obtener el ID
            
            # Crear productos de la categoría
            precio_base = precios_base[categoria_nombre]
            for i, plato in enumerate(platos):
                # Variar precio ligeramente
                precio = precio_base + (i * 2)
                if categoria_nombre == "bebidas":
                    if "Pisco" in plato or "Chilcano" in plato or "Sangría" in plato:
                        precio = 15.00 + (i * 1)
                    elif "Cerveza" in plato:
                        precio = 12.00
                
                producto = Product(
                    name=plato,
                    description=f"Delicioso {plato.lower()} preparado con ingredientes frescos",
                    price=precio,
                    category_id=categoria.id,
                    is_available=True,
                    ingredients="Ingredientes frescos de primera calidad"
                )
                db.session.add(producto)
                print(f"   ✅ {plato} - S/. {precio:.2f}")
        
        db.session.commit()
        print("🎉 Menú simple creado exitosamente!")

def main():
    print("🚀 Iniciando creación de menú simple...")
    
    # Crear aplicación
    app = create_app('mysql')
    
    try:
        # Limpiar menú actual
        limpiar_menu_actual(app)
        
        # Crear nuevo menú simple
        crear_menu_simple(app)
        
        print("\n✨ ¡Menú simple creado exitosamente!")
        print("📊 Resumen:")
        
        with app.app_context():
            categorias = Category.query.all()
            for categoria in categorias:
                productos_count = Product.query.filter_by(category_id=categoria.id).count()
                print(f"   {categoria.name}: {productos_count} productos")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()