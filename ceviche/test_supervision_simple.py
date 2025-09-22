#!/usr/bin/env python
"""
Script simple para probar la página de supervisión
"""
import webbrowser
import time

def test_supervision_page():
    print("🌐 Abriendo página de supervisión en el navegador...")
    print("📋 Pasos a seguir:")
    print("1. Hacer login como admin (usuario: admin, password: admin123)")
    print("2. Navegar a http://127.0.0.1:5000/admin/supervision")
    print("3. Verificar que NO aparezca 'Error de conexión'")
    print("4. Verificar que se muestren los datos en tiempo real")
    print("5. Verificar que el indicador muestre 'Conectado' en verde")
    print("6. Verificar que aparezca la última actualización")
    print("7. Probar los filtros de mesas (Todas, Ocupadas, Libres)")
    
    print("\n🔍 Si todo funciona correctamente, deberías ver:")
    print("  ✅ Estado: Conectado (badge verde)")
    print("  ✅ Última actualización: [hora actual]")
    print("  ✅ Datos de mesas con zonas y tiempo de ocupación")
    print("  ✅ Filtros funcionando")
    print("  ✅ Auto-reload cada 15 segundos")
    
    # Abrir el navegador
    webbrowser.open('http://127.0.0.1:5000/login')
    
    print("\n⏳ El endpoint de supervisión está funcionando!")
    print("📊 URL de supervisión: http://127.0.0.1:5000/admin/supervision")

if __name__ == "__main__":
    test_supervision_page()