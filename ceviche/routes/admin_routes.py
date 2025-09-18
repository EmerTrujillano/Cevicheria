from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Product, Category, Table, Order, OrderItem, UserSession
from config.extensions import db
from utils.decorators import role_required
from services.session_service import SessionService
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def check_admin_auth():
    """Verificar autenticación de admin usando sesión"""
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
        return redirect(url_for('main.login_page'))
    return render_template('admin/dashboard.html')

@admin_bp.route('/supervision')
def supervision():
    """Vista de supervisión en tiempo real"""
    if not check_admin_auth():
        return redirect(url_for('main.login_page'))
    return render_template('admin/supervision.html')

@admin_bp.route('/menu-management')
def menu_management():
    """Gestión del menú - productos y categorías"""
    if not check_admin_auth():
        return redirect(url_for('main.login_page'))
    return render_template('admin/menu_management.html')

@admin_bp.route('/api/dashboard-stats')
def get_dashboard_stats():
    """Obtener estadísticas para el dashboard del admin"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        # Contar mesas ocupadas
        mesas_ocupadas = Table.query.filter_by(status='ocupada').count()
        mesas_totales = Table.query.count()
        mesas_libres = mesas_totales - mesas_ocupadas
        
        # Obtener sesiones activas con detalles
        active_sessions = UserSession.query.filter_by(is_active=True).join(User).all()
        
        sesiones_activas = []
        usuarios_por_rol = {'admin': 0, 'mozo': 0, 'cocina': 0, 'cajero': 0}
        
        for user_session in active_sessions:
            user = user_session.user
            
            # Calcular tiempo de sesión
            tiempo_sesion = (datetime.utcnow() - user_session.created_at).total_seconds()
            tiempo_str = f"{int(tiempo_sesion // 60)}m"
            if tiempo_sesion > 3600:
                horas = int(tiempo_sesion // 3600)
                minutos = int((tiempo_sesion % 3600) // 60)
                tiempo_str = f"{horas}h {minutos}m"
            
            sesiones_activas.append({
                'session_id': user_session.id,
                'user_id': user.id,
                'username': user.username,
                'role': user.role,
                'created_at': user_session.created_at.strftime('%H:%M'),
                'tiempo_activo': tiempo_str,
                'last_activity': user_session.last_activity.strftime('%H:%M') if user_session.last_activity else 'N/A',
                'ip_address': user_session.ip_address or 'N/A'
            })
            
            # Contar por rol
            if user.role in usuarios_por_rol:
                usuarios_por_rol[user.role] += 1
        
        # Pedidos pendientes
        pedidos_pendientes = Order.query.filter(
            Order.status.in_(['pending', 'in_kitchen'])
        ).count()
        
        # Pedidos de hoy
        from datetime import date
        today = date.today()
        pedidos_hoy = Order.query.filter(
            db.func.date(Order.created_at) == today
        ).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'mesas': {
                    'ocupadas': mesas_ocupadas,
                    'libres': mesas_libres,
                    'total': mesas_totales
                },
                'sesiones': {
                    'total_activas': len(sesiones_activas),
                    'por_rol': usuarios_por_rol,
                    'detalle': sesiones_activas
                },
                'pedidos': {
                    'pendientes': pedidos_pendientes,
                    'hoy': pedidos_hoy
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/force-logout', methods=['POST'])
def force_logout_user():
    """Forzar logout de un usuario específico"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        username = data.get('username')
        
        if not session_id and not username:
            return jsonify({'success': False, 'message': 'Se requiere session_id o username'}), 400
        
        # Buscar sesiones a cerrar
        sessions_to_close = []
        
        if session_id:
            # Cerrar sesión específica
            user_session = UserSession.query.get(session_id)
            if user_session:
                sessions_to_close.append(user_session)
        
        if username:
            # Cerrar todas las sesiones del usuario
            user = User.query.filter_by(username=username).first()
            if user:
                user_sessions = UserSession.query.filter_by(user_id=user.id, is_active=True).all()
                sessions_to_close.extend(user_sessions)
        
        if not sessions_to_close:
            return jsonify({'success': False, 'message': 'No se encontraron sesiones activas'}), 404
        
        # Cerrar sesiones
        closed_count = 0
        for user_session in sessions_to_close:
            user_session.is_active = False
            user_session.ended_at = datetime.utcnow()
            user_session.end_reason = 'admin_force_logout'
            closed_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Se cerraron {closed_count} sesión(es)',
            'closed_sessions': closed_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
        mesas_ocupadas = 0
        mesas_disponibles = 0
        mesas_detalle = []
        
        try:
            todas_las_mesas = Table.query.all()
            for mesa in todas_las_mesas:
                if mesa.status == 'occupied':
                    mesas_ocupadas += 1
                else:
                    mesas_disponibles += 1
                
                # Calcular tiempo ocupado
                tiempo_ocupada = None
                tiempo_str = "-"
                if mesa.status == 'occupied' and hasattr(mesa, 'occupied_at') and mesa.occupied_at:
                    try:
                        tiempo_ocupada = (datetime.utcnow() - mesa.occupied_at).total_seconds()
                        if tiempo_ocupada > 3600:  # Más de 1 hora
                            horas = int(tiempo_ocupada // 3600)
                            minutos = int((tiempo_ocupada % 3600) // 60)
                            tiempo_str = f"{horas}h {minutos}m"
                        else:
                            tiempo_str = f"{int(tiempo_ocupada // 60)}m"
                    except:
                        tiempo_str = "N/A"
                
                # Obtener zona de forma segura
                zona = "General"
                try:
                    if hasattr(mesa, 'zone') and mesa.zone:
                        zona = mesa.zone.name
                except:
                    zona = "General"
                
                mesas_detalle.append({
                    'numero': mesa.number,
                    'estado': mesa.status,
                    'zona': zona,
                    'tiempo_ocupada': tiempo_str,
                    'tiempo_segundos': int(tiempo_ocupada) if tiempo_ocupada else 0
                })
        except Exception as e:
            print(f"Error en mesas: {e}")
            # Datos por defecto si hay problema con las mesas
            mesas_detalle = []
        
        # Usuarios activos
        usuarios_activos = 0
        usuarios_por_rol = {'admin': 0, 'mozo': 0, 'cocina': 0, 'cajero': 0}
        
        try:
            usuarios_activos = UserSession.query.filter_by(is_active=True).count()
            
            # Usuarios por rol (con debug)
            active_sessions = UserSession.query.filter_by(is_active=True).join(User).all()
            print(f"[DEBUG] Sesiones activas encontradas: {len(active_sessions)}")
            
            for session in active_sessions:
                role = session.user.role
                print(f"[DEBUG] Usuario {session.user.username} con rol: {role}")
                
                # Mapear roles a los nombres esperados
                if role == 'admin':
                    usuarios_por_rol['admin'] += 1
                elif role == 'mozo':
                    usuarios_por_rol['mozo'] += 1
                elif role == 'cocina':
                    usuarios_por_rol['cocina'] += 1
                elif role == 'cajero':
                    usuarios_por_rol['cajero'] += 1
                    
            print(f"[DEBUG] Conteo final por rol: {usuarios_por_rol}")
        except Exception as e:
            print(f"Error en usuarios: {e}")
        
        # Pedidos pendientes
        pedidos_pendientes = 0
        try:
            pedidos_pendientes = Order.query.filter(
                Order.status.in_(['pending', 'in_progress'])
            ).count()
        except Exception as e:
            print(f"Error en pedidos: {e}")
        
        # Ventas del día
        ventas_dia = 0.0
        try:
            from datetime import date
            today = date.today()
            pedidos_hoy = Order.query.filter(
                db.func.date(Order.created_at) == today,
                Order.status == 'completed'
            ).all()
            
            ventas_dia = sum(order.total_amount for order in pedidos_hoy if order.total_amount)
        except Exception as e:
            print(f"Error en ventas: {e}")
        
        return jsonify({
            'success': True,
            'usuarios_activos': usuarios_activos,
            'mesas_ocupadas': mesas_ocupadas,
            'pedidos_pendientes': pedidos_pendientes,
            'ventas_dia': float(ventas_dia),
            'usuarios_por_rol': usuarios_por_rol,
            'mesas_detalle': mesas_detalle,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"Error general en real-time-status: {e}")
        return jsonify({
            'success': False,
            'message': f'Error al obtener estado: {str(e)}'
        }), 500

@admin_bp.route('/user-management')
def user_management():
    """Gestión de usuarios"""
    if not check_admin_auth():
        return redirect(url_for('main.login_page'))
    return render_template('admin/user_management.html')

@admin_bp.route('/session-monitoring')
def session_monitoring():
    """Monitoreo de sesiones activas"""
    if not check_admin_auth():
        return redirect(url_for('main.login_page'))
    return render_template('admin/session_monitoring.html')

# APIs para gestión de usuarios
@admin_bp.route('/api/users', methods=['GET'])
def get_users():
    """Obtener lista de todos los usuarios (usando autenticación por sesión)"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
        
    try:
        users = User.query.all()
        users_data = []
        
        for user in users:
            # Obtener sesiones activas del usuario
            active_sessions = UserSession.query.filter_by(user_id=user.id, is_active=True).count()
            
            user_data = user.to_dict()
            user_data['active_sessions'] = active_sessions
            user_data['last_login'] = user.last_login.isoformat() if user.last_login else None
            users_data.append(user_data)
        
        return jsonify({
            'success': True,
            'data': users_data
        })
    except Exception as e:
        print(f"Error obteniendo usuarios: {e}")
        return jsonify({
            'success': False,
            'message': f'Error al obtener usuarios: {str(e)}'
        }), 500

@admin_bp.route('/api/users', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_user():
    """Crear nuevo usuario"""
    try:
        data = request.get_json()
        
        required_fields = ['username', 'password', 'role', 'full_name']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido: {field}'
                }), 400
        
        # Verificar que el username no exista
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'success': False,
                'message': 'El nombre de usuario ya existe'
            }), 400
        
        # Crear usuario
        user = User(
            username=data['username'],
            full_name=data['full_name'],
            role=data['role'],
            estacion=data.get('estacion')  # Solo para cocina
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Usuario creado exitosamente',
            'data': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al crear usuario: {str(e)}'
        }), 500

@admin_bp.route('/api/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_user(user_id):
    """Actualizar usuario"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Actualizar campos permitidos
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'role' in data:
            user.role = data['role']
        if 'estacion' in data:
            user.estacion = data['estacion']
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Usuario actualizado exitosamente',
            'data': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al actualizar usuario: {str(e)}'
        }), 500

@admin_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_user(user_id):
    """Eliminar usuario"""
    try:
        user = User.query.get_or_404(user_id)
        
        # No permitir eliminar el último admin
        if user.role == 'admin':
            admin_count = User.query.filter_by(role='admin').count()
            if admin_count <= 1:
                return jsonify({
                    'success': False,
                    'message': 'No se puede eliminar el último administrador'
                }), 400
        
        # Cerrar sesiones activas del usuario
        UserSession.query.filter_by(user_id=user.id).delete()
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Usuario eliminado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al eliminar usuario: {str(e)}'
        }), 500

