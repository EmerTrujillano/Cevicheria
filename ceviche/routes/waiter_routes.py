from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import role_required
from models import Floor, Zone, Table, Product, Category, Order, OrderItem
from config.extensions import db
from datetime import datetime
import uuid

waiter_bp = Blueprint('waiter', __name__, url_prefix='/waiter')

@waiter_bp.route('/dashboard')
@jwt_required()
@role_required(['waiter', 'admin'])
def dashboard():
    """Dashboard principal para mozos"""
    return render_template('waiter/dashboard.html')

@waiter_bp.route('/tables')
@jwt_required()
@role_required(['waiter', 'admin'])
def get_tables():
    """Obtener todas las mesas organizadas por piso y zona"""
    try:
        floors = Floor.query.all()
        tables_data = []
        
        for floor in floors:
            floor_data = {
                'floor': floor.to_dict(),
                'zones': []
            }
            
            for zone in floor.zones:
                zone_data = {
                    'zone': zone.to_dict(),
                    'tables': [table.to_dict() for table in zone.tables]
                }
                floor_data['zones'].append(zone_data)
            
            tables_data.append(floor_data)
        
        return jsonify({
            'success': True,
            'data': tables_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener las mesas: {str(e)}'
        }), 500

@waiter_bp.route('/tables/<int:table_id>/occupy', methods=['POST'])
@jwt_required()
@role_required(['waiter', 'admin'])
def occupy_table(table_id):
    """Marcar una mesa como ocupada"""
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
            'message': 'Mesa ocupada correctamente',
            'data': table.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al ocupar la mesa: {str(e)}'
        }), 500

@waiter_bp.route('/menu')
@jwt_required()
@role_required(['waiter', 'admin'])
def get_menu():
    """Obtener el menú organizado por categorías para tomar pedidos"""
    try:
        categories = Category.query.all()
        menu_data = []
        
        for category in categories:
            available_products = [
                product.to_dict() for product in category.products 
                if product.is_available
            ]
            
            if available_products:  # Solo incluir categorías con productos disponibles
                category_data = {
                    'category': category.to_dict(),
                    'products': available_products
                }
                menu_data.append(category_data)
        
        return jsonify({
            'success': True,
            'data': menu_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener el menú: {str(e)}'
        }), 500

@waiter_bp.route('/orders', methods=['POST'])
@jwt_required()
@role_required(['waiter', 'admin'])
def create_order():
    """Crear una nueva orden/comanda"""
    try:
        data = request.get_json()
        waiter_id = get_jwt_identity()
        
        # Validar datos requeridos
        required_fields = ['table_id', 'order_type', 'items']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido: {field}'
                }), 400
        
        # Verificar que la mesa esté disponible u ocupada
        table = Table.query.get_or_404(data['table_id'])
        if table.status not in ['available', 'occupied', 'temp_occupied']:
            return jsonify({
                'success': False,
                'message': 'La mesa no está disponible para nuevos pedidos'
            }), 400
        
        # Si hay una sesión QR activa, confirmarla
        qr_session_id = data.get('qr_session_id')
        if table.status == 'temp_occupied' and table.is_qr_session_active():
            if qr_session_id and table.qr_session_id == qr_session_id:
                # Confirmar la mesa (desactivar temporizador QR)
                from services.qr_session_service import QRSessionService
                confirm_result = QRSessionService.confirm_table_order(table.id, qr_session_id)
                if not confirm_result['success']:
                    return jsonify({
                        'success': False,
                        'message': f'Error al confirmar mesa: {confirm_result["message"]}'
                    }), 400
        
        # Generar número de orden único
        order_number = f"COM-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Crear la orden
        order = Order(
            order_number=order_number,
            table_id=data['table_id'],
            waiter_id=waiter_id,
            customer_name=data.get('customer_name', ''),
            order_type=data['order_type'],
            special_instructions=data.get('special_instructions', ''),
            status='pending'
        )
        
        db.session.add(order)
        db.session.flush()  # Para obtener el ID de la orden
        
        total_amount = 0
        
        # Crear los items de la orden
        for item_data in data['items']:
            product = Product.query.get_or_404(item_data['product_id'])
            
            if not product.is_available:
                db.session.rollback()
                return jsonify({
                    'success': False,
                    'message': f'El producto {product.name} no está disponible'
                }), 400
            
            quantity = item_data['quantity']
            unit_price = product.price
            total_price = unit_price * quantity
            total_amount += total_price
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                special_instructions=item_data.get('special_instructions', ''),
                station_type=product.station_type,
                status='pending'
            )
            
            db.session.add(order_item)
        
        # Actualizar el total de la orden
        order.total_amount = total_amount
        
        # Marcar la mesa como ocupada si no lo estaba
        if table.status in ['available', 'temp_occupied']:
            table.status = 'occupied'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Orden creada correctamente',
            'data': {
                'order': order.to_dict(),
                'order_items': [item.to_dict() for item in order.order_items],
                'qr_session_confirmed': qr_session_id is not None
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al crear la orden: {str(e)}'
        }), 500

@waiter_bp.route('/orders/<int:order_id>/status')
@jwt_required()
@role_required(['waiter', 'admin'])
def get_order_status(order_id):
    """Obtener el estado actual de una orden y sus items"""
    try:
        order = Order.query.get_or_404(order_id)
        
        return jsonify({
            'success': True,
            'data': {
                'order': order.to_dict(),
                'items': [item.to_dict() for item in order.order_items]
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener el estado de la orden: {str(e)}'
        }), 500

@waiter_bp.route('/orders/<int:order_id>/items/<int:item_id>/serve', methods=['PATCH'])
@jwt_required()
@role_required(['waiter', 'admin'])
def serve_item(order_id, item_id):
    """Marcar un item como servido/entregado"""
    try:
        order_item = OrderItem.query.filter_by(
            id=item_id, 
            order_id=order_id
        ).first_or_404()
        
        if order_item.status != 'ready':
            return jsonify({
                'success': False,
                'message': 'El item debe estar listo para poder ser servido'
            }), 400
        
        order_item.status = 'served'
        order_item.served_at = datetime.utcnow()
        
        # Verificar si todos los items han sido servidos
        order = order_item.order
        all_served = all(item.status == 'served' for item in order.order_items)
        
        if all_served:
            order.status = 'served'
            order.served_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Item marcado como servido',
            'data': order_item.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al marcar item como servido: {str(e)}'
        }), 500

@waiter_bp.route('/my-orders')
@jwt_required()
@role_required(['waiter', 'admin'])
def get_my_orders():
    """Obtener las órdenes del mozo actual"""
    try:
        waiter_id = get_jwt_identity()
        orders = Order.query.filter_by(waiter_id=waiter_id).order_by(Order.created_at.desc()).all()
        
        orders_data = []
        for order in orders:
            order_data = order.to_dict()
            order_data['items'] = [item.to_dict() for item in order.order_items]
            orders_data.append(order_data)
        
        return jsonify({
            'success': True,
            'data': orders_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener las órdenes: {str(e)}'
        }), 500