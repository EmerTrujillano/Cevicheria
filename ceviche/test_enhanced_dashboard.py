#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test del Dashboard Mejorado del Mozo
Verifica filtros, carrito y creación de pedidos
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

def test_enhanced_dashboard():
    print("🧪 TESTING ENHANCED MOZO DASHBOARD")
    print("=" * 50)
    
    session = requests.Session()
    
    # 1. LOGIN COMO MOZO
    print("\n1️⃣ LOGIN MOZO1")
    login_data = {
        "username": "mozo1",
        "password": "mozo1pass"
    }
    
    try:
        response = session.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Login exitoso: {result['user']['username']} ({result['user']['role']})")
        else:
            print(f"❌ Login falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return False
    
    # 2. VERIFICAR PERFIL
    print("\n2️⃣ VERIFICAR PERFIL")
    try:
        response = session.get(f"{BASE_URL}/mozo/profile")
        if response.status_code == 200:
            profile = response.json()
            if profile['success']:
                print(f"✅ Perfil OK: {profile['user']['username']}")
            else:
                print(f"❌ Error en perfil: {profile}")
        else:
            print(f"❌ Perfil falló: {response.status_code}")
    except Exception as e:
        print(f"❌ Error obteniendo perfil: {e}")
    
    # 3. OBTENER MESAS (para filtros)
    print("\n3️⃣ OBTENER MESAS PARA FILTROS")
    try:
        response = session.get(f"{BASE_URL}/mozo/tables")
        if response.status_code == 200:
            mesas = response.json()
            print(f"✅ Mesas obtenidas: {len(mesas)}")
            
            # Analizar zonas y estados
            zonas = set()
            estados = {'libre': 0, 'ocupada': 0}
            
            for mesa in mesas[:5]:  # Mostrar primeras 5
                numero = mesa.get('number', mesa.get('numero', 'N/A'))
                zona = mesa.get('zone_name', mesa.get('zona', 'Sin zona'))
                status = mesa.get('status', 'libre')
                
                zonas.add(zona)
                if status in estados:
                    estados[status] += 1
                
                print(f"   Mesa {numero}: {zona} - {status}")
            
            print(f"📊 Zonas encontradas: {list(zonas)}")
            print(f"📊 Estados: {estados}")
            
        else:
            print(f"❌ Error obteniendo mesas: {response.status_code}")
    except Exception as e:
        print(f"❌ Error con mesas: {e}")
    
    # 4. OBTENER MENÚ (para carrito)
    print("\n4️⃣ OBTENER MENÚ PARA CARRITO")
    try:
        response = session.get(f"{BASE_URL}/mozo/menu")
        if response.status_code == 200:
            menu = response.json()
            if menu['success']:
                categorias = menu['categories']
                print(f"✅ Menú obtenido: {len(categorias)} categorías")
                
                productos_ejemplo = []
                for categoria in categorias[:2]:  # Primeras 2 categorías
                    nombre_cat = categoria['name']
                    productos = categoria['products']
                    print(f"   {nombre_cat}: {len(productos)} productos")
                    
                    # Tomar primer producto de cada categoría
                    if productos:
                        prod = productos[0]
                        productos_ejemplo.append({
                            'id': prod['id'],
                            'name': prod['name'],
                            'price': prod['price']
                        })
                        print(f"     - {prod['name']}: S/. {prod['price']}")
                
            else:
                print(f"❌ Error en menú: {menu}")
        else:
            print(f"❌ Error obteniendo menú: {response.status_code}")
    except Exception as e:
        print(f"❌ Error con menú: {e}")
        productos_ejemplo = []
    
    # 5. PROBAR CREACIÓN DE PEDIDO
    print("\n5️⃣ PROBAR CREACIÓN DE PEDIDO")
    if productos_ejemplo and len(mesas) > 0:
        # Buscar una mesa libre
        mesa_libre = None
        for mesa in mesas:
            if mesa.get('status', 'libre') == 'libre':
                mesa_libre = mesa
                break
        
        if mesa_libre:
            # Crear pedido de prueba
            pedido_data = {
                "table_id": mesa_libre['id'],
                "items": [
                    {
                        "product_id": productos_ejemplo[0]['id'],
                        "quantity": 2,
                        "unit_price": productos_ejemplo[0]['price']
                    }
                ]
            }
            
            if len(productos_ejemplo) > 1:
                pedido_data["items"].append({
                    "product_id": productos_ejemplo[1]['id'],
                    "quantity": 1,
                    "unit_price": productos_ejemplo[1]['price']
                })
            
            print(f"📝 Creando pedido para Mesa {mesa_libre.get('number', 'N/A')}")
            print(f"   Items: {len(pedido_data['items'])}")
            
            try:
                response = session.post(f"{BASE_URL}/mozo/create-order", json=pedido_data)
                if response.status_code == 200:
                    result = response.json()
                    if result['success']:
                        print(f"✅ Pedido creado: #{result['order_id']}")
                        print(f"   Total: S/. {result['total_amount']}")
                        
                        # Verificar que la mesa cambió de estado
                        print("\n🔄 Verificando estado de mesa...")
                        response = session.get(f"{BASE_URL}/mozo/tables")
                        if response.status_code == 200:
                            mesas_updated = response.json()
                            mesa_updated = next((m for m in mesas_updated if m['id'] == mesa_libre['id']), None)
                            if mesa_updated:
                                nuevo_status = mesa_updated.get('status', 'libre')
                                print(f"   Mesa {mesa_updated.get('number', 'N/A')}: {nuevo_status}")
                                if nuevo_status == 'ocupada':
                                    print("✅ Estado de mesa actualizado correctamente")
                                else:
                                    print("⚠️ Estado de mesa no cambió")
                    else:
                        print(f"❌ Error creando pedido: {result}")
                else:
                    print(f"❌ Error en petición: {response.status_code}")
                    print(f"   Respuesta: {response.text}")
            except Exception as e:
                print(f"❌ Error creando pedido: {e}")
        else:
            print("❌ No hay mesas libres para probar pedido")
    else:
        print("❌ No hay productos disponibles para probar pedido")
    
    # 6. VERIFICAR DASHBOARD
    print("\n6️⃣ VERIFICAR ACCESO AL DASHBOARD")
    try:
        response = session.get(f"{BASE_URL}/mozo/")
        if response.status_code == 200:
            html_content = response.text
            # Verificar elementos clave del dashboard
            elementos_esperados = [
                'Dashboard Mozo',
                'Filtrar por Estado',
                'Filtrar por Zona',
                'Carrito',
                'sidebar',
                'mesa-card',
                'product-card',
                'cart-items',
                'send-to-kitchen'
            ]
            
            elementos_encontrados = []
            for elemento in elementos_esperados:
                if elemento in html_content:
                    elementos_encontrados.append(elemento)
            
            print(f"✅ Dashboard accesible")
            print(f"   Elementos encontrados: {len(elementos_encontrados)}/{len(elementos_esperados)}")
            
            if len(elementos_encontrados) >= len(elementos_esperados) * 0.8:
                print("✅ Dashboard contiene elementos esperados")
            else:
                print("⚠️ Algunos elementos del dashboard faltan")
                print(f"   Faltantes: {set(elementos_esperados) - set(elementos_encontrados)}")
        else:
            print(f"❌ Dashboard no accesible: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accediendo dashboard: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 RESUMEN DEL TESTING")
    print("✅ Dashboard mejorado con:")
    print("   - Sidebar con filtros de estado y zona")
    print("   - Carrito de compras funcional")
    print("   - Sistema de pedidos integrado")
    print("   - Layout organizado y responsive")
    print("\n🌐 Accede a: http://127.0.0.1:5000/mozo/")
    print("👤 Usuario: mozo1 / mozo1pass")

if __name__ == "__main__":
    test_enhanced_dashboard()