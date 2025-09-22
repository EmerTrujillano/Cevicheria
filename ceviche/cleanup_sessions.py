#!/usr/bin/env python3
"""
LIMPIAR SESIONES ACTIVAS PROBLEMÁTICAS
"""
from app import create_app
from config.extensions import db
from models.user_session import UserSession

def cleanup_sessions():
    app = create_app('mysql')
    with app.app_context():
        print("🧹 LIMPIANDO SESIONES ACTIVAS...")
        
        # Obtener todas las sesiones activas
        active_sessions = UserSession.query.filter_by(is_active=True).all()
        print(f"📊 Sesiones activas encontradas: {len(active_sessions)}")
        
        count = 0
        for session in active_sessions:
            print(f"  🗑️ Invalidando sesión: {session.session_id} (Usuario: {session.user.username})")
            session.invalidate('cleanup_manual')
            count += 1
        
        db.session.commit()
        print(f"✅ {count} sesiones limpiadas")
        
        # Verificar resultado
        remaining = UserSession.query.filter_by(is_active=True).count()
        print(f"📊 Sesiones activas restantes: {remaining}")

if __name__ == '__main__':
    cleanup_sessions()