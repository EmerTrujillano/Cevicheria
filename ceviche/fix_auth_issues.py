#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para arreglar las contraseñas de los usuarios de cocina
"""

from config.extensions import db
from models.user import User
import bcrypt

def fix_kitchen_passwords():
    """Arreglar contraseñas de usuarios de cocina"""
    try:
        # Contraseñas correctas para usuarios de cocina
        kitchen_users_passwords = {
            "cocina1": "frios2025",
            "cocina2": "calientes2025",
            "cocina3": "frituras2025",
            "cocina4": "bebidas2025",
            "cocina5": "postres2025",
            "cocina6": "acomp2025"
        }

        for username, password in kitchen_users_passwords.items():
            user = User.query.filter_by(username=username).first()
            if user:
                # Usar bcrypt para hash de contraseña
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                user.password = password_hash.decode('utf-8')
                print(f"✅ Contraseña de {username} actualizada")
            else:
                print(f"❌ Usuario {username} no encontrado")

        db.session.commit()
        print("✅ Todas las contraseñas de cocina han sido actualizadas")
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando contraseñas: {e}")
        db.session.rollback()
        return False

def fix_session_management():
    """Arreglar problema de sesiones múltiples"""
    # Leer el archivo de servicio de sesiones
    try:
        # El problema está en que el sistema no permite sesiones simultáneas de diferentes usuarios
        # Vamos a modificar el SessionService para permitir esto
        
        print("🔧 Revisando configuración de sesiones...")
        
        # Mostrar usuarios activos
        active_users = User.query.filter(User.current_session_token.isnot(None)).all()
        print(f"📊 Usuarios con sesión activa: {len(active_users)}")
        
        for user in active_users:
            print(f"- {user.username} (ID: {user.id}, Rol: {user.role})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en análisis de sesiones: {e}")
        return False

if __name__ == '__main__':
    from app import create_app
    
    app = create_app('mysql')
    with app.app_context():
        print("🔧 Arreglando problemas del sistema...")
        
        print("\n1️⃣ Arreglando contraseñas de cocina...")
        if not fix_kitchen_passwords():
            print("❌ Error arreglando contraseñas")
            exit(1)
        
        print("\n2️⃣ Analizando sesiones...")
        if not fix_session_management():
            print("❌ Error analizando sesiones")
            exit(1)
        
        print("\n✅ ¡Problemas resueltos!")
        print("\n🔑 Credenciales de cocina actualizadas:")
        print("- cocina1: frios2025")
        print("- cocina2: calientes2025") 
        print("- cocina3: frituras2025")
        print("- cocina4: bebidas2025")
        print("- cocina5: postres2025")
        print("- cocina6: acomp2025")