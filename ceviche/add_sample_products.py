#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para agregar productos con etiquetas y ingredientes
"""

from app import create_app
from models import Product, Category
from config.extensions import db

def add_sample_products():
    """Agregar productos de ejemplo con etiquetas e ingredientes"""
    app = create_app('mysql')
    
    with app.app_context():
        # Obtener categorías existentes
        ceviche_cat = Category.query.filter_by(name='Ceviches').first()
        pollo_cat = Category.query.filter_by(name='Pollo').first()
        bebidas_cat = Category.query.filter_by(name='Bebidas').first()
        
        if not ceviche_cat:
            ceviche_cat = Category(name='Ceviches', description='Ceviches frescos', estacion='frios')
            db.session.add(ceviche_cat)
            
        if not pollo_cat:
            pollo_cat = Category(name='Pollo', description='Platos de pollo', estacion='calientes')
            db.session.add(pollo_cat)
            
        if not bebidas_cat:
            bebidas_cat = Category(name='Bebidas', description='Bebidas variadas', estacion='bebidas')
            db.session.add(bebidas_cat)
        
        db.session.commit()
        
        # Productos de ejemplo
        productos = [
            {
                'name': 'Ceviche Clásico',
                'description': 'Ceviche tradicional con pescado fresco, cebolla, ají y limón',
                'price': 25.00,
                'category_id': ceviche_cat.id,
                'ingredients': 'pescado fresco,cebolla roja,ají amarillo,limón,sal,culantro',
                'tags': 'recomendado,mas_vendido',
                'is_available': True,
                'preparation_time': 15,
                'spice_level': 'medium'
            },
            {
                'name': 'Ceviche Mixto',
                'description': 'Ceviche con pescado, pulpo, camarones y conchas',
                'price': 35.00,
                'category_id': ceviche_cat.id,
                'ingredients': 'pescado,pulpo,camarones,conchas,cebolla roja,ají amarillo,limón',
                'tags': 'especial,picante',
                'is_available': True,
                'preparation_time': 20,
                'spice_level': 'hot'
            },
            {
                'name': 'Tiradito Nikkei',
                'description': 'Tiradito con salsa de ají amarillo y leche de tigre nikkei',
                'price': 28.00,
                'category_id': ceviche_cat.id,
                'ingredients': 'pescado,ají amarillo,jengibre,sillao,aceite de ajonjolí,limón',
                'tags': 'nuevo,especial',
                'is_available': True,
                'preparation_time': 18,
                'spice_level': 'medium'
            },
            {
                'name': 'Pollo a la Brasa',
                'description': 'Pollo entero a la brasa con papas y ensalada',
                'price': 45.00,
                'category_id': pollo_cat.id,
                'ingredients': 'pollo entero,papas,lechuga,tomate,cebolla,salsa criolla',
                'tags': 'mas_vendido,recomendado',
                'is_available': True,
                'preparation_time': 35,
                'spice_level': 'mild'
            },
            {
                'name': 'Aji de Gallina',
                'description': 'Tradicional ají de gallina con arroz blanco',
                'price': 22.00,
                'category_id': pollo_cat.id,
                'ingredients': 'gallina deshilachada,ají amarillo,leche,pan,nueces,arroz',
                'tags': 'recomendado',
                'is_available': True,
                'preparation_time': 25,
                'spice_level': 'medium'
            },
            {
                'name': 'Chicha Morada',
                'description': 'Refrescante chicha morada natural',
                'price': 8.00,
                'category_id': bebidas_cat.id,
                'ingredients': 'maíz morado,piña,manzana,canela,clavo de olor',
                'tags': 'recomendado',
                'is_available': True,
                'preparation_time': 5,
                'spice_level': 'mild'
            },
            {
                'name': 'Pisco Sour',
                'description': 'El clásico pisco sour peruano',
                'price': 18.00,
                'category_id': bebidas_cat.id,
                'ingredients': 'pisco,limón,clara de huevo,jarabe de goma,amargo de angostura',
                'tags': 'especial,mas_vendido',
                'is_available': True,
                'preparation_time': 8,
                'spice_level': 'mild'
            }
        ]
        
        for producto_data in productos:
            # Verificar si ya existe
            existing = Product.query.filter_by(name=producto_data['name']).first()
            if not existing:
                producto = Product(**producto_data)
                db.session.add(producto)
                print(f"✅ Agregado: {producto_data['name']}")
            else:
                # Actualizar datos existentes
                for key, value in producto_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                print(f"🔄 Actualizado: {producto_data['name']}")
        
        db.session.commit()
        print(f"\n🎉 Productos agregados/actualizados exitosamente!")
        
        # Mostrar resumen
        total_products = Product.query.count()
        total_categories = Category.query.count()
        print(f"📊 Total productos: {total_products}")
        print(f"📊 Total categorías: {total_categories}")

if __name__ == "__main__":
    add_sample_products()