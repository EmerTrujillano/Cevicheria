from models import Order, OrderItem, Table, Product
from config.extensions import db
from datetime import datetime
import uuid

class OrderService:
    """Servicio para gestión de órdenes"""
    
    @staticmethod
    def generate_order_number():
        """Generar número único de orden"""
        date_str = datetime.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"COM-{date_str}-{unique_id}"
    
    @staticmethod
    def create_order(waiter_id, table_id, order_type, items_data, customer_name=None, special_instructions=None):
        """
        Crear una nueva orden
        
        Args:
            waiter_id: ID del mozo
            table_id: ID de la mesa (puede ser None para delivery/takeaway)
            order_type: Tipo de orden (dine_in, takeaway, delivery, private_event)
            items_data: Lista de items con product_id, quantity, special_instructions
            customer_name: Nombre del cliente (opcional)
            special_instructions: Instrucciones especiales (opcional)
        
        Returns:
            dict: Resultado con success, message y data/error
        """
        try:
            # Validar que la mesa esté disponible si es necesaria
            if table_id:
                table = Table.query.get(table_id)
                if not table:
                    return {
                        'success': False,
                        'message': 'Mesa no encontrada'
                    }
                
                if table.status not in ['available', 'occupied']:
                    return {
                        'success': False,
                        'message': 'La mesa no está disponible'
                    }
            
            # Crear la orden
            order = Order(
                order_number=OrderService.generate_order_number(),
                table_id=table_id,
                waiter_id=waiter_id,
                customer_name=customer_name,
                order_type=order_type,
                special_instructions=special_instructions,
                status='pending'
            )
            
            db.session.add(order)
            db.session.flush()  # Para obtener el ID
            
            total_amount = 0
            created_items = []
            
            # Crear los items de la orden
            for item_data in items_data:
                product = Product.query.get(item_data['product_id'])
                if not product:
                    db.session.rollback()
                    return {
                        'success': False,
                        'message': f'Producto con ID {item_data["product_id"]} no encontrado'
                    }
                
                if not product.is_available:
                    db.session.rollback()
                    return {
                        'success': False,
                        'message': f'El producto {product.name} no está disponible'
                    }
                
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
                created_items.append(order_item)
            
            # Actualizar total de la orden
            order.total_amount = total_amount
            
            # Marcar mesa como ocupada si es necesario
            if table_id and table.status == 'available':
                table.status = 'occupied'
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Orden creada correctamente',
                'data': {
                    'order': order.to_dict(),
                    'items': [item.to_dict() for item in created_items]
                }
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error al crear orden: {str(e)}'
            }
    
    @staticmethod
    def update_order_status(order_id, new_status, user_id=None):
        """
        Actualizar estado de una orden
        
        Args:
            order_id: ID de la orden
            new_status: Nuevo estado
            user_id: ID del usuario que hace el cambio (opcional)
        
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
            
            old_status = order.status
            order.status = new_status
            
            # Actualizar timestamps según el estado
            if new_status == 'served' and old_status != 'served':
                order.served_at = datetime.utcnow()
            elif new_status == 'paid' and old_status != 'paid':
                order.paid_at = datetime.utcnow()
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Estado de orden actualizado de {old_status} a {new_status}',
                'data': order.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error al actualizar estado de orden: {str(e)}'
            }
    
    @staticmethod
    def update_item_status(item_id, new_status, user_id=None):
        """
        Actualizar estado de un item de orden
        
        Args:
            item_id: ID del item
            new_status: Nuevo estado
            user_id: ID del usuario que hace el cambio (opcional)
        
        Returns:
            dict: Resultado con success, message y data/error
        """
        try:
            order_item = OrderItem.query.get(item_id)
            if not order_item:
                return {
                    'success': False,
                    'message': 'Item no encontrado'
                }
            
            old_status = order_item.status
            order_item.status = new_status
            
            # Actualizar timestamps según el estado
            now = datetime.utcnow()
            if new_status == 'preparing' and old_status in ['pending', 'in_queue']:
                order_item.started_at = now
            elif new_status == 'ready' and old_status == 'preparing':
                order_item.ready_at = now
            elif new_status == 'served' and old_status == 'ready':
                order_item.served_at = now
            
            # Verificar si todos los items de la orden han cambiado de estado
            order = order_item.order
            
            if new_status == 'served':
                # Si todos los items están servidos, marcar orden como servida
                all_served = all(item.status == 'served' for item in order.order_items)
                if all_served and order.status != 'served':
                    order.status = 'served'
                    order.served_at = now
            
            elif new_status == 'ready':
                # Si todos los items están listos, marcar orden como lista
                all_ready = all(item.status in ['ready', 'served'] for item in order.order_items)
                if all_ready and order.status not in ['ready', 'served']:
                    order.status = 'ready'
            
            elif new_status == 'preparing':
                # Si al menos un item está en preparación, marcar orden como en cocina
                if order.status == 'pending':
                    order.status = 'in_kitchen'
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Estado de item actualizado de {old_status} a {new_status}',
                'data': {
                    'item': order_item.to_dict(),
                    'order_status_updated': order.status
                }
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error al actualizar estado de item: {str(e)}'
            }
    
    @staticmethod
    def cancel_item(item_id, reason, user_id=None):
        """
        Cancelar un item de orden
        
        Args:
            item_id: ID del item
            reason: Razón de la cancelación
            user_id: ID del usuario que cancela (opcional)
        
        Returns:
            dict: Resultado con success, message y data/error
        """
        try:
            order_item = OrderItem.query.get(item_id)
            if not order_item:
                return {
                    'success': False,
                    'message': 'Item no encontrado'
                }
            
            if order_item.status in ['served', 'cancelled']:
                return {
                    'success': False,
                    'message': 'El item no puede ser cancelado en su estado actual'
                }
            
            order_item.status = 'cancelled'
            order_item.special_instructions = f"{order_item.special_instructions or ''}\n[CANCELADO: {reason}]".strip()
            
            # Recalcular total de la orden
            order = order_item.order
            new_total = sum(
                item.total_price for item in order.order_items 
                if item.status != 'cancelled'
            )
            order.total_amount = new_total
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Item cancelado correctamente',
                'data': {
                    'item': order_item.to_dict(),
                    'new_order_total': float(new_total)
                }
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error al cancelar item: {str(e)}'
            }
    
    @staticmethod
    def get_orders_by_status(status_list, limit=None):
        """
        Obtener órdenes por estado(s)
        
        Args:
            status_list: Lista de estados a filtrar
            limit: Límite de resultados (opcional)
        
        Returns:
            list: Lista de órdenes que coinciden con los criterios
        """
        try:
            query = Order.query.filter(Order.status.in_(status_list))
            
            if limit:
                query = query.limit(limit)
            
            orders = query.order_by(Order.created_at.desc()).all()
            
            return [order.to_dict() for order in orders]
            
        except Exception as e:
            return []
    
    @staticmethod
    def get_items_by_station(station_type, status_list=['pending', 'in_queue', 'preparing']):
        """
        Obtener items por estación y estado
        
        Args:
            station_type: Tipo de estación (cold, hot, drinks, desserts)
            status_list: Lista de estados a filtrar
        
        Returns:
            list: Lista de items que coinciden con los criterios
        """
        try:
            items = OrderItem.query.join(Order).filter(
                OrderItem.station_type == station_type,
                OrderItem.status.in_(status_list),
                Order.status.in_(['pending', 'in_kitchen'])
            ).order_by(OrderItem.created_at.asc()).all()
            
            items_data = []
            for item in items:
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
            
            return items_data
            
        except Exception as e:
            return []