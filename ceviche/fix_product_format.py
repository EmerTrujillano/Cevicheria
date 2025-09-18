#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir el formato de productos: separar ingredientes de etiquetas
"""

from config.extensions import db
from models.product import Product
from models.category import Category

def fix_product_format():
    """Corregir formato de productos separando ingredientes y etiquetas"""
    try:
        # Mapeo de productos con formato correcto
        productos_details = {
            # PLATOS FRÍOS
            "Ceviche de Pescado": {
                "description": "Pescado fresco marinado en limón con cebolla, ají limo, culantro y camote",
                "ingredients": "Pescado fresco, limón, cebolla roja, ají limo, culantro, camote, choclo",
                "tags": "⭐ Recomendado, 🏆 Más vendido"
            },
            "Ceviche Mixto": {
                "description": "Pescado y mariscos frescos marinados con limón, cebolla y ají amarillo",
                "ingredients": "Pescado, camarones, pulpo, calamar, limón, cebolla, ají amarillo",
                "tags": "⭐ Recomendado, 🌶️ Picante"
            },
            "Ceviche de Conchas Negras": {
                "description": "Conchas negras frescas marinadas en su jugo con limón y especias",
                "ingredients": "Conchas negras frescas, limón, cebolla, culantro, ají limo",
                "tags": "🏆 Más vendido, 🆕 Nuevo"
            },
            "Tiradito de Pescado": {
                "description": "Finas láminas de pescado bañadas en crema de ají amarillo",
                "ingredients": "Pescado fresco, ají amarillo, limón, aceite de oliva, sal de maras",
                "tags": "⭐ Recomendado"
            },
            "Tiradito Nikkei": {
                "description": "Pescado fresco con salsa de soya, jengibre y ají amarillo",
                "ingredients": "Pescado, salsa de soya, jengibre, ají amarillo, ajonjolí",
                "tags": "🆕 Nuevo, 🌶️ Picante"
            },
            "Leche de Tigre": {
                "description": "Concentrado de ceviche con mariscos, culantro y especias",
                "ingredients": "Jugo de ceviche concentrado, mariscos, culantro, ají, limón",
                "tags": "🌶️ Picante, 🏆 Más vendido"
            },
            "Causa Limeña": {
                "description": "Capas de papa amarilla rellena con pollo, palta y mayonesa",
                "ingredients": "Papa amarilla, pollo deshilachado, palta, mayonesa, ají amarillo",
                "tags": "⭐ Recomendado"
            },
            "Causa de Mariscos": {
                "description": "Papa amarilla con mariscos frescos y palta",
                "ingredients": "Papa amarilla, mariscos frescos, palta, mayonesa, limón",
                "tags": "🏆 Más vendido"
            },
            "Choros a la Chalaca": {
                "description": "Mejillones frescos con salsa chalaca de cebolla, tomate y limón",
                "ingredients": "Mejillones frescos, cebolla, tomate, ají amarillo, limón, culantro",
                "tags": "⭐ Recomendado, 🌶️ Picante"
            },
            "Pulpo al Olivo": {
                "description": "Pulpo tierno bañado en crema de aceitunas negras",
                "ingredients": "Pulpo tierno, aceitunas negras, mayonesa, huevo duro, papa",
                "tags": "🏆 Más vendido, 🆕 Nuevo"
            },

            # PLATOS CALIENTES
            "Arroz con Mariscos": {
                "description": "Arroz amarillo con mariscos frescos y culantro",
                "ingredients": "Arroz, mariscos variados, pisco, culantro, ají amarillo",
                "tags": "⭐ Recomendado, 🏆 Más vendido"
            },
            "Arroz con Pollo": {
                "description": "Arroz cilantrado con pollo tierno y verduras",
                "ingredients": "Arroz, pollo, culantro, arvejas, zanahoria, pimiento",
                "tags": "⭐ Recomendado"
            },
            "Paella Peruana": {
                "description": "Arroz con mariscos, pollo y verduras al estilo peruano",
                "ingredients": "Arroz, mariscos, pollo, pimiento, arvejas, azafrán",
                "tags": "🏆 Más vendido, 🆕 Nuevo"
            },
            "Sudado de Pescado": {
                "description": "Pescado cocido al vapor con cebolla, tomate y culantro",
                "ingredients": "Pescado fresco, cebolla, tomate, culantro, ají amarillo, chicha de jora",
                "tags": "⭐ Recomendado"
            },
            "Sudado de Mariscos": {
                "description": "Mariscos frescos sudados con verduras y especias",
                "ingredients": "Mariscos frescos, cebolla, tomate, culantro, ají panca",
                "tags": "🏆 Más vendido, 🌶️ Picante"
            },
            "Parihuela": {
                "description": "Sopa concentrada de mariscos con pescado y ají panca",
                "ingredients": "Pescado, mariscos, ají panca, culantro, cebolla, tomate",
                "tags": "🌶️ Picante, 🏆 Más vendido"
            },
            "Chupe de Camarones": {
                "description": "Sopa cremosa de camarones con huevo, leche y queso",
                "ingredients": "Camarones, leche, huevo, queso fresco, arroz, habas",
                "tags": "⭐ Recomendado, 🏆 Más vendido"
            },
            "Aguadito de Mariscos": {
                "description": "Arroz aguado con mariscos, culantro y ají amarillo",
                "ingredients": "Arroz, mariscos, culantro, arvejas, zanahoria, ají amarillo",
                "tags": "⭐ Recomendado"
            },
            "Pescado a la Plancha": {
                "description": "Filete de pescado grillado con ensalada y papas",
                "ingredients": "Pescado fresco, ensalada mixta, papas doradas, limón",
                "tags": ""
            },
            "Saltado de Mariscos": {
                "description": "Mariscos salteados con cebolla, tomate y papas fritas",
                "ingredients": "Mariscos, cebolla, tomate, papas fritas, sillao, ají amarillo",
                "tags": "🌶️ Picante"
            },
            "Tacu Tacu con Mariscos": {
                "description": "Arroz con frejoles refritos coronado con mariscos",
                "ingredients": "Arroz, frejoles, mariscos, ají amarillo, culantro",
                "tags": "🏆 Más vendido"
            },
            "Picante de Mariscos": {
                "description": "Mariscos en salsa picante de ají amarillo",
                "ingredients": "Mariscos, ají amarillo, cebolla, ajo, papa, huacatay",
                "tags": "🌶️🌶️ Muy picante"
            },

            # FRITURAS
            "Chicharrón de Pescado": {
                "description": "Trozos de pescado fritos acompañados de yuca y salsa criolla",
                "ingredients": "Pescado fresco, yuca, camote, salsa criolla, limón",
                "tags": "⭐ Recomendado, 🏆 Más vendido"
            },
            "Chicharrón de Pollo": {
                "description": "Pollo frito crujiente con camote y salsa huancaína",
                "ingredients": "Pollo tierno, camote, salsa huancaína, limón",
                "tags": "⭐ Recomendado"
            },
            "Chicharrón Mixto": {
                "description": "Pescado y pollo frito con yuca y camote",
                "ingredients": "Pescado, pollo, yuca, camote, salsas variadas",
                "tags": "🏆 Más vendido"
            },
            "Jalea de Mariscos": {
                "description": "Mariscos y pescado fritos con yuca y salsa criolla",
                "ingredients": "Mariscos variados, pescado, yuca, salsa criolla, limón",
                "tags": "⭐ Recomendado, 🏆 Más vendido"
            },
            "Jalea Personal": {
                "description": "Porción individual de mariscos fritos",
                "ingredients": "Porción individual de mariscos fritos, yuca, limón",
                "tags": ""
            },
            "Pescado Frito": {
                "description": "Pescado entero frito con arroz y frejoles",
                "ingredients": "Pescado entero, arroz, frejoles, ensalada, limón",
                "tags": "⭐ Recomendado"
            },
            "Calamares Fritos": {
                "description": "Anillos de calamar empanizados con salsa tártara",
                "ingredients": "Anillos de calamar, harina, salsa tártara, limón",
                "tags": ""
            },
            "Tequeños de Mariscos": {
                "description": "Rollitos fritos rellenos de mariscos",
                "ingredients": "Masa wantán, mariscos, queso, aceite, salsa golf",
                "tags": "🆕 Nuevo"
            },
            "Yuquitas Fritas": {
                "description": "Yuca frita dorada acompañada de huancaína",
                "ingredients": "Yuca dorada, salsa huancaína, queso fresco",
                "tags": ""
            },

            # BEBIDAS
            "Chicha Morada": {
                "description": "Bebida tradicional de maíz morado con frutas",
                "ingredients": "Maíz morado, piña, manzana, canela, clavo de olor",
                "tags": "⭐ Recomendado, 🏆 Más vendido"
            },
            "Limonada": {
                "description": "Limonada fresca natural",
                "ingredients": "Limón fresco, agua, azúcar, hielo",
                "tags": "⭐ Recomendado"
            },
            "Limonada Frozen": {
                "description": "Limonada helada con hielo frappe",
                "ingredients": "Limón, hielo frappe, azúcar, agua helada",
                "tags": "🆕 Nuevo"
            },
            "Maracuyá": {
                "description": "Jugo de maracuyá natural",
                "ingredients": "Pulpa de maracuyá, agua, azúcar, hielo",
                "tags": ""
            },
            "Papaya": {
                "description": "Jugo de papaya fresco",
                "ingredients": "Papaya fresca, agua, azúcar, hielo",
                "tags": ""
            },
            "Piña": {
                "description": "Jugo de piña natural",
                "ingredients": "Piña natural, agua, azúcar, hielo",
                "tags": ""
            },
            "Naranja": {
                "description": "Jugo de naranja recién exprimido",
                "ingredients": "Naranjas frescas recién exprimidas",
                "tags": "⭐ Recomendado"
            },
            "Inca Kola": {
                "description": "Gaseosa nacional peruana",
                "ingredients": "Gaseosa nacional peruana",
                "tags": "🏆 Más vendido"
            },
            "Coca Cola": {
                "description": "Gaseosa clásica",
                "ingredients": "Gaseosa clásica",
                "tags": ""
            },
            "Agua": {
                "description": "Agua mineral sin gas",
                "ingredients": "Agua mineral pura",
                "tags": ""
            },
            "Agua con Gas": {
                "description": "Agua mineral con gas",
                "ingredients": "Agua mineral gasificada",
                "tags": ""
            },
            "Pisco Sour": {
                "description": "Cóctel peruano con pisco, limón y clara de huevo",
                "ingredients": "Pisco, limón, jarabe de goma, clara de huevo, amargo de angostura",
                "tags": "⭐ Recomendado, 🏆 Más vendido"
            },
            "Chilcano": {
                "description": "Pisco con ginger ale y limón",
                "ingredients": "Pisco, ginger ale, limón, hielo, angostura",
                "tags": "⭐ Recomendado"
            },
            "Cerveza": {
                "description": "Cerveza nacional fría",
                "ingredients": "Cerveza nacional fría",
                "tags": ""
            },

            # POSTRES
            "Suspiro Limeño": {
                "description": "Dulce de leche con merengue y canela",
                "ingredients": "Manjar blanco, merengue, canela, oporto",
                "tags": "⭐ Recomendado, 🏆 Más vendido"
            },
            "Tres Leches": {
                "description": "Bizcocho empapado en tres tipos de leche",
                "ingredients": "Bizcocho, leche evaporada, leche condensada, crema de leche",
                "tags": "⭐ Recomendado"
            },
            "Mazamorra Morada": {
                "description": "Postre tradicional de maíz morado con frutas",
                "ingredients": "Maíz morado, piña, membrillo, canela, clavo",
                "tags": "🏆 Más vendido"
            },
            "Arroz con Leche": {
                "description": "Arroz dulce con leche, canela y pasas",
                "ingredients": "Arroz, leche, canela, pasas, leche condensada",
                "tags": "⭐ Recomendado"
            },
            "Picarones": {
                "description": "Buñuelos de zapallo con miel de chancaca",
                "ingredients": "Zapallo, camote, harina, miel de chancaca",
                "tags": "🏆 Más vendido"
            },
            "Helado de Lúcuma": {
                "description": "Helado artesanal de fruta peruana",
                "ingredients": "Pulpa de lúcuma, leche, crema, azúcar",
                "tags": "🆕 Nuevo"
            },
            "Helado de Chirimoya": {
                "description": "Helado cremoso de chirimoya",
                "ingredients": "Pulpa de chirimoya, leche, crema, azúcar",
                "tags": "🆕 Nuevo"
            },
            "Flan de Vainilla": {
                "description": "Flan casero con caramelo",
                "ingredients": "Huevos, leche, azúcar, esencia de vainilla",
                "tags": ""
            },

            # ACOMPAÑAMIENTOS
            "Arroz Blanco": {
                "description": "Arroz blanco graneado",
                "ingredients": "Arroz grano largo, sal, aceite",
                "tags": ""
            },
            "Frejoles": {
                "description": "Frejoles canarios guisados",
                "ingredients": "Frejoles canarios, ajo, cebolla, comino",
                "tags": "⭐ Recomendado"
            },
            "Yuca Sancochada": {
                "description": "Yuca hervida tierna",
                "ingredients": "Yuca fresca, sal",
                "tags": ""
            },
            "Camote Sancochado": {
                "description": "Camote dulce hervido",
                "ingredients": "Camote dulce, sal",
                "tags": ""
            },
            "Platanos Maduros": {
                "description": "Plátanos dulces fritos",
                "ingredients": "Plátanos maduros, aceite, azúcar",
                "tags": ""
            },
            "Ensalada Mixta": {
                "description": "Lechuga, tomate, cebolla y aceitunas",
                "ingredients": "Lechuga, tomate, cebolla, aceitunas, aceite, vinagre",
                "tags": ""
            },
            "Palta": {
                "description": "Palta fresca en rodajas",
                "ingredients": "Palta fresca en rodajas",
                "tags": "⭐ Recomendado"
            },
            "Salsa Criolla": {
                "description": "Cebolla, ají y limón",
                "ingredients": "Cebolla roja, ají amarillo, limón, sal",
                "tags": "🌶️ Picante"
            },
            "Salsa Huancaína": {
                "description": "Crema de ají amarillo",
                "ingredients": "Ají amarillo, queso fresco, leche, galletas",
                "tags": "🌶️ Picante, ⭐ Recomendado"
            },
            "Salsa Ocopa": {
                "description": "Crema de huacatay",
                "ingredients": "Huacatay, queso fresco, ají amarillo, galletas",
                "tags": "🌶️ Picante"
            },
            "Cancha Serrana": {
                "description": "Maíz tostado salado",
                "ingredients": "Maíz gigante del Cusco, sal",
                "tags": ""
            }
        }

        updated_count = 0
        
        for product_name, details in productos_details.items():
            product = Product.query.filter_by(name=product_name).first()
            if product:
                # Crear descripción con formato correcto
                description = details["description"]
                ingredients = details["ingredients"]
                tags = details["tags"]
                
                # Formato: Descripción + salto de línea + Ingredientes + salto de línea + Etiquetas
                new_description = description
                new_description += f"\nIngredientes: {ingredients}"
                
                if tags:
                    new_description += f"\n{tags}"
                
                product.description = new_description
                updated_count += 1
                print(f"✅ {product_name} actualizado con formato correcto")
        
        db.session.commit()
        print(f"\n✅ {updated_count} productos actualizados con formato corregido")
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando formato: {e}")
        db.session.rollback()
        return False

if __name__ == '__main__':
    from app import create_app
    
    app = create_app('mysql')
    with app.app_context():
        print("🎨 Corrigiendo formato de productos...")
        
        if fix_product_format():
            print("\n📋 Nuevo formato:")
            print("Nombre del Producto")
            print("Descripción del producto")
            print("Ingredientes: lista de ingredientes")
            print("⭐ Etiquetas con colores")
        else:
            print("❌ Error en la corrección")