# APIs para monitoreo de sesiones
@admin_bp.route('/api/active-sessions')
@jwt_required()
@role_required('admin')
def get_active_sessions():
    """Obtener todas las sesiones activas"""
    try:
        sessions = SessionService.get_all_active_sessions()
        sessions_data = []
        
        for session in sessions:
            session_data = {
                'id': session.id,
                'session_id': session.session_id,
                'user': {
                    'id': session.user.id,
                    'username': session.user.username,
                    'full_name': session.user.full_name,
                    'role': session.user.role,
                    'estacion': session.user.estacion
                },
                'ip_address': session.ip_address,
                'device_info': session.device_info,
                'created_at': session.created_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'expires_at': session.expires_at.isoformat() if session.expires_at else None,
                'is_active': session.is_active
            }
            sessions_data.append(session_data)
        
        return jsonify({
            'success': True,
            'data': sessions_data,
            'total': len(sessions_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener sesiones: {str(e)}'
        }), 500

@admin_bp.route('/api/sessions/<session_id>/close', methods=['POST'])
@jwt_required()
@role_required('admin')
def close_session(session_id):
    """Cerrar una sesión específica"""
    try:
        session = UserSession.query.filter_by(session_id=session_id).first()
        if not session:
            return jsonify({
                'success': False,
                'message': 'Sesión no encontrada'
            }), 404
        
        session.invalidate()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Sesión de {session.user.username} cerrada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al cerrar sesión: {str(e)}'
        }), 500

