"""
Actualizar menú completo con categorías por estación y nuevos platos
"""
from app import create_app
from models import Category, Product, User
from config.extensions import db
from werkzeug.security import generate_password_hash

app = create_app('mysql')

def update_menu_and_users():
    print("🍽️ ACTUALIZANDO MENÚ COMPLETO Y USUARIOS DE COCINA")
    print("=" * 55)
    
    with app.app_context():
        try:
            # 1. Crear/actualizar categorías por estación
            stations_data = {
                "fríos": {
                    "description": "Platos que se preparan en la estación de fríos",
                    "platos": [
                        {"name": "Ceviche clásico", "description": "Pescado fresco marinado en limón, ají, cebolla y cilantro"},
                        {"name": "Ceviche mixto", "description": "Pescado, pulpo, calamar y camarones marinados en limón"},
                        {"name": "Ceviche nikkei", "description": "Fusión peruano-japonesa con leche de tigre y toques orientales"},
                        {"name": "Tiradito al ají amarillo", "description": "Láminas de pescado con crema de ají amarillo"},
                        {"name": "Tiradito tres ajíes", "description": "Pescado con salsa de ají amarillo, rocoto y ají limo"},
                        {"name": "Leche de tigre", "description": "Jugo concentrado de ceviche con camote y cancha"},
                        {"name": "Choritos a la chalaca", "description": "Mejillones con cebolla, tomate, choclo y limón"},
                        {"name": "Causa limeña (pollo)", "description": "Papa amarilla con pollo deshilachado y mayonesa"},
                        {"name": "Causa limeña (pulpo)", "description": "Papa amarilla con pulpo tierno y palta"},
                        {"name": "Causa limeña (cangrejo)", "description": "Papa amarilla con carne de cangrejo y palta"},
                        {"name": "Piqueo marino (frío)", "description": "Variedad de mariscos fríos con salsas criollas"}
                    ]
                },
                "calientes": {
                    "description": "Platos que se preparan en la estación de calientes",
                    "platos": [
                        {"name": "Arroz con mariscos", "description": "Arroz con mix de mariscos, ají amarillo y culantro"},
                        {"name": "Chaufa de mariscos", "description": "Arroz frito con mariscos, sillao y kion"},
                        {"name": "Tacu tacu con mariscos", "description": "Frijoles y arroz refritos con mariscos saltados"},
                        {"name": "Sudado de pescado", "description": "Pescado cocido al vapor con cebolla y ají amarillo"},
                        {"name": "Parihuela", "description": "Sopa concentrada de mariscos con ají panca"},
                        {"name": "Pescado a lo macho", "description": "Pescado con salsa de mariscos y ají amarillo"},
                        {"name": "Ají de gallina", "description": "Pollo deshilachado en crema de ají amarillo"},
                        {"name": "Piqueo marino (caliente)", "description": "Mariscos salteados con cebolla y ajíes"}
                    ]
                },
                "frituras": {
                    "description": "Platos que se preparan en la estación de frituras",
                    "platos": [
                        {"name": "Jalea mixta", "description": "Pescado, calamares y mariscos fritos con yuca y salsa criolla"},
                        {"name": "Chicharrón de calamar", "description": "Anillos de calamar crocantes con limón"},
                        {"name": "Pulpo a la parrilla", "description": "Pulpo tierno a la plancha con chimichurri"},
                        {"name": "Lomo saltado", "description": "Carne de res saltada con papas fritas y arroz"}
                    ]
                },
                "bebidas": {
                    "description": "Bebidas frías, calientes y cocteles",
                    "platos": [
                        {"name": "Chicha morada", "description": "Bebida tradicional de maíz morado con especias"},
                        {"name": "Chicha de jora", "description": "Bebida fermentada de maíz amarillo"},
                        {"name": "Inca Kola", "description": "Gaseosa peruana sabor tropical"},
                        {"name": "Jugo de maracuyá", "description": "Jugo natural de maracuyá"},
                        {"name": "Limonada", "description": "Limonada fresca con hielo"},
                        {"name": "Agua sin gas", "description": "Agua mineral sin gas"},
                        {"name": "Agua con gas", "description": "Agua mineral con gas"},
                        {"name": "Pisco Sour", "description": "Coctel de pisco, limón, jarabe y clara de huevo"},
                        {"name": "Chilcano clásico", "description": "Pisco, limón, ginger ale e hielo"},
                        {"name": "Chilcano de maracuyá", "description": "Pisco, maracuyá, ginger ale e hielo"},
                        {"name": "Chilcano de jengibre", "description": "Pisco, jengibre, limón y ginger ale"},
                        {"name": "Sangría", "description": "Vino tinto con frutas y especias"},
                        {"name": "Cerveza Pilsen", "description": "Cerveza peruana tradicional"},
                        {"name": "Cerveza Cusqueña", "description": "Cerveza premium del Cusco"},
                        {"name": "Cerveza artesanal", "description": "Cerveza artesanal local"}
                    ]
                },
                "postres": {
                    "description": "Dulces y postres tradicionales",
                    "platos": [
                        {"name": "Suspiro limeño", "description": "Manjar blanco con merengue de port"},
                        {"name": "Mazamorra morada", "description": "Postre de maíz morado con frutas"},
                        {"name": "Arroz con leche", "description": "Arroz dulce con leche, canela y pasas"},
                        {"name": "Tres leches", "description": "Bizcocho empapado en tres tipos de leche"},
                        {"name": "Helado de maracuyá", "description": "Helado artesanal de maracuyá"},
                        {"name": "Helado de chirimoya", "description": "Helado artesanal de chirimoya"}
                    ]
                },
                "acompañamientos": {
                    "description": "Guarniciones y acompañamientos",
                    "platos": [
                        {"name": "Camote glaseado", "description": "Camote hervido con glaseado dulce"},
                        {"name": "Choclo con queso", "description": "Choclo tierno con queso fresco"},
                        {"name": "Papa frita", "description": "Papas cortadas en bastones y fritas"},
                        {"name": "Yuca frita", "description": "Yuca hervida y frita hasta dorar"},
                        {"name": "Ensalada criolla", "description": "Cebolla, tomate y ají con limón"},
                        {"name": "Pan al ajo", "description": "Pan tostado con mantequilla de ajo"}
                    ]
                }
            }
            
            print("📋 Creando categorías por estación...")
            
            for estacion, data in stations_data.items():
                # Crear o actualizar categoría
                category = Category.query.filter_by(name=estacion.title()).first()
                if not category:
                    category = Category(
                        name=estacion.title(),
                        description=data["description"],
                        estacion=estacion
                    )
                    db.session.add(category)
                    print(f"   ✅ Categoría '{estacion}' creada")
                else:
                    category.estacion = estacion
                    category.description = data["description"]
                    print(f"   ✅ Categoría '{estacion}' actualizada")
                
                db.session.flush()  # Para obtener el ID
                
                # Limpiar productos existentes de esta categoría
                Product.query.filter_by(category_id=category.id).delete()
                
                # Agregar productos
                for plato in data["platos"]:
                    product = Product(
                        name=plato["name"],
                        description=plato["description"],
                        price=25.00,  # Precio base, se puede ajustar después
                        category_id=category.id,
                        is_available=True
                    )
                    db.session.add(product)
                
                print(f"   📝 {len(data['platos'])} platos agregados a {estacion}")
            
            # 2. Crear usuarios de cocina por estación
            print("\n👨‍🍳 Creando usuarios de cocina por estación...")
            
            # Eliminar usuarios de cocina existentes excepto cocina1, cocina2, cocina3
            existing_kitchen = User.query.filter_by(role='kitchen').all()
            for user in existing_kitchen:
                if user.username not in ['cocina1', 'cocina2', 'cocina3']:
                    db.session.delete(user)
            
            # Actualizar usuarios existentes y crear nuevos
            kitchen_users = [
                {"username": "cocina1", "estacion": "fríos", "password": "frios2025"},
                {"username": "cocina2", "estacion": "calientes", "password": "calientes2025"},
                {"username": "cocina3", "estacion": "frituras", "password": "frituras2025"},
                {"username": "cocina4", "estacion": "bebidas", "password": "bebidas2025"},
                {"username": "cocina5", "estacion": "postres", "password": "postres2025"},
                {"username": "cocina6", "estacion": "acompañamientos", "password": "acompa2025"}
            ]
            
            for user_data in kitchen_users:
                user = User.query.filter_by(username=user_data["username"]).first()
                if not user:
                    # Crear nuevo usuario
                    user = User(
                        username=user_data["username"],
                        password_hash=generate_password_hash(user_data["password"]),
                        role='kitchen',
                        estacion=user_data["estacion"]
                    )
                    db.session.add(user)
                    print(f"   ✅ Usuario {user_data['username']} creado para estación {user_data['estacion']}")
                else:
                    # Actualizar usuario existente
                    user.estacion = user_data["estacion"]
                    user.password_hash = generate_password_hash(user_data["password"])
                    print(f"   ✅ Usuario {user_data['username']} actualizado para estación {user_data['estacion']}")
            
            db.session.commit()
            
            print("\n🎉 ACTUALIZACIÓN COMPLETA:")
            print("✅ 6 categorías por estación creadas")
            print("✅ Menú completo con descripciones")
            print("✅ 6 usuarios de cocina especializados")
            print("\n📋 NUEVAS CREDENCIALES DE COCINA:")
            for user_data in kitchen_users:
                print(f"   🔑 {user_data['username']}: {user_data['password']} (Estación: {user_data['estacion']})")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    update_menu_and_users()