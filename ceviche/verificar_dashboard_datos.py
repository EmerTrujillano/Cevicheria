#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from models.table import Table
from models.product import Product
from models.category import Category

app = create_app()

with app.app_context():
    print("📊 VERIFICACIÓN DATOS DASHBOARD")
    print("=" * 50)
    
    # Verificar mesas
    total_mesas = Table.query.count()
    mesas_libres = Table.query.filter_by(status='libre').count()
    mesas_ocupadas = Table.query.filter_by(status='ocupada').count()
    
    print(f"🪑 MESAS:")
    print(f"   Total: {total_mesas}")
    print(f"   Libres: {mesas_libres}")
    print(f"   Ocupadas: {mesas_ocupadas}")
    
    # Verificar productos y categorías
    total_productos = Product.query.count()
    total_categorias = Category.query.count()
    
    print(f"\n🍽️ MENÚ:")
    print(f"   Categorías: {total_categorias}")
    print(f"   Productos: {total_productos}")
    
    # Mostrar categorías con productos
    print(f"\n📂 CATEGORÍAS CON PRODUCTOS:")
    categorias = Category.query.all()
    for categoria in categorias:
        productos_count = Product.query.filter_by(category_id=categoria.id).count()
        print(f"   {categoria.name}: {productos_count} productos")
    
    # Mostrar algunas mesas reorganizadas
    print(f"\n🪑 MUESTRA DE NUEVA NUMERACIÓN:")
    mesas_muestra = Table.query.order_by(Table.number).limit(15).all()
    for mesa in mesas_muestra:
        zona = mesa.zone.name if mesa.zone else "Sin zona"
        piso = mesa.floor.name if mesa.floor else "Sin piso"
        print(f"   Mesa {mesa.number} - {zona} ({piso}) - {mesa.status}")
        
    print("\n" + "=" * 50)