@admin_bp.route('/api/users/<int:user_id>/close-sessions', methods=['POST'])
def close_user_sessions(user_id):
    """Cerrar todas las sesiones de un usuario (usando autenticación por sesión)"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
        
    try:
        user = User.query.get_or_404(user_id)
        
        # Cerrar todas las sesiones del usuario de forma inmediata
        from services.session_service import SessionService
        closed_count = SessionService.close_user_sessions(user_id)
        
        return jsonify({
            'success': True,
            'message': f'Se cerraron {closed_count} sesiones de {user.username}',
            'closed_count': closed_count
        })
        
    except Exception as e:
        print(f"Error cerrando sesiones de usuario {user_id}: {e}")
        return jsonify({
            'success': False,
            'message': f'Error al cerrar sesiones: {str(e)}'
        }), 500

# APIs adicionales para supervisión
@admin_bp.route('/api/mesas-status')
def get_mesas_status():
    """Obtener estado de todas las mesas"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        mesas = Table.query.all()
        mesas_data = []
        
        for mesa in mesas:
            mesa_data = {
                'id': mesa.id,
                'number': mesa.number,
                'status': mesa.status,
                'tiempo': None  # Se puede calcular si hay pedidos activos
            }
            mesas_data.append(mesa_data)
        
        return jsonify({
            'success': True,
            'mesas': mesas_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener estado de mesas: {str(e)}'
        }), 500

