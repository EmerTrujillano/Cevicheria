#!/usr/bin/env python3
"""
VERIFICAR ROLES EN BASE DE DATOS
"""
from app import create_app
from models import User

def check_roles():
    app = create_app('mysql')
    with app.app_context():
        users = User.query.all()
        print("=== ROLES EN BASE DE DATOS ===")
        for u in users:
            print(f'{u.username:10} -> {u.role}')
        
        print("\n=== ROLES ÚNICOS ===")
        roles = set([u.role for u in users])
        for role in sorted(roles):
            print(f"'{role}'")

if __name__ == '__main__':
    check_roles()