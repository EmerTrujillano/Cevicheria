from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Product, Category, Table, Order, OrderItem, UserSession
from config.extensions import db
from utils.decorators import role_required
from services.session_service import SessionService
from datetime import datetime
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/logout')
def admin_logout():
    """Cerrar sesión del admin y redirigir al login"""
    session.clear()
    return redirect(url_for('main.login_page'))
import uuid
@admin_bp.route('/logout')
def admin_logout():
    """Cerrar sesión del admin y redirigir al login"""
    session.clear()
    return redirect(url_for('main.login_page'))

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def check_admin_auth():
    """Verificar autenticaci├│n de admin usando sesi├│n"""
    if 'user_id' not in session:
        return False
    
    user = User.query.get(session['user_id'])
    if not user or user.role != 'admin':
        return False
    
    return True

@admin_bp.route('/')
def admin_dashboard():
    """Panel principal del administrador"""
    if not check_admin_auth():
        session.clear()
        return redirect('/login')
    return render_template('admin/dashboard_new.html')

@admin_bp.route('/api/dashboard-stats')
def get_dashboard_stats():
    """Obtener estadísticas para el dashboard del admin"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        # Contar mesas ocupadas (simular por ahora ya que Table puede no estar configurado)
        mesas_ocupadas = 2  # TODO: Implementar cuando Table esté configurado
        
        # Contar sesiones activas 
        sesiones_activas = UserSession.query.filter_by(is_active=True).count()
        
        # Contar pedidos pendientes
        pedidos_pendientes = 0
        try:
            pedidos_pendientes = Order.query.filter(
                Order.status.in_(['pendiente', 'preparando', 'en_preparacion'])
            ).count()
        except Exception as e:
            print(f"Error contando pedidos: {e}")
            pedidos_pendientes = 0
        
        # Calcular ventas del día
        ventas_hoy = 0
        try:
            from datetime import datetime
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            orders_today = Order.query.filter(Order.created_at >= today).all()
            ventas_hoy = sum(order.total_amount for order in orders_today if order.total_amount)
        except Exception as e:
            print(f"Error calculando ventas: {e}")
            ventas_hoy = 0
        
        return jsonify({
            'success': True,
            'mesas_ocupadas': mesas_ocupadas,
            'sesiones_activas': sesiones_activas,
            'pedidos_pendientes': pedidos_pendientes,
            'ventas_hoy': float(ventas_hoy)
        })
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        return jsonify({
            'success': True,  # Devolver success=True con datos por defecto
            'mesas_ocupadas': 2,
            'sesiones_activas': UserSession.query.filter_by(is_active=True).count() if UserSession else 0,
            'pedidos_pendientes': 0,
            'ventas_hoy': 0.0
        })

@admin_bp.route('/api/actividad-reciente')
def get_actividad_reciente():
    """Obtener actividad reciente del sistema"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        # Obtener sesiones activas recientes
        sesiones = UserSession.query.filter_by(is_active=True).join(User).limit(10).all()
        
        actividad = []
        for sesion in sesiones:
            actividad.append({
                'usuario': sesion.user.username,
                'accion': 'Sesión activa',
                'timestamp': sesion.last_activity.strftime('%H:%M:%S') if sesion.last_activity else 'N/A',
                'rol': sesion.user.role,
                'tipo': 'success'
            })
        
        return jsonify(actividad)
    except Exception as e:
        print(f"Error obteniendo actividad: {e}")
        return jsonify([])

