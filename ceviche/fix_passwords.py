from app import create_app
from config.extensions import db, bcrypt
from models import User

def fix_passwords():
    app = create_app('development')
    
    with app.app_context():
        print("Actualizando contraseñas de usuarios existentes...")
        
        # Actualizar contraseñas de usuarios existentes
        users_to_update = [
            {'username': 'admin', 'password': 'admin123'},
            {'username': 'mozo1', 'password': 'mozo123'},
            {'username': 'kitchen1', 'password': 'kitchen123'},
            {'username': 'cashier1', 'password': 'cashier123'},
        ]
        
        for user_data in users_to_update:
            user = User.query.filter_by(username=user_data['username']).first()
            if user:
                hashed_password = bcrypt.generate_password_hash(user_data['password']).decode('utf-8')
                user.password = hashed_password
                print(f"Contraseña actualizada para: {user_data['username']}")
            else:
                # Si no existe, crear el usuario
                hashed_password = bcrypt.generate_password_hash(user_data['password']).decode('utf-8')
                role = 'admin' if user_data['username'] == 'admin' else \
                       'waiter' if 'mozo' in user_data['username'] else \
                       'kitchen' if 'kitchen' in user_data['username'] else 'cashier'
                
                new_user = User(
                    username=user_data['username'],
                    password=hashed_password,
                    role=role
                )
                db.session.add(new_user)
                print(f"Usuario creado: {user_data['username']} - {role}")
        
        db.session.commit()
        print("✅ Contraseñas actualizadas exitosamente!")
        
        # Verificar usuarios
        all_users = User.query.all()
        print(f"\nUsuarios en la base de datos:")
        for user in all_users:
            print(f"- {user.username} ({user.role})")

if __name__ == '__main__':
    fix_passwords()