from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Product, Category, Table, Order, OrderItem, Zone, Floor
from config.extensions import db
from utils.decorators import role_required
from datetime import datetime

mozo_bp = Blueprint('mozo', __name__, url_prefix='/mozo')

def check_mozo_auth():
    """Verificar autenticación de mozo usando sesión"""
    if 'user_id' not in session:
        return False
    
    user = User.query.get(session['user_id'])
    if not user or user.role != 'waiter':
        return False
    
    return True

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

# APIs para el mozo (estas siguen requiriendo JWT)
@mozo_bp.route('/api/mesas')

@mozo_bp.route('/profile')
def get_mozo_profile():
    """Obtener perfil del mozo (usa sesión, no JWT)"""
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
                'email': user.email
            }
        })
    
    except Exception as e:
        return jsonify({'error': f'Error obteniendo perfil: {str(e)}'}), 500

# APIs para el mozo (estas siguen requiriendo JWT)
@mozo_bp.route('/api/mesas')
@jwt_required()
@role_required('waiter')
def get_mesas():
    """Obtener estado de todas las mesas"""
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

@mozo_bp.route('/api/ocupar-mesa/<int:table_id>', methods=['POST'])
@jwt_required()
@role_required('waiter')
def ocupar_mesa(table_id):
    """Marcar mesa como ocupada"""
    try:
        table = Table.query.get_or_404(table_id)
        
        if table.status != 'available':
            return jsonify({
                'success': False,
                'message': 'La mesa no está disponible'
            }), 400
        
        table.status = 'occupied'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Mesa {table.number} marcada como ocupada'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al ocupar mesa: {str(e)}'
        }), 500

# Endpoints simples para el frontend (usan session auth)
@mozo_bp.route('/tables')
def get_tables():
    """Obtener todas las mesas (sin JWT, usa session)"""
    if not check_mozo_auth():
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        tables = Table.query.join(Zone).join(Floor).all()
        tables_data = []
        
        for table in tables:
            tables_data.append({
                'numero': table.number,
                'ocupada': table.status == 'occupied',
                'zona': table.zone.name if table.zone else 'Sin zona',
                'piso': table.zone.floor.name if table.zone and table.zone.floor else 'Sin piso',
                'id': table.id
            })
        
        return jsonify(tables_data)
    except Exception as e:
        return jsonify({'error': f'Error al obtener mesas: {str(e)}'}), 500

@mozo_bp.route('/tables/occupy', methods=['POST'])
def occupy_table():
    """Ocupar una mesa (sin JWT, usa session)"""
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
    """Liberar una mesa (sin JWT, usa session)"""
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

@mozo_bp.route('/menu')
def get_menu_by_station():
    """Obtener menú organizado por estaciones para el mozo (sin JWT, usa session)"""
    if not check_mozo_auth():
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        # Mapeo de categorías a estaciones para el frontend
        category_to_station = {
            'Platos Fríos': 'frios',
            'Platos Calientes': 'calientes', 
            'Frituras': 'frituras',
            'Bebidas': 'bebidas',
            'Postres': 'postres',
            'Acompañamientos': 'acompañamientos'
        }
        
        categories = Category.query.all()
        menu_data = {}
        
        for category in categories:
            station = category_to_station.get(category.name, 'otros')
            
            productos_disponibles = []
            for product in category.products:
                if product.is_available:
                    # Formatear datos del producto para el frontend
                    productos_disponibles.append({
                        'id': product.id,
                        'nombre': product.name,
                        'precio': float(product.price),
                        'descripcion': product.description,
                        'estacion': station,
                        'categoria': category.name
                    })
            
            if productos_disponibles:
                if station not in menu_data:
                    menu_data[station] = []
                menu_data[station].extend(productos_disponibles)
        
        return jsonify(menu_data)
    except Exception as e:
        return jsonify({'error': f'Error al obtener menú: {str(e)}'}), 500

# APIs para el mozo (estas siguen requiriendo JWT)

@mozo_bp.route('/api/productos-menu')
@jwt_required()
@role_required('waiter')
def get_productos_menu():
    """Obtener productos organizados por categoría para crear pedidos"""
    try:
        categories = Category.query.all()
        menu_data = []
        
        for category in categories:
            productos_disponibles = [
                product.to_dict() for product in category.products 
                if product.is_available
            ]
            
            if productos_disponibles:
                menu_data.append({
                    'categoria': category.to_dict(),
                    'productos': productos_disponibles
                })
        
        return jsonify({
            'success': True,
            'data': menu_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener menú: {str(e)}'
        }), 500

@mozo_bp.route('/api/crear-pedido', methods=['POST'])
@jwt_required()
@role_required('waiter')
def crear_pedido():
    """Crear nuevo pedido"""
    try:
        data = request.get_json()
        table_id = data.get('table_id')
        items = data.get('items', [])
        
        if not table_id or not items:
            return jsonify({
                'success': False,
                'message': 'Mesa e items son requeridos'
            }), 400
        
        # Verificar que la mesa existe
        table = Table.query.get_or_404(table_id)
        
        # Generar número de orden único
        last_order = Order.query.order_by(Order.id.desc()).first()
        if last_order and last_order.order_number:
            # Extraer número del último pedido (formato: COM-001)
            try:
                last_number = int(last_order.order_number.split('-')[1])
                new_number = last_number + 1
            except (IndexError, ValueError):
                new_number = 1
        else:
            new_number = 1
        
        order_number = f"COM-{new_number:03d}"
        
        # Crear el pedido
        order = Order(
            order_number=order_number,
            table_id=table_id,
            waiter_id=get_jwt_identity(),
            status='pending',
            created_at=datetime.utcnow()
        )
        db.session.add(order)
        db.session.flush()  # Para obtener el ID del pedido
        
        # Agregar items al pedido
        total = 0
        for item_data in items:
            product = Product.query.get(item_data['product_id'])
            if product and product.is_available:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=item_data['quantity'],
                    unit_price=product.price,
                    modifications=item_data.get('modifications', ''),
                    estacion=product.station or 'general'  # Asignar estación basada en el producto
                )
                db.session.add(order_item)
                total += product.price * item_data['quantity']
        
        order.total = total
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pedido creado exitosamente',
            'order_id': order.id,
            'total': total
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al crear pedido: {str(e)}'
        }), 500

