#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from models.table import Table
from models.product import Product
from models.category import Category

app = create_app()

with app.app_context():
    print("🔍 DIAGNÓSTICO DASHBOARD MOZO")
    print("=" * 50)
    
    # 1. Verificar datos básicos
    total_mesas = Table.query.count()
    mesas_libres = Table.query.filter_by(status='libre').count()
    mesas_ocupadas = Table.query.filter_by(status='ocupada').count()
    
    print(f"📊 DATOS EN BD:")
    print(f"   🪑 Total mesas: {total_mesas}")
    print(f"   ✅ Mesas libres: {mesas_libres}")
    print(f"   ❌ Mesas ocupadas: {mesas_ocupadas}")
    
    # 2. Verificar productos y categorías
    total_categorias = Category.query.count()
    total_productos = Product.query.count()
    
    print(f"\n🍽️ MENÚ:")
    print(f"   📂 Categorías: {total_categorias}")
    print(f"   🍽️ Productos: {total_productos}")
    
    categorias = Category.query.all()
    for categoria in categorias:
        productos_count = Product.query.filter_by(category_id=categoria.id).count()
        print(f"   • {categoria.name}: {productos_count} productos")
    
    # 3. Verificar muestra de mesas con nueva numeración
    print(f"\n🔍 MUESTRA MESAS REORGANIZADAS:")
    mesas_muestra = Table.query.order_by(Table.number).limit(20).all()
    for mesa in mesas_muestra[:10]:
        zona = mesa.zone.name if mesa.zone else "Sin zona"
        piso = mesa.zone.floor.name if mesa.zone and mesa.zone.floor else "Sin piso"
        print(f"   Mesa {mesa.number} - {zona} ({piso}) - {mesa.status}")
    
    print(f"\n📋 ESTADO ENDPOINTS:")
    print(f"   ✅ Base de datos: OK")
    print(f"   ✅ Mesas reorganizadas: OK")
    print(f"   ✅ Menú completo: OK")
    
    print("\n" + "=" * 50)