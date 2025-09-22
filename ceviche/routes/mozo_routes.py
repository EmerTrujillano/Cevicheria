from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
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

@mozo_bp.route('/tables', methods=['GET'])
def tables():
    """API para obtener todas las mesas con sus estados (JSON) o vista de gestión"""
    if not check_mozo_auth():
        # Si es una petición AJAX/JSON, devolver JSON de error
        if request.headers.get('Content-Type') == 'application/json' or 'application/json' in request.headers.get('Accept', ''):
            return jsonify({'success': False, 'message': 'No autorizado'}), 401
        # Si es petición normal del navegador, redirigir al login
        return redirect(url_for('main.login_page'))
    
    # Si es petición AJAX/JSON, devolver datos JSON
    if request.headers.get('Content-Type') == 'application/json' or 'application/json' in request.headers.get('Accept', ''):
        try:
            tables = Table.query.all()
            tables_data = []
            
            for table in tables:
                table_data = {
                    'id': table.id,
                    'number': table.number,
                    'numero': table.number,  # Compatibilidad con frontend viejo
                    'capacity': table.capacity,
                    'status': table.status,
                    'ocupada': table.status == 'ocupada',  # Boolean para compatibilidad
                    'available': table.status == 'libre',  # Boolean para nuevo formato
                    'zone_name': table.zone.name if table.zone else 'Sin zona',
                    'zona': table.zone.name if table.zone else 'Sin zona',  # Compatibilidad
                    'floor_name': table.zone.floor.name if table.zone and table.zone.floor else 'Sin piso',
                    'piso': table.zone.floor.name if table.zone and table.zone.floor else 'Sin piso'  # Compatibilidad
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
                            'created_at': current_order.created_at.isoformat() if current_order.created_at else None,
                            'total': float(current_order.total or 0),
                            'items_count': len(current_order.items) if current_order.items else 0
                        }
                
                tables_data.append(table_data)
            
            return jsonify(tables_data)
            
        except Exception as e:
            print(f"Error obteniendo mesas: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # Si es petición normal del navegador, devolver la template
    return render_template('mozo/tables.html')

@mozo_bp.route('/order/<int:table_id>')
def nuevo_pedido(table_id):
    """Vista para crear un nuevo pedido"""
    if not check_mozo_auth():
        return redirect(url_for('main.login_page'))
    return render_template('mozo/nuevo_pedido.html', table_id=table_id)

@mozo_bp.route('/orders')
def orders():
    """Vista de pedidos del mozo"""
    if not check_mozo_auth():
        return redirect(url_for('main.login_page'))
    return render_template('mozo/orders.html')

@mozo_bp.route('/profile')
def profile():
    """Obtener perfil del mozo actual"""
    if not check_mozo_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'name': user.username  # Usar username como nombre
            }
        })
        
    except Exception as e:
        print(f"Error obteniendo perfil: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@mozo_bp.route('/menu', methods=['GET'])
def get_menu():
    """Obtener menú completo organizado por categorías"""
    if not check_mozo_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        # Obtener todas las categorías con sus productos
        categories = Category.query.all()
        categories_data = []
        
        for category in categories:
            products = Product.query.filter_by(
                category_id=category.id,
                is_available=True
            ).all()
            
            products_data = []
            for product in products:
                product_data = {
                    'id': product.id,
                    'name': product.name,
                    'description': product.description or '',
                    'ingredients': product.ingredients or '',
                    'price': float(product.price),
                    'tags': product.tags.split() if product.tags else [],
                    'category_id': category.id,
                    'category_name': category.name
                }
                products_data.append(product_data)
            
            category_data = {
                'id': category.id,
                'name': category.name,
                'description': category.description or '',
                'products': products_data
            }
            categories_data.append(category_data)
        
        return jsonify({
            'success': True,
            'categories': categories_data
        })
        
    except Exception as e:
        print(f"Error obteniendo menú: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@mozo_bp.route('/create-order', methods=['POST'])
def create_order():
    """Crear un nuevo pedido y enviarlo a cocina"""
    if not check_mozo_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        table_id = data.get('table_id')
        items = data.get('items', [])
        
        if not table_id or not items:
            return jsonify({'success': False, 'message': 'Mesa y productos son requeridos'}), 400
        
        # Verificar que la mesa existe
        table = Table.query.get(table_id)
        if not table:
            return jsonify({'success': False, 'message': 'Mesa no encontrada'}), 404
        
        # PERMITIR pedidos tanto a mesas libres como ocupadas
        # Mesa libre = nuevo pedido (se ocupará automáticamente)
        # Mesa ocupada = agregar al pedido existente
        
        # Calcular total
        total_amount = 0
        order_items_data = []
        
        for item in items:
            product = Product.query.get(item['product_id'])
            if not product:
                return jsonify({'success': False, 'message': f'Producto {item["product_id"]} no encontrado'}), 404
            
            if not product.is_available:
                return jsonify({'success': False, 'message': f'Producto {product.name} no está disponible'}), 400
            
            quantity = item['quantity']
            unit_price = item.get('unit_price', product.price)
            special_instructions = item.get('special_instructions', '')
            item_total = quantity * unit_price
            total_amount += item_total
            
            order_items_data.append({
                'product': product,
                'quantity': quantity,
                'unit_price': unit_price,
                'special_instructions': special_instructions,
                'total_price': item_total
            })
        
        # Generar número de orden único
        import time
        order_number = f"COM-{int(time.time() * 1000) % 100000:05d}"
        
        # Crear el pedido
        new_order = Order(
            order_number=order_number,
            table_id=table_id,
            waiter_id=session.get('user_id'),
            status='pending',
            total_amount=float(total_amount),
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_order)
        db.session.flush()  # Para obtener el ID del pedido
        
        # Crear los items del pedido
        for item_data in order_items_data:
            # Determinar estación de cocina basada en la categoría del producto
            product = item_data['product']
            categoria_name = product.category.name.lower().strip() if product.category else 'general'
            
            # Mapeo de categorías a usuarios de cocina
            categoria_to_cocina = {
                'fríos': 'cocina1',           # Estación: fríos  
                'calientes': 'cocina2',       # Estación: calientes
                'frituras': 'cocina3',        # Estación: frituras
                'bebidas': 'cocina4',         # Estación: bebidas
                'postres': 'cocina5',         # Estación: postres
                'acompañamientos': 'cocina6'  # Estación: acompañamientos
            }
            
            assigned_station = categoria_to_cocina.get(categoria_name, 'cocina1')
            
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item_data['product'].id,
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price'],
                special_instructions=item_data['special_instructions'],
                status='pending'
            )
            
            # Agregar nota sobre estación asignada en las instrucciones
            if item_data['special_instructions']:
                order_item.special_instructions = f"[{assigned_station}] {item_data['special_instructions']}"
            else:
                order_item.special_instructions = f"[{assigned_station}]"
                
            db.session.add(order_item)
        
        # Solo ocupar la mesa si estaba libre (no cambiar estado si ya estaba ocupada)
        if table.status == 'libre':
            table.status = 'ocupada'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pedido creado exitosamente',
            'order_id': new_order.id,
            'total_amount': float(total_amount)
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creando pedido: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@mozo_bp.route('/orders', methods=['GET'])
def get_orders():
    """Obtener pedidos del mozo actual"""
    if not check_mozo_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        waiter_id = session.get('user_id')
        
        # Obtener pedidos del mozo ordenados por fecha
        orders = Order.query.filter_by(waiter_id=waiter_id).order_by(Order.created_at.desc()).all()
        
        orders_data = []
        for order in orders:
            order_data = {
                'id': order.id,
                'table_number': order.table.number if order.table else 'N/A',
                'status': order.status,
                'total_amount': float(order.total_amount or 0),
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'items_count': len(order.items) if order.items else 0
            }
            orders_data.append(order_data)
        
        return jsonify({
            'success': True,
            'orders': orders_data
        })
        
    except Exception as e:
        print(f"Error obteniendo pedidos: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@mozo_bp.route('/order/<int:order_id>', methods=['GET'])
def get_order_details(order_id):
    """Obtener detalles de un pedido específico"""
    if not check_mozo_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'success': False, 'message': 'Pedido no encontrado'}), 404
        
        # Verificar que el pedido pertenece al mozo actual
        if order.waiter_id != session.get('user_id'):
            return jsonify({'success': False, 'message': 'No autorizado para ver este pedido'}), 403
        
        items_data = []
        for item in order.order_items:  # Usar order_items en lugar de items
            # Mapear estado técnico a estado legible para el mozo
            status_mapping = {
                'pending': 'Pendiente',
                'in_queue': 'En Cola',
                'preparing': 'En Preparación',
                'ready': 'Listo',
                'served': 'Entregado'
            }
            
            readable_status = status_mapping.get(item.status, item.status.title())
            
            item_data = {
                'id': item.id,
                'product_name': item.product.name if item.product else 'Producto eliminado',
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'total_price': float(item.total_price),
                'status': item.status,  # Estado técnico
                'status_display': readable_status,  # Estado legible
                'special_instructions': item.special_instructions or '',
                'started_at': item.started_at.strftime('%H:%M') if item.started_at else None,
                'ready_at': item.ready_at.strftime('%H:%M') if item.ready_at else None,
                'served_at': item.served_at.strftime('%H:%M') if item.served_at else None
            }
            items_data.append(item_data)
        
        order_data = {
            'id': order.id,
            'table_number': order.table.number if order.table else 'N/A',
            'status': order.status,
            'total_amount': float(order.total_amount or 0),
            'created_at': order.created_at.isoformat() if order.created_at else None,
            'items': items_data
        }
        
        return jsonify({
            'success': True,
            'order': order_data
        })
        
    except Exception as e:
        print(f"Error obteniendo detalles del pedido: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@mozo_bp.route('/occupy-table', methods=['POST'])
def occupy_table():
    """Marcar una mesa como ocupada sin crear pedido"""
    if not check_mozo_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        table_id = data.get('table_id')
        
        if not table_id:
            return jsonify({'success': False, 'message': 'ID de mesa requerido'}), 400
        
        # Verificar que la mesa existe y esté libre
        table = Table.query.get(table_id)
        if not table:
            return jsonify({'success': False, 'message': 'Mesa no encontrada'}), 404
        
        if table.status != 'libre':
            return jsonify({'success': False, 'message': 'La mesa ya está ocupada'}), 400
        
        # Marcar como ocupada
        table.status = 'ocupada'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Mesa {table.number} marcada como ocupada'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error ocupando mesa: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@mozo_bp.route('/free-table', methods=['POST'])
def free_table():
    """Liberar una mesa (cancelar pedidos activos)"""
    if not check_mozo_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        table_id = data.get('table_id')
        
        if not table_id:
            return jsonify({'success': False, 'message': 'ID de mesa requerido'}), 400
        
        # Verificar que la mesa existe
        table = Table.query.get(table_id)
        if not table:
            return jsonify({'success': False, 'message': 'Mesa no encontrada'}), 404
        
        if table.status == 'libre':
            return jsonify({'success': False, 'message': 'La mesa ya está libre'}), 400
        
        # Cancelar pedidos activos en esta mesa
        active_orders = Order.query.filter_by(
            table_id=table_id,
            status='pending'
        ).all()
        
        for order in active_orders:
            order.status = 'cancelled'
            # También cancelar los items del pedido
            for item in order.items:
                item.status = 'cancelled'
        
        # Marcar mesa como libre
        table.status = 'libre'
        db.session.commit()
        
        orders_cancelled = len(active_orders)
        message = f'Mesa {table.number} liberada'
        if orders_cancelled > 0:
            message += f' ({orders_cancelled} pedido(s) cancelado(s))'
        
        return jsonify({
            'success': True,
            'message': message,
            'orders_cancelled': orders_cancelled
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error liberando mesa: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@mozo_bp.route('/api/mesa/<int:mesa_id>/pedido', methods=['GET'])
def get_mesa_order(mesa_id):
    """Obtener pedido activo de una mesa específica"""
    if not check_mozo_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        table = Table.query.get_or_404(mesa_id)
        
        # Buscar pedido activo de la mesa
        active_order = Order.query.filter_by(
            table_id=mesa_id,
            status='active'
        ).first()
        
        if not active_order:
            return jsonify({'success': False, 'message': 'No hay pedido activo para esta mesa'})
        
        # Obtener items del pedido con detalles
        order_items = OrderItem.query.filter_by(order_id=active_order.id).all()
        
        items_data = []
        for item in order_items:
            items_data.append({
                'producto': item.product.name,
                'cantidad': item.quantity,
                'precio': float(item.product.price),
                'estado': item.status,
                'modificaciones': item.special_instructions or ''
            })
        
        # Calcular total
        total = sum(item['precio'] * item['cantidad'] for item in items_data)
        
        pedido_data = {
            'id': active_order.id,
            'estado': active_order.status,
            'hora': active_order.created_at.strftime('%H:%M') if active_order.created_at else '',
            'total': total,
            'items': items_data
        }
        
        return jsonify({
            'success': True,
            'pedido': pedido_data
        })
        
    except Exception as e:
        print(f"Error obteniendo pedido de mesa: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500