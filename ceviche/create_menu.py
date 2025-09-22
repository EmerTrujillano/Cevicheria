from config.extensions import db
from models import Category, Product

def create_restaurant_menu():
    """Crear el menú completo del restaurante con categorías y platos"""
    
    # Datos del menú organizados por estación
    menu_data = {
        "fríos": {
            "description": "Platos frescos y ceviches tradicionales",
            "platos": [
                {
                    "name": "Ceviche clásico",
                    "description": "Pescado fresco marinado en limón con cebolla morada, ají y cilantro",
                    "ingredients": "Pescado del día, limón, cebolla morada, ají limo, cilantro, sal",
                    "price": 32.0,
                    "tags": ["🏆", "⭐"]
                },
                {
                    "name": "Ceviche mixto", 
                    "description": "Combinación de pescado y mariscos frescos en leche de tigre",
                    "ingredients": "Pescado, camarones, pulpo, calamar, limón, cebolla morada",
                    "price": 38.0,
                    "tags": ["⭐"]
                },
                {
                    "name": "Ceviche nikkei",
                    "description": "Fusión peruano-japonesa con toques de sésamo y jengibre", 
                    "ingredients": "Pescado, limón, ají amarillo, jengibre, ajonjolí, salsa de soya",
                    "price": 35.0,
                    "tags": ["🆕", "⭐"]
                },
                {
                    "name": "Tiradito al ají amarillo",
                    "description": "Finas láminas de pescado bañadas en crema de ají amarillo",
                    "ingredients": "Pescado, ají amarillo, limón, aceite de oliva, sal",
                    "price": 28.0,
                    "tags": ["🌶️"]
                },
                {
                    "name": "Tiradito tres ajíes",
                    "description": "Tiradito con mezcla de ají amarillo, rocoto y ají limo",
                    "ingredients": "Pescado, ají amarillo, rocoto, ají limo, limón",
                    "price": 30.0,
                    "tags": ["🌶️", "🌶️"]
                },
                {
                    "name": "Leche de tigre",
                    "description": "Concentrado puro de ceviche con mariscos",
                    "ingredients": "Jugo de ceviche, mariscos, cancha, camote",
                    "price": 18.0,
                    "tags": ["🏆"]
                },
                {
                    "name": "Choritos a la chalaca",
                    "description": "Choritos frescos con salsa chalaca criolla",
                    "ingredients": "Choritos, cebolla, tomate, ají limo, limón, cilantro",
                    "price": 24.0,
                    "tags": []
                },
                {
                    "name": "Causa limeña",
                    "description": "Papa amarilla con relleno a elegir: pollo, pulpo o cangrejo",
                    "ingredients": "Papa amarilla, ají amarillo, limón, mayonesa, relleno a elegir",
                    "price": 26.0,
                    "tags": ["⭐"]
                },
                {
                    "name": "Piqueo marino frío",
                    "description": "Variedad de ceviches y tiraditos para compartir",
                    "ingredients": "Mini porciones de ceviches, tiraditos y causas",
                    "price": 45.0,
                    "tags": []
                }
            ]
        },
        "calientes": {
            "description": "Platos calientes tradicionales peruanos",
            "platos": [
                {
                    "name": "Arroz con mariscos",
                    "description": "Arroz caldoso con mariscos frescos y culantro",
                    "ingredients": "Arroz, mariscos mixtos, culantro, ají amarillo, chicha de jora",
                    "price": 42.0,
                    "tags": ["🏆", "⭐"]
                },
                {
                    "name": "Chaufa de mariscos",
                    "description": "Arroz frito al estilo chino con mariscos",
                    "ingredients": "Arroz, mariscos, sillao, kión, cebolla china, huevo",
                    "price": 38.0,
                    "tags": ["🏆"]
                },
                {
                    "name": "Tacu tacu con mariscos",
                    "description": "Mezcla de arroz y frijoles con mariscos salteados",
                    "ingredients": "Arroz, frijoles, mariscos, ají amarillo, culantro",
                    "price": 35.0,
                    "tags": []
                },
                {
                    "name": "Sudado de pescado",
                    "description": "Pescado cocido al vapor con verduras y chicha de jora",
                    "ingredients": "Pescado, cebolla, tomate, culantro, chicha de jora",
                    "price": 32.0,
                    "tags": ["⭐"]
                },
                {
                    "name": "Parihuela",
                    "description": "Sopa concentrada de mariscos con un toque picante",
                    "ingredients": "Mariscos mixtos, pescado, ají panca, culantro, huevo",
                    "price": 38.0,
                    "tags": ["🌶️", "🏆"]
                },
                {
                    "name": "Pescado a lo macho",
                    "description": "Pescado frito cubierto con salsa de mariscos",
                    "ingredients": "Pescado, mariscos, ají amarillo, culantro, vino blanco",
                    "price": 45.0,
                    "tags": ["⭐"]
                },
                {
                    "name": "Ají de gallina",
                    "description": "Clásico guiso peruano con pollo deshilachado",
                    "ingredients": "Pollo, ají amarillo, pan, leche, nueces, queso",
                    "price": 28.0,
                    "tags": ["🏆"]
                },
                {
                    "name": "Piqueo marino caliente",
                    "description": "Variedad de mariscos calientes para compartir",
                    "ingredients": "Mariscos a la plancha, chicharrones, salsas variadas",
                    "price": 48.0,
                    "tags": []
                }
            ]
        },
        "frituras": {
            "description": "Frituras crujientes y mariscos a la parrilla",
            "platos": [
                {
                    "name": "Jalea mixta",
                    "description": "Fritura mixta de mariscos y pescado con salsa criolla",
                    "ingredients": "Pescado, calamares, camarones, yuca, salsa criolla",
                    "price": 42.0,
                    "tags": ["🏆", "⭐"]
                },
                {
                    "name": "Chicharrón de calamar",
                    "description": "Anillos de calamar fritos hasta el punto perfecto",
                    "ingredients": "Calamar, harina, sal, pimienta, aceite",
                    "price": 32.0,
                    "tags": ["🏆"]
                },
                {
                    "name": "Pulpo a la parrilla",
                    "description": "Pulpo tierno a la parrilla con chimichurri",
                    "ingredients": "Pulpo, aceite de oliva, ajo, perejil, vinagre",
                    "price": 38.0,
                    "tags": ["⭐"]
                },
                {
                    "name": "Lomo saltado",
                    "description": "Clásico peruano con lomo, papas fritas y arroz",
                    "ingredients": "Lomo de res, papas, cebolla, tomate, sillao, vinagre",
                    "price": 35.0,
                    "tags": ["🏆"]
                }
            ]
        },
        "bebidas": {
            "description": "Bebidas tradicionales y cócteles peruanos",
            "platos": [
                {
                    "name": "Chicha morada",
                    "description": "Refresco tradicional de maíz morado con especias",
                    "ingredients": "Maíz morado, piña, canela, clavo, azúcar",
                    "price": 8.0,
                    "tags": ["🏆"]
                },
                {
                    "name": "Chicha de jora",
                    "description": "Bebida ancestral de maíz fermentado",
                    "ingredients": "Maíz de jora fermentado, especias",
                    "price": 10.0,
                    "tags": []
                },
                {
                    "name": "Inca Kola",
                    "description": "La bebida dorada del Perú",
                    "ingredients": "Gaseosa Inca Kola",
                    "price": 6.0,
                    "tags": ["🏆"]
                },
                {
                    "name": "Jugo de maracuyá",
                    "description": "Jugo natural de maracuyá fresco",
                    "ingredients": "Maracuyá, agua, azúcar",
                    "price": 8.0,
                    "tags": ["⭐"]
                },
                {
                    "name": "Limonada",
                    "description": "Refrescante limonada natural",
                    "ingredients": "Limón, agua, azúcar, hielo",
                    "price": 7.0,
                    "tags": []
                },
                {
                    "name": "Agua sin/con gas",
                    "description": "Agua mineral natural o con gas",
                    "ingredients": "Agua mineral",
                    "price": 4.0,
                    "tags": []
                },
                {
                    "name": "Pisco Sour",
                    "description": "Cóctel bandera del Perú con pisco y limón",
                    "ingredients": "Pisco, limón, jarabe, clara de huevo, amargo de angostura",
                    "price": 18.0,
                    "tags": ["🏆", "⭐"]
                },
                {
                    "name": "Chilcano clásico",
                    "description": "Pisco con ginger ale y limón",
                    "ingredients": "Pisco, ginger ale, limón, hielo",
                    "price": 16.0,
                    "tags": ["⭐"]
                },
                {
                    "name": "Chilcano de maracuyá",
                    "description": "Chilcano con toque tropical de maracuyá",
                    "ingredients": "Pisco, maracuyá, ginger ale, limón",
                    "price": 18.0,
                    "tags": ["🆕"]
                },
                {
                    "name": "Chilcano de jengibre",
                    "description": "Chilcano con jengibre fresco",
                    "ingredients": "Pisco, jengibre, ginger ale, limón",
                    "price": 18.0,
                    "tags": ["🆕", "🌶️"]
                },
                {
                    "name": "Sangría",
                    "description": "Vino tinto con frutas frescas",
                    "ingredients": "Vino tinto, frutas de estación, canela",
                    "price": 15.0,
                    "tags": []
                },
                {
                    "name": "Cerveza Pilsen",
                    "description": "Cerveza clásica peruana",
                    "ingredients": "Cerveza Pilsen",
                    "price": 8.0,
                    "tags": ["🏆"]
                },
                {
                    "name": "Cerveza Cusqueña",
                    "description": "Cerveza premium del Cusco",
                    "ingredients": "Cerveza Cusqueña",
                    "price": 9.0,
                    "tags": ["⭐"]
                },
                {
                    "name": "Cerveza artesanal",
                    "description": "Cerveza artesanal de producción local",
                    "ingredients": "Cerveza artesanal variada",
                    "price": 12.0,
                    "tags": ["🆕"]
                }
            ]
        },
        "postres": {
            "description": "Dulces tradicionales peruanos",
            "platos": [
                {
                    "name": "Suspiro limeño",
                    "description": "Manjar blanco cubierto con merengue y canela",
                    "ingredients": "Leche condensada, yemas, merengue, canela, oporto",
                    "price": 15.0,
                    "tags": ["🏆", "⭐"]
                },
                {
                    "name": "Mazamorra morada",
                    "description": "Postre tradicional de maíz morado con frutas",
                    "ingredients": "Maíz morado, frutas, canela, clavo, azúcar",
                    "price": 12.0,
                    "tags": ["🏆"]
                },
                {
                    "name": "Arroz con leche",
                    "description": "Clásico arroz con leche peruano con canela",
                    "ingredients": "Arroz, leche, azúcar, canela, clavo, vainilla",
                    "price": 10.0,
                    "tags": ["🏆"]
                },
                {
                    "name": "Tres leches",
                    "description": "Bizcocho empapado en tres tipos de leche",
                    "ingredients": "Bizcocho, leche condensada, leche evaporada, crema",
                    "price": 14.0,
                    "tags": ["⭐"]
                },
                {
                    "name": "Helado de maracuyá",
                    "description": "Helado artesanal de maracuyá",
                    "ingredients": "Maracuyá, leche, azúcar, crema",
                    "price": 12.0,
                    "tags": ["⭐"]
                },
                {
                    "name": "Helado de chirimoya",
                    "description": "Helado artesanal de chirimoya",
                    "ingredients": "Chirimoya, leche, azúcar, crema",
                    "price": 12.0,
                    "tags": ["⭐"]
                }
            ]
        },
        "acompañamientos": {
            "description": "Acompañamientos tradicionales",
            "platos": [
                {
                    "name": "Camote glaseado",
                    "description": "Camote dulce glaseado al horno",
                    "ingredients": "Camote, azúcar, mantequilla",
                    "price": 8.0,
                    "tags": ["⭐"]
                },
                {
                    "name": "Choclo con queso",
                    "description": "Mazorca tierna con queso fresco",
                    "ingredients": "Choclo, queso fresco",
                    "price": 10.0,
                    "tags": ["🏆"]
                },
                {
                    "name": "Papa frita",
                    "description": "Papas fritas doradas",
                    "ingredients": "Papa, aceite, sal",
                    "price": 8.0,
                    "tags": []
                },
                {
                    "name": "Yuca frita",
                    "description": "Yuca frita crujiente",
                    "ingredients": "Yuca, aceite, sal",
                    "price": 8.0,
                    "tags": []
                },
                {
                    "name": "Ensalada criolla",
                    "description": "Cebolla morada encurtida con ají",
                    "ingredients": "Cebolla morada, ají limo, limón, cilantro",
                    "price": 6.0,
                    "tags": ["🏆"]
                },
                {
                    "name": "Pan al ajo",
                    "description": "Pan tostado con mantequilla de ajo",
                    "ingredients": "Pan, mantequilla, ajo, perejil",
                    "price": 8.0,
                    "tags": []
                }
            ]
        }
    }
    
    print("🍽️ Creando menú completo del restaurante...")
    
    for categoria_name, categoria_info in menu_data.items():
        # Buscar o crear categoría
        categoria = Category.query.filter_by(name=categoria_name).first()
        if not categoria:
            categoria = Category(
                name=categoria_name,
                description=categoria_info["description"]
            )
            db.session.add(categoria)
            db.session.commit()
            print(f"✅ Categoría '{categoria_name}' creada")
        
        # Agregar productos
        for plato_info in categoria_info["platos"]:
            # Verificar si el producto ya existe
            existing_product = Product.query.filter_by(
                name=plato_info["name"], 
                category_id=categoria.id
            ).first()
            
            if not existing_product:
                # Crear tags string
                tags_str = " ".join(plato_info.get("tags", []))
                
                producto = Product(
                    name=plato_info["name"],
                    description=plato_info["description"],
                    ingredients=plato_info["ingredients"],
                    price=plato_info["price"],
                    category_id=categoria.id,
                    is_available=True,
                    tags=tags_str
                )
                db.session.add(producto)
                print(f"  ➕ {plato_info['name']} - S/{plato_info['price']}")
    
    try:
        db.session.commit()
        print("\n🎉 ¡Menú completo creado exitosamente!")
        
        # Mostrar resumen
        print("\n📊 RESUMEN DEL MENÚ:")
        for categoria_name, categoria_info in menu_data.items():
            count = len(categoria_info["platos"])
            print(f"🏷️  {categoria_name.title()}: {count} platos")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creando menú: {e}")

if __name__ == '__main__':
    from app import create_app
    
    app = create_app('mysql')
    with app.app_context():
        create_restaurant_menu()