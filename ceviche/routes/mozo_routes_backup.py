from flask import Blueprint, rende@mozo_bp.route('/')
def mozo_dashboard():
    """Panel principal del mozo"""
    if not check_mozo_auth():
        return redirect(url_for('auth.login_page'))
    return render_template('mozo/dashboard_new.html')late, request, jsonify, session, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from models import User, Product, Category, Table, Order, OrderItem, Zone, Floor
from config.extensions import db
from utils.decorators import role_required
from datetime import datetime

mozo_bp = Blueprint('mozo', __name__, url_prefix='/mozo')

def check_mozo_auth():
    """Verificar autenticación de mozo usando JWT o sesión"""
    # Primer intento: verificar JWT
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        if user_id:
            user = User.query.get(int(user_id))
            if user and user.role == 'mozo':
                # Establecer sesión Flask para compatibilidad
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                return True
    except:
        pass
    
    # Segundo intento: verificar sesión Flask
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.role == 'mozo':
            return True
    
    return False

@mozo_bp.route('/')
def mozo_dashboard():
    """Panel principal del mozo"""
    if not check_mozo_auth():
        return redirect(url_for('main.login_page'))
    return render_template('mozo/dashboard.html')

@mozo_bp.route('/mesas')
def gestionar_mesas():
    """Vista de gestión de mesas"""
    if not check_mozo_auth():
        return redirect(url_for('main.login_page'))
    return render_template('mozo/mesas.html')

@mozo_bp.route('/nuevo-pedido/<int:table_id>')
def nuevo_pedido(table_id):
    """Crear nuevo pedido para una mesa específica"""
    if not check_mozo_auth():
        return redirect(url_for('main.login_page'))
    return render_template('mozo/nuevo_pedido.html', table_id=table_id)

@mozo_bp.route('/pedidos-activos')
def pedidos_activos():
    """Ver pedidos activos del mozo"""
    if not check_mozo_auth():
        return redirect(url_for('main.login_page'))
    return render_template('mozo/pedidos_activos.html')

@mozo_bp.route('/profile')
def get_mozo_profile():
    """Obtener perfil del mozo (usa sesión)"""
    if not check_mozo_auth():
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'estacion': user.estacion
            }
        })
    
    except Exception as e:
        return jsonify({'error': f'Error obteniendo perfil: {str(e)}'}), 500

# APIs para obtener datos
@mozo_bp.route('/api/mesas')
def get_mesas():
    """Obtener estado de todas las mesas"""
    if not check_mozo_auth():
        return jsonify({'error': 'No autorizado'}), 401
    try:
        tables = Table.query.join(Zone).join(Floor).all()
        mesas_data = []
        
        for table in tables:
            mesa_dict = table.to_dict()
            mesa_dict['zona'] = table.zone.name if table.zone else 'Sin zona'
            mesa_dict['piso'] = table.zone.floor.name if table.zone and table.zone.floor else 'Sin piso'
            mesas_data.append(mesa_dict)
        
        return jsonify({
            'success': True,
            'data': mesas_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener mesas: {str(e)}'
        }), 500