@admin_bp.route('/api/actividad-reciente')
def get_actividad_reciente():
    """Obtener actividad reciente del sistema"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        # Obtener últimas sesiones creadas
        recent_sessions = UserSession.query.order_by(UserSession.created_at.desc()).limit(10).all()
        
        actividades = []
        for session in recent_sessions:
            actividades.append({
                'hora': session.created_at.strftime('%H:%M'),
                'usuario': session.user.username,
                'accion': 'Inicio de sesión',
                'detalles': f'IP: {session.ip_address}'
            })
        
        return jsonify({
            'success': True,
            'actividades': actividades
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener actividad reciente: {str(e)}'
        }), 500

# APIs para gestión de categorías y productos
@admin_bp.route('/api/categorias')
def get_categorias():
    """Obtener todas las categorías"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        categorias = Category.query.all()
        categorias_data = []
        
        for categoria in categorias:
            productos_count = Product.query.filter_by(category_id=categoria.id).count()
            
            categoria_data = {
                'id': categoria.id,
                'name': categoria.name,
                'description': categoria.description,
                'station': categoria.station,
                'productos_count': productos_count
            }
            categorias_data.append(categoria_data)
        
        return jsonify({
            'success': True,
            'categorias': categorias_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener categorías: {str(e)}'
        }), 500

