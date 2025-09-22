"""
Limpiar todas las sesiones activas para resolver el 409
"""
from app import create_app
from models import User
from models.user_session import UserSession
from config.extensions import db

app = create_app('mysql')

def force_clean_all_sessions():
    print("🧹 LIMPIEZA COMPLETA DE SESIONES")
    print("=" * 40)
    
    with app.app_context():
        try:
            # 1. Obtener todas las sesiones activas
            active_sessions = UserSession.query.filter_by(is_active=True).all()
            print(f"Sesiones activas encontradas: {len(active_sessions)}")
            
            # 2. Desactivar todas las sesiones
            for session in active_sessions:
                print(f"Desactivando sesión: {session.session_id[:20]}... (Usuario {session.user_id})")
                session.is_active = False
                session.invalidated_at = db.func.now()
                session.invalidation_reason = 'manual_cleanup'
            
            # 3. Limpiar tokens de usuarios
            users_with_tokens = User.query.filter(User.current_session_token.isnot(None)).all()
            print(f"Usuarios con tokens: {len(users_with_tokens)}")
            
            for user in users_with_tokens:
                print(f"Limpiando token de: {user.username}")
                user.current_session_token = None
                user.last_activity = None
                user.session_expires_at = None
            
            # 4. Commit cambios
            db.session.commit()
            print("✅ LIMPIEZA COMPLETA EXITOSA")
            
            # 5. Verificación final
            remaining_active = UserSession.query.filter_by(is_active=True).count()
            remaining_tokens = User.query.filter(User.current_session_token.isnot(None)).count()
            
            print(f"\n📊 ESTADO FINAL:")
            print(f"Sesiones activas: {remaining_active}")
            print(f"Tokens restantes: {remaining_tokens}")
            
            if remaining_active == 0 and remaining_tokens == 0:
                print("🎉 Sistema limpio - listo para login")
            else:
                print("⚠️ Aún hay residuos")
                
        except Exception as e:
            print(f"❌ Error durante limpieza: {e}")
            db.session.rollback()

if __name__ == "__main__":
    force_clean_all_sessions()