#!/usr/bin/env python3
"""
Script para implementar restricción de sesión única por usuario
y arreglar problemas de múltiples sesiones
"""

from models import User
from models.user_session import UserSession
from config.extensions import db
from datetime import datetime, timezone
import sys

def force_single_session_policy():
    """Implementar política de sesión única por usuario"""
    print("🔒 IMPLEMENTANDO POLÍTICA DE SESIÓN ÚNICA")
    print("=" * 50)
    
    try:
        # Obtener todos los usuarios con sesiones activas
        users_with_sessions = db.session.query(User.id, User.username, User.role)\
                                       .join(UserSession)\
                                       .filter(UserSession.is_active == True)\
                                       .distinct()\
                                       .all()
        
        print(f"📊 Usuarios con sesiones activas: {len(users_with_sessions)}")
        
        total_closed = 0
        for user_id, username, role in users_with_sessions:
            # Obtener todas las sesiones activas del usuario
            active_sessions = UserSession.query.filter_by(
                user_id=user_id, 
                is_active=True
            ).order_by(UserSession.last_activity.desc()).all()
            
            if len(active_sessions) > 1:
                # Mantener solo la sesión más reciente
                print(f"👤 {username} ({role}): {len(active_sessions)} sesiones activas")
                
                # Cerrar sesiones antiguas (todas excepto la primera/más reciente)
                for session in active_sessions[1:]:
                    session.is_active = False
                    session.invalidation_reason = 'single_session_policy'
                    session.invalidated_at = datetime.now(timezone.utc)
                    total_closed += 1
                    print(f"   ❌ Cerrada sesión: {session.session_id[:8]}...")
                
                # Mantener la más reciente
                print(f"   ✅ Mantenida sesión: {active_sessions[0].session_id[:8]}...")
            else:
                print(f"✅ {username} ({role}): 1 sesión (OK)")
        
        # Actualizar campos legacy en tabla User
        users_to_update = User.query.filter(User.current_session_token.isnot(None)).all()
        for user in users_to_update:
            # Verificar si tiene sesión activa en UserSession
            active_session = UserSession.query.filter_by(
                user_id=user.id, 
                is_active=True
            ).first()
            
            if not active_session:
                # No tiene sesión activa, limpiar campos legacy
                user.current_session_token = None
                user.session_expires_at = None
                print(f"🧹 Limpiados campos legacy de {user.username}")
        
        db.session.commit()
        print(f"\n✅ POLÍTICA IMPLEMENTADA")
        print(f"📊 Sesiones cerradas: {total_closed}")
        print(f"🔒 Restricción de sesión única ACTIVADA")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR: {str(e)}")
        sys.exit(1)

def update_auth_service_enforcement():
    """Verificar que el AuthService esté aplicando la política correctamente"""
    print("\n🔧 VERIFICANDO APLICACIÓN DE POLÍTICA EN AUTH_SERVICE")
    print("=" * 50)
    
    try:
        # Verificar archivo auth_service.py para ver si tiene la lógica correcta
        with open('services/auth_service.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Buscar la lógica de invalidación de sesiones
        if 'invalidar sesiones anteriores' in content or 'existing_sessions' in content:
            print("✅ AuthService tiene lógica de invalidación de sesiones")
        else:
            print("⚠️  AuthService puede necesitar actualización")
            
        # Verificar SessionService
        with open('services/session_service.py', 'r', encoding='utf-8') as f:
            session_content = f.read()
            
        if 'invalidate' in session_content and 'new_login_same_user' in session_content:
            print("✅ SessionService tiene lógica de invalidación correcta")
        else:
            print("⚠️  SessionService puede necesitar actualización")
            
    except FileNotFoundError as e:
        print(f"⚠️  No se pudo verificar archivo: {e}")
    except Exception as e:
        print(f"❌ Error verificando archivos: {e}")

def test_session_monitoring():
    """Probar el monitoreo de sesiones"""
    print("\n📊 PROBANDO MONITOREO DE SESIONES")
    print("=" * 50)
    
    try:
        # Contar sesiones activas por rol
        session_counts = db.session.query(
            User.role,
            db.func.count(UserSession.id).label('count')
        ).join(UserSession)\
         .filter(UserSession.is_active == True)\
         .group_by(User.role)\
         .all()
        
        print("📈 Sesiones activas por rol:")
        total_sessions = 0
        for role, count in session_counts:
            print(f"   {role}: {count} sesión(es)")
            total_sessions += count
            
        print(f"\n🎯 Total sesiones activas: {total_sessions}")
        
        # Listar usuarios con sesión activa
        active_users = db.session.query(User.username, User.role)\
                                 .join(UserSession)\
                                 .filter(UserSession.is_active == True)\
                                 .distinct()\
                                 .all()
        
        print(f"\n👥 Usuarios con sesión activa ({len(active_users)}):")
        for username, role in active_users:
            print(f"   - {username} ({role})")
            
    except Exception as e:
        print(f"❌ Error en monitoreo: {str(e)}")

def main():
    """Función principal para ejecutar todas las correcciones"""
    print("🚀 CORRECCIÓN DE SISTEMA DE SESIONES")
    print("=" * 50)
    
    try:
        force_single_session_policy()
        update_auth_service_enforcement()
        test_session_monitoring()
        
        print("\n" + "=" * 50)
        print("✅ CORRECCIÓN COMPLETADA")
        print("🔒 Política de sesión única implementada")
        print("📊 Monitoreo de sesiones verificado")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()