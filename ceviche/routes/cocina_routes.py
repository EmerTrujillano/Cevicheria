from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Product, Category, Order, OrderItem
from config.extensions import db
from utils.decorators import role_required
from datetime import datetime

cocina_bp = Blueprint('cocina', __name__, url_prefix='/cocina')

def check_cocina_auth():
    """Verificar autenticación de cocina usando sesión"""
    if 'user_id' not in session:
        return False
    
    user = User.query.get(session['user_id'])
    if not user or user.role != 'cocina':  # Cambié 'kitchen' por 'cocina'
        return False
    
    return True

@cocina_bp.route('/')
def cocina_dashboard():
    """Panel Kanban de cocina"""
    if not check_cocina_auth():
        return redirect(url_for('main.login_page'))
    return render_template('cocina/kanban.html')

@cocina_bp.route('/kanban')
def cocina_kanban():
    """Panel Kanban de cocina (alias para compatibilidad)"""
    if not check_cocina_auth():
        return redirect(url_for('main.login_page'))
    return render_template('cocina/kanban.html')

@cocina_bp.route('/api/kanban')
def api_kanban():
    """API para obtener datos del Kanban de cocina filtrados por estación"""
    if not check_cocina_auth():
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Determinar estación del usuario
        username_to_station = {
            'cocina1': 'fríos',
            'cocina2': 'calientes', 
            'cocina3': 'frituras',
            'cocina4': 'bebidas',
            'cocina5': 'postres',
            'cocina6': 'acompañamientos'
        }
        
        user_station = username_to_station.get(user.username, 'general')
        cocina_user = user.username  # cocina1, cocina2, etc.
        
        # Obtener items de pedidos activos que corresponden a esta estación
        order_items = OrderItem.query.join(Order).join(Product).filter(
            Order.status.in_(['pending', 'in_kitchen', 'ready']),
            OrderItem.special_instructions.like(f'%[{cocina_user}]%')
        ).all()
        
        # Crear lista plana para el kanban
        kanban_items = []
        for item in order_items:
            # Determinar estado del item para kanban
            kanban_estado = 'pendiente'  # Por defecto en cola
            if item.order.status == 'in_kitchen':
                kanban_estado = 'preparando'
            elif item.order.status == 'ready':
                kanban_estado = 'listo'
                
            # Limpiar las instrucciones para mostrar solo las del cliente
            instrucciones_limpias = item.special_instructions or ''
            if f'[{cocina_user}]' in instrucciones_limpias:
                instrucciones_limpias = instrucciones_limpias.replace(f'[{cocina_user}]', '').strip()
                
            kanban_items.append({
                'id': item.id,
                'order_id': item.order.id,
                'mesa_numero': item.order.table.number if item.order.table else 'N/A',
                'producto_nombre': item.product.name,
                'cantidad': item.quantity,
                'estado': kanban_estado,
                'tiempo_creacion': item.order.created_at.strftime('%H:%M') if item.order.created_at else '',
                'modificaciones': instrucciones_limpias
            })
        
        return jsonify(kanban_items)
    except Exception as e:
        return jsonify({'error': f'Error al cargar kanban: {str(e)}'}), 500

@cocina_bp.route('/update-status', methods=['POST'])
def update_status():
    """Actualizar estado de item en kanban"""
    if not check_cocina_auth():
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        nuevo_estado = data.get('estado')
        
        if not item_id or not nuevo_estado:
            return jsonify({'success': False, 'error': 'ID del item y estado son requeridos'}), 400
        
        order_item = OrderItem.query.get_or_404(item_id)
        
        # Agregar campo kitchen_status si no existe
        if not hasattr(order_item, 'kitchen_status'):
            # Simulamos el estado por ahora - en producción se haría una migración
            pass
        
        # Mapear estados del kanban a estados de la orden
        if nuevo_estado == 'preparando':
            order_item.order.status = 'in_kitchen'
        elif nuevo_estado == 'listo':
            order_item.order.status = 'ready'
        elif nuevo_estado == 'entregado':
            order_item.order.status = 'served'
        
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Error: {str(e)}'}), 500

