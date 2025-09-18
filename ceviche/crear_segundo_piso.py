#!/usr/bin/env python3
"""
Script para agregar segundo piso con mesas adicionales
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import Floor, Zone, Table
from config.extensions import db

def crear_segundo_piso():
    """Crear segundo piso con nuevas zonas y mesas"""
    print("🏢 Creando segundo piso...")
    
    app = create_app('mysql')
    
    with app.app_context():
        # Crear segundo piso
        segundo_piso = Floor.query.filter_by(name='Segundo Piso').first()
        if not segundo_piso:
            segundo_piso = Floor(
                name='Segundo Piso',
                description='Segundo nivel del restaurante con vista panorámica'
            )
            db.session.add(segundo_piso)
            db.session.flush()
            print("✅ Segundo piso creado")
        else:
            print("ℹ️ Segundo piso ya existe")
        
        # Zonas del segundo piso
        zonas_segundo_piso = [
            {
                'name': 'Balcón',
                'description': 'Área con vista exterior y ambiente relajado',
                'zone_type': 'dining',
                'mesas': 8
            },
            {
                'name': 'Sala Privada',
                'description': 'Espacio reservado para eventos especiales',
                'zone_type': 'private_event', 
                'mesas': 6
            },
            {
                'name': 'Terraza Superior',
                'description': 'Terraza al aire libre en el segundo piso',
                'zone_type': 'dining',
                'mesas': 10
            },
            {
                'name': 'Zona Familiar',
                'description': 'Área diseñada para familias con niños',
                'zone_type': 'dining',
                'mesas': 12
            }
        ]
        
        # Obtener el último número de mesa
        ultima_mesa = Table.query.order_by(Table.number.desc()).first()
        siguiente_numero = int(ultima_mesa.number if ultima_mesa else 0) + 1
        
        total_mesas_nuevas = 0
        
        for zona_data in zonas_segundo_piso:
            # Crear zona
            zona = Zone.query.filter_by(name=zona_data['name'], floor_id=segundo_piso.id).first()
            if not zona:
                zona = Zone(
                    name=zona_data['name'],
                    description=zona_data['description'],
                    zone_type=zona_data['zone_type'],
                    floor_id=segundo_piso.id
                )
                db.session.add(zona)
                db.session.flush()
                print(f"📍 Zona '{zona_data['name']}' creada")
            else:
                print(f"ℹ️ Zona '{zona_data['name']}' ya existe")
            
            # Verificar mesas existentes en esta zona
            mesas_existentes = Table.query.filter_by(zone_id=zona.id).count()
            mesas_a_crear = zona_data['mesas'] - mesas_existentes
            
            if mesas_a_crear > 0:
                # Crear mesas
                for i in range(mesas_a_crear):
                    # Determinar capacidad según el tipo de zona
                    if zona_data['zone_type'] == 'private_event':
                        capacity = 8  # Mesas grandes para eventos
                    elif zona_data['name'] == 'Zona Familiar':
                        capacity = 6  # Mesas familiares
                    else:
                        capacity = 4  # Mesas estándar
                    
                    mesa = Table(
                        number=siguiente_numero,
                        capacity=capacity,
                        status='available',
                        zone_id=zona.id
                    )
                    db.session.add(mesa)
                    siguiente_numero += 1
                    total_mesas_nuevas += 1
                
                print(f"   ✅ {mesas_a_crear} mesas creadas en {zona_data['name']}")
            else:
                print(f"   ℹ️ {zona_data['name']} ya tiene suficientes mesas")
        
        db.session.commit()
        
        print(f"\n🎉 Segundo piso completado!")
        print(f"📊 Total de mesas nuevas creadas: {total_mesas_nuevas}")
        
        # Mostrar resumen final
        print("\n=== RESUMEN GENERAL ===")
        pisos = Floor.query.all()
        for piso in pisos:
            total_mesas_piso = sum([len(zona.tables) for zona in piso.zones])
            print(f"🏢 {piso.name}: {total_mesas_piso} mesas")
            for zona in piso.zones:
                print(f"   📍 {zona.name}: {len(zona.tables)} mesas")

if __name__ == "__main__":
    crear_segundo_piso()