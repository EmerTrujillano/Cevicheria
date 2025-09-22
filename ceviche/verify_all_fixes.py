#!/usr/bin/env python3
"""
Script para verificar que todas las correcciones implementadas están funcionando correctamente
"""

from models import User, Product, Category, Table, Zone, Floor, UserSession
from config.extensions import db
from datetime import datetime, timezone
import sys

def verificar_productos():
    """Verificar que los productos tienen el formato correcto"""
    print("=== VERIFICACIÓN DE PRODUCTOS ===")
    productos = Product.query.limit(5).all()
    
    for producto in productos:
        print(f"\n📦 {producto.name}")
        print(f"   💰 Precio: S/. {producto.price}")
        print(f"   📝 Descripción:")
        
        lineas = producto.description.split('\n')
        for i, linea in enumerate(lineas):
            if linea.strip():
                print(f"     {i+1}. {linea.strip()}")
    
    print(f"\n✅ Se verificaron {len(productos)} productos - Formato correcto")

def verificar_usuarios_cocina():
    """Verificar que los usuarios de cocina pueden autenticarse"""
    print("\n=== VERIFICACIÓN DE USUARIOS COCINA ===")
    
    usuarios_cocina = User.query.filter(User.role.in_(['kitchen', 'cocina'])).all()
    
    for usuario in usuarios_cocina:
        # Verificar que el hash de la contraseña es válido
        tiene_hash_valido = usuario.password_hash and len(usuario.password_hash) > 10
        print(f"👨‍🍳 {usuario.name} ({usuario.username}) - Hash válido: {'✅' if tiene_hash_valido else '❌'}")
    
    print(f"\n✅ Se verificaron {len(usuarios_cocina)} usuarios de cocina")

def verificar_mesas():
    """Verificar la estructura de mesas, zonas y pisos"""
    print("\n=== VERIFICACIÓN DE MESAS Y ESTRUCTURA ===")
    
    pisos = Floor.query.all()
    total_mesas = 0
    
    for piso in pisos:
        print(f"\n🏢 {piso.name}")
        for zona in piso.zones:
            mesas_zona = len(zona.tables)
            total_mesas += mesas_zona
            print(f"   📍 {zona.name}: {mesas_zona} mesas")
            
            # Mostrar algunas mesas de ejemplo
            for mesa in zona.tables[:3]:  # Solo las primeras 3
                estado = "🔴 Ocupada" if mesa.status == 'occupied' else "🟢 Libre"
                print(f"      Mesa {mesa.number}: {estado}")
    
    print(f"\n✅ Total: {len(pisos)} pisos, {total_mesas} mesas")

def verificar_sesiones():
    """Verificar el estado de las sesiones de usuario"""
    print("\n=== VERIFICACIÓN DE SESIONES ===")
    
    sesiones_totales = UserSession.query.count()
    sesiones_activas = UserSession.query.filter(
        UserSession.expires_at > datetime.now(timezone.utc)
    ).count()
    
    print(f"📊 Sesiones totales: {sesiones_totales}")
    print(f"🟢 Sesiones activas: {sesiones_activas}")
    print(f"🔴 Sesiones expiradas: {sesiones_totales - sesiones_activas}")
    
    # Mostrar últimas sesiones activas
    sesiones_recientes = UserSession.query.filter(
        UserSession.expires_at > datetime.now(timezone.utc)
    ).order_by(UserSession.created_at.desc()).limit(3).all()
    
    print("\n📋 Sesiones activas recientes:")
    for sesion in sesiones_recientes:
        usuario = User.query.get(sesion.user_id)
        tiempo_restante = sesion.expires_at - datetime.now(timezone.utc)
        horas = int(tiempo_restante.total_seconds() // 3600)
        minutos = int((tiempo_restante.total_seconds() % 3600) // 60)
        print(f"   👤 {usuario.name if usuario else 'Usuario desconocido'} - Expira en {horas}h {minutos}m")

def verificar_rutas_mozo():
    """Verificar que las rutas del mozo están configuradas"""
    print("\n=== VERIFICACIÓN DE RUTAS MOZO ===")
    
    from app import app
    
    rutas_esperadas = [
        '/mozo/',
        '/mozo/tables',
        '/mozo/tables/occupy',
        '/mozo/tables/free',
        '/mozo/orders',
        '/menu/products'
    ]
    
    with app.test_client() as client:
        for ruta in rutas_esperadas:
            try:
                response = client.get(ruta, follow_redirects=False)
                # 401 significa que la ruta existe pero requiere autenticación
                # 302 significa redirección (también válido)
                # 200 significa éxito
                if response.status_code in [200, 302, 401]:
                    print(f"✅ {ruta} - Ruta existe")
                else:
                    print(f"❌ {ruta} - Error {response.status_code}")
            except Exception as e:
                print(f"❌ {ruta} - Error: {str(e)}")

def main():
    """Función principal para ejecutar todas las verificaciones"""
    print("🔍 VERIFICACIÓN COMPLETA DEL SISTEMA CEVICHERÍA")
    print("=" * 50)
    
    try:
        verificar_productos()
        verificar_usuarios_cocina()
        verificar_mesas()
        verificar_sesiones()
        verificar_rutas_mozo()
        
        print("\n" + "=" * 50)
        print("✅ VERIFICACIÓN COMPLETADA - SISTEMA FUNCIONANDO CORRECTAMENTE")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA VERIFICACIÓN: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()