#!/usr/bin/env python3
"""
Script para verificar que todos los datos estén correctamente en la base de datos
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from config.extensions import db
from models.table import Table, Zone, Floor
from models.product import Product
from models.category import Category
from models.user import User
from models.permission import TemporaryPermission
from app import create_app

def verificar_datos():
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("🔍 VERIFICANDO DATOS EN LA BASE DE DATOS")
        print("=" * 60)
        
        # 1. Verificar mesas
        print("\n📋 VERIFICANDO MESAS:")
        mesas = Table.query.all()
        print(f"Total de mesas encontradas: {len(mesas)}")
        
        # Contar por piso
        pisos = Floor.query.all()
        print(f"\n📍 Distribución por pisos:")
        for piso in pisos:
            # Contar mesas en este piso
            zonas_piso = Zone.query.filter_by(floor_id=piso.id).all()
            mesas_piso = 0
            for zona in zonas_piso:
                mesas_piso += Table.query.filter_by(zone_id=zona.id).count()
            print(f"• {piso.name}: {mesas_piso} mesas")
        
        # Mostrar algunas mesas de ejemplo
        print("\n📍 Mesas de ejemplo:")
        mesas_ejemplo = Table.query.limit(10).all()
        for mesa in mesas_ejemplo:
            print(f"  Mesa {mesa.number} - Zona: {mesa.zone.name if mesa.zone else 'Sin zona'} - Piso: {mesa.zone.floor.name if mesa.zone and mesa.zone.floor else 'Sin piso'}")
        
        # 2. Verificar categorías
        print("\n📂 VERIFICANDO CATEGORÍAS:")
        categorias = Category.query.all()
        print(f"Total de categorías encontradas: {len(categorias)}")
        
        for categoria in categorias:
            productos_count = Product.query.filter_by(category_id=categoria.id).count()
            print(f"• {categoria.name}: {productos_count} productos")
        
        # 3. Verificar productos
        print("\n🍽️ VERIFICANDO PRODUCTOS:")
        productos = Product.query.all()
        print(f"Total de productos encontrados: {len(productos)}")
        
        # Mostrar productos por categoría
        for categoria in categorias:
            productos_categoria = Product.query.filter_by(category_id=categoria.id).all()
            print(f"\n📂 {categoria.name}:")
            for producto in productos_categoria:
                print(f"   • {producto.name} - S/. {producto.price}")
        
        # 4. Verificar usuarios mozo
        print("\n👥 VERIFICANDO USUARIOS MOZO:")
        mozos = User.query.filter_by(role='mozo').all()
        print(f"Total de mozos encontrados: {len(mozos)}")
        
        for mozo in mozos:
            print(f"• Usuario: {mozo.username} - Activo: {mozo.is_active}")
        
        # 5. Verificar permisos temporales
        print("\n🔐 VERIFICANDO PERMISOS TEMPORALES:")
        permisos = TemporaryPermission.query.all()
        print(f"Total de permisos temporales encontrados: {len(permisos)}")
        
        for permiso in permisos:
            print(f"• Usuario {permiso.user_id} - Área: {permiso.area} - Activo: {permiso.is_active}")
        
        print("\n" + "=" * 60)
        print("✅ VERIFICACIÓN COMPLETADA")
        print("=" * 60)
        
        return {
            'mesas': len(mesas),
            'productos': len(productos),
            'categorias': len(categorias),
            'mozos': len(mozos),
            'permisos': len(permisos)
        }

if __name__ == "__main__":
    resultado = verificar_datos()
    print(f"\n📊 RESUMEN:")
    print(f"• Mesas: {resultado['mesas']}")
    print(f"• Productos: {resultado['productos']}")
    print(f"• Categorías: {resultado['categorias']}")
    print(f"• Mozos: {resultado['mozos']}")
    print(f"• Permisos: {resultado['permisos']}")