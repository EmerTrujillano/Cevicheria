from config.extensions import db
from models import Floor, Zone, Table

def add_more_tables():
    """Agregar más mesas organizadas por zonas"""
    
    # Buscar el piso principal
    piso_principal = Floor.query.filter_by(name='Piso Principal').first()
    if not piso_principal:
        piso_principal = Floor(name='Piso Principal', description='Piso principal del restaurante')
        db.session.add(piso_principal)
        db.session.commit()
    
    # Crear zonas si no existen
    zonas_data = [
        {
            'name': 'Terraza',
            'description': 'Área exterior con vista panorámica',
            'zone_type': 'dining',
            'mesas': 6  # Mesas 11-16
        },
        {
            'name': 'Salón Principal',
            'description': 'Área principal del restaurante',
            'zone_type': 'dining',
            'mesas': 8  # Mesas 17-24
        },
        {
            'name': 'Área VIP',
            'description': 'Zona privada para eventos especiales',
            'zone_type': 'private_event',
            'mesas': 4  # Mesas 25-28
        },
        {
            'name': 'Barra',
            'description': 'Zona de barra para comidas rápidas',
            'zone_type': 'dining',
            'mesas': 6  # Mesas 29-34
        },
        {
            'name': 'Delivery',
            'description': 'Mesa virtual para pedidos de delivery',
            'zone_type': 'delivery',
            'mesas': 1  # Mesa 35
        }
    ]
    
    # Obtener número de mesa más alto actual
    max_table_number = db.session.query(db.func.max(Table.number)).scalar() or 0
    current_table_num = int(max_table_number) + 1
    
    for zona_data in zonas_data:
        # Verificar si la zona ya existe
        zona = Zone.query.filter_by(name=zona_data['name'], floor_id=piso_principal.id).first()
        if not zona:
            zona = Zone(
                name=zona_data['name'],
                description=zona_data['description'],
                floor_id=piso_principal.id,
                zone_type=zona_data['zone_type']
            )
            db.session.add(zona)
            db.session.commit()
            
            # Agregar mesas a esta zona
            for i in range(zona_data['mesas']):
                # Calcular capacidad según zona
                if zona_data['name'] == 'Área VIP':
                    capacity = 6  # Mesas más grandes para VIP
                elif zona_data['name'] == 'Barra':
                    capacity = 2  # Mesas de barra más pequeñas
                elif zona_data['name'] == 'Delivery':
                    capacity = 1  # Mesa virtual
                else:
                    capacity = 4  # Mesas estándar
                
                nueva_mesa = Table(
                    number=str(current_table_num),
                    capacity=capacity,
                    zone_id=zona.id,
                    status='available'
                )
                db.session.add(nueva_mesa)
                current_table_num += 1
        else:
            print(f"Zona '{zona_data['name']}' ya existe, saltando...")
    
    try:
        db.session.commit()
        print(f"✅ Se agregaron mesas hasta la número {current_table_num - 1}")
        print("📍 Zonas creadas/verificadas:")
        for zona_data in zonas_data:
            print(f"   - {zona_data['name']}: {zona_data['mesas']} mesas ({zona_data['zone_type']})")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al agregar mesas: {e}")

if __name__ == '__main__':
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from app import create_app
    
    app = create_app('mysql')
    with app.app_context():
        add_more_tables()
        
        # Mostrar resumen de mesas por zona
        print("\n📊 RESUMEN DE MESAS POR ZONA:")
        zonas = Zone.query.join(Floor).all()
        for zona in zonas:
            mesas_count = Table.query.filter_by(zone_id=zona.id).count()
            mesas_disponibles = Table.query.filter_by(zone_id=zona.id, status='available').count()
            print(f"🏷️  {zona.floor.name} > {zona.name}")
            print(f"    📊 {mesas_count} mesas totales, {mesas_disponibles} disponibles")
            print(f"    🏢 Tipo: {zona.zone_type}")