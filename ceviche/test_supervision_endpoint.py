#!/usr/bin/env python
"""
Script para probar el endpoint de supervisión con autenticación
"""
import requests
import json

def test_supervision_endpoint():
    base_url = "http://127.0.0.1:5000"
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    print("🔐 Intentando login como admin...")
    
    # Primero hacer login como admin
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    login_response = session.post(f"{base_url}/login", data=login_data)
    
    if login_response.status_code == 200:
        print("✅ Login exitoso como admin")
        
        # Ahora probar el endpoint de supervisión
        print("\n📊 Probando endpoint de supervisión...")
        
        status_response = session.get(f"{base_url}/admin/api/real-time-status")
        
        print(f"Status Code: {status_response.status_code}")
        
        if status_response.status_code == 200:
            data = status_response.json()
            print("✅ Endpoint funcionando correctamente!")
            print(f"📈 Datos recibidos:")
            print(f"  - Usuarios activos: {data.get('usuarios_activos', 'N/A')}")
            print(f"  - Mesas ocupadas: {data.get('mesas_ocupadas', 'N/A')}")
            print(f"  - Pedidos pendientes: {data.get('pedidos_pendientes', 'N/A')}")
            print(f"  - Ventas del día: S/. {data.get('ventas_dia', 0):.2f}")
            print(f"  - Número de mesas en detalle: {len(data.get('mesas_detalle', []))}")
            
            # Mostrar algunos detalles de mesas si existen
            if data.get('mesas_detalle'):
                print(f"\n🪑 Primeras 3 mesas:")
                for i, mesa in enumerate(data['mesas_detalle'][:3]):
                    print(f"  Mesa {mesa['numero']}: {mesa['estado']} - {mesa['zona']} - {mesa['tiempo_ocupada']}")
            
        else:
            print(f"❌ Error {status_response.status_code}: {status_response.text}")
    
    else:
        print(f"❌ Error en login: {login_response.status_code}")
        print(f"Response: {login_response.text[:200]}")

if __name__ == "__main__":
    test_supervision_endpoint()