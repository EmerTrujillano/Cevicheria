from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import role_required
from models import Order, OrderItem, User
from config.extensions import db
from datetime import datetime
from sqlalchemy import or_

kitchen_bp = Blueprint('kitchen', __name__, url_prefix='/kitchen')

@kitchen_bp.route('/dashboard')
@jwt_required()
@role_required(['kitchen', 'admin'])
def dashboard():
    """Dashboard principal para cocina"""
    return render_template('kitchen/dashboard.html')

@kitchen_bp.route('/orders')
@jwt_required()
@role_required(['kitchen', 'admin'])
def get_pending_orders():
    """Obtener todas las órdenes pendientes organizadas por estación"""
    try:
        # Obtener items de órdenes que están en estado pending o in_queue
        pending_items = OrderItem.query.join(Order).filter(
            OrderItem.status.in_(['pending', 'in_queue', 'preparing']),
            Order.status.in_(['pending', 'in_kitchen'])
        ).order_by(OrderItem.created_at.asc()).all()
        
        # Organizar por estación
        stations = {
            'cold': [],      # Ceviches, ensaladas, entradas frías
            'hot': [],       # Platos calientes, principales
            'drinks': [],    # Bebidas, jugos
            'desserts': []   # Postres
        }
        
        for item in pending_items:
            station = item.station_type or 'hot'
            item_data = item.to_dict()
            
            # Agregar información de la orden
            order = item.order
            item_data['order_info'] = {
                'order_number': order.order_number,
                'table_number': order.table.number if order.table else 'Delivery/Takeaway',
                'zone_name': order.table.zone.name if order.table and order.table.zone else '',
                'floor_name': order.table.zone.floor.name if order.table and order.table.zone and order.table.zone.floor else '',
                'waiter_name': order.waiter.username if order.waiter else '',
                'order_type': order.order_type,
                'created_at': order.created_at.isoformat(),
                'special_instructions': order.special_instructions
            }
            
            if station in stations:
                stations[station].append(item_data)
            else:
                stations['hot'].append(item_data)  # Default a hot station
        
        return jsonify({
            'success': True,
            'data': stations
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener las órdenes: {str(e)}'
        }), 500

@kitchen_bp.route('/orders/items/<int:item_id>/start', methods=['PATCH'])
@jwt_required()
@role_required(['kitchen', 'admin'])
def start_preparation(item_id):
    """Marcar un item como 'en preparación'"""
    try:
        order_item = OrderItem.query.get_or_404(item_id)
        
        if order_item.status not in ['pending', 'in_queue']:
            return jsonify({
                'success': False,
                'message': 'El item no puede ser marcado como en preparación'
            }), 400
        
        order_item.status = 'preparing'
        order_item.started_at = datetime.utcnow()
        
        # Actualizar el estado de la orden si es necesario
        order = order_item.order
        if order.status == 'pending':
            order.status = 'in_kitchen'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Item marcado como en preparación',
            'data': order_item.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al iniciar preparación: {str(e)}'
        }), 500

@kitchen_bp.route('/orders/items/<int:item_id>/ready', methods=['PATCH'])
@jwt_required()
@role_required(['kitchen', 'admin'])
def mark_ready(item_id):
    """Marcar un item como 'listo para entregar'"""
    try:
        order_item = OrderItem.query.get_or_404(item_id)
        
        if order_item.status != 'preparing':
            return jsonify({
                'success': False,
                'message': 'El item debe estar en preparación para marcarlo como listo'
            }), 400
        
        order_item.status = 'ready'
        order_item.ready_at = datetime.utcnow()
        
        # Verificar si todos los items de la orden están listos
        order = order_item.order
        all_ready = all(item.status in ['ready', 'served'] for item in order.order_items)
        
        if all_ready:
            order.status = 'ready'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Item marcado como listo',
            'data': order_item.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al marcar como listo: {str(e)}'
        }), 500

