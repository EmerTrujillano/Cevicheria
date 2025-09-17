from models import Table, Zone, Floor
from config.extensions import db
from datetime import datetime

class TableService:
    """Servicio para gestión de mesas"""
    
    @staticmethod
    def get_all_tables_by_location():
        """
        Obtener todas las mesas organizadas por piso y zona
        
        Returns:
            list: Lista organizada de pisos con sus zonas y mesas
        """
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
                        'tables': []
                    }
                    
                    for table in zone.tables:
                        table_data = table.to_dict()
                        
                        # Agregar información de orden actual si existe
                        from models import Order
                        current_order = Order.query.filter_by(
                            table_id=table.id
                        ).filter(
                            Order.status.in_(['pending', 'in_kitchen', 'ready', 'served'])
                        ).first()
                        
                        if current_order:
                            table_data['current_order'] = {
                                'order_number': current_order.order_number,
                                'status': current_order.status,
                                'waiter_name': current_order.waiter.username if current_order.waiter else '',
                                'created_at': current_order.created_at.isoformat(),
                                'total_amount': float(current_order.total_amount)
                            }
                        else:
                            table_data['current_order'] = None
                        
                        zone_data['tables'].append(table_data)
                    
                    floor_data['zones'].append(zone_data)
                
                tables_data.append(floor_data)
            
            return tables_data
            
        except Exception as e:
            return []
    
    @staticmethod
    def update_table_status(table_id, new_status, user_id=None):
        """
        Actualizar estado de una mesa
        
        Args:
            table_id: ID de la mesa
            new_status: Nuevo estado (available, occupied, reserved, cleaning)
            user_id: ID del usuario que hace el cambio (opcional)
        
        Returns:
            dict: Resultado con success, message y data/error
        """
        try:
            table = Table.query.get(table_id)
            if not table:
                return {
                    'success': False,
                    'message': 'Mesa no encontrada'
                }
            
            valid_statuses = ['available', 'occupied', 'reserved', 'cleaning']
            if new_status not in valid_statuses:
                return {
                    'success': False,
                    'message': f'Estado no válido. Estados permitidos: {", ".join(valid_statuses)}'
                }
            
            old_status = table.status
            table.status = new_status
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Estado de mesa actualizado de {old_status} a {new_status}',
                'data': table.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error al actualizar estado de mesa: {str(e)}'
            }
    
    @staticmethod
    def get_available_tables(zone_id=None, capacity=None):
        """
        Obtener mesas disponibles con filtros opcionales
        
        Args:
            zone_id: ID de zona para filtrar (opcional)
            capacity: Capacidad mínima requerida (opcional)
        
        Returns:
            list: Lista de mesas disponibles
        """
        try:
            query = Table.query.filter_by(status='available')
            
            if zone_id:
                query = query.filter_by(zone_id=zone_id)
            
            if capacity:
                query = query.filter(Table.capacity >= capacity)
            
            tables = query.all()
            return [table.to_dict() for table in tables]
            
        except Exception as e:
            return []
    
    @staticmethod
    def get_occupied_tables():
        """
        Obtener todas las mesas ocupadas con información de órdenes
        
        Returns:
            list: Lista de mesas ocupadas con información adicional
        """
        try:
            from models import Order, User
            
            occupied_tables = Table.query.filter_by(status='occupied').all()
            tables_data = []
            
            for table in occupied_tables:
                table_data = table.to_dict()
                
                # Buscar orden activa
                current_order = Order.query.filter_by(
                    table_id=table.id
                ).filter(
                    Order.status.in_(['pending', 'in_kitchen', 'ready', 'served'])
                ).first()
                
                if current_order:
                    table_data['current_order'] = {
                        'order_number': current_order.order_number,
                        'status': current_order.status,
                        'waiter_id': current_order.waiter_id,
                        'waiter_name': current_order.waiter.username if current_order.waiter else '',
                        'customer_name': current_order.customer_name,
                        'created_at': current_order.created_at.isoformat(),
                        'total_amount': float(current_order.total_amount),
                        'items_count': len(current_order.order_items)
                    }
                else:
                    # Mesa marcada como ocupada pero sin orden activa
                    table_data['current_order'] = None
                
                tables_data.append(table_data)
            
            return tables_data
            
        except Exception as e:
            return []
    
    @staticmethod
    def free_table(table_id, user_id=None):
        """
        Liberar una mesa (marcarla como disponible)
        
        Args:
            table_id: ID de la mesa
            user_id: ID del usuario que libera la mesa (opcional)
        
        Returns:
            dict: Resultado con success, message y data/error
        """
        try:
            from models import Order
            
            table = Table.query.get(table_id)
            if not table:
                return {
                    'success': False,
                    'message': 'Mesa no encontrada'
                }
            
            # Verificar que no haya órdenes activas pendientes
            active_orders = Order.query.filter_by(
                table_id=table_id
            ).filter(
                Order.status.in_(['pending', 'in_kitchen', 'ready', 'served'])
            ).count()
            
            if active_orders > 0:
                return {
                    'success': False,
                    'message': 'No se puede liberar la mesa. Hay órdenes activas pendientes.'
                }
            
            table.status = 'available'
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Mesa liberada correctamente',
                'data': table.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error al liberar mesa: {str(e)}'
            }
    
    @staticmethod
    def get_table_history(table_id, days=7):
        """
        Obtener historial de una mesa
        
        Args:
            table_id: ID de la mesa
            days: Número de días hacia atrás para el historial
        
        Returns:
            dict: Historial de la mesa
        """
        try:
            from models import Order, Payment
            from datetime import datetime, timedelta
            
            table = Table.query.get(table_id)
            if not table:
                return {
                    'success': False,
                    'message': 'Mesa no encontrada'
                }
            
            # Calcular fecha límite
            date_limit = datetime.utcnow() - timedelta(days=days)
            
            # Obtener órdenes de la mesa en el período
            orders = Order.query.filter(
                Order.table_id == table_id,
                Order.created_at >= date_limit
            ).order_by(Order.created_at.desc()).all()
            
            orders_data = []
            total_revenue = 0
            
            for order in orders:
                order_data = order.to_dict()
                
                # Agregar información de pago si existe
                if order.payments:
                    payment = order.payments[0]  # Asumiendo un pago por orden
                    order_data['payment'] = payment.to_dict()
                    if order.status == 'paid':
                        total_revenue += float(order.total_amount)
                
                orders_data.append(order_data)
            
            return {
                'success': True,
                'data': {
                    'table': table.to_dict(),
                    'period_days': days,
                    'orders': orders_data,
                    'orders_count': len(orders_data),
                    'total_revenue': total_revenue
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al obtener historial de mesa: {str(e)}'
            }
    
    @staticmethod
    def get_zone_statistics(zone_id=None):
        """
        Obtener estadísticas de zona(s)
        
        Args:
            zone_id: ID de zona específica (opcional, si no se proporciona obtiene todas)
        
        Returns:
            dict: Estadísticas de zonas
        """
        try:
            from models import Order
            from sqlalchemy import func
            from datetime import datetime, timedelta
            
            if zone_id:
                zones = Zone.query.filter_by(id=zone_id).all()
            else:
                zones = Zone.query.all()
            
            zones_stats = []
            today = datetime.utcnow().date()
            
            for zone in zones:
                zone_data = zone.to_dict()
                
                # Estadísticas de mesas
                total_tables = len(zone.tables)
                available_tables = len([t for t in zone.tables if t.status == 'available'])
                occupied_tables = len([t for t in zone.tables if t.status == 'occupied'])
                
                # Órdenes del día en esta zona
                table_ids = [t.id for t in zone.tables]
                
                if table_ids:
                    today_orders = Order.query.filter(
                        Order.table_id.in_(table_ids),
                        func.date(Order.created_at) == today
                    ).count()
                    
                    today_revenue = db.session.query(
                        func.sum(Order.total_amount)
                    ).join(
                        Payment = None,  # Esto necesita ser ajustado según tu estructura
                    ).filter(
                        Order.table_id.in_(table_ids),
                        func.date(Order.created_at) == today,
                        Order.status == 'paid'
                    ).scalar() or 0
                else:
                    today_orders = 0
                    today_revenue = 0
                
                zone_data['statistics'] = {
                    'total_tables': total_tables,
                    'available_tables': available_tables,
                    'occupied_tables': occupied_tables,
                    'occupancy_rate': (occupied_tables / total_tables * 100) if total_tables > 0 else 0,
                    'today_orders': today_orders,
                    'today_revenue': float(today_revenue)
                }
                
                zones_stats.append(zone_data)
            
            return {
                'success': True,
                'data': zones_stats
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al obtener estadísticas de zona: {str(e)}'
            }