@mozo_bp.route('/orders', methods=['POST'])
def create_order():
    """Crear nuevo pedido (sin JWT, usa session)"""
    if not check_mozo_auth():
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        table_number = data.get('mesa')
        items = data.get('items', [])
        
        if not table_number or not items:
            return jsonify({'error': 'Mesa e items son requeridos'}), 400
        
        # Buscar mesa por número
        table = Table.query.filter_by(number=table_number).first()
        if not table:
            return jsonify({'error': 'Mesa no encontrada'}), 404
        
        # Generar número de orden único
        last_order = Order.query.order_by(Order.id.desc()).first()
        if last_order and last_order.order_number:
            # Extraer número del último pedido (formato: COM-001)
            try:
                last_number = int(last_order.order_number.split('-')[1])
                new_number = last_number + 1
            except (IndexError, ValueError):
                new_number = 1
        else:
            new_number = 1
        
        order_number = f"COM-{new_number:03d}"
        
        # Crear el pedido
        order = Order(
            order_number=order_number,
            table_id=table.id,
            waiter_id=session['user_id'],
            status='pending',
            created_at=datetime.utcnow()
        )
        db.session.add(order)
        db.session.flush()  # Para obtener el ID del pedido
        
        # Agregar items al pedido
        total = 0
        for item_data in items:
            product = Product.query.get(item_data['id'])
            if product and product.is_available:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=item_data['cantidad'],
                    unit_price=product.price,
                    modifications=item_data.get('observaciones', ''),
                    estacion=product.station or 'general'
                )
                db.session.add(order_item)
                total += product.price * item_data['cantidad']
        
        order.total = total
        
        # Ocupar la mesa si no está ocupada
        if table.status != 'occupied':
            table.status = 'occupied'
        
        db.session.commit()
        
        return jsonify({
            'success': 'Pedido creado exitosamente',
            'order_id': order.id,
            'total': total
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al crear pedido: {str(e)}'}), 500

@mozo_bp.route('/orders/mesa/<int:mesa_number>')
def get_table_orders(mesa_number):
    """Obtener pedidos de una mesa específica (sin JWT, usa session)"""
    if not check_mozo_auth():
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        table = Table.query.filter_by(number=mesa_number).first()
        if not table:
            return jsonify({'error': 'Mesa no encontrada'}), 404
        
        orders = Order.query.filter_by(table_id=table.id).order_by(Order.created_at.desc()).all()
        orders_data = []
        
        for order in orders:
            order_dict = order.to_dict()
            order_dict['items'] = [item.to_dict() for item in order.items]
            order_dict['waiter_name'] = order.waiter.name if order.waiter else 'Desconocido'
            orders_data.append(order_dict)
        
        return jsonify(orders_data)
    except Exception as e:
        return jsonify({'error': f'Error al obtener pedidos: {str(e)}'}), 500

@mozo_bp.route('/orders/all')
def get_all_orders():
    """Obtener todos los pedidos para seguimiento (sin JWT, usa session)"""
    if not check_mozo_auth():
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        # Obtener pedidos de las últimas 24 horas
        from datetime import datetime, timedelta
        desde = datetime.utcnow() - timedelta(hours=24)
        
        orders = Order.query.filter(
            Order.created_at >= desde
        ).order_by(Order.created_at.desc()).all()
        
        orders_data = []
        for order in orders:
            # Calcular tiempo transcurrido
            tiempo_transcurrido = datetime.utcnow() - order.created_at
            horas = int(tiempo_transcurrido.total_seconds() // 3600)
            minutos = int((tiempo_transcurrido.total_seconds() % 3600) // 60)
            
            if horas > 0:
                tiempo_str = f"{horas}h {minutos}m"
            else:
                tiempo_str = f"{minutos}m"
            
            order_dict = {
                'id': order.id,
                'mesa_numero': order.table.number if order.table else 'Sin mesa',
                'status': order.status,
                'total': float(order.total) if order.total else 0.0,
                'created_at': order.created_at.strftime('%d/%m %H:%M'),
                'tiempo_transcurrido': tiempo_str,
                'waiter_name': order.waiter.name if order.waiter else 'Desconocido',
                'items': []
            }
            
            # Agregar items del pedido
            for item in order.items:
                item_dict = {
                    'product_name': item.product.name if item.product else 'Producto desconocido',
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price) if item.unit_price else 0.0,
                    'modifications': item.modifications or ''
                }
                order_dict['items'].append(item_dict)
            
            orders_data.append(order_dict)
        
        return jsonify(orders_data)
    except Exception as e:
        return jsonify({'error': f'Error al obtener pedidos: {str(e)}'}), 500

@mozo_bp.route('/orders/<int:order_id>/served', methods=['POST'])
def mark_order_served(order_id):
    """Marcar un pedido como servido (sin JWT, usa session)"""
    if not check_mozo_auth():
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        order = Order.query.get_or_404(order_id)
        order.status = 'served'
        db.session.commit()
        
        return jsonify({'success': 'Pedido marcado como servido'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar pedido: {str(e)}'}), 500