@mozo_bp.route('/api/zones')
def get_zones():
    """Obtener todas las zonas con estadísticas de mesas"""
    if not check_mozo_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        zones = Zone.query.join(Floor).all()
        zones_data = []
        
        for zone in zones:
            # Contar mesas por estado
            available_tables = Table.query.filter_by(zone_id=zone.id, status='available').count()
            occupied_tables = Table.query.filter_by(zone_id=zone.id, status='occupied').count()
            reserved_tables = Table.query.filter_by(zone_id=zone.id, status='reserved').count()
            cleaning_tables = Table.query.filter_by(zone_id=zone.id, status='cleaning').count()
            
            zone_data = {
                'id': zone.id,
                'name': zone.name,
                'description': zone.description,
                'zone_type': zone.zone_type,
                'floor_name': zone.floor.name,
                'available_tables': available_tables,
                'occupied_tables': occupied_tables,
                'reserved_tables': reserved_tables,
                'cleaning_tables': cleaning_tables,
                'total_tables': available_tables + occupied_tables + reserved_tables + cleaning_tables
            }
            zones_data.append(zone_data)
        
        return jsonify({
            'success': True,
            'zones': zones_data
        })
        
    except Exception as e:
        print(f"Error obteniendo zonas: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@mozo_bp.route('/api/zones/<int:zone_id>/tables')
def get_zone_tables(zone_id):
    """Obtener todas las mesas de una zona específica"""
    if not check_mozo_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        zone = Zone.query.get_or_404(zone_id)
        tables = Table.query.filter_by(zone_id=zone_id).order_by(Table.number).all()
        
        tables_data = []
        for table in tables:
            table_data = {
                'id': table.id,
                'number': table.number,
                'capacity': table.capacity,
                'status': table.status,
                'zone_id': zone.id,
                'zone_name': zone.name
            }
            
            # Si está ocupada, obtener info del pedido actual
            if table.status == 'occupied':
                current_order = Order.query.filter_by(
                    table_id=table.id,
                    status='in_progress'
                ).first()
                
                if current_order:
                    table_data['current_order'] = {
                        'id': current_order.id,
                        'created_at': current_order.created_at.isoformat(),
                        'total': float(current_order.total or 0),
                        'items_count': len(current_order.items)
                    }
            
            tables_data.append(table_data)
        
        return jsonify({
            'success': True,
            'zone': {
                'id': zone.id,
                'name': zone.name,
                'description': zone.description,
                'zone_type': zone.zone_type
            },
            'tables': tables_data
        })
        
    except Exception as e:
        print(f"Error obteniendo mesas de zona {zone_id}: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@mozo_bp.route('/api/tables/assign', methods=['POST'])
def assign_table():
    """Asignar una mesa a un cliente"""
    if not check_mozo_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        table_id = data.get('table_id')
        zone_id = data.get('zone_id')
        
        if not table_id:
            return jsonify({'success': False, 'message': 'ID de mesa requerido'}), 400
        
        table = Table.query.get_or_404(table_id)
        
        if table.status != 'available':
            return jsonify({'success': False, 'message': 'La mesa no está disponible'}), 400
        
        # Cambiar estado de la mesa
        table.status = 'occupied'
        table.occupied_at = datetime.utcnow()
        
        # Crear nuevo pedido
        new_order = Order(
            table_id=table.id,
            waiter_id=session.get('user_id'),  # ID del mozo actual
            status='in_progress',
            total=0.0
        )
        
        db.session.add(new_order)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Mesa {table.number} asignada correctamente',
            'order': {
                'id': new_order.id,
                'table_number': table.number,
                'zone_name': table.zone.name if table.zone else 'Sin zona'
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error asignando mesa: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@mozo_bp.route('/menu')
def get_menu():
    """Obtener productos organizados por estación"""
    if not check_mozo_auth():
        return jsonify({'error': 'No autorizado'}), 401
    try:
        categories = Category.query.all()
        menu_data = {}
        
        for category in categories:
            # Obtener productos activos de esta categoría
            products = Product.query.filter_by(
                category_id=category.id,
                is_active=True
            ).all()
            
            if products:  # Solo agregar si hay productos
                # Determinar estación basada en el tipo de categoría
                station = 'cocina1'  # Por defecto
                if category.name and any(keyword in category.name.lower() for keyword in ['caliente', 'frito', 'plancha', 'grill']):
                    station = 'cocina2'
                elif category.name and any(keyword in category.name.lower() for keyword in ['bebida', 'jugo', 'refresco']):
                    station = 'bar'
                
                productos_disponibles = []
                for product in products:
                    productos_disponibles.append({
                        'id': product.id,
                        'name': product.name,
                        'price': float(product.price),
                        'description': product.description or '',
                        'category': category.name,
                        'station_type': station
                    })
                
                if station not in menu_data:
                    menu_data[station] = []
                menu_data[station].extend(productos_disponibles)
        
        return jsonify(menu_data)
    except Exception as e:
        return jsonify({'error': f'Error al obtener menú: {str(e)}'}), 500

@mozo_bp.route('/tables/occupy', methods=['POST'])
def occupy_table():
    """Ocupar una mesa"""
    if not check_mozo_auth():
        return jsonify({'error': 'No autorizado'}), 401
    try:
        data = request.get_json()
        table_number = data.get('numero')
        
        if not table_number:
            return jsonify({'error': 'Número de mesa requerido'}), 400
        
        table = Table.query.filter_by(number=table_number).first()
        if not table:
            return jsonify({'error': 'Mesa no encontrada'}), 404
        
        if table.status == 'occupied':
            return jsonify({'error': 'La mesa ya está ocupada'}), 400
        
        table.status = 'occupied'
        db.session.commit()
        
        return jsonify({'success': f'Mesa {table_number} ocupada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al ocupar mesa: {str(e)}'}), 500

@mozo_bp.route('/tables/free', methods=['POST'])
def free_table():
    """Liberar una mesa"""
    if not check_mozo_auth():
        return jsonify({'error': 'No autorizado'}), 401
    try:
        data = request.get_json()
        table_number = data.get('numero')
        
        if not table_number:
            return jsonify({'error': 'Número de mesa requerido'}), 400
        
        table = Table.query.filter_by(number=table_number).first()
        if not table:
            return jsonify({'error': 'Mesa no encontrada'}), 404
        
        table.status = 'available'
        db.session.commit()
        
        return jsonify({'success': f'Mesa {table_number} liberada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al liberar mesa: {str(e)}'}), 500

@mozo_bp.route('/api/crear-pedido', methods=['POST'])
def crear_pedido():
    """Crear un nuevo pedido"""
    if not check_mozo_auth():
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        current_user_id = session['user_id']
        
        # Validar datos requeridos
        if not data.get('mesa_numero'):
            return jsonify({'error': 'Número de mesa requerido'}), 400
        
        if not data.get('items') or len(data.get('items', [])) == 0:
            return jsonify({'error': 'Debe incluir al menos un producto'}), 400
        
        # Verificar que la mesa existe
        table = Table.query.filter_by(number=data['mesa_numero']).first()
        if not table:
            return jsonify({'error': 'Mesa no encontrada'}), 404
        
        # Crear la orden
        order = Order(
            table_id=table.id,
            waiter_id=current_user_id,
            status='pending',
            order_time=datetime.now(),
            total_amount=0
        )
        
        db.session.add(order)
        db.session.flush()  # Para obtener el ID de la orden
        
        total = 0
        
        # Procesar items del pedido
        for item in data['items']:
            product = Product.query.get(item['product_id'])
            if not product:
                db.session.rollback()
                return jsonify({'error': f'Producto {item["product_id"]} no encontrado'}), 404
            
            # Determinar estación
            station_type = 'cocina1'  # Por defecto
            if product.category:
                if any(keyword in product.category.name.lower() for keyword in ['caliente', 'frito', 'plancha', 'grill']):
                    station_type = 'cocina2'
                elif any(keyword in product.category.name.lower() for keyword in ['bebida', 'jugo', 'refresco']):
                    station_type = 'bar'
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item['quantity'],
                unit_price=product.price,
                station_type=station_type,
                status='pending'
            )
            
            db.session.add(order_item)
            total += product.price * item['quantity']
        
        # Actualizar total de la orden
        order.total_amount = total
        
        # Marcar mesa como ocupada si no lo está
        if table.status != 'occupied':
            table.status = 'occupied'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pedido creado exitosamente',
            'order_id': order.id,
            'total': float(total)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al crear pedido: {str(e)}'}), 500

@mozo_bp.route('/api/mis-pedidos')
def mis_pedidos():
    """Obtener pedidos del mozo actual"""
    if not check_mozo_auth():
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        current_user_id = session['user_id']
        
        # Obtener pedidos del mozo
        orders = Order.query.filter_by(waiter_id=current_user_id).all()
        
        pedidos_data = []
        for order in orders:
            table = Table.query.get(order.table_id)
            
            pedidos_data.append({
                'id': order.id,
                'mesa_numero': table.number if table else 'N/A',
                'total': float(order.total_amount),
                'estado': order.status,
                'hora': order.order_time.strftime('%H:%M') if order.order_time else 'N/A',
                'fecha': order.order_time.strftime('%Y-%m-%d') if order.order_time else 'N/A'
            })
        
        return jsonify({
            'success': True,
            'data': pedidos_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener pedidos: {str(e)}'}), 500