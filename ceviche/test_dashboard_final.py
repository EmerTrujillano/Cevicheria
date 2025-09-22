#!/usr/bin/env python3
"""
Prueba final - verificar que el dashboard muestre los datos correctos
"""

import requests
import json

def test_final():
    base_url = "http://192.168.0.5:5000"  # Usar la IP que está en el log
    
    print("=" * 70)
    print("🎯 PRUEBA FINAL DEL DASHBOARD DEL MOZO")
    print("=" * 70)
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    # 1. Hacer login forzado
    print("\n🔐 STEP 1: Login como mozo1")
    login_data = {
        "username": "mozo1",
        "password": "mozo1pass",
        "force_new": True
    }
    
    try:
        # Primero intentar login normal
        response = session.post(f"{base_url}/api/auth/login", json=login_data)
        
        if response.status_code == 401:
            # Forzar cierre de sesiones remotas
            print("⚠️ Sesión activa detectada, cerrando sesiones remotas...")
            response = session.post(f"{base_url}/api/auth/close-remote-sessions", json=login_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Login exitoso como {result['user']['username']}")
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(f"Respuesta: {response.text[:200]}")
            return
            
    except Exception as e:
        print(f"❌ Error de conexión en login: {e}")
        return
    
    # 2. Probar endpoint de mesas
    print("\n📋 STEP 2: Obteniendo datos de mesas para contadores")
    try:
        headers = {'Accept': 'application/json'}
        response = session.get(f"{base_url}/mozo/tables", headers=headers)
        
        if response.status_code == 200:
            mesas = response.json()
            
            if isinstance(mesas, list):
                libres = sum(1 for mesa in mesas if mesa.get('status') == 'available' or mesa.get('available') == True)
                ocupadas = len(mesas) - libres
                
                print(f"✅ Datos de mesas obtenidos:")
                print(f"   📊 Total de mesas: {len(mesas)}")
                print(f"   🟢 Mesas libres: {libres}")
                print(f"   🔴 Mesas ocupadas: {ocupadas}")
                print(f"   📍 Distribución por zonas:")
                
                zonas = {}
                for mesa in mesas:
                    zona = mesa.get('zone_name', 'Sin zona')
                    if zona not in zonas:
                        zonas[zona] = {'libres': 0, 'ocupadas': 0}
                    
                    if mesa.get('status') == 'available' or mesa.get('available') == True:
                        zonas[zona]['libres'] += 1
                    else:
                        zonas[zona]['ocupadas'] += 1
                
                for zona, datos in zonas.items():
                    print(f"     • {zona}: {datos['libres']} libres, {datos['ocupadas']} ocupadas")
                    
            else:
                print(f"⚠️ Formato inesperado de mesas: {type(mesas)}")
                
        else:
            print(f"❌ Error obteniendo mesas: {response.status_code}")
            print(f"Respuesta: {response.text[:300]}")
            
    except Exception as e:
        print(f"❌ Error de conexión en mesas: {e}")
    
    # 3. Probar endpoint de menú
    print("\n🍽️ STEP 3: Obteniendo datos del menú para mostrar platos")
    try:
        headers = {'Accept': 'application/json'}
        response = session.get(f"{base_url}/mozo/menu", headers=headers)
        
        if response.status_code == 200:
            menu = response.json()
            
            print(f"✅ Datos del menú obtenidos:")
            
            if 'categories' in menu:
                categorias = menu['categories']
                total_productos = 0
                
                print(f"   📂 Total de categorías: {len(categorias)}")
                
                for categoria in categorias:
                    productos = categoria.get('products', [])
                    total_productos += len(productos)
                    print(f"     📂 {categoria.get('name', 'Sin nombre')}: {len(productos)} productos")
                    
                    # Mostrar algunos productos de ejemplo
                    if productos:
                        print(f"        Ejemplos:")
                        for producto in productos[:3]:
                            precio = producto.get('price', 0)
                            print(f"         • {producto.get('name', 'Sin nombre')} - S/. {precio:.2f}")
                        if len(productos) > 3:
                            print(f"         ... y {len(productos) - 3} más")
                    print()
                
                print(f"   🍽️ Total de productos disponibles: {total_productos}")
                
            else:
                print(f"⚠️ Formato inesperado de menú:")
                print(f"   Claves disponibles: {list(menu.keys()) if isinstance(menu, dict) else 'No es dict'}")
                
        else:
            print(f"❌ Error obteniendo menú: {response.status_code}")
            print(f"Respuesta: {response.text[:300]}")
            
    except Exception as e:
        print(f"❌ Error de conexión en menú: {e}")
    
    print("\n" + "=" * 70)
    print("🎯 RESUMEN DE LA PRUEBA")
    print("=" * 70)
    print("✅ Si todo funcionó correctamente, el dashboard debería mostrar:")
    print("   📊 Números correctos en 'Libres' y 'Ocupadas'")
    print("   🍽️ Todos los platos del menú organizados por categorías")
    print("   🔄 Actualización automática de datos")
    print("\n💻 Accede a: http://192.168.0.5:5000/mozo/")
    print("=" * 70)

if __name__ == "__main__":
    test_final()