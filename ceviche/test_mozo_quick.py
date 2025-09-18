#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

# Test rápido de los endpoints del mozo
BASE_URL = "http://127.0.0.1:5000"

def test_direct_endpoints():
    """Test directo usando requests con sesión"""
    
    session = requests.Session()
    
    # Hacer login primero
    login_data = {
        "username": "mozo1",
        "password": "mozo1pass"
    }
    
    print("🔐 Haciendo login...")
    response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"   Login status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Login exitoso")
        
        # Test endpoint profile
        print("\n👤 Probando /mozo/profile...")
        response = session.get(f"{BASE_URL}/mozo/profile")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Usuario: {data.get('user', {}).get('username')}")
        else:
            print(f"   ❌ Error: {response.text}")
        
        # Test endpoint tables con headers JSON
        print("\n🪑 Probando /mozo/tables...")
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        response = session.get(f"{BASE_URL}/mozo/tables", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Total mesas: {len(data)}")
            
            # Contar por status
            libres = len([m for m in data if m.get('status') == 'libre'])
            ocupadas = len([m for m in data if m.get('status') == 'ocupada'])
            
            print(f"   📊 Libres: {libres}")
            print(f"   📊 Ocupadas: {ocupadas}")
            
            # Mostrar muestra
            print(f"   🔍 Muestra (3 primeras):")
            for mesa in data[:3]:
                numero = mesa.get('number') or mesa.get('numero')
                zona = mesa.get('zone_name') or mesa.get('zona')
                status = mesa.get('status')
                print(f"      Mesa {numero} - {zona} - {status}")
        else:
            print(f"   ❌ Error: {response.text}")
        
        # Test endpoint menu
        print("\n🍽️ Probando /mozo/menu...")
        response = session.get(f"{BASE_URL}/mozo/menu")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'categories' in data:
                categories = data['categories']
                print(f"   ✅ Categorías: {len(categories)}")
                
                for categoria in categories[:3]:  # Solo primeras 3
                    productos = categoria.get('products', [])
                    print(f"   📂 {categoria.get('name')}: {len(productos)} productos")
            else:
                print(f"   ❌ Formato incorrecto: {list(data.keys())}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    else:
        print(f"   ❌ Login falló: {response.text}")

if __name__ == "__main__":
    print("🧪 TEST RÁPIDO ENDPOINTS MOZO")
    print("=" * 40)
    test_direct_endpoints()
    print("=" * 40)