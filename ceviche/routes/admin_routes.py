from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.decorators import role_required
from models import (Floor, Zone, Table, Product, Category, Order, OrderItem, 
                   Payment, User, Review)
from config.extensions import db
from datetime import datetime, date
from sqlalchemy import func, and_, or_
import uuid

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@jwt_required()
@role_required(['admin'])
def dashboard():
    """Dashboard principal para administradores"""
    return render_template('admin/dashboard.html')

# === GESTIÓN DE ESTRUCTURA DEL LOCAL ===

@admin_bp.route('/floors', methods=['GET', 'POST'])
@jwt_required()
@role_required(['admin'])
def manage_floors():
    """Gestionar pisos del local"""
    if request.method == 'GET':
        floors = Floor.query.all()
        floors_data = []
        
        for floor in floors:
            floor_data = floor.to_dict()
            floor_data['zones'] = [zone.to_dict() for zone in floor.zones]
            floors_data.append(floor_data)
        
        return jsonify({
            'success': True,
            'data': floors_data
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            floor = Floor(
                name=data['name'],
                description=data.get('description', '')
            )
            
            db.session.add(floor)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Piso creado correctamente',
                'data': floor.to_dict()
            })
        
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Error al crear piso: {str(e)}'
            }), 500

@admin_bp.route('/zones', methods=['GET', 'POST'])
@jwt_required()
@role_required(['admin'])
def manage_zones():
    """Gestionar zonas del local"""
    if request.method == 'GET':
        zones = Zone.query.all()
        return jsonify({
            'success': True,
            'data': [zone.to_dict() for zone in zones]
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            zone = Zone(
                name=data['name'],
                description=data.get('description', ''),
                floor_id=data['floor_id'],
                zone_type=data.get('zone_type', 'dining')
            )
            
            db.session.add(zone)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Zona creada correctamente',
                'data': zone.to_dict()
            })
        
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Error al crear zona: {str(e)}'
            }), 500

@admin_bp.route('/tables', methods=['GET', 'POST'])
@jwt_required()
@role_required(['admin'])
def manage_tables():
    """Gestionar mesas del local"""
    if request.method == 'GET':
        tables = Table.query.all()
        return jsonify({
            'success': True,
            'data': [table.to_dict() for table in tables]
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Generar código QR único
            qr_code = f"/menu/qr/{data['number']}"
            
            table = Table(
                number=data['number'],
                capacity=data.get('capacity', 4),
                zone_id=data['zone_id'],
                qr_code=qr_code
            )
            
            db.session.add(table)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Mesa creada correctamente',
                'data': table.to_dict()
            })
        
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Error al crear mesa: {str(e)}'
            }), 500

# === GESTIÓN DE PRODUCTOS Y MENÚ ===

@admin_bp.route('/products/<int:product_id>/availability', methods=['PATCH'])
@jwt_required()
@role_required(['admin'])
def toggle_product_availability(product_id):
    """Marcar producto como disponible/agotado"""
    try:
        product = Product.query.get_or_404(product_id)
        product.is_available = not product.is_available
        
        db.session.commit()
        
        status = 'disponible' if product.is_available else 'agotado'
        return jsonify({
            'success': True,
            'message': f'Producto marcado como {status}',
            'data': product.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al actualizar disponibilidad: {str(e)}'
        }), 500

@admin_bp.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
@role_required(['admin'])
def update_product(product_id):
    """Actualizar información de un producto"""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        # Actualizar campos permitidos
        allowed_fields = ['name', 'description', 'price', 'ingredients', 'tags', 
                         'image_url', 'image_gallery', 'station_type', 
                         'preparation_time', 'spice_level', 'category_id']
        
        for field in allowed_fields:
            if field in data:
                setattr(product, field, data[field])
        
        product.last_updated = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Producto actualizado correctamente',
            'data': product.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al actualizar producto: {str(e)}'
        }), 500

# === MONITOREO EN TIEMPO REAL ===

