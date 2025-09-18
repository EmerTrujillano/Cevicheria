"""
Verificar sistema de hasheo y autenticación
"""
from app import create_app
from models import User
from services.auth_service import AuthService
import bcrypt

app = create_app('mysql')

def test_authentication():
    print("🔐 VERIFICANDO SISTEMA DE AUTENTICACIÓN")
    print("=" * 50)
    
    with app.app_context():
        # Lista de usuarios y contraseñas únicas
        test_users = [
            ("admin", "admin2025"),
            ("mozo1", "mozo1pass"),
            ("mozo2", "mozo2pass"),
            ("cocina1", "cocina1pass"),
            ("cajero1", "cajero1pass")
        ]
        
        for username, password in test_users:
            print(f"\n👤 Probando {username}...")
            
            # 1. Verificar que el usuario existe
            user = User.query.filter_by(username=username).first()
            if not user:
                print(f"   ❌ Usuario {username} no existe")
                continue
            
            print(f"   ✅ Usuario encontrado - ID: {user.id}")
            print(f"   📝 Hash guardado: {user.password_hash[:50]}...")
            
            # 2. Verificar hash directo con bcrypt
            try:
                is_valid_bcrypt = bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))
                print(f"   🔍 Verificación bcrypt directa: {is_valid_bcrypt}")
            except Exception as e:
                print(f"   ⚠️ Error en bcrypt directo: {e}")
            
            # 3. Verificar con AuthService
            try:
                auth_user, token, error = AuthService.authenticate_user(username, password)
                if error:
                    print(f"   ❌ AuthService error: {error}")
                else:
                    print(f"   ✅ AuthService exitoso - Token presente: {bool(token)}")
            except Exception as e:
                print(f"   ❌ AuthService excepción: {e}")

if __name__ == "__main__":
    test_authentication()