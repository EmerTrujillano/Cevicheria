#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para revisar la tabla user_sessions y limpiar registros innecesarios
"""

from config.extensions import db
from models.user_session import UserSession
from models.user import User
from datetime import datetime, timedelta
from utils.timezone_utils import lima_now

def review_user_sessions():
    """Revisar el estado de la tabla user_sessions"""
    try:
        print("🔍 Revisando tabla user_sessions...")
        
        # Estadísticas generales
        total_sessions = UserSession.query.count()
        active_sessions = UserSession.query.filter_by(is_active=True).count()
        inactive_sessions = UserSession.query.filter_by(is_active=False).count()
        
        print(f"📊 Estadísticas:")
        print(f"   - Total de sesiones: {total_sessions}")
        print(f"   - Sesiones activas: {active_sessions}")
        print(f"   - Sesiones inactivas: {inactive_sessions}")
        
        # Sesiones por usuario
        print(f"\n👥 Sesiones por usuario:")
        users_with_sessions = db.session.query(
            User.username, 
            User.role,
            db.func.count(UserSession.id).label('session_count')
        ).join(UserSession).group_by(User.id).all()
        
        for username, role, count in users_with_sessions:
            print(f"   - {username} ({role}): {count} sesiones")
        
        # Sesiones recientes
        print(f"\n⏰ Últimas 10 sesiones:")
        recent_sessions = UserSession.query.join(User).order_by(UserSession.created_at.desc()).limit(10).all()
        
        for session in recent_sessions:
            status = "✅ Activa" if session.is_active else "❌ Inactiva"
            print(f"   - {session.user.username}: {session.created_at} ({status})")
        
        # Sesiones expiradas pero marcadas como activas
        now = lima_now()
        expired_active = UserSession.query.filter(
            UserSession.is_active == True,
            UserSession.expires_at < now
        ).count()
        
        print(f"\n⚠️ Sesiones expiradas pero marcadas como activas: {expired_active}")
        
        return {
            'total': total_sessions,
            'active': active_sessions,
            'inactive': inactive_sessions,
            'expired_active': expired_active
        }
        
    except Exception as e:
        print(f"❌ Error revisando sesiones: {e}")
        return None

def cleanup_old_sessions(days_old=7):
    """Limpiar sesiones antiguas"""
    try:
        print(f"\n🧹 Limpiando sesiones inactivas de más de {days_old} días...")
        
        cutoff_date = lima_now() - timedelta(days=days_old)
        
        old_sessions = UserSession.query.filter(
            UserSession.is_active == False,
            UserSession.created_at < cutoff_date
        ).all()
        
        count = len(old_sessions)
        
        if count > 0:
            for session in old_sessions:
                db.session.delete(session)
            
            db.session.commit()
            print(f"✅ {count} sesiones antiguas eliminadas")
        else:
            print("✅ No hay sesiones antiguas que limpiar")
        
        return count
        
    except Exception as e:
        print(f"❌ Error limpiando sesiones: {e}")
        db.session.rollback()
        return 0

def fix_expired_sessions():
    """Marcar sesiones expiradas como inactivas"""
    try:
        print(f"\n🔧 Marcando sesiones expiradas como inactivas...")
        
        now = lima_now()
        expired_sessions = UserSession.query.filter(
            UserSession.is_active == True,
            UserSession.expires_at < now
        ).all()
        
        count = len(expired_sessions)
        
        if count > 0:
            for session in expired_sessions:
                session.invalidate('expired_cleanup')
            
            db.session.commit()
            print(f"✅ {count} sesiones expiradas marcadas como inactivas")
        else:
            print("✅ No hay sesiones expiradas que corregir")
        
        return count
        
    except Exception as e:
        print(f"❌ Error corrigiendo sesiones expiradas: {e}")
        db.session.rollback()
        return 0

if __name__ == '__main__':
    from app import create_app
    
    app = create_app('mysql')
    with app.app_context():
        print("🚀 Revisión y limpieza de user_sessions...")
        
        # Paso 1: Revisar estado actual
        stats = review_user_sessions()
        
        if stats:
            # Paso 2: Corregir sesiones expiradas
            expired_fixed = fix_expired_sessions()
            
            # Paso 3: Limpiar sesiones antiguas
            old_cleaned = cleanup_old_sessions(7)
            
            # Paso 4: Revisar estado final
            print(f"\n📈 Resumen final:")
            final_stats = review_user_sessions()
            
            if final_stats:
                print(f"\n✅ Limpieza completada:")
                print(f"   - Sesiones expiradas corregidas: {expired_fixed}")
                print(f"   - Sesiones antiguas eliminadas: {old_cleaned}")
                print(f"   - Sesiones activas finales: {final_stats['active']}")
                print(f"   - Total final: {final_stats['total']}")
        else:
            print("❌ No se pudo completar la revisión")