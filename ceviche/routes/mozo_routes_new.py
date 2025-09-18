from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from models import User, Product, Category, Table, Order, OrderItem, Zone, Floor
from config.extensions import db
from utils.decorators import role_required
from datetime import datetime

mozo_bp = Blueprint('mozo', __name__, url_prefix='/mozo')

def check_mozo_auth():
    """Verificar autenticación de mozo usando JWT o sesión"""
    # Primer intento: verificar JWT
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        if user_id:
            user = User.query.get(int(user_id))
            if user and user.role == 'mozo':
                # Establecer sesión Flask para compatibilidad
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = user.role
                return True
    except:
        pass
    
    # Segundo intento: verificar sesión Flask
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.role == 'mozo':
            return True
    
    return False

@mozo_bp.route('/')
def mozo_dashboard():
    """Panel principal del mozo"""
    if not check_mozo_auth():
        return redirect(url_for('auth.login_page'))
    return render_template('mozo/dashboard_new.html')

@mozo_bp.route('/api/zones')
def get_zones():
    """Obtener todas las zonas con estadísticas de mesas"""
    if not check_mozo_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        zones = Zone.query.join(Floor).all()
        zones_data = []
        
        for zone in zones:
            # Contar mesas por estado
            available_tables = Table.query.filter_by(zone_id=zone.id, status='available').count()
            occupied_tables = Table.query.filter_by(zone_id=zone.id, status='occupied').count()
            reserved_tables = Table.query.filter_by(zone_id=zone.id, status='reserved').count()
            cleaning_tables = Table.query.filter_by(zone_id=zone.id, status='cleaning').count()
            
            zone_data = {
                'id': zone.id,
                'name': zone.name,
                'description': zone.description,
                'zone_type': zone.zone_type,
                'floor_name': zone.floor.name,
                'available_tables': available_tables,
                'occupied_tables': occupied_tables,
                'reserved_tables': reserved_tables,
                'cleaning_tables': cleaning_tables,
                'total_tables': available_tables + occupied_tables + reserved_tables + cleaning_tables
            }
            zones_data.append(zone_data)
        
        return jsonify({
            'success': True,
            'zones': zones_data
        })
        
    except Exception as e:
        print(f"Error obteniendo zonas: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@mozo_bp.route('/api/zones/<int:zone_id>/tables')
def get_zone_tables(zone_id):
    """Obtener todas las mesas de una zona específica"""
    if not check_mozo_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        zone = Zone.query.get_or_404(zone_id)
        tables = Table.query.filter_by(zone_id=zone_id).order_by(Table.number).all()
        
        tables_data = []
        for table in tables:
            table_data = {
                'id': table.id,
                'number': table.number,
                'capacity': table.capacity,
                'status': table.status,
                'zone_id': zone.id,
                'zone_name': zone.name
            }
            
            # Si está ocupada, obtener info del pedido actual
            if table.status == 'occupied':
                current_order = Order.query.filter_by(
                    table_id=table.id,
                    status='in_progress'
                ).first()
                
                if current_order:
                    table_data['current_order'] = {
                        'id': current_order.id,
                        'created_at': current_order.created_at.isoformat(),
                        'total': float(current_order.total or 0),
                        'items_count': len(current_order.items)
                    }
            
            tables_data.append(table_data)
        
        return jsonify({
            'success': True,
            'zone': {
                'id': zone.id,
                'name': zone.name,
                'description': zone.description,
                'zone_type': zone.zone_type
            },
            'tables': tables_data
        })
        
    except Exception as e:
        print(f"Error obteniendo mesas de zona {zone_id}: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@mozo_bp.route('/api/tables/assign', methods=['POST'])
def assign_table():
    """Asignar una mesa a un cliente"""
    if not check_mozo_auth():
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        table_id = data.get('table_id')
        zone_id = data.get('zone_id')
        
        if not table_id:
            return jsonify({'success': False, 'message': 'ID de mesa requerido'}), 400
        
        table = Table.query.get_or_404(table_id)
        
        if table.status != 'available':
            return jsonify({'success': False, 'message': 'La mesa no está disponible'}), 400
        
        # Cambiar estado de la mesa
        table.status = 'occupied'
        table.occupied_at = datetime.utcnow()
        
        # Crear nuevo pedido
        new_order = Order(
            table_id=table.id,
            waiter_id=session.get('user_id'),  # ID del mozo actual
            status='in_progress',
            total=0.0
        )
        
        db.session.add(new_order)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Mesa {table.number} asignada correctamente',
            'order': {
                'id': new_order.id,
                'table_number': table.number,
                'zone_name': table.zone.name if table.zone else 'Sin zona'
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error asignando mesa: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500