@cocina_bp.route('/profile')
def get_cocina_profile():
    """Obtener perfil de cocina con estación determinada por username"""
    if not check_cocina_auth():
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Determinar estación basada en el username
        username_to_station = {
            'cocina1': 'frios',
            'cocina2': 'calientes', 
            'cocina3': 'frituras',
            'cocina4': 'postres',
            'cocina5': 'bebidas',
            'cocina6': 'general'
        }
        
        estacion = username_to_station.get(user.username, 'general')
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'estacion': estacion
            }
        })
    except Exception as e:
        return jsonify({'error': f'Error al obtener perfil: {str(e)}'}), 500

# APIs para cocina
@cocina_bp.route('/api/pedidos-estacion')
@jwt_required()
@role_required('cocina')
def get_pedidos_estacion():
    """Obtener pedidos para la estación del usuario"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user.estacion:
            return jsonify({
                'success': False,
                'message': 'Usuario no tiene estación asignada'
            }), 400
        
        # Obtener items de pedidos para esta estación
        order_items = OrderItem.query.join(Order).filter(
            OrderItem.station_type == user.estacion,
            Order.status.in_(['pending', 'in_progress'])
        ).all()
        
        # Organizar por estado
        pedidos_kanban = {
            'en_cola': [],
            'en_preparacion': [],
            'listo': [],
            'entregado': [],
            'cancelado': []
        }
        
        for item in order_items:
            item_data = {
                'id': item.id,
                'order_id': item.order.id,
                'producto': item.product.name,
                'cantidad': item.quantity,
                'modificaciones': item.special_instructions,
                'mesa': item.order.table.number if item.order.table else 'N/A',
                'tiempo_creacion': item.created_at.isoformat() if hasattr(item, 'created_at') else None,
                'estado': getattr(item, 'status', 'pending')
            }
            
            # Mapear estados a columnas del Kanban
            estado = getattr(item, 'status', 'pending')
            if estado == 'pending':
                pedidos_kanban['en_cola'].append(item_data)
            elif estado == 'in_progress':
                pedidos_kanban['en_preparacion'].append(item_data)
            elif estado == 'ready':
                pedidos_kanban['listo'].append(item_data)
            elif estado == 'delivered':
                pedidos_kanban['entregado'].append(item_data)
            elif estado == 'cancelled':
                pedidos_kanban['cancelado'].append(item_data)
        
        return jsonify({
            'success': True,
            'data': {
                'estacion': user.estacion,
                'pedidos': pedidos_kanban
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener pedidos: {str(e)}'
        }), 500

@cocina_bp.route('/api/cambiar-estado', methods=['POST'])
@jwt_required()
@role_required('cocina')
def cambiar_estado():
    """Cambiar estado de un item de pedido"""
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        nuevo_estado = data.get('estado')
        
        if not item_id or not nuevo_estado:
            return jsonify({
                'success': False,
                'message': 'ID del item y estado son requeridos'
            }), 400
        
        # Verificar que el usuario puede modificar este item
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        order_item = OrderItem.query.get_or_404(item_id)
        
        if order_item.estacion != user.estacion:
            return jsonify({
                'success': False,
                'message': 'No tienes permisos para modificar este item'
            }), 403
        
        # Actualizar estado
        if hasattr(order_item, 'status'):
            order_item.status = nuevo_estado
        else:
            # Si no existe el campo status, agregarlo dinámicamente
            # (esto requeriría una migración de BD en un caso real)
            pass
        
        # Actualizar timestamp de modificación
        if hasattr(order_item, 'updated_at'):
            order_item.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Estado cambiado a {nuevo_estado}'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al cambiar estado: {str(e)}'
        }), 500

@cocina_bp.route('/api/marcar-listo/<int:item_id>', methods=['POST'])
@jwt_required()
@role_required('cocina')
def marcar_listo(item_id):
    """Marcar item como listo para entregar"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        order_item = OrderItem.query.get_or_404(item_id)
        
        if order_item.estacion != user.estacion:
            return jsonify({
                'success': False,
                'message': 'No tienes permisos para modificar este item'
            }), 403
        
        # Marcar como listo
        if hasattr(order_item, 'status'):
            order_item.status = 'ready'
        
        if hasattr(order_item, 'updated_at'):
            order_item.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Plato marcado como listo'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al marcar como listo: {str(e)}'
        }), 500
