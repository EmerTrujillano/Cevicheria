#!/usr/bin/env python3
"""
ARREGLAR HASHES DE CONTRASEÑAS DEFECTUOSOS
"""
from app import create_app
from config.extensions import db, bcrypt
from models import User

def fix_password_hashes():
    """Regenerar todos los hashes de contraseñas correctamente"""
    app = create_app('mysql')
    with app.app_context():
        print("🔧 ARREGLANDO HASHES DE CONTRASEÑAS...")
        
        # Contraseñas correctas
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
        
        users_fixed = 0
        for username, password in passwords.items():
            user = User.query.filter_by(username=username).first()
            if user:
                # FORZAR regeneración de hash
                new_hash = bcrypt.generate_password_hash(password).decode('utf-8')
                user.password = new_hash
                users_fixed += 1
                print(f"  🔄 {username}: {password} → hash regenerado")
                
                # Verificar inmediatamente
                try:
                    test_result = bcrypt.check_password_hash(new_hash, password)
                    status = "✅" if test_result else "❌"
                    print(f"    {status} Verificación inmediata")
                except Exception as e:
                    print(f"    ❌ Error verificando: {e}")
            else:
                print(f"  ❌ Usuario no encontrado: {username}")
        
        try:
            db.session.commit()
            print(f"\n✅ {users_fixed} HASHES REGENERADOS Y GUARDADOS")
            
            # Verificación final con contexto fresco
            print("\n🧪 VERIFICACIÓN FINAL:")
            for username, password in passwords.items():
                user = User.query.filter_by(username=username).first()
                if user:
                    try:
                        is_valid = bcrypt.check_password_hash(user.password, password)
                        status = "✅" if is_valid else "❌"
                        print(f"{status} {username}: {password}")
                        if not is_valid:
                            print(f"    Hash actual: {user.password[:50]}...")
                    except Exception as e:
                        print(f"❌ {username}: ERROR - {e}")
            
            return True
                    
        except Exception as e:
            print(f"❌ Error guardando: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    if fix_password_hashes():
        print("\n🚀 HASHES ARREGLADOS - REINICIA EL SERVIDOR")
    else:
        print("\n💥 ERROR AL ARREGLAR HASHES")