#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar todas las funcionalidades del dashboard de admin
"""

import requests
import json
import time
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:5000"
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin2025"
}

class AdminTester:
    def __init__(self):
        self.session = requests.Session()
        self.logged_in = False
        
    def log(self, message, level="INFO"):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def login_admin(self):
        """Hacer login como admin"""
        self.log("Intentando login como admin...")
        
        try:
            # Primero obtener la página de login
            response = self.session.get(f"{BASE_URL}/login")
            if response.status_code != 200:
                self.log(f"Error al acceder a página de login: {response.status_code}", "ERROR")
                return False
            
            # Hacer login
            login_data = {
                "username": ADMIN_CREDENTIALS["username"],
                "password": ADMIN_CREDENTIALS["password"]
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.logged_in = True
                    self.log("✅ Login exitoso como admin")
                    return True
                else:
                    self.log(f"❌ Error en login: {result.get('message')}", "ERROR")
                    return False
            else:
                self.log(f"❌ Error HTTP en login: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Excepción en login: {str(e)}", "ERROR")
            return False
    
    def test_admin_dashboard(self):
        """Probar acceso al dashboard principal"""
        self.log("Probando dashboard principal...")
        
        try:
            response = self.session.get(f"{BASE_URL}/admin/")
            if response.status_code == 200:
                self.log("✅ Dashboard principal accesible")
                return True
            else:
                self.log(f"❌ Error en dashboard: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Excepción en dashboard: {str(e)}", "ERROR")
            return False
    
    def test_supervision_page(self):
        """Probar página de supervisión"""
        self.log("Probando página de supervisión...")
        
        try:
            response = self.session.get(f"{BASE_URL}/admin/supervision")
            if response.status_code == 200:
                self.log("✅ Página de supervisión accesible")
                return True
            else:
                self.log(f"❌ Error en supervisión: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Excepción en supervisión: {str(e)}", "ERROR")
            return False
    
    def test_menu_management_page(self):
        """Probar página de gestión de menú"""
        self.log("Probando página de gestión de menú...")
        
        try:
            response = self.session.get(f"{BASE_URL}/admin/menu-management")
            if response.status_code == 200:
                self.log("✅ Página de gestión de menú accesible")
                return True
            else:
                self.log(f"❌ Error en gestión de menú: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Excepción en gestión de menú: {str(e)}", "ERROR")
            return False
    
    def test_api_real_time_status(self):
        """Probar API de estado en tiempo real"""
        self.log("Probando API de estado en tiempo real...")
        
        try:
            response = self.session.get(f"{BASE_URL}/admin/api/real-time-status")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log("✅ API de estado en tiempo real funcionando")
                    self.log(f"   - Usuarios activos: {data.get('usuarios_activos', 'N/A')}")
                    self.log(f"   - Mesas ocupadas: {data.get('mesas_ocupadas', 'N/A')}")
                    self.log(f"   - Pedidos pendientes: {data.get('pedidos_pendientes', 'N/A')}")
                    return True
                else:
                    self.log(f"❌ API devolvió error: {data.get('message')}", "ERROR")
                    return False
            else:
                self.log(f"❌ Error HTTP en API: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Excepción en API: {str(e)}", "ERROR")
            return False
    
    def test_api_active_sessions(self):
        """Probar API de sesiones activas"""
        self.log("Probando API de sesiones activas...")
        
        try:
            response = self.session.get(f"{BASE_URL}/admin/api/active-sessions")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log("✅ API de sesiones activas funcionando")
                    self.log(f"   - Total de sesiones: {data.get('total', 'N/A')}")
                    return True
                else:
                    self.log(f"❌ API devolvió error: {data.get('message')}", "ERROR")
                    return False
            else:
                self.log(f"❌ Error HTTP en API: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Excepción en API: {str(e)}", "ERROR")
            return False
    
    def test_api_categorias(self):
        """Probar API de categorías"""
        self.log("Probando API de categorías...")
        
        try:
            response = self.session.get(f"{BASE_URL}/admin/api/categorias")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    categorias = data.get('categorias', [])
                    self.log("✅ API de categorías funcionando")
                    self.log(f"   - Total de categorías: {len(categorias)}")
                    return True
                else:
                    self.log(f"❌ API devolvió error: {data.get('message')}", "ERROR")
                    return False
            else:
                self.log(f"❌ Error HTTP en API: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Excepción en API: {str(e)}", "ERROR")
            return False
    
    def test_api_productos(self):
        """Probar API de productos"""
        self.log("Probando API de productos...")
        
        try:
            response = self.session.get(f"{BASE_URL}/admin/api/productos")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    productos = data.get('productos', [])
                    self.log("✅ API de productos funcionando")
                    self.log(f"   - Total de productos: {len(productos)}")
                    return True
                else:
                    self.log(f"❌ API devolvió error: {data.get('message')}", "ERROR")
                    return False
            else:
                self.log(f"❌ Error HTTP en API: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Excepción en API: {str(e)}", "ERROR")
            return False
    
    def test_admin_status(self):
        """Probar ruta de estado admin"""
        self.log("Probando ruta de estado admin...")
        
        try:
            response = self.session.get(f"{BASE_URL}/admin/status")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.log("✅ Ruta de estado admin funcionando")
                    stats = data.get('stats', {})
                    self.log(f"   - Total usuarios: {stats.get('total_users', 'N/A')}")
                    self.log(f"   - Sesiones activas: {stats.get('active_sessions', 'N/A')}")
                    return True
                else:
                    self.log(f"❌ API devolvió error: {data.get('message')}", "ERROR")
                    return False
            else:
                self.log(f"❌ Error HTTP en estado: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Excepción en estado: {str(e)}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        self.log("🚀 Iniciando pruebas del dashboard de admin")
        self.log("=" * 50)
        
        tests = [
            ("Login Admin", self.login_admin),
            ("Dashboard Principal", self.test_admin_dashboard),
            ("Página Supervisión", self.test_supervision_page),
            ("Página Gestión Menú", self.test_menu_management_page),
            ("API Estado Tiempo Real", self.test_api_real_time_status),
            ("API Sesiones Activas", self.test_api_active_sessions),
            ("API Categorías", self.test_api_categorias),
            ("API Productos", self.test_api_productos),
            ("Estado Admin", self.test_admin_status)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            self.log(f"\n--- Ejecutando: {test_name} ---")
            try:
                result = test_func()
                results.append((test_name, result))
                
                if not result and test_name == "Login Admin":
                    self.log("❌ Login falló, no se pueden ejecutar más pruebas", "ERROR")
                    break
                    
            except Exception as e:
                self.log(f"❌ Error inesperado en {test_name}: {str(e)}", "ERROR")
                results.append((test_name, False))
        
        # Resumen final
        self.log("\n" + "=" * 50)
        self.log("📊 RESUMEN DE PRUEBAS")
        self.log("=" * 50)
        
        passed = 0
        failed = 0
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{status} - {test_name}")
            if result:
                passed += 1
            else:
                failed += 1
        
        self.log(f"\nResultado final: {passed} exitosas, {failed} fallidas")
        
        if failed == 0:
            self.log("🎉 ¡Todas las pruebas pasaron! El dashboard de admin está funcionando correctamente.")
        else:
            self.log(f"⚠️  {failed} pruebas fallaron. Revisa los errores arriba.")
        
        return failed == 0

def main():
    """Función principal"""
    print("🔧 PRUEBAS DEL DASHBOARD DE ADMIN - SISTEMA CEVICHERÍA")
    print("=" * 60)
    
    tester = AdminTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 ¡Sistema admin completamente funcional!")
        exit(0)
    else:
        print("\n❌ Hay problemas que requieren atención.")
        exit(1)

if __name__ == "__main__":
    main()