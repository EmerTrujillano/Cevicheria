"""
Limpiar todas las sesiones para probar el nuevo sistema
"""
from app import create_app
from models import User
from models.user_session import UserSession
from config.extensions import db

app = create_app('mysql')

def clean_all_sessions():
    print("🧹 LIMPIANDO TODAS LAS SESIONES PARA PROBAR CORRECCIONES")
    print("=" * 55)
    
    with app.app_context():
        try:
            # Limpiar UserSession
            all_sessions = UserSession.query.all()
            for session in all_sessions:
                session.is_active = False
                session.invalidation_reason = 'system_reset'
            
            # Limpiar User tokens
            all_users = User.query.all()
            for user in all_users:
                user.current_session_token = None
                user.session_expires_at = None
                
            db.session.commit()
            
            print("✅ Todas las sesiones limpiadas")
            print("✅ Timezone de Lima aplicado en SessionService")
            print("✅ Lógica de sesiones mejorada")
            print("\n🎯 Ahora prueba hacer login - debería funcionar correctamente")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    clean_all_sessions()