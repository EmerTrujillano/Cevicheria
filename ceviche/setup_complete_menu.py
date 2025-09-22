#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar el menú completo de la cevichería según especificaciones
"""

from app import create_app
from models import Product, Category
from config.extensions import db

def setup_complete_menu():
    """Configurar el menú completo de la cevichería"""
    app = create_app('mysql')
    
    with app.app_context():
        # Limpiar productos y categorías existentes
        print("🗑️ Limpiando productos existentes...")
        Product.query.delete()
        Category.query.delete()
        db.session.commit()
        
        # Definir las estaciones y sus platos
        menu_data = {
            "fríos": {
                "description": "Platos frescos y fríos de la casa",
                "platos": [
                    {
                        "name": "Ceviche clásico",
                        "description": "Pescado fresco marinado en limón con cebolla roja, ají amarillo y culantro",
                        "ingredients": "Pescado del día, limón, cebolla roja, ají amarillo, culantro, sal, pimienta",
                        "price": 28.00,
                        "tags": "recomendado,mas_vendido",
                        "preparation_time": 15
                    },
                    {
                        "name": "Ceviche mixto",
                        "description": "Combinación de pescado, pulpo, camarones y conchas negras en leche de tigre",
                        "ingredients": "Pescado, pulpo, camarones, conchas negras, limón, cebolla roja, ají amarillo",
                        "price": 35.00,
                        "tags": "recomendado",
                        "preparation_time": 20
                    },
                    {
                        "name": "Ceviche nikkei",
                        "description": "Fusión peruano-japonesa con pescado, leche de tigre y toques orientales",
                        "ingredients": "Pescado, limón, jengibre, ají amarillo, cebolla roja, salsa de soya, ajonjolí",
                        "price": 32.00,
                        "tags": "nuevo",
                        "preparation_time": 18
                    },
                    {
                        "name": "Tiradito al ají amarillo",
                        "description": "Finas láminas de pescado bañadas en crema de ají amarillo",
                        "ingredients": "Pescado, ají amarillo, limón, aceite de oliva, sal",
                        "price": 30.00,
                        "tags": "picante",
                        "preparation_time": 12
                    },
                    {
                        "name": "Tiradito tres ajíes",
                        "description": "Pescado en láminas con salsa de tres ajíes peruanos",
                        "ingredients": "Pescado, ají amarillo, ají panca, rocoto, limón, aceite de oliva",
                        "price": 32.00,
                        "tags": "picante",
                        "preparation_time": 15
                    },
                    {
                        "name": "Leche de tigre",
                        "description": "Concentrado puro de ceviche, energizante natural",
                        "ingredients": "Jugo de pescado, limón, ají amarillo, apio, cebolla, culantro",
                        "price": 15.00,
                        "tags": "recomendado",
                        "preparation_time": 8
                    },
                    {
                        "name": "Choritos a la chalaca",
                        "description": "Choros frescos con salsa chalaca de cebolla, tomate y ají",
                        "ingredients": "Choros, cebolla roja, tomate, ají amarillo, choclo, culantro, limón",
                        "price": 22.00,
                        "tags": "",
                        "preparation_time": 15
                    },
                    {
                        "name": "Causa limeña (pollo / pulpo / cangrejo)",
                        "description": "Papa amarilla en capas con relleno a elección, palta y mayonesa",
                        "ingredients": "Papa amarilla, palta, mayonesa, limón, ají amarillo, relleno a elección",
                        "price": 25.00,
                        "tags": "recomendado",
                        "preparation_time": 20
                    },
                    {
                        "name": "Piqueo marino (frío)",
                        "description": "Variedad de mariscos y pescados fríos para compartir",
                        "ingredients": "Ceviche, tiradito, pulpo, camarones, conchas, palta, choclo",
                        "price": 65.00,
                        "tags": "mas_vendido",
                        "preparation_time": 25
                    }
                ]
            },
            "calientes": {
                "description": "Platos calientes y reconfortantes",
                "platos": [
                    {
                        "name": "Arroz con mariscos",
                        "description": "Arroz amarillo con mariscos frescos y sofrito criollo",
                        "ingredients": "Arroz, mariscos variados, ají amarillo, culantro, ajo, cebolla, chicha de jora",
                        "price": 38.00,
                        "tags": "mas_vendido,recomendado",
                        "preparation_time": 30
                    },
                    {
                        "name": "Chaufa de mariscos",
                        "description": "Arroz frito al wok con mariscos al estilo chino-peruano",
                        "ingredients": "Arroz, mariscos, cebolla china, sillao, aceite de ajonjolí, huevo, kion",
                        "price": 35.00,
                        "tags": "recomendado",
                        "preparation_time": 25
                    },
                    {
                        "name": "Tacu tacu con mariscos",
                        "description": "Mezcla de arroz y frijoles con mariscos salteados",
                        "ingredients": "Arroz, frijoles, mariscos, ajo, cebolla, culantro, aceite",
                        "price": 32.00,
                        "tags": "",
                        "preparation_time": 20
                    },
                    {
                        "name": "Sudado de pescado",
                        "description": "Pescado cocido al vapor con cebolla, tomate y culantro",
                        "ingredients": "Pescado, cebolla, tomate, culantro, ají amarillo, chicha de jora",
                        "price": 30.00,
                        "tags": "",
                        "preparation_time": 25
                    },
                    {
                        "name": "Parihuela",
                        "description": "Sopa concentrada de mariscos con un toque de pisco",
                        "ingredients": "Mariscos variados, pescado, ají panca, tomate, cebolla, culantro, pisco",
                        "price": 40.00,
                        "tags": "recomendado,picante",
                        "preparation_time": 35
                    },
                    {
                        "name": "Pescado a lo macho",
                        "description": "Pescado frito bañado en salsa de mariscos picante",
                        "ingredients": "Pescado, pulpo, camarones, ají amarillo, ají panca, cebolla, tomate",
                        "price": 42.00,
                        "tags": "picante,mas_vendido",
                        "preparation_time": 30
                    },
                    {
                        "name": "Ají de gallina",
                        "description": "Pollo deshilachado en crema de ají amarillo con nueces",
                        "ingredients": "Pollo, ají amarillo, leche, pan, nueces, queso parmesano, papa",
                        "price": 28.00,
                        "tags": "",
                        "preparation_time": 25
                    },
                    {
                        "name": "Piqueo marino (caliente)",
                        "description": "Variedad de mariscos calientes, perfecto para compartir",
                        "ingredients": "Jalea, chicharrón de calamar, pescado a la plancha, yuca frita",
                        "price": 70.00,
                        "tags": "mas_vendido",
                        "preparation_time": 35
                    }
                ]
            },
            "frituras": {
                "description": "Platos fritos crujientes y dorados",
                "platos": [
                    {
                        "name": "Jalea mixta",
                        "description": "Mariscos y pescados fritos acompañados de yuca y salsa criolla",
                        "ingredients": "Pescado, calamares, camarones, pulpo, yuca, cebolla roja, ají amarillo",
                        "price": 45.00,
                        "tags": "mas_vendido,recomendado",
                        "preparation_time": 25
                    },
                    {
                        "name": "Chicharrón de calamar",
                        "description": "Anillos de calamar fritos hasta quedar dorados y crujientes",
                        "ingredients": "Calamar, harina, huevo, aceite, sal, pimienta, limón",
                        "price": 32.00,
                        "tags": "recomendado",
                        "preparation_time": 20
                    },
                    {
                        "name": "Pulpo a la parrilla",
                        "description": "Tentáculos de pulpo a la parrilla con papas nativas",
                        "ingredients": "Pulpo, papas nativas, aceite de oliva, ajo, perejil, limón",
                        "price": 38.00,
                        "tags": "",
                        "preparation_time": 30
                    },
                    {
                        "name": "Lomo saltado",
                        "description": "Clásico peruano de lomo saltado con papas fritas y arroz",
                        "ingredients": "Lomo de res, cebolla, tomate, ají amarillo, papas, arroz, sillao",
                        "price": 35.00,
                        "tags": "mas_vendido",
                        "preparation_time": 20
                    }
                ]
            },
            "bebidas": {
                "description": "Bebidas refrescantes y tradicionales",
                "platos": [
                    {
                        "name": "Chicha morada",
                        "description": "Bebida tradicional de maíz morado con frutas y especias",
                        "ingredients": "Maíz morado, piña, manzana, canela, clavo de olor, azúcar, limón",
                        "price": 8.00,
                        "tags": "recomendado",
                        "preparation_time": 5
                    },
                    {
                        "name": "Chicha de jora",
                        "description": "Bebida ancestral fermentada de maíz amarillo",
                        "ingredients": "Maíz de jora fermentado, azúcar, especias",
                        "price": 12.00,
                        "tags": "",
                        "preparation_time": 5
                    },
                    {
                        "name": "Inca Kola",
                        "description": "La bebida dorada del Perú",
                        "ingredients": "Gaseosa Inca Kola",
                        "price": 6.00,
                        "tags": "",
                        "preparation_time": 2
                    },
                    {
                        "name": "Jugo de maracuyá",
                        "description": "Jugo natural de maracuyá fresco",
                        "ingredients": "Maracuyá, agua, azúcar, hielo",
                        "price": 10.00,
                        "tags": "recomendado",
                        "preparation_time": 5
                    },
                    {
                        "name": "Limonada",
                        "description": "Limonada fresca con hierbas",
                        "ingredients": "Limón, agua, azúcar, hielo, hierba buena",
                        "price": 8.00,
                        "tags": "",
                        "preparation_time": 5
                    },
                    {
                        "name": "Agua sin/con gas",
                        "description": "Agua mineral natural o con gas",
                        "ingredients": "Agua mineral",
                        "price": 4.00,
                        "tags": "",
                        "preparation_time": 1
                    },
                    {
                        "name": "Pisco Sour",
                        "description": "Cóctel nacional peruano con pisco, limón y clara de huevo",
                        "ingredients": "Pisco, limón, jarabe de goma, clara de huevo, amargo de angostura",
                        "price": 18.00,
                        "tags": "recomendado,mas_vendido",
                        "preparation_time": 8
                    },
                    {
                        "name": "Chilcano (clásico, maracuyá, jengibre)",
                        "description": "Cóctel refrescante de pisco con ginger ale y limón",
                        "ingredients": "Pisco, ginger ale, limón, hielo, variante a elección",
                        "price": 16.00,
                        "tags": "recomendado",
                        "preparation_time": 5
                    },
                    {
                        "name": "Sangría",
                        "description": "Bebida refrescante con vino tinto y frutas",
                        "ingredients": "Vino tinto, frutas de estación, brandy, azúcar, gaseosa",
                        "price": 20.00,
                        "tags": "",
                        "preparation_time": 10
                    },
                    {
                        "name": "Cerveza (Pilsen, Cusqueña, artesanal)",
                        "description": "Variedades de cerveza nacional y artesanal",
                        "ingredients": "Cerveza a elección",
                        "price": 12.00,
                        "tags": "",
                        "preparation_time": 2
                    }
                ]
            },
            "postres": {
                "description": "Dulces tradicionales peruanos",
                "platos": [
                    {
                        "name": "Suspiro limeño",
                        "description": "Postre cremoso de manjar blanco con merengue de port",
                        "ingredients": "Leche condensada, leche evaporada, yemas, port, claras, azúcar",
                        "price": 15.00,
                        "tags": "recomendado,mas_vendido",
                        "preparation_time": 10
                    },
                    {
                        "name": "Mazamorra morada",
                        "description": "Postre tradicional de maíz morado con frutas",
                        "ingredients": "Maíz morado, frutas, chuño, canela, clavo, azúcar",
                        "price": 12.00,
                        "tags": "",
                        "preparation_time": 8
                    },
                    {
                        "name": "Arroz con leche",
                        "description": "Cremoso arroz con leche, canela y pasas",
                        "ingredients": "Arroz, leche, azúcar, canela, pasas, clavo de olor",
                        "price": 10.00,
                        "tags": "",
                        "preparation_time": 5
                    },
                    {
                        "name": "Tres leches",
                        "description": "Torta esponjosa bañada en tres tipos de leche",
                        "ingredients": "Bizcocho, leche condensada, leche evaporada, crema de leche",
                        "price": 18.00,
                        "tags": "mas_vendido",
                        "preparation_time": 8
                    },
                    {
                        "name": "Helado de maracuyá o chirimoya",
                        "description": "Helado artesanal de frutas peruanas",
                        "ingredients": "Pulpa de fruta, leche, azúcar, crema",
                        "price": 14.00,
                        "tags": "recomendado",
                        "preparation_time": 3
                    }
                ]
            },
            "acompañamientos": {
                "description": "Guarniciones y acompañamientos perfectos",
                "platos": [
                    {
                        "name": "Camote glaseado",
                        "description": "Camote dulce glaseado con miel y especias",
                        "ingredients": "Camote, miel, mantequilla, canela",
                        "price": 8.00,
                        "tags": "",
                        "preparation_time": 15
                    },
                    {
                        "name": "Choclo con queso",
                        "description": "Mazorca de maíz gigante con queso fresco",
                        "ingredients": "Choclo, queso fresco, sal",
                        "price": 10.00,
                        "tags": "recomendado",
                        "preparation_time": 12
                    },
                    {
                        "name": "Papa o yuca frita",
                        "description": "Papas o yuca doradas y crujientes",
                        "ingredients": "Papa o yuca, aceite, sal",
                        "price": 8.00,
                        "tags": "",
                        "preparation_time": 15
                    },
                    {
                        "name": "Ensalada criolla",
                        "description": "Ensalada fresca de cebolla roja con limón y ají",
                        "ingredients": "Cebolla roja, ají amarillo, limón, culantro, sal",
                        "price": 6.00,
                        "tags": "",
                        "preparation_time": 8
                    },
                    {
                        "name": "Pan al ajo",
                        "description": "Pan tostado con mantequilla de ajo y perejil",
                        "ingredients": "Pan, mantequilla, ajo, perejil, sal",
                        "price": 8.00,
                        "tags": "",
                        "preparation_time": 10
                    }
                ]
            }
        }
        
        # Crear categorías y productos
        print("🍽️ Creando menú completo...")
        
        for estacion, data in menu_data.items():
            # Crear categoría
            category = Category(
                name=estacion.capitalize(),
                description=data["description"],
                estacion=estacion
            )
            db.session.add(category)
            db.session.flush()  # Para obtener el ID
            
            print(f"📂 Estación: {estacion} ({len(data['platos'])} platos)")
            
            # Crear productos de la estación
            for plato_data in data["platos"]:
                product = Product(
                    name=plato_data["name"],
                    description=plato_data["description"],
                    price=plato_data["price"],
                    category_id=category.id,
                    ingredients=plato_data["ingredients"],
                    tags=plato_data["tags"],
                    is_available=True,
                    preparation_time=plato_data["preparation_time"],
                    spice_level='mild' if 'picante' not in plato_data["tags"] else 'hot'
                )
                db.session.add(product)
        
        # Confirmar cambios
        db.session.commit()
        
        # Mostrar resumen
        print("\n✅ Menú creado exitosamente!")
        print(f"📊 Total de categorías: {Category.query.count()}")
        print(f"🍽️ Total de productos: {Product.query.count()}")
        
        print("\n📋 Resumen por estación:")
        for category in Category.query.all():
            count = Product.query.filter_by(category_id=category.id).count()
            print(f"  {category.name}: {count} platos")

if __name__ == "__main__":
    setup_complete_menu()