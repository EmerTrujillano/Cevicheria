from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Order, Payment
from config.extensions import db
from utils.decorators import role_required
from datetime import datetime

caja_bp = Blueprint('caja', __name__, url_prefix='/caja')

def check_caja_auth():
    """Verificar autenticación de caja usando sesión"""
    if 'user_id' not in session:
        return False
    
    user = User.query.get(session['user_id'])
    if not user or user.role != 'cashier':
        return False
    
    return True

@caja_bp.route('/')
def caja_dashboard():
    """Panel principal de caja"""
    if not check_caja_auth():
        return redirect(url_for('main.login_page'))
    return render_template('caja/dashboard.html')

@caja_bp.route('/ventas')
def ventas():
    """Vista de ventas y pagos"""
    if not check_caja_auth():
        return redirect(url_for('main.login_page'))
    return render_template('caja/ventas.html')

# APIs para caja (mantienen JWT)
@caja_bp.route('/api/orders/pending')
@jwt_required()
@role_required(['cashier', 'admin'])
def get_pending_orders():
    """Obtener pedidos pendientes de pago"""
    try:
        orders = Order.query.filter_by(payment_status='pending').all()
        orders_data = [order.to_dict() for order in orders]
        
        return jsonify({
            'success': True,
            'data': orders_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener pedidos: {str(e)}'
        }), 500

@caja_bp.route('/api/payment', methods=['POST'])
@jwt_required()
@role_required(['cashier', 'admin'])
def process_payment():
    """Procesar pago de un pedido"""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        payment_method = data.get('payment_method')
        amount = data.get('amount')
        
        if not order_id or not payment_method or not amount:
            return jsonify({
                'success': False,
                'message': 'Datos de pago incompletos'
            }), 400
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({
                'success': False,
                'message': 'Pedido no encontrado'
            }), 404
        
        # Crear registro de pago
        payment = Payment(
            order_id=order_id,
            amount=amount,
            payment_method=payment_method,
            payment_date=datetime.utcnow(),
            processed_by=get_jwt_identity()
        )
        
        # Actualizar estado del pedido
        order.payment_status = 'paid'
        order.status = 'completed'
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pago procesado exitosamente',
            'payment_id': payment.id
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al procesar pago: {str(e)}'
        }), 500