@admin_bp.route('/api/real-time-status')
def get_real_time_status():
    """Obtener estado en tiempo real del sistema"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        # Obtener sesiones activas con detalles
        active_sessions = UserSession.query.filter_by(is_active=True).join(User).all()
        
        sesiones_activas = []
        usuarios_por_rol = {'admin': 0, 'mozo': 0, 'cocina': 0, 'cajero': 0}
        
        for user_session in active_sessions:
            user = user_session.user
            
            # Calcular tiempo de sesi├│n
            tiempo_sesion = (datetime.utcnow() - user_session.created_at).total_seconds()
            tiempo_str = f"{int(tiempo_sesion // 60)}m"
            
            sesiones_activas.append({
                'usuario_id': user.id,
                'username': user.username,
                'rol': user.role,
                'tiempo_sesion': tiempo_str,
                'ultima_actividad': user_session.last_activity.isoformat() if user_session.last_activity else None,
                'token': user_session.session_token[:12] + '...' if user_session.session_token else None
            })
            
            # Contar por rol
            if user.role in usuarios_por_rol:
                usuarios_por_rol[user.role] += 1
        
        # Mesas ocupadas (simular datos ya que no tenemos model Table activo)
        mesas_ocupadas = 5  # Placeholder
        
        # Pedidos pendientes
        try:
            from models.order import Order
            pedidos_pendientes = Order.query.filter(
                Order.status.in_(['pendiente', 'preparando'])
            ).count()
        except Exception:
            pedidos_pendientes = 0
        
        # Ventas del d├¡a
        ventas_dia = 0
        try:
            pedidos_hoy = Order.query.filter(
                Order.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            ).all()
            ventas_dia = sum(order.total_amount for order in pedidos_hoy if order.total_amount)
        except Exception:
            ventas_dia = 0
        
        return jsonify({
            'success': True,
            'usuarios_activos': len(sesiones_activas),
            'sesiones_activas': sesiones_activas,
            'mesas_ocupadas': mesas_ocupadas,
            'pedidos_pendientes': pedidos_pendientes,
            'ventas_dia': float(ventas_dia),
            'usuarios_por_rol': usuarios_por_rol,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"Error en real-time-status: {e}")
        return jsonify({
            'success': False,
            'message': f'Error obteniendo estado: {str(e)}'
        }), 500

@admin_bp.route('/api/usuarios')
def get_usuarios():
    """Obtener lista de todos los usuarios"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        usuarios = User.query.all()
        usuarios_data = []
        
        for user in usuarios:
            # Buscar ├║ltima sesi├│n
            ultima_sesion = UserSession.query.filter_by(user_id=user.id).order_by(UserSession.created_at.desc()).first()
            
            usuarios_data.append({
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'is_active': bool(UserSession.query.filter_by(user_id=user.id, is_active=True).first()),
                'last_login': ultima_sesion.created_at.strftime('%Y-%m-%d %H:%M') if ultima_sesion else None
            })
        
        return jsonify(usuarios_data)
    except Exception as e:
        print(f"Error obteniendo usuarios: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/api/sesiones-activas')
def get_sesiones_activas():
    """Obtener todas las sesiones activas"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        sesiones = UserSession.query.filter_by(is_active=True).join(User).all()
        
        sesiones_data = []
        for sesion in sesiones:
            sesiones_data.append({
                'id': sesion.id,
                'user_id': sesion.user_id,
                'username': sesion.user.username,
                'role': sesion.user.role,
                'ip_address': sesion.ip_address,
                'created_at': sesion.created_at.isoformat() if sesion.created_at else None,
                'last_activity': sesion.last_activity.isoformat() if sesion.last_activity else None
            })
        
        return jsonify(sesiones_data)
    except Exception as e:
        print(f"Error obteniendo sesiones: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/api/crear-usuario', methods=['POST'])
def crear_usuario():
    """Crear un nuevo usuario"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # Validaciones
        if not username or not password or not role:
            return jsonify({'success': False, 'message': 'Todos los campos son requeridos'})
        
        # Verificar si el usuario ya existe
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'El usuario ya existe'})
        
        # Crear nuevo usuario
        new_user = User(
            username=username,
            role=role,
            estacion=request.form.get('estacion')  # Para usuarios de cocina
        )
        new_user.set_password(password)  # Usar el método del modelo
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Usuario creado exitosamente'})
    
    except Exception as e:
        db.session.rollback()
        print(f"Error creando usuario: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/api/eliminar-usuario/<int:user_id>', methods=['DELETE'])
def eliminar_usuario(user_id):
    """Eliminar un usuario"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        # Buscar el usuario
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'})
        
        # No permitir eliminar el último admin
        if user.role == 'admin':
            admin_count = User.query.filter_by(role='admin').count()
            if admin_count <= 1:
                return jsonify({'success': False, 'message': 'No se puede eliminar el último administrador'})
        
        # Eliminar todas las sesiones del usuario (no solo invalidar)
        # Primero obtener todas las sesiones (activas e inactivas)
        sesiones = UserSession.query.filter_by(user_id=user_id).all()
        print(f"[ADMIN] Eliminando {len(sesiones)} sesiones del usuario {user.username}")
        
        # Eliminar todas las sesiones
        for sesion in sesiones:
            db.session.delete(sesion)
        
        # Hacer commit de la eliminación de sesiones primero
        db.session.commit()
        print(f"[ADMIN] Sesiones eliminadas exitosamente")
        
        # Ahora eliminar el usuario
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        print(f"[ADMIN] Usuario {username} eliminado")
        
        return jsonify({'success': True, 'message': f'Usuario {username} eliminado exitosamente'})
    
    except Exception as e:
        db.session.rollback()
        print(f"Error eliminando usuario: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/api/usuarios/<int:user_id>', methods=['PUT'])
def actualizar_usuario(user_id):
    """Actualizar un usuario existente"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        usuario = User.query.get(user_id)
        if not usuario:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'})
        
        username = request.form.get('username')
        role = request.form.get('role')
        estacion = request.form.get('estacion', '')
        
        # Validaciones
        if not username or not username.strip():
            return jsonify({'success': False, 'message': 'El nombre de usuario es requerido'})
        
        if not role:
            return jsonify({'success': False, 'message': 'El rol es requerido'})
        
        # Verificar si el username ya existe (excepto para el usuario actual)
        existing = User.query.filter_by(username=username.strip()).first()
        if existing and existing.id != user_id:
            return jsonify({'success': False, 'message': 'Ya existe un usuario con ese nombre'})
        
        # Validar estación para cocina
        if role == 'cocina' and not estacion:
            return jsonify({'success': False, 'message': 'La estación es requerida para el rol de cocina'})
        
        # Actualizar usuario
        usuario.username = username.strip()
        usuario.role = role
        usuario.estacion = estacion.strip() if estacion and role == 'cocina' else None
        usuario.last_updated = datetime.utcnow()
        
        db.session.commit()
        
        print(f"[ADMIN] Usuario ID {user_id} ('{username}') actualizado - Rol: {role}")
        
        return jsonify({
            'success': True, 
            'message': f'Usuario "{username}" actualizado exitosamente'
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error actualizando usuario: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/api/force-logout', methods=['POST'])
def force_logout_user():
    """Cerrar la sesión de un usuario específico"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': 'ID de usuario requerido'})
        
        # Invalidar todas las sesiones del usuario
        sesiones = UserSession.query.filter_by(user_id=user_id, is_active=True).all()
        
        for sesion in sesiones:
            sesion.is_active = False
            sesion.logout_time = datetime.utcnow()
        
        db.session.commit()
        
        print(f"[ADMIN] Sesiones del usuario {user_id} cerradas forzadamente")
        
        return jsonify({
            'success': True, 
            'message': f'Se cerraron {len(sesiones)} sesiones del usuario',
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error en logout forzado: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ===============================
# CRUD DE CATEGORÍAS
# ===============================

@admin_bp.route('/api/categorias', methods=['GET'])
def get_categorias():
    """Obtener todas las categorías"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        categorias = Category.query.all()
        categorias_data = []
        
        for categoria in categorias:
            categorias_data.append({
                'id': categoria.id,
                'name': categoria.name,
                'description': categoria.description,
                'estacion': categoria.estacion,
                'created_at': categoria.created_at.isoformat() if categoria.created_at else None,
                'products_count': len(categoria.products)
            })
        
        return jsonify(categorias_data)
    except Exception as e:
        print(f"Error obteniendo categorías: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/api/categorias', methods=['POST'])
def crear_categoria():
    """Crear una nueva categoría"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        name = request.form.get('name')
        description = request.form.get('description', '')
        estacion = request.form.get('estacion', '')
        
        # Validaciones
        if not name or not name.strip():
            return jsonify({'success': False, 'message': 'El nombre es requerido'})
        
        # Verificar si la categoría ya existe
        if Category.query.filter_by(name=name.strip()).first():
            return jsonify({'success': False, 'message': 'La categoría ya existe'})
        
        # Crear nueva categoría
        nueva_categoria = Category(
            name=name.strip(),
            description=description.strip(),
            estacion=estacion.strip() if estacion else None
        )
        
        db.session.add(nueva_categoria)
        db.session.commit()
        
        print(f"[ADMIN] Categoría '{name}' creada exitosamente")
        
        return jsonify({
            'success': True, 
            'message': 'Categoría creada exitosamente',
            'categoria': {
                'id': nueva_categoria.id,
                'name': nueva_categoria.name,
                'description': nueva_categoria.description,
                'estacion': nueva_categoria.estacion
            }
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error creando categoría: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/api/categorias/<int:categoria_id>', methods=['PUT'])
def actualizar_categoria(categoria_id):
    """Actualizar una categoría existente"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        categoria = Category.query.get(categoria_id)
        if not categoria:
            return jsonify({'success': False, 'message': 'Categoría no encontrada'})
        
        name = request.form.get('name')
        description = request.form.get('description', '')
        estacion = request.form.get('estacion', '')
        
        # Validaciones
        if not name or not name.strip():
            return jsonify({'success': False, 'message': 'El nombre es requerido'})
        
        # Verificar si el nuevo nombre ya existe (excepto para la categoría actual)
        existing = Category.query.filter_by(name=name.strip()).first()
        if existing and existing.id != categoria_id:
            return jsonify({'success': False, 'message': 'Ya existe una categoría con ese nombre'})
        
        # Actualizar categoría
        categoria.name = name.strip()
        categoria.description = description.strip()
        categoria.estacion = estacion.strip() if estacion else None
        
        db.session.commit()
        
        print(f"[ADMIN] Categoría ID {categoria_id} actualizada")
        
        return jsonify({
            'success': True, 
            'message': 'Categoría actualizada exitosamente'
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error actualizando categoría: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/api/categorias/<int:categoria_id>', methods=['DELETE'])
def eliminar_categoria(categoria_id):
    """Eliminar una categoría"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        categoria = Category.query.get(categoria_id)
        if not categoria:
            return jsonify({'success': False, 'message': 'Categoría no encontrada'})
        
        # Verificar si tiene productos
        if len(categoria.products) > 0:
            return jsonify({
                'success': False, 
                'message': f'No se puede eliminar la categoría porque tiene {len(categoria.products)} producto(s) asociado(s)'
            })
        
        categoria_name = categoria.name
        db.session.delete(categoria)
        db.session.commit()
        
        print(f"[ADMIN] Categoría '{categoria_name}' eliminada")
        
        return jsonify({
            'success': True, 
            'message': f'Categoría "{categoria_name}" eliminada exitosamente'
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error eliminando categoría: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ===============================
# CRUD DE PRODUCTOS
# ===============================

@admin_bp.route('/api/productos', methods=['GET'])
def get_productos():
    """Obtener todos los productos"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        productos = Product.query.join(Category).all()
        productos_data = []
        
        for producto in productos:
            productos_data.append({
                'id': producto.id,
                'name': producto.name,
                'description': producto.description,
                'ingredients': producto.ingredients,
                'image_url': producto.image_url,
                'price': float(producto.price) if producto.price else 0,
                'tags': producto.tags,
                'category_id': producto.category_id,
                'category_name': producto.category.name,
                'is_available': producto.is_available,
                'station_type': producto.station_type,
                'preparation_time': producto.preparation_time,
                'spice_level': producto.spice_level,
                'created_at': producto.created_at.isoformat() if producto.created_at else None
            })
        
        return jsonify(productos_data)
    except Exception as e:
        print(f"Error obteniendo productos: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/api/productos', methods=['POST'])
def crear_producto():
    """Crear un nuevo producto"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        # Obtener datos del formulario
        name = request.form.get('name')
        description = request.form.get('description', '')
        ingredients = request.form.get('ingredients', '')
        image_url = request.form.get('image_url', '')
        price = request.form.get('price')
        tags = request.form.get('tags', '')
        category_id = request.form.get('category_id')
        preparation_time = request.form.get('preparation_time', '15')
        spice_level = request.form.get('spice_level', 'mild')
        
        # Validaciones
        if not name or not name.strip():
            return jsonify({'success': False, 'message': 'El nombre es requerido'})
        
        if not price:
            return jsonify({'success': False, 'message': 'El precio es requerido'})
        
        try:
            price = float(price)
            if price < 0:
                return jsonify({'success': False, 'message': 'El precio debe ser mayor o igual a 0'})
        except ValueError:
            return jsonify({'success': False, 'message': 'Precio inválido'})
        
        if not category_id:
            return jsonify({'success': False, 'message': 'La categoría es requerida'})
        
        # Verificar que la categoría existe
        categoria = Category.query.get(category_id)
        if not categoria:
            return jsonify({'success': False, 'message': 'Categoría no encontrada'})
        
        try:
            preparation_time = int(preparation_time)
            if preparation_time < 1:
                preparation_time = 15
        except ValueError:
            preparation_time = 15
        
        # Crear nuevo producto
        nuevo_producto = Product(
            name=name.strip(),
            description=description.strip(),
            ingredients=ingredients.strip(),
            image_url=image_url.strip() if image_url else None,
            price=price,
            tags=tags.strip(),
            category_id=int(category_id),
            preparation_time=preparation_time,
            spice_level=spice_level,
            is_available=True
        )
        
        db.session.add(nuevo_producto)
        db.session.commit()
        
        print(f"[ADMIN] Producto '{name}' creado exitosamente")
        
        return jsonify({
            'success': True, 
            'message': 'Producto creado exitosamente',
            'producto': {
                'id': nuevo_producto.id,
                'name': nuevo_producto.name,
                'price': float(nuevo_producto.price),
                'category_name': categoria.name
            }
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error creando producto: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/api/productos/<int:producto_id>', methods=['PUT'])
def actualizar_producto(producto_id):
    """Actualizar un producto existente"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        producto = Product.query.get(producto_id)
        if not producto:
            return jsonify({'success': False, 'message': 'Producto no encontrado'})
        
        # Obtener datos del formulario
        name = request.form.get('name')
        description = request.form.get('description', '')
        ingredients = request.form.get('ingredients', '')
        image_url = request.form.get('image_url', '')
        price = request.form.get('price')
        tags = request.form.get('tags', '')
        category_id = request.form.get('category_id')
        preparation_time = request.form.get('preparation_time', '15')
        spice_level = request.form.get('spice_level', 'mild')
        is_available = request.form.get('is_available', 'true').lower() == 'true'
        
        # Validaciones
        if not name or not name.strip():
            return jsonify({'success': False, 'message': 'El nombre es requerido'})
        
        if not price:
            return jsonify({'success': False, 'message': 'El precio es requerido'})
        
        try:
            price = float(price)
            if price < 0:
                return jsonify({'success': False, 'message': 'El precio debe ser mayor o igual a 0'})
        except ValueError:
            return jsonify({'success': False, 'message': 'Precio inválido'})
        
        if category_id:
            categoria = Category.query.get(category_id)
            if not categoria:
                return jsonify({'success': False, 'message': 'Categoría no encontrada'})
            producto.category_id = int(category_id)
        
        try:
            preparation_time = int(preparation_time)
            if preparation_time < 1:
                preparation_time = 15
        except ValueError:
            preparation_time = 15
        
        # Actualizar producto
        producto.name = name.strip()
        producto.description = description.strip()
        producto.ingredients = ingredients.strip()
        producto.image_url = image_url.strip() if image_url else None
        producto.price = price
        producto.tags = tags.strip()
        producto.preparation_time = preparation_time
        producto.spice_level = spice_level
        producto.is_available = is_available
        producto.last_updated = datetime.utcnow()
        
        db.session.commit()
        
        print(f"[ADMIN] Producto ID {producto_id} actualizado")
        
        return jsonify({
            'success': True, 
            'message': 'Producto actualizado exitosamente'
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error actualizando producto: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/api/productos/<int:producto_id>', methods=['DELETE'])
def eliminar_producto(producto_id):
    """Eliminar un producto"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        producto = Product.query.get(producto_id)
        if not producto:
            return jsonify({'success': False, 'message': 'Producto no encontrado'})
        
        producto_name = producto.name
        db.session.delete(producto)
        db.session.commit()
        
        print(f"[ADMIN] Producto '{producto_name}' eliminado")
        
        return jsonify({
            'success': True, 
            'message': f'Producto "{producto_name}" eliminado exitosamente'
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error eliminando producto: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Configuración para upload de imágenes
UPLOAD_FOLDER = 'static/uploads/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Verificar si la extensión del archivo está permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/upload-image', methods=['POST'])
def upload_image():
    """Subir imagen de producto"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'No se seleccionó archivo'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No se seleccionó archivo'}), 400
        
        if file and allowed_file(file.filename):
            # Generar nombre único para evitar conflictos
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            
            # Crear directorio si no existe
            upload_path = os.path.join(os.getcwd(), UPLOAD_FOLDER)
            os.makedirs(upload_path, exist_ok=True)
            
            # Guardar archivo
            file_path = os.path.join(upload_path, unique_filename)
            file.save(file_path)
            
            # URL relativa para la base de datos
            image_url = f"/static/uploads/images/{unique_filename}"
            
            print(f"[ADMIN] Imagen subida: {image_url}")
            
            return jsonify({
                'success': True, 
                'image_url': image_url,
                'message': 'Imagen subida exitosamente'
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Tipo de archivo no permitido. Use: PNG, JPG, JPEG, GIF, WEBP'
            }), 400
    
    except Exception as e:
        print(f"Error subiendo imagen: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
