#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para probar las URLs del admin y verificar que respondan correctamente
"""

import requests
import json
from datetime import datetime

def test_admin_endpoints():
    """Probar endpoints del admin de manera simple"""
    base_url = "http://127.0.0.1:5000"
    
    # Crear sesión con cookies
    session = requests.Session()
    
    print("🔧 PRUEBA SIMPLE DE ENDPOINTS DEL ADMIN")
    print("=" * 50)
    
    # Lista de endpoints a probar
    endpoints = [
        ("GET", "/admin/", "Dashboard Principal"),
        ("GET", "/admin/supervision", "Página de Supervisión"),
        ("GET", "/admin/menu-management", "Gestión de Menú"),
        ("GET", "/admin/status", "Estado Admin"),
        ("GET", "/admin/api/real-time-status", "API Estado Tiempo Real"),
        ("GET", "/admin/api/categorias", "API Categorías"),
        ("GET", "/admin/api/productos", "API Productos"),
        ("GET", "/admin/api/mesas-status", "API Estado Mesas"),
        ("GET", "/admin/api/actividad-reciente", "API Actividad Reciente")
    ]
    
    results = []
    
    for method, endpoint, description in endpoints:
        try:
            url = base_url + endpoint
            response = session.get(url, timeout=10)
            
            status = response.status_code
            if status == 200:
                print(f"✅ {description}: {status} OK")
                results.append((description, True, status))
            elif status == 302:
                print(f"🔄 {description}: {status} Redirect (posiblemente requiere login)")
                results.append((description, True, status))
            elif status == 401:
                print(f"🔐 {description}: {status} No autorizado (normal sin login)")
                results.append((description, True, status))
            else:
                print(f"❌ {description}: {status} Error")
                results.append((description, False, status))
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {description}: Conexión rechazada - servidor no disponible")
            results.append((description, False, "CONNECTION_ERROR"))
        except Exception as e:
            print(f"❌ {description}: Excepción - {str(e)}")
            results.append((description, False, "EXCEPTION"))
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN")
    print("=" * 50)
    
    ok_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)
    
    print(f"Endpoints funcionando: {ok_count}/{total_count}")
    
    if ok_count == total_count:
        print("🎉 ¡Todos los endpoints responden correctamente!")
        print("\n💡 NOTA: Algunos endpoints requieren login (redirects 302 o 401 son normales)")
        return True
    else:
        print("⚠️ Algunos endpoints tienen problemas")
        return False

def main():
    print(f"Ejecutando pruebas en: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    success = test_admin_endpoints()
    
    if success:
        print("\n✅ Las rutas del admin están funcionando correctamente")
    else:
        print("\n❌ Hay problemas con las rutas del admin")

if __name__ == "__main__":
    main()