@admin_bp.route('/api/categorias', methods=['POST'])
def create_categoria():
    """Crear nueva categoría"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({
                'success': False,
                'message': 'El nombre de la categoría es requerido'
            }), 400
        
        categoria = Category(
            name=data['name'],
            description=data.get('description'),
            station=data.get('station')
        )
        
        db.session.add(categoria)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Categoría creada exitosamente',
            'categoria': {
                'id': categoria.id,
                'name': categoria.name,
                'description': categoria.description,
                'station': categoria.station
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al crear categoría: {str(e)}'
        }), 500

@admin_bp.route('/api/productos')
def get_productos():
    """Obtener todos los productos"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        productos = db.session.query(Product, Category.name.label('category_name')).join(Category, Product.category_id == Category.id).all()
        productos_data = []
        
        for producto, category_name in productos:
            producto_data = {
                'id': producto.id,
                'name': producto.name,
                'description': producto.description,
                'price': float(producto.price),
                'available': producto.available,
                'category_id': producto.category_id,
                'category_name': category_name
            }
            productos_data.append(producto_data)
        
        return jsonify({
            'success': True,
            'productos': productos_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener productos: {str(e)}'
        }), 500

@admin_bp.route('/api/productos', methods=['POST'])
def create_producto():
    """Crear nuevo producto"""
    if not check_admin_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        
        required_fields = ['name', 'price', 'category_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido: {field}'
                }), 400
        
        # Verificar que la categoría existe
        categoria = Category.query.get(data['category_id'])
        if not categoria:
            return jsonify({
                'success': False,
                'message': 'Categoría no encontrada'
            }), 400
        
        producto = Product(
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            category_id=data['category_id'],
            available=data.get('available', True)
        )
        
        db.session.add(producto)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Producto creado exitosamente',
            'producto': {
                'id': producto.id,
                'name': producto.name,
                'description': producto.description,
                'price': float(producto.price),
                'available': producto.available,
                'category_id': producto.category_id
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al crear producto: {str(e)}'
        }), 500

@admin_bp.route('/status')
def admin_status():
    """Estado general del admin para dashboard"""
    if not check_admin_auth():
        return redirect(url_for('main.login_page'))
    
    try:
        # Estadísticas que espera el dashboard
        usuarios_activos = UserSession.query.filter_by(is_active=True).count()
        mesas_ocupadas = Table.query.filter_by(status='occupied').count()
        pedidos_pendientes = Order.query.filter(Order.status.in_(['pending', 'in_kitchen'])).count()
        
        # Calcular ventas del día
        from datetime import date
        today = date.today()
        ventas_hoy = db.session.query(db.func.sum(Order.total_amount)).filter(
            db.func.date(Order.created_at) == today,
            Order.status == 'paid'
        ).scalar() or 0
        
        # Estado del sistema
        sistema = {
            'sesiones_activas': usuarios_activos,
            'tiempo_activo': 'N/A'  # Puedes implementar esto si tienes timestamp de inicio del servidor
        }
        
        # Actividad reciente (últimas acciones)
        actividad_reciente = []
        try:
            recent_orders = Order.query.order_by(Order.created_at.desc()).limit(3).all()
            for order in recent_orders:
                actividad_reciente.append({
                    'tipo': 'Nuevo Pedido',
                    'descripcion': f'Pedido #{order.order_number} - Mesa {order.table.number if order.table else "N/A"}',
                    'tiempo': order.created_at.strftime('%H:%M')
                })
        except Exception as e:
            print(f"Error obteniendo actividad reciente: {e}")
        
        return jsonify({
            'usuarios_activos': usuarios_activos,
            'mesas_ocupadas': mesas_ocupadas,
            'pedidos_pendientes': pedidos_pendientes,
            'ventas_hoy': float(ventas_hoy),
            'sistema': sistema,
            'actividad_reciente': actividad_reciente
        })
        
    except Exception as e:
        print(f"Error en admin_status: {e}")
        return jsonify({
            'usuarios_activos': 0,
            'mesas_ocupadas': 0,
            'pedidos_pendientes': 0,
            'ventas_hoy': 0,
            'sistema': {'sesiones_activas': 0, 'tiempo_activo': 'Error'},
            'actividad_reciente': []
        }), 500