@admin_bp.route('/monitor/tables')
@jwt_required()
@role_required(['admin'])
def monitor_tables():
    """Monitor del estado de todas las mesas"""
    try:
        floors = Floor.query.all()
        monitor_data = []
        
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
                    
                    # Agregar información de la orden actual si existe
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
                            'total_amount': float(current_order.total_amount),
                            'created_at': current_order.created_at.isoformat()
                        }
                    else:
                        table_data['current_order'] = None
                    
                    zone_data['tables'].append(table_data)
                
                floor_data['zones'].append(zone_data)
            
            monitor_data.append(floor_data)
        
        return jsonify({
            'success': True,
            'data': monitor_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener monitor de mesas: {str(e)}'
        }), 500

@admin_bp.route('/monitor/orders')
@jwt_required()
@role_required(['admin'])
def monitor_orders():
    """Monitor de todas las órdenes activas"""
    try:
        active_orders = Order.query.filter(
            Order.status.in_(['pending', 'in_kitchen', 'ready', 'served'])
        ).order_by(Order.created_at.desc()).all()
        
        orders_data = []
        for order in active_orders:
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
            'message': f'Error al obtener monitor de órdenes: {str(e)}'
        }), 500

# === REPORTES Y ESTADÍSTICAS ===

@admin_bp.route('/reports/sales')
@jwt_required()
@role_required(['admin'])
def sales_report():
    """Reporte de ventas"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Por defecto, ventas del día actual
        if not date_from:
            date_from = date.today()
        else:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        
        if not date_to:
            date_to = date_from
        else:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        # Ventas totales por día
        daily_sales = db.session.query(
            func.date(Payment.created_at).label('date'),
            func.sum(Payment.amount).label('total'),
            func.count(Payment.id).label('orders_count')
        ).filter(
            and_(
                func.date(Payment.created_at) >= date_from,
                func.date(Payment.created_at) <= date_to
            )
        ).group_by(func.date(Payment.created_at)).all()
        
        # Ventas por método de pago
        payment_methods = db.session.query(
            Payment.payment_method,
            func.sum(Payment.amount).label('total'),
            func.count(Payment.id).label('count')
        ).filter(
            and_(
                func.date(Payment.created_at) >= date_from,
                func.date(Payment.created_at) <= date_to
            )
        ).group_by(Payment.payment_method).all()
        
        # Productos más vendidos
        top_products = db.session.query(
            Product.name,
            func.sum(OrderItem.quantity).label('quantity_sold'),
            func.sum(OrderItem.total_price).label('revenue')
        ).join(OrderItem).join(Order).join(Payment).filter(
            and_(
                func.date(Payment.created_at) >= date_from,
                func.date(Payment.created_at) <= date_to,
                OrderItem.status != 'cancelled'
            )
        ).group_by(Product.id, Product.name).order_by(
            func.sum(OrderItem.quantity).desc()
        ).limit(10).all()
        
        # Ventas por mozo
        waiter_sales = db.session.query(
            User.username,
            func.sum(Payment.amount).label('total'),
            func.count(Payment.id).label('orders_count')
        ).join(Order, Order.waiter_id == User.id).join(Payment).filter(
            and_(
                func.date(Payment.created_at) >= date_from,
                func.date(Payment.created_at) <= date_to
            )
        ).group_by(User.id, User.username).order_by(
            func.sum(Payment.amount).desc()
        ).all()
        
        report_data = {
            'period': {
                'from': date_from.isoformat(),
                'to': date_to.isoformat()
            },
            'daily_sales': [
                {
                    'date': sale.date.isoformat(),
                    'total': float(sale.total),
                    'orders_count': sale.orders_count
                }
                for sale in daily_sales
            ],
            'payment_methods': [
                {
                    'method': method.payment_method,
                    'total': float(method.total),
                    'count': method.count
                }
                for method in payment_methods
            ],
            'top_products': [
                {
                    'name': product.name,
                    'quantity_sold': product.quantity_sold,
                    'revenue': float(product.revenue)
                }
                for product in top_products
            ],
            'waiter_sales': [
                {
                    'waiter': waiter.username,
                    'total': float(waiter.total),
                    'orders_count': waiter.orders_count
                }
                for waiter in waiter_sales
            ]
        }
        
        return jsonify({
            'success': True,
            'data': report_data
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al generar reporte: {str(e)}'
        }), 500

# === GESTIÓN DE USUARIOS ===

@admin_bp.route('/users', methods=['GET', 'POST'])
@jwt_required()
@role_required(['admin'])
def manage_users():
    """Gestionar usuarios del sistema"""
    if request.method == 'GET':
        users = User.query.filter(User.role != 'admin').all()
        return jsonify({
            'success': True,
            'data': [user.to_dict() for user in users]
        })
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Verificar que el username no exista
            if User.query.filter_by(username=data['username']).first():
                return jsonify({
                    'success': False,
                    'message': 'El nombre de usuario ya existe'
                }), 400
            
            user = User(
                username=data['username'],
                password=data['password'],  # En producción, hashear la contraseña
                role=data['role']
            )
            
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Usuario creado correctamente',
                'data': user.to_dict()
            })
        
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Error al crear usuario: {str(e)}'
            }), 500

@admin_bp.route('/users/<int:user_id>/role', methods=['PATCH'])
@jwt_required()
@role_required(['admin'])
def update_user_role(user_id):
    """Actualizar el rol de un usuario"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # No permitir cambiar el rol de administradores
        if user.role == 'admin':
            return jsonify({
                'success': False,
                'message': 'No se puede cambiar el rol de un administrador'
            }), 400
        
        user.role = data['role']
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Rol actualizado correctamente',
            'data': user.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al actualizar rol: {str(e)}'
        }), 500

