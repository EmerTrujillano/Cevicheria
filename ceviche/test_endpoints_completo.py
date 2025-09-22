#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

# Test de endpoints del dashboard mozo
BASE_URL = "http://127.0.0.1:5000"

def test_mozo_login():
    """Test login mozo1"""
    login_data = {
        "username": "mozo1",
        "password": "mozo1pass"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"🔐 LOGIN MOZO:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"   ✅ Login exitoso")
            print(f"   Usuario: {data.get('user', {}).get('username')}")
            print(f"   Rol: {data.get('user', {}).get('role')}")
            return token
        else:
            print(f"   ❌ Login falló: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def test_mozo_tables(token):
    """Test endpoint de mesas"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/mozo/tables", headers=headers)
        print(f"\n🪑 ENDPOINT MESAS:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Total mesas: {len(data)}")
            
            # Contar por status
            libres = len([m for m in data if m.get('status') == 'libre'])
            ocupadas = len([m for m in data if m.get('status') == 'ocupada'])
            
            print(f"   📊 Libres: {libres}")
            print(f"   📊 Ocupadas: {ocupadas}")
            
            # Mostrar muestra de mesas
            print(f"   🔍 Muestra (primeras 10):")
            for mesa in data[:10]:
                zona = mesa.get('zone_name', 'Sin zona')
                status = mesa.get('status', 'unknown')
                print(f"      Mesa {mesa.get('number')} - {zona} - {status}")
                
            return True
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_mozo_menu(token):
    """Test endpoint del menú"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/mozo/menu", headers=headers)
        print(f"\n🍽️ ENDPOINT MENÚ:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'categories' in data:
                categories = data['categories']
                print(f"   ✅ Categorías: {len(categories)}")
                
                total_productos = 0
                for categoria in categories:
                    productos = categoria.get('products', [])
                    total_productos += len(productos)
                    print(f"   📂 {categoria.get('name')}: {len(productos)} productos")
                
                print(f"   🍽️ Total productos: {total_productos}")
                
                # Mostrar muestra de productos
                if categories and categories[0].get('products'):
                    print(f"   🔍 Muestra productos ({categories[0].get('name')}):")
                    for producto in categories[0]['products'][:3]:
                        print(f"      {producto.get('name')} - ${producto.get('price')}")
                
                return True
            else:
                print(f"   ❌ Formato incorrecto: {data}")
                return False
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTING ENDPOINTS DASHBOARD MOZO")
    print("=" * 50)
    
    token = test_mozo_login()
    if token:
        test_mozo_tables(token)
        test_mozo_menu(token)
    else:
        print("❌ No se pudo continuar sin token de autenticación")
    
    print("\n" + "=" * 50)