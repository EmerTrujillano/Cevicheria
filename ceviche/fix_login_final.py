#!/usr/bin/env python3
"""
SCRIPT PARA VERIFICAR Y ARREGLAR EL LOGIN RÁPIDAMENTE
"""
from app import create_app
from config.extensions import db, bcrypt
from models import User

def fix_login_system():
    """Arreglar el sistema de login para que funcione"""
    app = create_app('mysql')
    with app.app_context():
        print("🔧 VERIFICANDO SISTEMA DE LOGIN...")
        
        # Verificar usuarios existentes
        users = User.query.all()
        print(f"👥 Usuarios encontrados: {len(users)}")
        
        for user in users:
            print(f"  - {user.username} ({user.role}) - Estación: {user.estacion}")
            
            # Verificar contraseña según las credenciales
            passwords = {
                'admin': 'admin2025',
                'mozo1': 'mozo1pass',
                'mozo2': 'mozo2pass',
                'cocina1': 'frios2025',
                'cocina2': 'calientes2025',
                'cocina3': 'frituras2025',
                'cocina4': 'bebidas2025',
                'cocina5': 'postres2025',
                'cocina6': 'acomp2025',
                'cajero1': 'cajero1pass',
            }
            
            if user.username in passwords:
                expected_password = passwords[user.username]
                try:
                    is_valid = bcrypt.check_password_hash(user.password, expected_password)
                    if not is_valid:
                        # Regenerar hash
                        new_hash = bcrypt.generate_password_hash(expected_password).decode('utf-8')
                        user.password = new_hash
                        print(f"    🔄 Contraseña actualizada para {user.username}")
                except Exception as e:
                    # Regenerar hash por error
                    new_hash = bcrypt.generate_password_hash(expected_password).decode('utf-8')
                    user.password = new_hash
                    print(f"    🔧 Hash corregido para {user.username}")
        
        # Actualizar estaciones si faltan
        estaciones = {
            'cocina1': 'frios',
            'cocina2': 'calientes', 
            'cocina3': 'frituras',
            'cocina4': 'bebidas',
            'cocina5': 'postres',
            'cocina6': 'acomp'
        }
        
        for username, estacion in estaciones.items():
            user = User.query.filter_by(username=username).first()
            if user and not user.estacion:
                user.estacion = estacion
                print(f"    🏪 Estación asignada: {username} → {estacion}")
        
        try:
            db.session.commit()
            print("✅ SISTEMA DE LOGIN ARREGLADO")
            
            # Verificar que funcionan
            print("\n🔐 VERIFICANDO CONTRASEÑAS...")
            for username, password in passwords.items():
                user = User.query.filter_by(username=username).first()
                if user:
                    is_valid = bcrypt.check_password_hash(user.password, password)
                    status = "✅" if is_valid else "❌"
                    print(f"{status} {username}: {password}")
            
            return True
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    if fix_login_system():
        print("\n🚀 LOGIN SYSTEM READY!")
        print("URL: http://127.0.0.1:5000/login")
    else:
        print("\n💥 ERROR AL ARREGLAR LOGIN")