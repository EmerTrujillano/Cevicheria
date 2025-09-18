#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para resolver el problema de claves foráneas y actualizar el sistema de menú completo
"""

from config.extensions import db
from models.category import Category
from models.product import Product
from models.user import User
from models.review import Review
import bcrypt

# Primero necesitamos eliminar las reseñas para evitar errores de clave foránea
def clean_reviews():
    """Limpiar todas las reseñas para evitar conflictos de clave foránea"""
    try:
        # Eliminar todas las reseñas
        Review.query.delete()
        db.session.commit()
        print("✅ Reseñas eliminadas exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error eliminando reseñas: {e}")
        db.session.rollback()
        return False

# Luego actualizar categorías
def update_categories():
    """Actualizar categorías con estaciones"""
    try:
        # Primero eliminar productos para evitar error de clave foránea
        Product.query.delete()
        db.session.commit()
        
        # Luego eliminar categorías existentes
        Category.query.delete()
        db.session.commit()

        # Crear las nuevas categorías con estaciones
        categories_data = [
            {"name": "Platos Fríos", "description": "Ceviches, tiraditos y platos fríos", "estacion": "frios"},
            {"name": "Platos Calientes", "description": "Arroces, sudados y guisos", "estacion": "calientes"},
            {"name": "Frituras", "description": "Chicharrones, jalea y frituras", "estacion": "frituras"},
            {"name": "Bebidas", "description": "Jugos, refrescos y bebidas", "estacion": "bebidas"},
            {"name": "Postres", "description": "Dulces y postres peruanos", "estacion": "postres"},
            {"name": "Acompañamientos", "description": "Guarniciones y extras", "estacion": "acompañamientos"}
        ]

        for cat_data in categories_data:
            category = Category(
                name=cat_data["name"],
                description=cat_data["description"],
                estacion=cat_data["estacion"]
            )
            db.session.add(category)

        db.session.commit()
        print("✅ Categorías actualizadas exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error actualizando categorías: {e}")
        db.session.rollback()
        return False

# Actualizar productos
def update_products():
    """Actualizar productos con el nuevo menú completo"""
    try:
        # Los productos ya fueron eliminados en update_categories()
        # No necesitamos eliminarlos nuevamente

        # Obtener IDs de categorías
        frios_cat = Category.query.filter_by(estacion="frios").first()
        calientes_cat = Category.query.filter_by(estacion="calientes").first()
        frituras_cat = Category.query.filter_by(estacion="frituras").first()
        bebidas_cat = Category.query.filter_by(estacion="bebidas").first()
        postres_cat = Category.query.filter_by(estacion="postres").first()
        acomp_cat = Category.query.filter_by(estacion="acompañamientos").first()

        # PLATOS FRÍOS (Estación: fríos)
        productos_frios = [
            {"name": "Ceviche de Pescado", "description": "Pescado fresco marinado en limón con cebolla, ají limo, culantro y camote", "price": 25.00},
            {"name": "Ceviche Mixto", "description": "Pescado y mariscos frescos marinados con limón, cebolla y ají amarillo", "price": 32.00},
            {"name": "Ceviche de Conchas Negras", "description": "Conchas negras frescas marinadas en su jugo con limón y especias", "price": 35.00},
            {"name": "Tiradito de Pescado", "description": "Finas láminas de pescado bañadas en crema de ají amarillo", "price": 28.00},
            {"name": "Tiradito Nikkei", "description": "Pescado fresco con salsa de soya, jengibre y ají amarillo", "price": 30.00},
            {"name": "Leche de Tigre", "description": "Concentrado de ceviche con mariscos, culantro y especias", "price": 15.00},
            {"name": "Causa Limeña", "description": "Capas de papa amarilla rellena con pollo, palta y mayonesa", "price": 18.00},
            {"name": "Causa de Mariscos", "description": "Papa amarilla con mariscos frescos y palta", "price": 22.00},
            {"name": "Choros a la Chalaca", "description": "Mejillones frescos con salsa chalaca de cebolla, tomate y limón", "price": 20.00},
            {"name": "Pulpo al Olivo", "description": "Pulpo tierno bañado en crema de aceitunas negras", "price": 28.00}
        ]

        # PLATOS CALIENTES (Estación: calientes)
        productos_calientes = [
            {"name": "Arroz con Mariscos", "description": "Arroz amarillo con mariscos frescos y culantro", "price": 30.00},
            {"name": "Arroz con Pollo", "description": "Arroz cilantrado con pollo tierno y verduras", "price": 22.00},
            {"name": "Paella Peruana", "description": "Arroz con mariscos, pollo y verduras al estilo peruano", "price": 35.00},
            {"name": "Sudado de Pescado", "description": "Pescado cocido al vapor con cebolla, tomate y culantro", "price": 26.00},
            {"name": "Sudado de Mariscos", "description": "Mariscos frescos sudados con verduras y especias", "price": 32.00},
            {"name": "Parihuela", "description": "Sopa concentrada de mariscos con pescado y ají panca", "price": 28.00},
            {"name": "Chupe de Camarones", "description": "Sopa cremosa de camarones con huevo, leche y queso", "price": 30.00},
            {"name": "Aguadito de Mariscos", "description": "Arroz aguado con mariscos, culantro y ají amarillo", "price": 25.00},
            {"name": "Pescado a la Plancha", "description": "Filete de pescado grillado con ensalada y papas", "price": 24.00},
            {"name": "Saltado de Mariscos", "description": "Mariscos salteados con cebolla, tomate y papas fritas", "price": 28.00},
            {"name": "Tacu Tacu con Mariscos", "description": "Arroz con frejoles refritos coronado con mariscos", "price": 26.00},
            {"name": "Picante de Mariscos", "description": "Mariscos en salsa picante de ají amarillo", "price": 29.00}
        ]

        # FRITURAS (Estación: frituras)
        productos_frituras = [
            {"name": "Chicharrón de Pescado", "description": "Trozos de pescado fritos acompañados de yuca y salsa criolla", "price": 22.00},
            {"name": "Chicharrón de Pollo", "description": "Pollo frito crujiente con camote y salsa huancaína", "price": 20.00},
            {"name": "Chicharrón Mixto", "description": "Pescado y pollo frito con yuca y camote", "price": 25.00},
            {"name": "Jalea de Mariscos", "description": "Mariscos y pescado fritos con yuca y salsa criolla", "price": 32.00},
            {"name": "Jalea Personal", "description": "Porción individual de mariscos fritos", "price": 18.00},
            {"name": "Pescado Frito", "description": "Pescado entero frito con arroz y frejoles", "price": 24.00},
            {"name": "Calamares Fritos", "description": "Anillos de calamar empanizados con salsa tártara", "price": 20.00},
            {"name": "Tequeños de Mariscos", "description": "Rollitos fritos rellenos de mariscos", "price": 16.00},
            {"name": "Yuquitas Fritas", "description": "Yuca frita dorada acompañada de huancaína", "price": 12.00}
        ]

        # BEBIDAS (Estación: bebidas)
        productos_bebidas = [
            {"name": "Chicha Morada", "description": "Bebida tradicional de maíz morado con frutas", "price": 8.00},
            {"name": "Limonada", "description": "Limonada fresca natural", "price": 6.00},
            {"name": "Limonada Frozen", "description": "Limonada helada con hielo frappe", "price": 8.00},
            {"name": "Maracuyá", "description": "Jugo de maracuyá natural", "price": 7.00},
            {"name": "Papaya", "description": "Jugo de papaya fresco", "price": 7.00},
            {"name": "Piña", "description": "Jugo de piña natural", "price": 7.00},
            {"name": "Naranja", "description": "Jugo de naranja recién exprimido", "price": 6.00},
            {"name": "Inca Kola", "description": "Gaseosa nacional peruana", "price": 5.00},
            {"name": "Coca Cola", "description": "Gaseosa clásica", "price": 5.00},
            {"name": "Agua", "description": "Agua mineral sin gas", "price": 3.00},
            {"name": "Agua con Gas", "description": "Agua mineral con gas", "price": 4.00},
            {"name": "Pisco Sour", "description": "Cóctel peruano con pisco, limón y clara de huevo", "price": 15.00},
            {"name": "Chilcano", "description": "Pisco con ginger ale y limón", "price": 12.00},
            {"name": "Cerveza", "description": "Cerveza nacional fría", "price": 8.00}
        ]

        # POSTRES (Estación: postres)
        productos_postres = [
            {"name": "Suspiro Limeño", "description": "Dulce de leche con merengue y canela", "price": 12.00},
            {"name": "Tres Leches", "description": "Bizcocho empapado en tres tipos de leche", "price": 10.00},
            {"name": "Mazamorra Morada", "description": "Postre tradicional de maíz morado con frutas", "price": 8.00},
            {"name": "Arroz con Leche", "description": "Arroz dulce con leche, canela y pasas", "price": 8.00},
            {"name": "Picarones", "description": "Buñuelos de zapallo con miel de chancaca", "price": 10.00},
            {"name": "Helado de Lúcuma", "description": "Helado artesanal de fruta peruana", "price": 9.00},
            {"name": "Helado de Chirimoya", "description": "Helado cremoso de chirimoya", "price": 9.00},
            {"name": "Flan de Vainilla", "description": "Flan casero con caramelo", "price": 8.00}
        ]

        # ACOMPAÑAMIENTOS (Estación: acompañamientos)
        productos_acomp = [
            {"name": "Arroz Blanco", "description": "Arroz blanco graneado", "price": 5.00},
            {"name": "Frejoles", "description": "Frejoles canarios guisados", "price": 6.00},
            {"name": "Yuca Sancochada", "description": "Yuca hervida tierna", "price": 5.00},
            {"name": "Camote Sancochado", "description": "Camote dulce hervido", "price": 5.00},
            {"name": "Platanos Maduros", "description": "Plátanos dulces fritos", "price": 6.00},
            {"name": "Ensalada Mixta", "description": "Lechuga, tomate, cebolla y aceitunas", "price": 8.00},
            {"name": "Palta", "description": "Palta fresca en rodajas", "price": 4.00},
            {"name": "Salsa Criolla", "description": "Cebolla, ají y limón", "price": 3.00},
            {"name": "Salsa Huancaína", "description": "Crema de ají amarillo", "price": 4.00},
            {"name": "Salsa Ocopa", "description": "Crema de huacatay", "price": 4.00},
            {"name": "Cancha Serrana", "description": "Maíz tostado salado", "price": 3.00}
        ]

        # Crear productos para cada categoría
        categorias_productos = [
            (frios_cat.id, productos_frios),
            (calientes_cat.id, productos_calientes),
            (frituras_cat.id, productos_frituras),
            (bebidas_cat.id, productos_bebidas),
            (postres_cat.id, productos_postres),
            (acomp_cat.id, productos_acomp)
        ]

        for categoria_id, productos in categorias_productos:
            for prod_data in productos:
                product = Product(
                    name=prod_data["name"],
                    description=prod_data["description"],
                    price=prod_data["price"],
                    category_id=categoria_id,
                    is_available=True
                )
                db.session.add(product)

        db.session.commit()
        print("✅ Productos actualizados exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error actualizando productos: {e}")
        db.session.rollback()
        return False

# Crear usuarios de cocina especializados
def create_kitchen_users():
    """Crear usuarios de cocina para cada estación"""
    try:
        # Crear usuarios de cocina especializados
        kitchen_users = [
            {"username": "cocina1", "password": "frios2025", "estacion": "frios"},
            {"username": "cocina2", "password": "calientes2025", "estacion": "calientes"},
            {"username": "cocina3", "password": "frituras2025", "estacion": "frituras"},
            {"username": "cocina4", "password": "bebidas2025", "estacion": "bebidas"},
            {"username": "cocina5", "password": "postres2025", "estacion": "postres"},
            {"username": "cocina6", "password": "acomp2025", "estacion": "acompañamientos"}
        ]

        for user_data in kitchen_users:
            # Verificar si el usuario ya existe
            existing_user = User.query.filter_by(username=user_data["username"]).first()
            if not existing_user:
                # Hash de la contraseña
                password_hash = bcrypt.hashpw(user_data["password"].encode('utf-8'), bcrypt.gensalt())
                
                user = User(
                    username=user_data["username"],
                    password=password_hash.decode('utf-8'),
                    role="cocina",
                    estacion=user_data["estacion"]
                )
                db.session.add(user)
                print(f"✅ Usuario {user_data['username']} creado para estación {user_data['estacion']}")
            else:
                # Actualizar usuario existente
                password_hash = bcrypt.hashpw(user_data["password"].encode('utf-8'), bcrypt.gensalt())
                existing_user.password = password_hash.decode('utf-8')
                existing_user.estacion = user_data["estacion"]
                print(f"✅ Usuario {user_data['username']} actualizado para estación {user_data['estacion']}")

        db.session.commit()
        print("✅ Usuarios de cocina creados/actualizados exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error creando usuarios de cocina: {e}")
        db.session.rollback()
        return False

if __name__ == '__main__':
    from app import create_app
    
    app = create_app('mysql')
    with app.app_context():
        print("🚀 Iniciando actualización completa del sistema de menú...")
        
        # Paso 1: Limpiar reseñas
        print("\n📝 Paso 1: Limpiando reseñas...")
        if not clean_reviews():
            print("❌ Error en paso 1. Deteniendo proceso.")
            exit(1)
        
        # Paso 2: Actualizar categorías
        print("\n📂 Paso 2: Actualizando categorías...")
        if not update_categories():
            print("❌ Error en paso 2. Deteniendo proceso.")
            exit(1)
        
        # Paso 3: Actualizar productos
        print("\n🍽️ Paso 3: Actualizando productos...")
        if not update_products():
            print("❌ Error en paso 3. Deteniendo proceso.")
            exit(1)
        
        # Paso 4: Crear usuarios de cocina
        print("\n👨‍🍳 Paso 4: Creando usuarios de cocina...")
        if not create_kitchen_users():
            print("❌ Error en paso 4. Deteniendo proceso.")
            exit(1)
        
        print("\n✅ ¡Sistema de menú actualizado completamente!")
        print("\n📊 Resumen:")
        print(f"- Categorías: {Category.query.count()}")
        print(f"- Productos: {Product.query.count()}")
        print(f"- Usuarios de cocina: {User.query.filter_by(role='cocina').count()}")
        
        print("\n🔑 Credenciales de usuarios de cocina:")
        kitchen_users = User.query.filter_by(role='cocina').all()
        for user in kitchen_users:
            print(f"- {user.username} (Estación: {user.estacion})")