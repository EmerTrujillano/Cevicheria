from models import Payment, Order
from config.extensions import db
from datetime import datetime

class PaymentService:
    """Servicio para gestión de pagos"""
    
    @staticmethod
    def process_payment(order_id, payment_data, cashier_id):
        """
        Procesar un pago
        
        Args:
            order_id: ID de la orden
            payment_data: Datos del pago (amount, payment_method, etc.)
            cashier_id: ID del cajero
        
        Returns:
            dict: Resultado con success, message y data/error
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                return {
                    'success': False,
                    'message': 'Orden no encontrada'
                }
            
            # Verificar que la orden esté lista para pagar
            if order.status not in ['served', 'ready']:
                return {
                    'success': False,
                    'message': 'La orden no está lista para ser cobrada'
                }
            
            # Verificar que no haya sido pagada ya
            if order.payments:
                return {
                    'success': False,
                    'message': 'Esta orden ya ha sido pagada'
                }
            
            # Calcular total actual (excluyendo items cancelados)
            current_total = sum(
                float(item.total_price) for item in order.order_items 
                if item.status != 'cancelled'
            )
            
            payment_amount = float(payment_data['amount'])
            
            # Validar que el monto sea correcto
            if payment_amount < current_total:
                return {
                    'success': False,
                    'message': f'El monto pagado ({payment_amount}) es menor al total de la orden ({current_total})'
                }
            
            # Crear el registro de pago
            payment = Payment(
                order_id=order.id,
                amount=payment_amount,
                payment_method=payment_data['payment_method'],
                cashier_id=cashier_id,
                transaction_id=payment_data.get('transaction_id'),
                notes=payment_data.get('notes', '')
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
            
            return {
                'success': True,
                'message': 'Pago procesado correctamente',
                'data': {
                    'payment': payment.to_dict(),
                    'order': order.to_dict(),
                    'change': float(change),
                    'table_freed': order.table.status == 'available' if order.table else False
                }
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error al procesar el pago: {str(e)}'
            }
    
    @staticmethod
    def get_payment_methods():
        """
        Obtener métodos de pago disponibles
        
        Returns:
            list: Lista de métodos de pago
        """
        return [
            {'id': 'cash', 'name': 'Efectivo', 'icon': 'fa-money-bill'},
            {'id': 'card', 'name': 'Tarjeta', 'icon': 'fa-credit-card'},
            {'id': 'transfer', 'name': 'Transferencia', 'icon': 'fa-exchange-alt'},
            {'id': 'mobile', 'name': 'Pago móvil', 'icon': 'fa-mobile-alt'}
        ]
    
    @staticmethod
    def get_daily_sales_summary(date=None, cashier_id=None):
        """
        Obtener resumen de ventas diarias
        
        Args:
            date: Fecha específica (opcional, por defecto hoy)
            cashier_id: ID del cajero para filtrar (opcional)
        
        Returns:
            dict: Resumen de ventas
        """
        try:
            from sqlalchemy import func, and_
            from datetime import date as date_type
            
            if date is None:
                date = datetime.utcnow().date()
            elif isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d').date()
            
            # Query base
            query = Payment.query.filter(func.date(Payment.created_at) == date)
            
            if cashier_id:
                query = query.filter(Payment.cashier_id == cashier_id)
            
            # Ventas totales
            total_sales = query.with_entities(func.sum(Payment.amount)).scalar() or 0
            total_orders = query.count()
            
            # Ventas por método de pago
            sales_by_method = db.session.query(
                Payment.payment_method,
                func.count(Payment.id).label('count'),
                func.sum(Payment.amount).label('total')
            ).filter(func.date(Payment.created_at) == date)
            
            if cashier_id:
                sales_by_method = sales_by_method.filter(Payment.cashier_id == cashier_id)
            
            sales_by_method = sales_by_method.group_by(Payment.payment_method).all()
            
            # Ventas por hora
            hourly_sales = db.session.query(
                func.extract('hour', Payment.created_at).label('hour'),
                func.count(Payment.id).label('count'),
                func.sum(Payment.amount).label('total')
            ).filter(func.date(Payment.created_at) == date)
            
            if cashier_id:
                hourly_sales = hourly_sales.filter(Payment.cashier_id == cashier_id)
            
            hourly_sales = hourly_sales.group_by(
                func.extract('hour', Payment.created_at)
            ).order_by(
                func.extract('hour', Payment.created_at)
            ).all()
            
            return {
                'success': True,
                'data': {
                    'date': date.isoformat(),
                    'total_sales': float(total_sales),
                    'total_orders': total_orders,
                    'average_order_value': float(total_sales / total_orders) if total_orders > 0 else 0,
                    'sales_by_method': [
                        {
                            'method': method.payment_method,
                            'count': method.count,
                            'total': float(method.total),
                            'percentage': float(method.total / total_sales * 100) if total_sales > 0 else 0
                        }
                        for method in sales_by_method
                    ],
                    'hourly_sales': [
                        {
                            'hour': int(hour.hour),
                            'count': hour.count,
                            'total': float(hour.total)
                        }
                        for hour in hourly_sales
                    ]
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al obtener resumen de ventas: {str(e)}'
            }
    
    @staticmethod
    def get_cashier_performance(cashier_id, date_from=None, date_to=None):
        """
        Obtener rendimiento de un cajero
        
        Args:
            cashier_id: ID del cajero
            date_from: Fecha inicio (opcional)
            date_to: Fecha fin (opcional)
        
        Returns:
            dict: Estadísticas del cajero
        """
        try:
            from sqlalchemy import func, and_
            from datetime import datetime, timedelta
            
            if date_from is None:
                date_from = datetime.utcnow().date()
            elif isinstance(date_from, str):
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            
            if date_to is None:
                date_to = date_from
            elif isinstance(date_to, str):
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            
            # Pagos del cajero en el período
            payments = Payment.query.filter(
                and_(
                    Payment.cashier_id == cashier_id,
                    func.date(Payment.created_at) >= date_from,
                    func.date(Payment.created_at) <= date_to
                )
            ).all()
            
            if not payments:
                return {
                    'success': True,
                    'data': {
                        'cashier_id': cashier_id,
                        'period': {
                            'from': date_from.isoformat(),
                            'to': date_to.isoformat()
                        },
                        'total_sales': 0,
                        'total_orders': 0,
                        'average_order_value': 0,
                        'sales_by_method': [],
                        'daily_performance': []
                    }
                }
            
            # Calcular estadísticas
            total_sales = sum(float(p.amount) for p in payments)
            total_orders = len(payments)
            average_order_value = total_sales / total_orders if total_orders > 0 else 0
            
            # Agrupar por método de pago
            method_stats = {}
            for payment in payments:
                method = payment.payment_method
                if method not in method_stats:
                    method_stats[method] = {'count': 0, 'total': 0}
                method_stats[method]['count'] += 1
                method_stats[method]['total'] += float(payment.amount)
            
            # Agrupar por día
            daily_stats = {}
            for payment in payments:
                day = payment.created_at.date()
                if day not in daily_stats:
                    daily_stats[day] = {'count': 0, 'total': 0}
                daily_stats[day]['count'] += 1
                daily_stats[day]['total'] += float(payment.amount)
            
            return {
                'success': True,
                'data': {
                    'cashier_id': cashier_id,
                    'period': {
                        'from': date_from.isoformat(),
                        'to': date_to.isoformat()
                    },
                    'total_sales': total_sales,
                    'total_orders': total_orders,
                    'average_order_value': average_order_value,
                    'sales_by_method': [
                        {
                            'method': method,
                            'count': stats['count'],
                            'total': stats['total'],
                            'percentage': (stats['total'] / total_sales * 100) if total_sales > 0 else 0
                        }
                        for method, stats in method_stats.items()
                    ],
                    'daily_performance': [
                        {
                            'date': day.isoformat(),
                            'count': stats['count'],
                            'total': stats['total']
                        }
                        for day, stats in sorted(daily_stats.items())
                    ]
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al obtener rendimiento del cajero: {str(e)}'
            }
    
    @staticmethod
    def void_payment(payment_id, reason, user_id):
        """
        Anular un pago (solo administradores)
        
        Args:
            payment_id: ID del pago
            reason: Razón de la anulación
            user_id: ID del usuario que anula
        
        Returns:
            dict: Resultado con success, message y data/error
        """
        try:
            payment = Payment.query.get(payment_id)
            if not payment:
                return {
                    'success': False,
                    'message': 'Pago no encontrado'
                }
            
            order = payment.order
            
            # Marcar el pago como anulado (agregar campo si es necesario)
            payment.notes = f"{payment.notes}\n[ANULADO: {reason} - Usuario: {user_id}]".strip()
            
            # Revertir el estado de la orden
            order.status = 'served' if order.served_at else 'ready'
            order.paid_at = None
            
            # Reocupar la mesa si es necesario
            if order.table and order.order_type == 'dine_in':
                order.table.status = 'occupied'
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Pago anulado correctamente',
                'data': {
                    'payment': payment.to_dict(),
                    'order': order.to_dict()
                }
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error al anular pago: {str(e)}'
            }