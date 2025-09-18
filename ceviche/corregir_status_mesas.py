#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from models.table import Table
from config.extensions import db

app = create_app()

with app.app_context():
    print("🔧 CORRIGIENDO STATUS DE MESAS")
    print("=" * 50)
    
    # Actualizar status de mesas de 'available' a 'libre'
    mesas = Table.query.all()
    print(f"Total mesas a actualizar: {len(mesas)}")
    
    for mesa in mesas:
        if mesa.status == 'available' or mesa.status is None:
            mesa.status = 'libre'
    
    # Guardar cambios
    db.session.commit()
    
    # Verificar cambios
    mesas_libres = Table.query.filter_by(status='libre').count()
    print(f"✅ Mesas actualizadas a 'libre': {mesas_libres}")
    
    # Mostrar muestra de mesas organizadas
    print(f"\n🪑 MUESTRA DE MESAS REORGANIZADAS:")
    mesas_muestra = Table.query.order_by(Table.number).limit(20).all()
    for mesa in mesas_muestra:
        zona = mesa.zone.name if mesa.zone else "Sin zona"
        piso = mesa.zone.floor.name if mesa.zone and mesa.zone.floor else "Sin piso"
        print(f"   Mesa {mesa.number} - {zona} ({piso}) - {mesa.status}")
    
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   🪑 Total mesas: {Table.query.count()}")
    print(f"   ✅ Mesas libres: {Table.query.filter_by(status='libre').count()}")
    print(f"   ❌ Mesas ocupadas: {Table.query.filter_by(status='ocupada').count()}")
    
    print("\n" + "=" * 50)