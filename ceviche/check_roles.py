#!/usr/bin/env python3
"""
VERIFICAR ROLES EN LA BD
"""
from app import create_app
from models import User

def check_roles():
    app = create_app('mysql')
    with app.app_context():
        users = User.query.all()
        print("ROLES EN BD:")
        for u in users:
            print(f'{u.username}: {u.role}')

if __name__ == '__main__':
    check_roles()