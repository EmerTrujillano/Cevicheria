from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import role_required
from models import Order, OrderItem, Payment, Table
from config.extensions import db
from datetime import datetime, date
from sqlalchemy import and_, func

cashier_bp = Blueprint('cashier', __name__, url_prefix='/cashier')

@cashier_bp.route('/dashboard')
@jwt_required()
@role_required(['cashier', 'admin'])
def dashboard():
    """Dashboard principal para cajeros"""
    return render_template('cashier/dashboard.html')

@cashier_bp.route('/orders/ready-to-pay')
@jwt_required()
@role_required(['cashier', 'admin'])
def get_orders_ready_to_pay():
    """Obtener órdenes listas para cobrar"""
    try:
        # Obtener órdenes que están servidas pero no pagadas
        orders = Order.query.filter(
            Order.status.in_(['served', 'ready']),
            ~Order.payments.any(Payment.id.isnot(None))  # No tienen pagos
        ).order_by(Order.served_at.desc()).all()
        
        orders_data = []
        for order in orders:
            order_data = order.to_dict()
            order_data['items'] = [item.to_dict() for item in order.order_items if item.status != 'cancelled']
            # Recalcular total excluyendo items cancelados
            order_data['current_total'] = sum(
                item.total_price for item in order.order_items if item.status != 'cancelled'
            )
            orders_data.append(order_data)
        
        return jsonify({
            'success': True,
            'data': orders_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener órdenes para cobrar: {str(e)}'
        }), 500

