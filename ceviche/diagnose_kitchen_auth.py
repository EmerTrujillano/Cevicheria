#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para diagnosticar y arreglar el problema de contraseñas de cocina
"""

from config.extensions import db
from models.user import User
import bcrypt

def diagnose_kitchen_users():
    """Diagnosticar problema de contraseñas de cocina"""
    try:
        print("🔍 Diagnóstico de usuarios de cocina...")
        
        kitchen_users = User.query.filter(User.role.in_(['kitchen', 'cocina'])).all()
        
        print(f"📊 Encontrados {len(kitchen_users)} usuarios de cocina:")
        
        for user in kitchen_users:
            print(f"\n👤 Usuario: {user.username}")
            print(f"   ID: {user.id}")
            print(f"   Rol: {user.role}")
            print(f"   Estación: {user.estacion}")
            print(f"   Contraseña hash: {user.password[:50]}...")
            print(f"   Longitud hash: {len(user.password)}")
            
            # Verificar si el hash es válido
            if not user.password or len(user.password) < 10:
                print(f"   ❌ Hash inválido o vacío")
            elif user.password.startswith('$2b$'):
                print(f"   ✅ Hash bcrypt válido")
            elif user.password.startswith('pbkdf2:'):
                print(f"   ✅ Hash Werkzeug válido")
            else:
                print(f"   ❌ Formato de hash desconocido")
        
        return kitchen_users
        
    except Exception as e:
        print(f"❌ Error en diagnóstico: {e}")
        return []

def fix_kitchen_passwords_completely():
    """Arreglar contraseñas de cocina completamente"""
    try:
        print("\n🔧 Arreglando contraseñas de cocina...")
        
        # Mapeo correcto de usuarios y contraseñas
        password_mapping = {
            'cocina1': 'frios2025',
            'cocina2': 'calientes2025', 
            'cocina3': 'frituras2025',
            'cocina4': 'bebidas2025',
            'cocina5': 'postres2025',
            'cocina6': 'acomp2025'
        }
        
        for username, new_password in password_mapping.items():
            user = User.query.filter_by(username=username).first()
            
            if user:
                # Usar el método de la clase User para establecer contraseña
                user.set_password(new_password)
                print(f"✅ {username}: contraseña actualizada usando set_password()")
                
                # Verificar que se estableció correctamente
                if user.check_password(new_password):
                    print(f"   ✅ Verificación exitosa para {username}")
                else:
                    print(f"   ❌ Verificación falló para {username}")
            else:
                print(f"❌ Usuario {username} no encontrado")
        
        db.session.commit()
        print("\n✅ Todas las contraseñas actualizadas y verificadas")
        return True
        
    except Exception as e:
        print(f"❌ Error arreglando contraseñas: {e}")
        db.session.rollback()
        return False

def test_kitchen_login():
    """Probar login de usuarios de cocina"""
    try:
        print("\n🧪 Probando login de usuarios de cocina...")
        
        test_cases = [
            ('cocina1', 'frios2025'),
            ('cocina2', 'calientes2025'),
            ('cocina3', 'frituras2025'),
            ('cocina4', 'bebidas2025'),
            ('cocina5', 'postres2025'),
            ('cocina6', 'acomp2025')
        ]
        
        for username, password in test_cases:
            user = User.query.filter_by(username=username).first()
            if user:
                if user.check_password(password):
                    print(f"✅ {username}: login exitoso con {password}")
                else:
                    print(f"❌ {username}: login falló con {password}")
            else:
                print(f"❌ {username}: usuario no encontrado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando login: {e}")
        return False

if __name__ == '__main__':
    from app import create_app
    
    app = create_app('mysql')
    with app.app_context():
        print("🚀 Diagnóstico completo de usuarios de cocina...")
        
        # Paso 1: Diagnosticar
        kitchen_users = diagnose_kitchen_users()
        
        if kitchen_users:
            # Paso 2: Arreglar
            if fix_kitchen_passwords_completely():
                # Paso 3: Probar
                test_kitchen_login()
            else:
                print("❌ No se pudo arreglar las contraseñas")
        else:
            print("❌ No se encontraron usuarios de cocina")
        
        print("\n🔑 Credenciales finales de cocina:")
        print("- cocina1: frios2025")
        print("- cocina2: calientes2025") 
        print("- cocina3: frituras2025")
        print("- cocina4: bebidas2025")
        print("- cocina5: postres2025")
        print("- cocina6: acomp2025")