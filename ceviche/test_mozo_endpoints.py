#!/usr/bin/env python3
"""
Script para probar los endpoints del mozo con autenticación de sesión
"""

import requests
import json
from pprint import pprint

def test_mozo_endpoints():
    base_url = "http://127.0.0.1:5000"
    
    # Crear una sesión para mantener las cookies
    session = requests.Session()
    
    print("=" * 60)
    print("🧪 PROBANDO ENDPOINTS DEL MOZO CON SESIÓN")
    print("=" * 60)
    
    # 1. Hacer login como mozo2 (para evitar conflictos de sesión)
    print("\n🔐 STEP 1: Login como mozo2")
    login_data = {
        "username": "mozo2",
        "password": "mozo2pass"
    }
    
    try:
        login_response = session.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print(f"✅ Login exitoso!")
            print(f"   Usuario: {login_result['user']['username']}")
            print(f"   Rol: {login_result['user']['role']}")
            print(f"   Cookies de sesión: {session.cookies}")
        elif login_response.status_code == 401:
            # Sesión activa, intentar cerrar sesiones remotas
            print("⚠️ Sesión activa detectada, cerrando sesiones remotas...")
            force_login_data = {
                "username": "mozo2",
                "password": "mozo2pass",
                "force_new": True
            }
            
            force_response = session.post(
                f"{base_url}/api/auth/close-remote-sessions",
                json=force_login_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if force_response.status_code == 200:
                login_result = force_response.json()
                print(f"✅ Login forzado exitoso!")
                print(f"   Usuario: {login_result['user']['username']}")
                print(f"   Rol: {login_result['user']['role']}")
                print(f"   Cookies de sesión: {session.cookies}")
            else:
                print(f"❌ Error en login forzado: {force_response.status_code}")
                print(f"   Respuesta: {force_response.text}")
                return
        else:
            print(f"❌ Error en login: {login_response.status_code}")
            print(f"   Respuesta: {login_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return
    
    # 2. Probar endpoint de mesas
    print("\n📋 STEP 2: Obteniendo mesas")
    try:
        mesas_response = session.get(f"{base_url}/mozo/tables")
        
        if mesas_response.status_code == 200:
            mesas_data = mesas_response.json()
            print(f"✅ Mesas obtenidas exitosamente!")
            print(f"   Total de mesas: {len(mesas_data) if isinstance(mesas_data, list) else 'N/A'}")
            
            if isinstance(mesas_data, list) and len(mesas_data) > 0:
                print(f"   Primeras 5 mesas:")
                for i, mesa in enumerate(mesas_data[:5]):
                    print(f"     Mesa {mesa.get('number', 'N/A')} - Estado: {mesa.get('status', 'N/A')} - Zona: {mesa.get('zone_name', 'N/A')}")
                    
                # Contar mesas disponibles
                mesas_disponibles = sum(1 for mesa in mesas_data if mesa.get('status') == 'available')
                print(f"   🟢 Mesas disponibles: {mesas_disponibles}")
                print(f"   🔴 Mesas ocupadas: {len(mesas_data) - mesas_disponibles}")
            else:
                print(f"   ⚠️ Formato de respuesta inesperado: {type(mesas_data)}")
                
        else:
            print(f"❌ Error obteniendo mesas: {mesas_response.status_code}")
            print(f"   Respuesta: {mesas_response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error conectando a endpoint de mesas: {e}")
    
    # 3. Probar endpoint de menú
    print("\n🍽️ STEP 3: Obteniendo menú")
    try:
        menu_response = session.get(f"{base_url}/mozo/menu")
        
        if menu_response.status_code == 200:
            menu_data = menu_response.json()
            print(f"✅ Menú obtenido exitosamente!")
            
            if isinstance(menu_data, dict) and 'categories' in menu_data:
                categorias = menu_data['categories']
                print(f"   Total de categorías: {len(categorias)}")
                
                total_productos = 0
                for categoria in categorias:
                    productos_count = len(categoria.get('products', []))
                    total_productos += productos_count
                    print(f"     📂 {categoria.get('name', 'N/A')}: {productos_count} productos")
                    
                    # Mostrar algunos productos de ejemplo
                    productos = categoria.get('products', [])
                    if productos:
                        print(f"       Ejemplos:")
                        for producto in productos[:3]:
                            print(f"         • {producto.get('name', 'N/A')} - S/. {producto.get('price', 'N/A')}")
                        if len(productos) > 3:
                            print(f"         ... y {len(productos) - 3} más")
                    print()
                
                print(f"   🍽️ Total de productos en el menú: {total_productos}")
                
            else:
                print(f"   ⚠️ Formato de respuesta inesperado:")
                pprint(menu_data)
                
        else:
            print(f"❌ Error obteniendo menú: {menu_response.status_code}")
            print(f"   Respuesta: {menu_response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error conectando a endpoint de menú: {e}")
    
    # 4. Probar endpoint de perfil
    print("\n👤 STEP 4: Obteniendo perfil")
    try:
        profile_response = session.get(f"{base_url}/mozo/profile")
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            print(f"✅ Perfil obtenido exitosamente!")
            print(f"   Usuario: {profile_data.get('username', 'N/A')}")
            print(f"   Rol: {profile_data.get('role', 'N/A')}")
            print(f"   Email: {profile_data.get('email', 'N/A')}")
            print(f"   Activo: {profile_data.get('is_active', 'N/A')}")
        else:
            print(f"❌ Error obteniendo perfil: {profile_response.status_code}")
            print(f"   Respuesta: {profile_response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Error conectando a endpoint de perfil: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 RESUMEN DE PRUEBAS COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    test_mozo_endpoints()