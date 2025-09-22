#!/usr/bin/env python3
"""
TEST LOGIN COMPLETO - SIMULA EL FLUJO DEL FRONTEND
"""
import requests
import json

def test_login_flow():
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 TESTANDO FLUJO COMPLETO DE LOGIN...")
    
    # Test 1: Login con mozo1
    print("\n1️⃣ Probando login de mozo1...")
    login_data = {
        "username": "mozo1",
        "password": "mozo1pass"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login exitoso")
            print(f"Usuario: {data['user']['username']}")
            print(f"Rol: {data['user']['role']}")
            print(f"Token: {data['access_token'][:20]}...")
            
            # Test 2: Verificar ruta /mozo/
            print("\n2️⃣ Probando acceso a /mozo/...")
            try:
                mozo_response = requests.get(f"{base_url}/mozo/")
                print(f"Status Code /mozo/: {mozo_response.status_code}")
                if mozo_response.status_code == 200:
                    print("✅ Ruta /mozo/ responde correctamente")
                else:
                    print(f"❌ Ruta /mozo/ falló: {mozo_response.text[:200]}...")
            except Exception as e:
                print(f"❌ Error accediendo a /mozo/: {e}")
            
        else:
            print(f"❌ Login falló")
            try:
                error_data = response.json()
                print(f"Error: {error_data.get('message', 'Sin mensaje')}")
            except:
                print(f"Error sin JSON: {response.text}")
    
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Test 3: Admin para comparar
    print("\n3️⃣ Probando login de admin (para comparar)...")
    admin_data = {
        "username": "admin",
        "password": "admin2025"
    }
    
    try:
        admin_response = requests.post(
            f"{base_url}/api/auth/login",
            json=admin_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code Admin: {admin_response.status_code}")
        if admin_response.status_code == 200:
            admin_data = admin_response.json()
            print(f"✅ Admin login exitoso")
            print(f"Usuario: {admin_data['user']['username']}")
            print(f"Rol: {admin_data['user']['role']}")
        else:
            print(f"❌ Admin login falló")
    
    except Exception as e:
        print(f"❌ Error admin: {e}")

if __name__ == '__main__':
    test_login_flow()