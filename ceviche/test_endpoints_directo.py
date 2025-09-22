#!/usr/bin/env python3
"""
Prueba rápida y directa de endpoints sin problemas de sesión
"""

import requests
import json
from pprint import pprint

def test_directo():
    base_url = "http://127.0.0.1:5000"
    
    print("=" * 60)
    print("🧪 PRUEBA DIRECTA DE ENDPOINTS")
    print("=" * 60)
    
    # Probar endpoint de mesas con headers JSON
    print("\n📋 Probando endpoint de mesas:")
    try:
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Test Script'
        }
        
        response = requests.get(f"{base_url}/mozo/tables", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"✅ Mesas obtenidas: {len(data)}")
                    if len(data) > 0:
                        mesa_ejemplo = data[0]
                        print(f"   Ejemplo: Mesa {mesa_ejemplo.get('number')} - {mesa_ejemplo.get('status')}")
                else:
                    print(f"⚠️ Formato inesperado: {type(data)}")
            except:
                print("❌ Respuesta no es JSON válido")
                print(f"   Contenido: {response.text[:200]}")
        else:
            print(f"❌ Error {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # Probar endpoint de menú con headers JSON
    print("\n🍽️ Probando endpoint de menú:")
    try:
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Test Script'
        }
        
        response = requests.get(f"{base_url}/mozo/menu", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Menú obtenido")
                print(f"   Estructura: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                
                if 'categories' in data:
                    categorias = data['categories']
                    print(f"   Categorías: {len(categorias)}")
                    for cat in categorias[:3]:
                        print(f"     • {cat.get('name')}: {len(cat.get('products', []))} productos")
                        
            except:
                print("❌ Respuesta no es JSON válido")
                print(f"   Contenido: {response.text[:200]}")
        else:
            print(f"❌ Error {response.status_code}")
            print(f"   Respuesta: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 RESUMEN DE PRUEBAS")
    print("=" * 60)

if __name__ == "__main__":
    test_directo()