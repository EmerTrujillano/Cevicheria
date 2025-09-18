#!/usr/bin/env python3
"""
INSPECCIONAR HASHES EN LA BASE DE DATOS
"""
from app import create_app
from config.extensions import db, bcrypt
from models import User

def inspect_password_hashes():
    """Inspeccionar los hashes actuales en la BD"""
    app = create_app('mysql')
    with app.app_context():
        print("🔍 INSPECCIONANDO HASHES EN LA BASE DE DATOS...")
        
        users = User.query.all()
        for user in users:
            print(f"\n👤 Usuario: {user.username}")
            print(f"  ID: {user.id}")
            print(f"  Rol: {user.role}")
            print(f"  Hash completo: '{user.password}'")
            print(f"  Longitud hash: {len(user.password) if user.password else 0}")
            print(f"  ¿Es None?: {user.password is None}")
            print(f"  ¿Es vacío?: '{user.password}' == ''")
            
            # Intentar descifrar algunos caracteres
            if user.password and len(user.password) > 0:
                print(f"  Primeros 10 chars: '{user.password[:10]}'")
                print(f"  Últimos 10 chars: '{user.password[-10:]}'")
                print(f"  ¿Empieza con $2b$?: {user.password.startswith('$2b$')}")
            
            # Hacer una prueba de bcrypt
            if user.username == 'admin':
                try:
                    test_password = 'admin2025'
                    result = bcrypt.check_password_hash(user.password, test_password)
                    print(f"  🧪 Test bcrypt con '{test_password}': {result}")
                except Exception as e:
                    print(f"  ❌ Error test bcrypt: {e}")

if __name__ == '__main__':
    inspect_password_hashes()