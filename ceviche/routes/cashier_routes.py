from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from models import Order, OrderItem, Product, Table, User
from config.extensions import db
from datetime import datetime
import uuid

cashier_bp = Blueprint('cashier', __name__, url_prefix='/cashier')

def check_cashier_auth():
    """Verificar si el usuario tiene permisos de cajero"""
    return (
        session.get('user_id') and 
        session.get('role') in ['cashier', 'admin']
    )

@cashier_bp.route('/')
def dashboard():
    """Dashboard principal de caja"""
    if not check_cashier_auth():
        return redirect(url_for('main.login_page'))
    return render_template('cashier/dashboard.html')

@cashier_bp.route('/api/open-tables')
def api_open_tables():
    """API para obtener mesas con cuentas abiertas"""
    if not check_cashier_auth():
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

@cashier_bp.route('/api/table/<int:table_id>')
def api_table_details(table_id):
    """API para obtener detalles de una mesa específica"""
    if not check_cashier_auth():
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

@cashier_bp.route('/api/process-payment', methods=['POST'])
def api_process_payment():
    """API para procesar el pago de una mesa"""
    if not check_cashier_auth():
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
        receipt_url = f'/cashier/receipt/{order.id}'
        
        return jsonify({
            'success': True,
            'message': 'Pago procesado exitosamente',
            'receipt_url': receipt_url,
            'order_id': order.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al procesar pago: {str(e)}'}), 500

@cashier_bp.route('/receipt/<int:order_id>')
def receipt(order_id):
    """Generar e imprimir recibo"""
    if not check_cashier_auth():
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

@cashier_bp.route('/reports')
def reports():
    """Reportes de caja"""
    if not check_cashier_auth():
        return redirect(url_for('main.login_page'))
    
    # TODO: Implementar reportes de ventas
    return render_template('cashier/reports.html')