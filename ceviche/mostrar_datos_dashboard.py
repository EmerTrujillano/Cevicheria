#!/usr/bin/env python3
"""
Script directo para mostrar mesas y menú usando la base de datos
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from config.extensions import db
from models.table import Table, Zone, Floor
from models.product import Product
from models.category import Category
from models.user import User
from app import create_app

def mostrar_datos_para_dashboard():
    app = create_app()
    
    with app.app_context():
        print("=" * 80)
        print("🎯 DATOS PARA EL DASHBOARD DEL MOZO")
        print("=" * 80)
        
        # 1. Mostrar mesas disponibles
        print("\n📋 MESAS DISPONIBLES:")
        mesas = Table.query.all()
        mesas_disponibles = [mesa for mesa in mesas if mesa.status == 'available']
        mesas_ocupadas = [mesa for mesa in mesas if mesa.status != 'available']
        
        print(f"🟢 Total mesas disponibles: {len(mesas_disponibles)} de {len(mesas)}")
        print(f"🔴 Mesas ocupadas: {len(mesas_ocupadas)}")
        
        print(f"\n📍 Distribución por pisos:")
        pisos = Floor.query.all()
        for piso in pisos:
            zonas_piso = Zone.query.filter_by(floor_id=piso.id).all()
            mesas_piso_disponibles = 0
            mesas_piso_total = 0
            
            for zona in zonas_piso:
                mesas_zona = Table.query.filter_by(zone_id=zona.id).all()
                mesas_piso_total += len(mesas_zona)
                mesas_piso_disponibles += len([m for m in mesas_zona if m.status == 'available'])
            
            print(f"  • {piso.name}: {mesas_piso_disponibles}/{mesas_piso_total} disponibles")
        
        print(f"\n📋 LISTADO DE MESAS PARA SELECCIÓN:")
        print("-" * 60)
        print(f"{'Mesa':<8} {'Estado':<12} {'Zona':<20} {'Piso':<15}")
        print("-" * 60)
        
        # Ordenar mesas por número para mejor visualización
        mesas_ordenadas = sorted(mesas, key=lambda x: int(x.number) if x.number.isdigit() else 999)
        
        for mesa in mesas_ordenadas[:20]:  # Primeras 20 mesas
            estado = "🟢 Libre" if mesa.status == 'available' else "🔴 Ocupada"
            zona_nombre = mesa.zone.name if mesa.zone else "Sin zona"
            piso_nombre = mesa.zone.floor.name if mesa.zone and mesa.zone.floor else "Sin piso"
            print(f"{mesa.number:<8} {estado:<12} {zona_nombre:<20} {piso_nombre:<15}")
        
        if len(mesas) > 20:
            print(f"... y {len(mesas) - 20} mesas más")
        
        # 2. Mostrar menú completo
        print(f"\n🍽️ MENÚ COMPLETO PARA AGREGAR AL CARRITO:")
        categorias = Category.query.all()
        
        total_productos = 0
        for categoria in categorias:
            productos = Product.query.filter_by(category_id=categoria.id).all()
            total_productos += len(productos)
            
            print(f"\n📂 {categoria.name.upper()}")
            print("-" * 50)
            
            for producto in productos:
                print(f"  • {producto.name:<35} S/. {producto.price:>6.2f}")
        
        print(f"\n🎯 RESUMEN PARA EL DASHBOARD:")
        print(f"   📋 Total de mesas: {len(mesas)} ({len(mesas_disponibles)} disponibles)")
        print(f"   🍽️ Total de productos: {total_productos} en {len(categorias)} categorías")
        print(f"   📍 Distribución: {len(pisos)} pisos con múltiples zonas")
        
        # 3. Generar JSON simulado para el frontend
        print(f"\n💾 ESTRUCTURA DE DATOS SIMULADA:")
        
        # Datos de mesas
        mesas_json = []
        for mesa in mesas_ordenadas:
            mesa_data = {
                'id': mesa.id,
                'number': mesa.number,
                'status': mesa.status,
                'available': mesa.status == 'available',
                'capacity': mesa.capacity,
                'zone_name': mesa.zone.name if mesa.zone else 'Sin zona',
                'floor_name': mesa.zone.floor.name if mesa.zone and mesa.zone.floor else 'Sin piso'
            }
            mesas_json.append(mesa_data)
        
        print(f"📋 Datos de mesas (primeras 5):")
        for mesa in mesas_json[:5]:
            print(f"   Mesa {mesa['number']}: {mesa['status']} - {mesa['zone_name']}")
        
        # Datos de menú
        menu_json = {'categories': []}
        for categoria in categorias:
            productos = Product.query.filter_by(category_id=categoria.id).all()
            cat_data = {
                'id': categoria.id,
                'name': categoria.name,
                'products': []
            }
            
            for producto in productos:
                prod_data = {
                    'id': producto.id,
                    'name': producto.name,
                    'price': float(producto.price),
                    'description': producto.description or ""
                }
                cat_data['products'].append(prod_data)
            
            menu_json['categories'].append(cat_data)
        
        print(f"\n🍽️ Datos de menú por categorías:")
        for categoria in menu_json['categories']:
            print(f"   📂 {categoria['name']}: {len(categoria['products'])} productos")
        
        print("\n" + "=" * 80)
        print("✅ TODOS LOS DATOS ESTÁN LISTOS PARA EL DASHBOARD")
        print("Las mesas y el menú pueden ser cargados correctamente")
        print("=" * 80)

if __name__ == "__main__":
    mostrar_datos_para_dashboard()