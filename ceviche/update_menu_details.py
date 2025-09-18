#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar productos con etiquetas visuales e ingredientes
"""

from config.extensions import db
from models.product import Product
from models.category import Category

def update_products_with_details():
    """Actualizar productos con etiquetas e ingredientes"""
    try:
        # Mapeo de productos con sus etiquetas e ingredientes
        productos_details = {
            # PLATOS FRÍOS
            "Ceviche de Pescado": {
                "tags": "⭐ 🏆",
                "ingredients": "Pescado fresco, limón, cebolla roja, ají limo, culantro, camote, choclo"
            },
            "Ceviche Mixto": {
                "tags": "⭐ 🌶️",
                "ingredients": "Pescado, camarones, pulpo, calamar, limón, cebolla, ají amarillo"
            },
            "Ceviche de Conchas Negras": {
                "tags": "🏆 🆕",
                "ingredients": "Conchas negras frescas, limón, cebolla, culantro, ají limo"
            },
            "Tiradito de Pescado": {
                "tags": "⭐",
                "ingredients": "Pescado fresco, ají amarillo, limón, aceite de oliva, sal de maras"
            },
            "Tiradito Nikkei": {
                "tags": "🆕 🌶️",
                "ingredients": "Pescado, salsa de soya, jengibre, ají amarillo, ajonjolí"
            },
            "Leche de Tigre": {
                "tags": "🌶️ 🏆",
                "ingredients": "Jugo de ceviche concentrado, mariscos, culantro, ají, limón"
            },
            "Causa Limeña": {
                "tags": "⭐",
                "ingredients": "Papa amarilla, pollo deshilachado, palta, mayonesa, ají amarillo"
            },
            "Causa de Mariscos": {
                "tags": "🏆",
                "ingredients": "Papa amarilla, mariscos frescos, palta, mayonesa, limón"
            },
            "Choros a la Chalaca": {
                "tags": "⭐ 🌶️",
                "ingredients": "Mejillones frescos, cebolla, tomate, ají amarillo, limón, culantro"
            },
            "Pulpo al Olivo": {
                "tags": "🏆 🆕",
                "ingredients": "Pulpo tierno, aceitunas negras, mayonesa, huevo duro, papa"
            },

            # PLATOS CALIENTES
            "Arroz con Mariscos": {
                "tags": "⭐ 🏆",
                "ingredients": "Arroz, mariscos variados, pisco, culantro, ají amarillo"
            },
            "Arroz con Pollo": {
                "tags": "⭐",
                "ingredients": "Arroz, pollo, culantro, arvejas, zanahoria, pimiento"
            },
            "Paella Peruana": {
                "tags": "🏆 🆕",
                "ingredients": "Arroz, mariscos, pollo, pimiento, arvejas, azafrán"
            },
            "Sudado de Pescado": {
                "tags": "⭐",
                "ingredients": "Pescado fresco, cebolla, tomate, culantro, ají amarillo, chicha de jora"
            },
            "Sudado de Mariscos": {
                "tags": "🏆 🌶️",
                "ingredients": "Mariscos frescos, cebolla, tomate, culantro, ají panca"
            },
            "Parihuela": {
                "tags": "🌶️ 🏆",
                "ingredients": "Pescado, mariscos, ají panca, culantro, cebolla, tomate"
            },
            "Chupe de Camarones": {
                "tags": "⭐ 🏆",
                "ingredients": "Camarones, leche, huevo, queso fresco, arroz, habas"
            },
            "Aguadito de Mariscos": {
                "tags": "⭐",
                "ingredients": "Arroz, mariscos, culantro, arvejas, zanahoria, ají amarillo"
            },
            "Pescado a la Plancha": {
                "tags": "",
                "ingredients": "Pescado fresco, ensalada mixta, papas doradas, limón"
            },
            "Saltado de Mariscos": {
                "tags": "🌶️",
                "ingredients": "Mariscos, cebolla, tomate, papas fritas, sillao, ají amarillo"
            },
            "Tacu Tacu con Mariscos": {
                "tags": "🏆",
                "ingredients": "Arroz, frejoles, mariscos, ají amarillo, culantro"
            },
            "Picante de Mariscos": {
                "tags": "🌶️ 🌶️",
                "ingredients": "Mariscos, ají amarillo, cebolla, ajo, papa, huacatay"
            },

            # FRITURAS
            "Chicharrón de Pescado": {
                "tags": "⭐ 🏆",
                "ingredients": "Pescado fresco, yuca, camote, salsa criolla, limón"
            },
            "Chicharrón de Pollo": {
                "tags": "⭐",
                "ingredients": "Pollo tierno, camote, salsa huancaína, limón"
            },
            "Chicharrón Mixto": {
                "tags": "🏆",
                "ingredients": "Pescado, pollo, yuca, camote, salsas variadas"
            },
            "Jalea de Mariscos": {
                "tags": "⭐ 🏆",
                "ingredients": "Mariscos variados, pescado, yuca, salsa criolla, limón"
            },
            "Jalea Personal": {
                "tags": "",
                "ingredients": "Porción individual de mariscos fritos, yuca, limón"
            },
            "Pescado Frito": {
                "tags": "⭐",
                "ingredients": "Pescado entero, arroz, frejoles, ensalada, limón"
            },
            "Calamares Fritos": {
                "tags": "",
                "ingredients": "Anillos de calamar, harina, salsa tártara, limón"
            },
            "Tequeños de Mariscos": {
                "tags": "🆕",
                "ingredients": "Masa wantán, mariscos, queso, aceite, salsa golf"
            },
            "Yuquitas Fritas": {
                "tags": "",
                "ingredients": "Yuca dorada, salsa huancaína, queso fresco"
            },

            # BEBIDAS
            "Chicha Morada": {
                "tags": "⭐ 🏆",
                "ingredients": "Maíz morado, piña, manzana, canela, clavo de olor"
            },
            "Limonada": {
                "tags": "⭐",
                "ingredients": "Limón fresco, agua, azúcar, hielo"
            },
            "Limonada Frozen": {
                "tags": "🆕",
                "ingredients": "Limón, hielo frappe, azúcar, agua helada"
            },
            "Maracuyá": {
                "tags": "",
                "ingredients": "Pulpa de maracuyá, agua, azúcar, hielo"
            },
            "Papaya": {
                "tags": "",
                "ingredients": "Papaya fresca, agua, azúcar, hielo"
            },
            "Piña": {
                "tags": "",
                "ingredients": "Piña natural, agua, azúcar, hielo"
            },
            "Naranja": {
                "tags": "⭐",
                "ingredients": "Naranjas frescas recién exprimidas"
            },
            "Inca Kola": {
                "tags": "🏆",
                "ingredients": "Gaseosa nacional peruana"
            },
            "Coca Cola": {
                "tags": "",
                "ingredients": "Gaseosa clásica"
            },
            "Agua": {
                "tags": "",
                "ingredients": "Agua mineral pura"
            },
            "Agua con Gas": {
                "tags": "",
                "ingredients": "Agua mineral gasificada"
            },
            "Pisco Sour": {
                "tags": "⭐ 🏆",
                "ingredients": "Pisco, limón, jarabe de goma, clara de huevo, amargo de angostura"
            },
            "Chilcano": {
                "tags": "⭐",
                "ingredients": "Pisco, ginger ale, limón, hielo, angostura"
            },
            "Cerveza": {
                "tags": "",
                "ingredients": "Cerveza nacional fría"
            },

            # POSTRES
            "Suspiro Limeño": {
                "tags": "⭐ 🏆",
                "ingredients": "Manjar blanco, merengue, canela, oporto"
            },
            "Tres Leches": {
                "tags": "⭐",
                "ingredients": "Bizcocho, leche evaporada, leche condensada, crema de leche"
            },
            "Mazamorra Morada": {
                "tags": "🏆",
                "ingredients": "Maíz morado, piña, membrillo, canela, clavo"
            },
            "Arroz con Leche": {
                "tags": "⭐",
                "ingredients": "Arroz, leche, canela, pasas, leche condensada"
            },
            "Picarones": {
                "tags": "🏆",
                "ingredients": "Zapallo, camote, harina, miel de chancaca"
            },
            "Helado de Lúcuma": {
                "tags": "🆕",
                "ingredients": "Pulpa de lúcuma, leche, crema, azúcar"
            },
            "Helado de Chirimoya": {
                "tags": "🆕",
                "ingredients": "Pulpa de chirimoya, leche, crema, azúcar"
            },
            "Flan de Vainilla": {
                "tags": "",
                "ingredients": "Huevos, leche, azúcar, esencia de vainilla"
            },

            # ACOMPAÑAMIENTOS
            "Arroz Blanco": {
                "tags": "",
                "ingredients": "Arroz grano largo, sal, aceite"
            },
            "Frejoles": {
                "tags": "⭐",
                "ingredients": "Frejoles canarios, ajo, cebolla, comino"
            },
            "Yuca Sancochada": {
                "tags": "",
                "ingredients": "Yuca fresca, sal"
            },
            "Camote Sancochado": {
                "tags": "",
                "ingredients": "Camote dulce, sal"
            },
            "Platanos Maduros": {
                "tags": "",
                "ingredients": "Plátanos maduros, aceite, azúcar"
            },
            "Ensalada Mixta": {
                "tags": "",
                "ingredients": "Lechuga, tomate, cebolla, aceitunas, aceite, vinagre"
            },
            "Palta": {
                "tags": "⭐",
                "ingredients": "Palta fresca en rodajas"
            },
            "Salsa Criolla": {
                "tags": "🌶️",
                "ingredients": "Cebolla roja, ají amarillo, limón, sal"
            },
            "Salsa Huancaína": {
                "tags": "🌶️ ⭐",
                "ingredients": "Ají amarillo, queso fresco, leche, galletas"
            },
            "Salsa Ocopa": {
                "tags": "🌶️",
                "ingredients": "Huacatay, queso fresco, ají amarillo, galletas"
            },
            "Cancha Serrana": {
                "tags": "",
                "ingredients": "Maíz gigante del Cusco, sal"
            }
        }

        updated_count = 0
        
        for product_name, details in productos_details.items():
            product = Product.query.filter_by(name=product_name).first()
            if product:
                # Crear nueva descripción con etiquetas e ingredientes
                tags = details["tags"]
                ingredients = details["ingredients"]
                
                # Mantener la descripción original y añadir etiquetas e ingredientes
                new_description = product.description
                
                if tags:
                    new_description += f"\n\n{tags}"
                
                new_description += f"\n\n🥘 Ingredientes: {ingredients}"
                
                product.description = new_description
                updated_count += 1
                print(f"✅ {product_name} actualizado")
        
        db.session.commit()
        print(f"\n✅ {updated_count} productos actualizados con etiquetas e ingredientes")
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando productos: {e}")
        db.session.rollback()
        return False

if __name__ == '__main__':
    from app import create_app
    
    app = create_app('mysql')
    with app.app_context():
        print("🎨 Actualizando productos con etiquetas visuales e ingredientes...")
        
        if update_products_with_details():
            print("\n📊 Resumen de etiquetas:")
            print("⭐ Recomendado")
            print("🌶️ Picante") 
            print("🏆 Más vendido")
            print("🆕 Nuevo")
            print("🥘 Ingredientes incluidos")
        else:
            print("❌ Error en la actualización")