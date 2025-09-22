"""
Migración para agregar campo estacion a la tabla category
"""
from app import create_app
from config.extensions import db
from sqlalchemy import text

app = create_app('mysql')

def migrate_database():
    print("🔄 MIGRANDO BASE DE DATOS")
    print("=" * 30)
    
    with app.app_context():
        try:
            # Verificar si el campo estacion ya existe
            result = db.session.execute(text("SHOW COLUMNS FROM category LIKE 'estacion'"))
            if result.fetchone():
                print("✅ Campo 'estacion' ya existe en la tabla category")
            else:
                # Agregar campo estacion a category
                db.session.execute(text("ALTER TABLE category ADD COLUMN estacion VARCHAR(50) DEFAULT NULL"))
                print("✅ Campo 'estacion' agregado a la tabla category")
            
            # Verificar si el campo estacion ya existe en user (debería existir)
            result = db.session.execute(text("SHOW COLUMNS FROM user LIKE 'estacion'"))
            if result.fetchone():
                print("✅ Campo 'estacion' ya existe en la tabla user")
            else:
                # Agregar campo estacion a user si no existe
                db.session.execute(text("ALTER TABLE user ADD COLUMN estacion VARCHAR(50) DEFAULT NULL"))
                print("✅ Campo 'estacion' agregado a la tabla user")
            
            db.session.commit()
            print("🎉 Migración completada exitosamente")
            
        except Exception as e:
            print(f"❌ Error en migración: {e}")
            db.session.rollback()

if __name__ == "__main__":
    migrate_database()