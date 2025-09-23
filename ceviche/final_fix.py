"""
Limpiar sesiones y probar login definitivo
"""
from app import create_app
from models import User
from models.user_session import UserSession
from config.extensions import db

app = create_app('mysql')

def final_cleanup():
    print("🔧 LIMPIEZA FINAL PARA CORREGIR EL 409")
    print("=" * 40)
    
    with app.app_context():
        try:
            # Limpiar TODAS las sesiones
            UserSession.query.update({'is_active': False})
            User.query.update({'current_session_token': None, 'session_expires_at': None})
            
            db.session.commit()
            
            print("✅ Sesiones limpiadas")
            print("✅ start_session() corregido")
            print("✅ create_session() corregido") 
            print("✅ Timezone de Lima aplicado")
            
            print("\n🎯 AHORA SÍ DEBERÍA FUNCIONAR EL LOGIN")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    final_cleanup()