@cashier_bp.route('/orders/<int:order_id>/pay', methods=['POST'])
@jwt_required()
@role_required(['cashier', 'admin'])
def process_payment(order_id):
    """Procesar el pago de una orden"""
    try:
        data = request.get_json()
        cashier_id = get_jwt_identity()
        
        # Validar datos requeridos
        required_fields = ['payment_method', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Campo requerido: {field}'
                }), 400
        
        order = Order.query.get_or_404(order_id)
        
        # Verificar que la orden esté lista para pagar
        if order.status not in ['served', 'ready']:
            return jsonify({
                'success': False,
                'message': 'La orden no está lista para ser cobrada'
            }), 400
        
        # Verificar que no haya sido pagada ya
        if order.payments:
            return jsonify({
                'success': False,
                'message': 'Esta orden ya ha sido pagada'
            }), 400
        
        # Calcular total actual (excluyendo items cancelados)
        current_total = sum(
            float(item.total_price) for item in order.order_items 
            if item.status != 'cancelled'
        )
        
        payment_amount = float(data['amount'])
        
        # Validar que el monto sea correcto
        if payment_amount < current_total:
            return jsonify({
                'success': False,
                'message': f'El monto pagado ({payment_amount}) es menor al total de la orden ({current_total})'
            }), 400
        
        # Crear el registro de pago
        payment = Payment(
            order_id=order.id,
            amount=payment_amount,
            payment_method=data['payment_method'],
            cashier_id=cashier_id,
            transaction_id=data.get('transaction_id'),
            notes=data.get('notes', '')
        )
        
        db.session.add(payment)
        
        # Actualizar el estado de la orden
        order.status = 'paid'
        order.paid_at = datetime.utcnow()
        
        # Liberar la mesa si es para consumo en mesa
        if order.table and order.order_type == 'dine_in':
            order.table.status = 'available'
        
        db.session.commit()
        
        # Calcular cambio si es necesario
        change = payment_amount - current_total if payment_amount > current_total else 0
        
        return jsonify({
            'success': True,
            'message': 'Pago procesado correctamente',
            'data': {
                'payment': payment.to_dict(),
                'order': order.to_dict(),
                'change': float(change),
                'table_freed': order.table.status == 'available' if order.table else False
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al procesar el pago: {str(e)}'
        }), 500

@cashier_bp.route('/payments/history')
@jwt_required()
@role_required(['cashier', 'admin'])
def get_payments_history():
    """Obtener historial de pagos con filtros"""
    try:
        # Parámetros de filtrado
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        payment_method = request.args.get('payment_method')
        waiter_id = request.args.get('waiter_id', type=int)
        
        # Construir query base
        query = Payment.query.join(Order)
        
        # Aplicar filtros
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                query = query.filter(func.date(Payment.created_at) >= date_from)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                query = query.filter(func.date(Payment.created_at) <= date_to)
            except ValueError:
                pass
        
        if payment_method:
            query = query.filter(Payment.payment_method == payment_method)
        
        if waiter_id:
            query = query.filter(Order.waiter_id == waiter_id)
        
        # Solo para cajeros: filtrar por sus propios pagos
        current_user_role = getattr(request, 'current_user_role', None)
        if current_user_role == 'cashier':
            cashier_id = get_jwt_identity()
            query = query.filter(Payment.cashier_id == cashier_id)
        
        # Paginar resultados
        payments = query.order_by(Payment.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        payments_data = []
        for payment in payments.items:
            payment_data = payment.to_dict()
            # Agregar información adicional de la orden
            order = payment.order
            payment_data['order_details'] = {
                'table_number': order.table.number if order.table else 'Delivery/Takeaway',
                'zone_name': order.table.zone.name if order.table and order.table.zone else '',
                'order_type': order.order_type,
                'items_count': len([item for item in order.order_items if item.status != 'cancelled'])
            }
            payments_data.append(payment_data)
        
        return jsonify({
            'success': True,
            'data': {
                'payments': payments_data,
                'pagination': {
                    'page': payments.page,
                    'pages': payments.pages,
                    'per_page': payments.per_page,
                    'total': payments.total
                }
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener historial de pagos: {str(e)}'
        }), 500

@cashier_bp.route('/sales/summary')
@jwt_required()
@role_required(['cashier', 'admin'])
def get_sales_summary():
    """Obtener resumen de ventas del día"""
    try:
        today = date.today()
        
        # Ventas del día por método de pago
        sales_by_method = db.session.query(
            Payment.payment_method,
            func.count(Payment.id).label('count'),
            func.sum(Payment.amount).label('total')
        ).filter(
            func.date(Payment.created_at) == today
        ).group_by(Payment.payment_method).all()
        
        # Total general del día
        total_sales = db.session.query(
            func.sum(Payment.amount)
        ).filter(
            func.date(Payment.created_at) == today
        ).scalar() or 0
        
        # Número de órdenes pagadas
        orders_count = db.session.query(
            func.count(Payment.id)
        ).filter(
            func.date(Payment.created_at) == today
        ).scalar() or 0
        
        # Solo para cajeros: sus propias ventas
        current_user_role = getattr(request, 'current_user_role', None)
        if current_user_role == 'cashier':
            cashier_id = get_jwt_identity()
            
            my_sales = db.session.query(
                func.sum(Payment.amount)
            ).filter(
                func.date(Payment.created_at) == today,
                Payment.cashier_id == cashier_id
            ).scalar() or 0
            
            my_orders_count = db.session.query(
                func.count(Payment.id)
            ).filter(
                func.date(Payment.created_at) == today,
                Payment.cashier_id == cashier_id
            ).scalar() or 0
        
        sales_summary = {
            'date': today.isoformat(),
            'total_sales': float(total_sales),
            'orders_count': orders_count,
            'sales_by_method': [
                {
                    'method': method,
                    'count': count,
                    'total': float(total)
                }
                for method, count, total in sales_by_method
            ]
        }
        
        # Agregar datos personales para cajeros
        if current_user_role == 'cashier':
            sales_summary['my_sales'] = float(my_sales)
            sales_summary['my_orders_count'] = my_orders_count
        
        return jsonify({
            'success': True,
            'data': sales_summary
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener resumen de ventas: {str(e)}'
        }), 500

@cashier_bp.route('/orders/<int:order_id>/details')
@jwt_required()
@role_required(['cashier', 'admin'])
def get_order_details(order_id):
    """Obtener detalles completos de una orden para el cobro"""
    try:
        order = Order.query.get_or_404(order_id)
        
        order_data = order.to_dict()
        order_data['items'] = [
            item.to_dict() for item in order.order_items 
            if item.status != 'cancelled'
        ]
        
        # Calcular totales actuales
        order_data['current_total'] = sum(
            item.total_price for item in order.order_items 
            if item.status != 'cancelled'
        )
        
        order_data['cancelled_items'] = [
            item.to_dict() for item in order.order_items 
            if item.status == 'cancelled'
        ]
        
        # Verificar si ya tiene pagos
        order_data['payments'] = [payment.to_dict() for payment in order.payments]
        order_data['is_paid'] = len(order.payments) > 0
        
        return jsonify({
            'success': True,
            'data': order_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener detalles de la orden: {str(e)}'
        }), 500