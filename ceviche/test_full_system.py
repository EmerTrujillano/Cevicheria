"""
Diagnóstico completo del sistema de login
"""
import requests
import json

def test_connection():
    print("🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000"
    
    # 1. Probar conexión básica
    print("1️⃣ PROBANDO CONEXIÓN BÁSICA:")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   ✅ GET / - Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ GET / - Error: {e}")
        return False
    
    # 2. Probar página de login
    print("\n2️⃣ PROBANDO PÁGINA DE LOGIN:")
    try:
        response = requests.get(f"{base_url}/login", timeout=5)
        print(f"   ✅ GET /login - Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ GET /login - Error: {e}")
    
    # 3. Probar endpoint de API auth
    print("\n3️⃣ PROBANDO ENDPOINT DE AUTENTICACIÓN:")
    try:
        test_data = {
            "username": "admin",
            "password": "admin2025"
        }
        
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   📡 POST /api/auth/login - Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ LOGIN EXITOSO!")
            data = response.json()
            print(f"   👤 Usuario: {data.get('user', {}).get('username', 'N/A')}")
            print(f"   🔑 Token presente: {'access_token' in data}")
        elif response.status_code == 409:
            print("   ⚠️ CONFLICTO DE SESIÓN (409)")
            print("   📝 Respuesta:", response.json().get('message', 'N/A'))
        elif response.status_code == 401:
            print("   ❌ CREDENCIALES INVÁLIDAS (401)")
            print("   📝 Respuesta:", response.json().get('message', 'N/A'))
        else:
            print(f"   ❓ CÓDIGO INESPERADO: {response.status_code}")
            print(f"   📝 Respuesta: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ ERROR DE CONEXIÓN - El servidor no responde")
        return False
    except requests.exceptions.Timeout:
        print("   ⏰ TIMEOUT - El servidor tarda mucho en responder")
        return False
    except Exception as e:
        print(f"   ❌ ERROR INESPERADO: {e}")
        return False
    
    # 4. Probar otros usuarios
    print("\n4️⃣ PROBANDO OTROS USUARIOS:")
    users_to_test = [
        ("mozo1", "mozo1pass"),
        ("mozo2", "mozo2pass"),
        ("cocina1", "cocina1pass")
    ]
    
    for username, password in users_to_test:
        try:
            test_data = {"username": username, "password": password}
            response = requests.post(
                f"{base_url}/api/auth/login",
                json=test_data,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            print(f"   {username}: Status {response.status_code}")
        except Exception as e:
            print(f"   {username}: Error - {e}")
    
    print("\n📊 DIAGNÓSTICO COMPLETADO")
    return True

if __name__ == "__main__":
    test_connection()