@kitchen_bp.route('/orders/items/<int:item_id>/cancel', methods=['PATCH'])
@jwt_required()
@role_required(['kitchen', 'admin'])
def cancel_item(item_id):
    """Cancelar un item de la orden"""
    try:
        data = request.get_json()
        reason = data.get('reason', 'Cancelado desde cocina')
        
        order_item = OrderItem.query.get_or_404(item_id)
        
        if order_item.status in ['served', 'cancelled']:
            return jsonify({
                'success': False,
                'message': 'El item no puede ser cancelado en su estado actual'
            }), 400
        
        order_item.status = 'cancelled'
        order_item.special_instructions = f"{order_item.special_instructions or ''}\n[CANCELADO: {reason}]".strip()
        
        # Recalcular el total de la orden
        order = order_item.order
        new_total = sum(
            item.total_price for item in order.order_items 
            if item.status != 'cancelled'
        )
        order.total_amount = new_total
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Item cancelado correctamente',
            'data': order_item.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al cancelar el item: {str(e)}'
        }), 500

@kitchen_bp.route('/orders/history')
@jwt_required()
@role_required(['kitchen', 'admin'])
def get_orders_history():
    """Obtener historial de órdenes completadas, canceladas o modificadas"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Obtener órdenes finalizadas del día
        today = datetime.utcnow().date()
        orders = Order.query.filter(
            or_(
                Order.status.in_(['served', 'paid', 'cancelled']),
                Order.created_at >= today
            )
        ).order_by(Order.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        orders_data = []
        for order in orders.items:
            order_data = order.to_dict()
            order_data['items'] = [item.to_dict() for item in order.order_items]
            orders_data.append(order_data)
        
        return jsonify({
            'success': True,
            'data': {
                'orders': orders_data,
                'pagination': {
                    'page': orders.page,
                    'pages': orders.pages,
                    'per_page': orders.per_page,
                    'total': orders.total
                }
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener el historial: {str(e)}'
        }), 500

@kitchen_bp.route('/stations/<station_type>')
@jwt_required()
@role_required(['kitchen', 'admin'])
def get_station_orders(station_type):
    """Obtener órdenes específicas de una estación"""
    try:
        valid_stations = ['cold', 'hot', 'drinks', 'desserts']
        if station_type not in valid_stations:
            return jsonify({
                'success': False,
                'message': 'Tipo de estación no válido'
            }), 400
        
        # Obtener items pendientes de la estación específica
        pending_items = OrderItem.query.join(Order).filter(
            OrderItem.status.in_(['pending', 'in_queue', 'preparing']),
            OrderItem.station_type == station_type,
            Order.status.in_(['pending', 'in_kitchen'])
        ).order_by(OrderItem.created_at.asc()).all()
        
        items_data = []
        for item in pending_items:
            item_data = item.to_dict()
            
            # Agregar información de la orden
            order = item.order
            item_data['order_info'] = {
                'order_number': order.order_number,
                'table_number': order.table.number if order.table else 'Delivery/Takeaway',
                'zone_name': order.table.zone.name if order.table and order.table.zone else '',
                'floor_name': order.table.zone.floor.name if order.table and order.table.zone and order.table.zone.floor else '',
                'waiter_name': order.waiter.username if order.waiter else '',
                'order_type': order.order_type,
                'created_at': order.created_at.isoformat(),
                'special_instructions': order.special_instructions
            }
            
            items_data.append(item_data)
        
        return jsonify({
            'success': True,
            'data': items_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener órdenes de la estación: {str(e)}'
        }), 500

@kitchen_bp.route('/orders/ready')
@jwt_required()
@role_required(['kitchen', 'admin'])
def get_ready_orders():
    """Obtener órdenes listas para entrega"""
    try:
        ready_items = OrderItem.query.join(Order).filter(
            OrderItem.status == 'ready'
        ).order_by(OrderItem.ready_at.asc()).all()
        
        # Agrupar por orden
        orders_dict = {}
        for item in ready_items:
            order_id = item.order_id
            if order_id not in orders_dict:
                order = item.order
                orders_dict[order_id] = {
                    'order': order.to_dict(),
                    'ready_items': []
                }
            orders_dict[order_id]['ready_items'].append(item.to_dict())
        
        return jsonify({
            'success': True,
            'data': list(orders_dict.values())
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener órdenes listas: {str(e)}'
        }), 500