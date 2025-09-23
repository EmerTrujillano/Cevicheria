#!/usr/bin/env python3
"""
Script para reorganizar completamente las mesas con numeración lógica
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from config.extensions import db
from models.table import Table, Zone, Floor
from app import create_app

def reorganizar_mesas():
    app = create_app()
    
    with app.app_context():
        print("=" * 80)
        print("🔄 REORGANIZANDO MESAS CON NUMERACIÓN LÓGICA")
        print("=" * 80)
        
        # 1. Limpiar todas las mesas existentes
        print("\n🗑️ Eliminando mesas existentes...")
        mesas_existentes = Table.query.count()
        print(f"   Mesas actuales: {mesas_existentes}")
        
        Table.query.delete()
        db.session.commit()
        print("✅ Todas las mesas eliminadas")
        
        # 2. Verificar pisos y zonas existentes
        print("\n📍 Verificando pisos y zonas...")
        pisos = Floor.query.all()
        for piso in pisos:
            print(f"   • {piso.name} (ID: {piso.id})")
            zonas = Zone.query.filter_by(floor_id=piso.id).all()
            for zona in zonas:
                print(f"     - {zona.name} (ID: {zona.id})")
        
        # 3. Obtener IDs de pisos
        piso_principal = Floor.query.filter_by(name='Piso Principal').first()
        segundo_piso = Floor.query.filter_by(name='Segundo Piso').first()
        
        if not piso_principal or not segundo_piso:
            print("❌ Error: No se encontraron los pisos necesarios")
            return
        
        # 4. Crear nuevas zonas organizadas
        print("\n🏗️ Creando zonas organizadas...")
        
        # Limpiar zonas existentes
        Zone.query.delete()
        db.session.commit()
        
        # PISO PRINCIPAL - Zonas
        zonas_principal = [
            {"name": "Zona Principal", "description": "Mesas principales del restaurante"},
            {"name": "Zona Barra", "description": "Mesas tipo barra para grupos pequeños"},
            {"name": "Zona Familiar", "description": "Mesas grandes para familias"},
            {"name": "Zona Ventana", "description": "Mesas junto a las ventanas"}
        ]
        
        zonas_principal_ids = []
        for zona_data in zonas_principal:
            zona = Zone(
                name=zona_data["name"],
                description=zona_data["description"],
                floor_id=piso_principal.id,
                zone_type="dining"
            )
            db.session.add(zona)
            db.session.flush()
            zonas_principal_ids.append(zona.id)
            print(f"   ✅ {zona.name} creada (ID: {zona.id})")
        
        # SEGUNDO PISO - Zonas  
        zonas_segundo = [
            {"name": "Sala VIP", "description": "Zona exclusiva del segundo piso"},
            {"name": "Terraza", "description": "Mesas en la terraza"},
            {"name": "Salón Privado", "description": "Salón para eventos privados"},
            {"name": "Zona Balcón", "description": "Mesas con vista al exterior"}
        ]
        
        zonas_segundo_ids = []
        for zona_data in zonas_segundo:
            zona = Zone(
                name=zona_data["name"],
                description=zona_data["description"],
                floor_id=segundo_piso.id,
                zone_type="dining"
            )
            db.session.add(zona)
            db.session.flush()
            zonas_segundo_ids.append(zona.id)
            print(f"   ✅ {zona.name} creada (ID: {zona.id})")
        
        db.session.commit()
        
        # 5. Crear mesas con numeración lógica
        print("\n🪑 Creando mesas con numeración lógica...")
        
        mesas_creadas = 0
        
        # PISO PRINCIPAL
        print(f"\n📍 PISO PRINCIPAL:")
        
        # Zona Principal: Mesas 1-15
        zona_principal_id = zonas_principal_ids[0]
        for i in range(1, 16):
            mesa = Table(
                number=str(i),
                capacity=4,
                zone_id=zona_principal_id,
                status='available'
            )
            db.session.add(mesa)
            mesas_creadas += 1
        print(f"   ✅ Zona Principal: Mesas 1-15 (15 mesas)")
        
        # Zona Barra: Mesas B1-B8
        zona_barra_id = zonas_principal_ids[1]
        for i in range(1, 9):
            mesa = Table(
                number=f"B{i}",
                capacity=2,
                zone_id=zona_barra_id,
                status='available'
            )
            db.session.add(mesa)
            mesas_creadas += 1
        print(f"   ✅ Zona Barra: Mesas B1-B8 (8 mesas)")
        
        # Zona Familiar: Mesas F1-F6
        zona_familiar_id = zonas_principal_ids[2]
        for i in range(1, 7):
            mesa = Table(
                number=f"F{i}",
                capacity=6,
                zone_id=zona_familiar_id,
                status='available'
            )
            db.session.add(mesa)
            mesas_creadas += 1
        print(f"   ✅ Zona Familiar: Mesas F1-F6 (6 mesas)")
        
        # Zona Ventana: Mesas V1-V6
        zona_ventana_id = zonas_principal_ids[3]
        for i in range(1, 7):
            mesa = Table(
                number=f"V{i}",
                capacity=4,
                zone_id=zona_ventana_id,
                status='available'
            )
            db.session.add(mesa)
            mesas_creadas += 1
        print(f"   ✅ Zona Ventana: Mesas V1-V6 (6 mesas)")
        
        # SEGUNDO PISO
        print(f"\n📍 SEGUNDO PISO:")
        
        # Sala VIP: Mesas S1-S8
        zona_vip_id = zonas_segundo_ids[0]
        for i in range(1, 9):
            mesa = Table(
                number=f"S{i}",
                capacity=4,
                zone_id=zona_vip_id,
                status='available'
            )
            db.session.add(mesa)
            mesas_creadas += 1
        print(f"   ✅ Sala VIP: Mesas S1-S8 (8 mesas)")
        
        # Terraza: Mesas T1-T10
        zona_terraza_id = zonas_segundo_ids[1]
        for i in range(1, 11):
            mesa = Table(
                number=f"T{i}",
                capacity=4,
                zone_id=zona_terraza_id,
                status='available'
            )
            db.session.add(mesa)
            mesas_creadas += 1
        print(f"   ✅ Terraza: Mesas T1-T10 (10 mesas)")
        
        # Salón Privado: Mesas P1-P4
        zona_privado_id = zonas_segundo_ids[2]
        for i in range(1, 5):
            mesa = Table(
                number=f"P{i}",
                capacity=8,
                zone_id=zona_privado_id,
                status='available'
            )
            db.session.add(mesa)
            mesas_creadas += 1
        print(f"   ✅ Salón Privado: Mesas P1-P4 (4 mesas)")
        
        # Zona Balcón: Mesas L1-L8
        zona_balcon_id = zonas_segundo_ids[3]
        for i in range(1, 9):
            mesa = Table(
                number=f"L{i}",
                capacity=4,
                zone_id=zona_balcon_id,
                status='available'
            )
            db.session.add(mesa)
            mesas_creadas += 1
        print(f"   ✅ Zona Balcón: Mesas L1-L8 (8 mesas)")
        
        # 6. Confirmar cambios
        db.session.commit()
        
        print(f"\n" + "=" * 80)
        print("✅ REORGANIZACIÓN COMPLETADA")
        print("=" * 80)
        print(f"📊 RESUMEN:")
        print(f"   🪑 Total de mesas creadas: {mesas_creadas}")
        print(f"   📍 Piso Principal: 35 mesas (1-15, B1-B8, F1-F6, V1-V6)")
        print(f"   📍 Segundo Piso: 30 mesas (S1-S8, T1-T10, P1-P4, L1-L8)")
        print(f"   🏗️ Total de zonas: 8 zonas organizadas")
        print(f"\n💡 NUEVA NUMERACIÓN:")
        print(f"   • Mesas 1-15: Zona Principal")
        print(f"   • Mesas B1-B8: Zona Barra (2 personas)")
        print(f"   • Mesas F1-F6: Zona Familiar (6 personas)")
        print(f"   • Mesas V1-V6: Zona Ventana")
        print(f"   • Mesas S1-S8: Sala VIP (Segundo Piso)")
        print(f"   • Mesas T1-T10: Terraza (Segundo Piso)")
        print(f"   • Mesas P1-P4: Salón Privado (8 personas)")
        print(f"   • Mesas L1-L8: Zona Balcón")
        print("=" * 80)

if __name__ == "__main__":
    reorganizar_mesas()