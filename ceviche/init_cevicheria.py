"""
Script para inicializar la base de datos de la cevichería con datos de ejemplo
"""
from flask import Flask
from config.extensions import db
from models import (User, Category, Product, Floor, Zone, Table, Review)
from werkzeug.security import generate_password_hash
import uuid

def init_cevicheria_data():
    """Inicializar datos básicos de la cevichería"""
    
    # 1. Crear usuarios del sistema
    print("Creando usuarios del sistema...")
    
    # Admin
    admin = User(
        username='admin',
        password=generate_password_hash('admin123'),
        role='admin'
    )
    db.session.add(admin)
    
    # Mozos
    mozo1 = User(
        username='mozo1',
        password=generate_password_hash('mozo123'),
        role='waiter'
    )
    db.session.add(mozo1)
    
    mozo2 = User(
        username='mozo2',
        password=generate_password_hash('mozo123'),
        role='waiter'
    )
    db.session.add(mozo2)
    
    # Personal de cocina
    cocina1 = User(
        username='cocina1',
        password=generate_password_hash('cocina123'),
        role='kitchen'
    )
    db.session.add(cocina1)
    
    cocina2 = User(
        username='cocina2',
        password=generate_password_hash('cocina123'),
        role='kitchen'
    )
    db.session.add(cocina2)
    
    # Cajeros
    cajero1 = User(
        username='cajero1',
        password=generate_password_hash('cajero123'),
        role='cashier'
    )
    db.session.add(cajero1)
    
    db.session.commit()
    print("✓ Usuarios creados")
    
    # 2. Crear categorías del menú
    print("Creando categorías del menú...")
    
    categories_data = [
        {
            'name': 'Entradas',
            'description': 'Aperitivos y entradas para compartir'
        },
        {
            'name': 'Ceviches',
            'description': 'Ceviches frescos y tradicionales'
        },
        {
            'name': 'Platos Calientes',
            'description': 'Platos principales calientes'
        },
        {
            'name': 'Bebidas',
            'description': 'Bebidas frías, calientes y alcohólicas'
        },
        {
            'name': 'Postres',
            'description': 'Dulces y postres tradicionales'
        }
    ]
    
    categories = {}
    for cat_data in categories_data:
        category = Category(
            name=cat_data['name'],
            description=cat_data['description']
        )
        db.session.add(category)
        categories[cat_data['name']] = category
    
    db.session.commit()
    print("✓ Categorías creadas")
    
    # 3. Crear productos del menú
    print("Creando productos del menú...")
    
    products_data = [
        # Entradas
        {
            'name': 'Causa Limeña',
            'description': 'Papa amarilla con relleno de pollo y mayonesa',
            'price': 18.00,
            'category': 'Entradas',
            'ingredients': 'papa amarilla,pollo,mayonesa,palta,aceituna',
            'tags': 'recomendado',
            'station_type': 'cold',
            'preparation_time': 10,
            'spice_level': 'mild'
        },
        {
            'name': 'Anticuchos',
            'description': 'Brochetas de corazón de res marinadas',
            'price': 25.00,
            'category': 'Entradas',
            'ingredients': 'corazón de res,ají panca,chicha de jora',
            'tags': 'picante,mas_vendido',
            'station_type': 'hot',
            'preparation_time': 15,
            'spice_level': 'medium'
        },
        
        # Ceviches
        {
            'name': 'Ceviche Clásico',
            'description': 'Pescado fresco marinado en limón con cebolla, cilantro y ají',
            'price': 32.00,
            'category': 'Ceviches',
            'ingredients': 'pescado fresco,limón,cebolla roja,cilantro,ají limo',
            'tags': 'recomendado,mas_vendido',
            'station_type': 'cold',
            'preparation_time': 12,
            'spice_level': 'medium'
        },
        {
            'name': 'Ceviche Mixto',
            'description': 'Pescado, camarones y pulpo marinados en limón',
            'price': 45.00,
            'category': 'Ceviches',
            'ingredients': 'pescado,camarones,pulpo,limón,cebolla roja,cilantro',
            'tags': 'recomendado',
            'station_type': 'cold',
            'preparation_time': 15,
            'spice_level': 'medium'
        },
        {
            'name': 'Tiradito de Pescado',
            'description': 'Finas láminas de pescado con salsa de ají amarillo',
            'price': 28.00,
            'category': 'Ceviches',
            'ingredients': 'pescado fresco,ají amarillo,limón,apio',
            'tags': 'nuevo',
            'station_type': 'cold',
            'preparation_time': 10,
            'spice_level': 'mild'
        },
        
        # Platos Calientes
        {
            'name': 'Arroz con Mariscos',
            'description': 'Arroz amarillo con mariscos variados',
            'price': 38.00,
            'category': 'Platos Calientes',
            'ingredients': 'arroz,mariscos,culantro,ají amarillo,chicha de jora',
            'tags': 'mas_vendido',
            'station_type': 'hot',
            'preparation_time': 25,
            'spice_level': 'mild'
        },
        {
            'name': 'Lomo Saltado',
            'description': 'Lomo de res saltado con papas fritas y arroz',
            'price': 35.00,
            'category': 'Platos Calientes',
            'ingredients': 'lomo de res,papas,cebolla,tomate,arroz',
            'tags': 'recomendado',
            'station_type': 'hot',
            'preparation_time': 20,
            'spice_level': 'mild'
        },
        {
            'name': 'Ají de Gallina',
            'description': 'Pollo deshilachado en salsa cremosa de ají amarillo',
            'price': 28.00,
            'category': 'Platos Calientes',
            'ingredients': 'pollo,ají amarillo,leche,pan,nueces',
            'tags': '',
            'station_type': 'hot',
            'preparation_time': 18,
            'spice_level': 'mild'
        },
        
        # Bebidas
        {
            'name': 'Chicha Morada',
            'description': 'Bebida tradicional de maíz morado',
            'price': 8.00,
            'category': 'Bebidas',
            'ingredients': 'maíz morado,piña,canela,clavo',
            'tags': 'recomendado',
            'station_type': 'drinks',
            'preparation_time': 5,
            'spice_level': 'mild'
        },
        {
            'name': 'Pisco Sour',
            'description': 'Cóctel bandera del Perú',
            'price': 18.00,
            'category': 'Bebidas',
            'ingredients': 'pisco,limón,jarabe de goma,clara de huevo,amargo',
            'tags': 'mas_vendido',
            'station_type': 'drinks',
            'preparation_time': 8,
            'spice_level': 'mild'
        },
        {
            'name': 'Inca Kola',
            'description': 'Gaseosa amarilla peruana',
            'price': 6.00,
            'category': 'Bebidas',
            'ingredients': 'gaseosa inca kola',
            'tags': '',
            'station_type': 'drinks',
            'preparation_time': 2,
            'spice_level': 'mild'
        },
        
        # Postres
        {
            'name': 'Suspiro Limeño',
            'description': 'Dulce de leche con merengue de vainilla',
            'price': 15.00,
            'category': 'Postres',
            'ingredients': 'dulce de leche,claras de huevo,vainilla,oporto',
            'tags': 'recomendado',
            'station_type': 'desserts',
            'preparation_time': 10,
            'spice_level': 'mild'
        },
        {
            'name': 'Mazamorra Morada',
            'description': 'Postre tradicional de maíz morado',
            'price': 12.00,
            'category': 'Postres',
            'ingredients': 'maíz morado,frutas,canela,clavo,azúcar',
            'tags': '',
            'station_type': 'desserts',
            'preparation_time': 8,
            'spice_level': 'mild'
        }
    ]
    
    for prod_data in products_data:
        product = Product(
            name=prod_data['name'],
            description=prod_data['description'],
            price=prod_data['price'],
            category_id=categories[prod_data['category']].id,
            ingredients=prod_data['ingredients'],
            tags=prod_data['tags'],
            station_type=prod_data['station_type'],
            preparation_time=prod_data['preparation_time'],
            spice_level=prod_data['spice_level'],
            is_available=True
        )
        db.session.add(product)
    
    db.session.commit()
    print("✓ Productos creados")
    
    # 4. Crear estructura del local (pisos, zonas, mesas)
    print("Creando estructura del local...")
    
    # Piso 1
    piso1 = Floor(
        name='Piso 1',
        description='Planta baja del restaurant'
    )
    db.session.add(piso1)
    db.session.flush()
    
    # Piso 2
    piso2 = Floor(
        name='Piso 2',
        description='Segundo piso del restaurant'
    )
    db.session.add(piso2)
    db.session.flush()
    
    # Zonas del Piso 1
    zona_principal = Zone(
        name='Salón Principal',
        description='Área principal del restaurant',
        floor_id=piso1.id,
        zone_type='dining'
    )
    db.session.add(zona_principal)
    
    zona_barra = Zone(
        name='Barra',
        description='Área de barra y bar',
        floor_id=piso1.id,
        zone_type='dining'
    )
    db.session.add(zona_barra)
    
    zona_terraza = Zone(
        name='Terraza',
        description='Terraza al aire libre',
        floor_id=piso1.id,
        zone_type='dining'
    )
    db.session.add(zona_terraza)
    
    # Zonas del Piso 2
    zona_privado = Zone(
        name='Salón Privado',
        description='Área para eventos privados',
        floor_id=piso2.id,
        zone_type='private_event'
    )
    db.session.add(zona_privado)
    
    zona_ninos = Zone(
        name='Área Niños',
        description='Zona familiar con niños',
        floor_id=piso2.id,
        zone_type='dining'
    )
    db.session.add(zona_ninos)
    
    db.session.commit()
    
    # Crear mesas
    zones = [zona_principal, zona_barra, zona_terraza, zona_privado, zona_ninos]
    table_configs = {
        zona_principal.id: {'prefix': '', 'count': 15, 'capacity': 4},
        zona_barra.id: {'prefix': 'B', 'count': 8, 'capacity': 2},
        zona_terraza.id: {'prefix': 'T', 'count': 10, 'capacity': 4},
        zona_privado.id: {'prefix': 'P', 'count': 4, 'capacity': 8},
        zona_ninos.id: {'prefix': 'N', 'count': 6, 'capacity': 6}
    }
    
    for zone in zones:
        config = table_configs[zone.id]
        for i in range(1, config['count'] + 1):
            table_number = f"{config['prefix']}{i}" if config['prefix'] else str(i)
            
            table = Table(
                number=table_number,
                capacity=config['capacity'],
                zone_id=zone.id,
                qr_code=f"/menu/qr/{table_number}",
                status='available'
            )
            db.session.add(table)
    
    db.session.commit()
    print("✓ Estructura del local creada")
    
    # 5. Crear algunas reseñas de ejemplo
    print("Creando reseñas de ejemplo...")
    
    # Obtener algunos productos para reseñas
    ceviche_clasico = Product.query.filter_by(name='Ceviche Clásico').first()
    pisco_sour = Product.query.filter_by(name='Pisco Sour').first()
    lomo_saltado = Product.query.filter_by(name='Lomo Saltado').first()
    
    reviews_data = [
        {
            'product': ceviche_clasico,
            'customer_name': 'María González',
            'rating': 5,
            'comment': '¡Excelente! El pescado muy fresco y el punto de limón perfecto.',
            'is_approved': True
        },
        {
            'product': ceviche_clasico,
            'customer_name': 'Carlos Mendoza',
            'rating': 4,
            'comment': 'Muy bueno, aunque le faltó un poco más de ají.',
            'is_approved': True
        },
        {
            'product': pisco_sour,
            'customer_name': 'Ana Torres',
            'rating': 5,
            'comment': 'El mejor pisco sour que he probado. Perfectamente balanceado.',
            'is_approved': True
        },
        {
            'product': lomo_saltado,
            'customer_name': 'Roberto Silva',
            'rating': 4,
            'comment': 'Plato clásico bien preparado. Las papas estaban crujientes.',
            'is_approved': True
        }
    ]
    
    for review_data in reviews_data:
        if review_data['product']:
            review = Review(
                product_id=review_data['product'].id,
                customer_name=review_data['customer_name'],
                rating=review_data['rating'],
                comment=review_data['comment'],
                is_approved=review_data['is_approved'],
                approved_by=admin.id if review_data['is_approved'] else None
            )
            db.session.add(review)
    
    db.session.commit()
    print("✓ Reseñas de ejemplo creadas")
    
    print("\n🎉 Inicialización completada exitosamente!")
    print("\n📋 Usuarios creados:")
    print("  - admin / admin123 (Administrador)")
    print("  - mozo1 / mozo123 (Mozo)")
    print("  - mozo2 / mozo123 (Mozo)")
    print("  - cocina1 / cocina123 (Cocina)")
    print("  - cocina2 / cocina123 (Cocina)")
    print("  - cajero1 / cajero123 (Cajero)")
    print("\n🏢 Estructura del local:")
    print("  - Piso 1: Salón Principal (15 mesas), Barra (8 mesas), Terraza (10 mesas)")
    print("  - Piso 2: Salón Privado (4 mesas), Área Niños (6 mesas)")
    print(f"\n🍽️ Menú: {len(products_data)} productos en 5 categorías")
    print(f"📝 Reseñas: {len(reviews_data)} reseñas de ejemplo")

if __name__ == '__main__':
    from app import create_app
    
    # Crear aplicación
    app = create_app('development')
    
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        
        # Verificar si ya hay datos
        if User.query.count() > 0:
            print("⚠️  Ya existen datos en la base de datos.")
            response = input("¿Desea reinicializar? (s/N): ")
            if response.lower() != 's':
                print("Inicialización cancelada.")
                exit()
            
            # Limpiar datos existentes
            print("Limpiando datos existentes...")
            db.drop_all()
            db.create_all()
        
        # Inicializar datos
        init_cevicheria_data()