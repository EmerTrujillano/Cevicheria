from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Order, Payment
from config.extensions import db
from utils.decorators import role_required
from datetime import datetime
import qrcode
import io
import base64

caja_bp = Blueprint('caja', __name__, url_prefix='/caja')

def check_caja_auth():
    """Verificar autenticación de caja usando sesión"""
    if 'user_id' not in session:
        return False
    
    user = User.query.get(session['user_id'])
    if not user or user.role not in ['cajero', 'cashier', 'admin']:  # Permitir múltiples roles
        return False
    
    return True

@caja_bp.route('/')
def caja_dashboard():
    """Panel principal de caja - nueva interfaz moderna"""
    if not check_caja_auth():
        return redirect(url_for('main.login_page'))
    return render_template('cashier/dashboard.html')  # Usar nueva interfaz

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

# ==========================================
# NUEVAS RUTAS API PARA INTERFAZ MODERNA
# ==========================================

@caja_bp.route('/api/open-tables')
def api_open_tables():
    """API para obtener mesas con cuentas abiertas"""
    if not check_caja_auth():
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        # Obtener órdenes que están listas para cobro (estados: ready, served)
        orders = Order.query.filter(
            Order.status.in_(['ready', 'served']),
            Order.payment_status.in_(['pending'])
        ).all()
        
        tables_data = []
        for order in orders:
            # Calcular total de la orden
            total = sum(item.quantity * item.product.price for item in order.order_items)
            
            # Contar items
            items_count = sum(item.quantity for item in order.order_items)
            
            # Obtener nombre del mozo
            waiter_name = None
            if order.waiter_id:
                waiter = User.query.get(order.waiter_id)
                waiter_name = waiter.username if waiter else None
            
            tables_data.append({
                'id': order.id,
                'number': order.table.number if order.table else 'N/A',
                'total': float(total),
                'waiter_name': waiter_name,
                'items_count': items_count,
                'created_at': order.created_at.strftime('%H:%M') if order.created_at else '',
                'status': order.status
            })
        
        return jsonify({
            'success': True,
            'tables': tables_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Error al cargar mesas: {str(e)}'}), 500

@caja_bp.route('/api/table/<int:table_id>')
def api_table_details(table_id):
    """API para obtener detalles de una mesa específica"""
    if not check_caja_auth():
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        # Buscar la orden por ID (table_id es realmente order_id)
        order = Order.query.get_or_404(table_id)
        
        # Verificar que esté en estado para cobro
        if order.status not in ['ready', 'served'] or order.payment_status != 'pending':
            return jsonify({'error': 'Esta mesa no está lista para cobro'}), 400
        
        # Calcular total
        total = sum(item.quantity * item.product.price for item in order.order_items)
        
        # Preparar items
        items_data = []
        for item in order.order_items:
            items_data.append({
                'id': item.id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'price': float(item.product.price),
                'subtotal': float(item.quantity * item.product.price),
                'special_instructions': item.special_instructions
            })
        
        # Obtener datos del mozo
        waiter_name = None
        if order.waiter_id:
            waiter = User.query.get(order.waiter_id)
            waiter_name = waiter.username if waiter else None
        
        table_data = {
            'id': order.id,
            'number': order.table.number if order.table else 'N/A',
            'total': float(total),
            'waiter_name': waiter_name,
            'items': items_data,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M') if order.created_at else '',
            'status': order.status
        }
        
        return jsonify({
            'success': True,
            'table': table_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Error al cargar detalles: {str(e)}'}), 500

@caja_bp.route('/api/process-payment', methods=['POST'])
def api_process_payment():
    """API para procesar el pago de una mesa"""
    if not check_caja_auth():
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        order_id = data.get('table_id')  # Es realmente order_id
        payment_method = data.get('payment_method')
        amount_received = data.get('amount_received', 0)
        change = data.get('change', 0)
        
        if not order_id or not payment_method:
            return jsonify({'error': 'Datos incompletos'}), 400
        
        # Buscar la orden
        order = Order.query.get_or_404(order_id)
        
        # Verificar que esté en estado para cobro
        if order.status not in ['ready', 'served'] or order.payment_status != 'pending':
            return jsonify({'error': 'Esta mesa ya fue cobrada o no está lista'}), 400
        
        # Calcular total real
        total = sum(item.quantity * item.product.price for item in order.order_items)
        
        # Validar monto para efectivo
        if payment_method == 'efectivo' and amount_received < total:
            return jsonify({'error': 'Monto insuficiente'}), 400
        
        # Actualizar orden
        order.payment_status = 'paid'
        order.payment_method = payment_method
        order.paid_at = datetime.utcnow()
        order.cashier_id = session['user_id']
        
        # Si todos los items están servidos, marcar orden como completada
        if all(item.status == 'served' for item in order.order_items):
            order.status = 'completed'
        
        # Crear registro de pago (opcional, podrías crear una tabla Payment)
        # Por ahora guardamos en la orden
        order.amount_received = amount_received
        order.change_given = change
        
        db.session.commit()
        
        # Generar URL del recibo (implementar después)
        receipt_url = f'/caja/receipt/{order.id}'
        
        return jsonify({
            'success': True,
            'message': 'Pago procesado exitosamente',
            'receipt_url': receipt_url,
            'order_id': order.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al procesar pago: {str(e)}'}), 500

@caja_bp.route('/receipt/<int:order_id>')
def receipt(order_id):
    """Generar e imprimir recibo"""
    if not check_caja_auth():
        return redirect(url_for('main.login_page'))
    
    try:
        order = Order.query.get_or_404(order_id)
        
        if order.payment_status != 'paid':
            return "Esta orden no ha sido pagada", 400
        
        # Calcular total
        total = sum(item.quantity * item.product.price for item in order.order_items)
        
        # Datos para el recibo
        receipt_data = {
            'order': order,
            'total': total,
            'items': order.order_items,
            'cashier': User.query.get(order.cashier_id) if order.cashier_id else None,
            'waiter': User.query.get(order.waiter_id) if order.waiter_id else None
        }
        
        return render_template('cashier/receipt.html', **receipt_data)
    
    except Exception as e:
        return f"Error al generar recibo: {str(e)}", 500

@caja_bp.route('/api/generate-payment-qr/<int:table_id>')
def generate_payment_qr(table_id):
    """Generar QR code para pagos de Yape/Plin"""
    if not check_caja_auth():
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        # Obtener la orden de la mesa
        order = Order.query.filter_by(
            table_id=table_id,
            status='served',
            payment_status='pending'
        ).first()
        
        if not order:
            return jsonify({'error': 'Mesa no encontrada o ya pagada'}), 404
        
        # Calcular total
        total = sum(item.quantity * item.product.price for item in order.order_items)
        
        # Crear datos para el QR (formato común para Yape/Plin)
        # En un entorno real, esto sería la URL o datos específicos de la pasarela de pago
        payment_data = f"cevicheria-pago:{order.id}:{total:.2f}"
        
        # Generar QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(payment_data)
        qr.make(fit=True)
        
        # Crear imagen del QR
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        img_buffer = io.BytesIO()
        qr_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'qr_image': f'data:image/png;base64,{img_str}',
            'payment_data': payment_data,
            'total': total,
            'order_id': order.id
        })
        
    except Exception as e:
        return jsonify({'error': f'Error al generar QR: {str(e)}'}), 500