# === GESTIÓN DE SESIONES QR ===

@admin_bp.route('/qr-sessions')
@jwt_required()
@role_required(['admin'])
def get_active_qr_sessions():
    """Obtener todas las sesiones QR activas"""
    try:
        from services.qr_session_service import QRSessionService
        
        active_sessions = QRSessionService.get_active_qr_sessions()
        
        return jsonify({
            'success': True,
            'data': active_sessions,
            'count': len(active_sessions)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener sesiones QR: {str(e)}'
        }), 500

@admin_bp.route('/qr-sessions/<int:table_id>/end', methods=['POST'])
@jwt_required()
@role_required(['admin'])
def end_qr_session(table_id):
    """Finalizar manualmente una sesión QR"""
    try:
        table = Table.query.get_or_404(table_id)
        
        if table.status != 'temp_occupied':
            return jsonify({
                'success': False,
                'message': 'La mesa no tiene una sesión QR activa'
            }), 400
        
        table.end_qr_session()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sesión QR finalizada manualmente',
            'data': table.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al finalizar sesión QR: {str(e)}'
        }), 500

# === GESTIÓN DE RESEÑAS ===

@admin_bp.route('/reviews/pending')
@jwt_required()
@role_required(['admin'])
def get_pending_reviews():
    """Obtener reseñas pendientes de aprobación"""
    try:
        pending_reviews = Review.query.filter_by(is_approved=False).order_by(
            Review.created_at.desc()
        ).all()
        
        return jsonify({
            'success': True,
            'data': [review.to_dict() for review in pending_reviews]
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al obtener reseñas pendientes: {str(e)}'
        }), 500

@admin_bp.route('/reviews/<int:review_id>/approve', methods=['PATCH'])
@jwt_required()
@role_required(['admin'])
def approve_review(review_id):
    """Aprobar una reseña"""
    try:
        review = Review.query.get_or_404(review_id)
        admin_id = get_jwt_identity()
        
        review.is_approved = True
        review.approved_at = datetime.utcnow()
        review.approved_by = admin_id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Reseña aprobada correctamente',
            'data': review.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al aprobar reseña: {str(e)}'
        }), 500