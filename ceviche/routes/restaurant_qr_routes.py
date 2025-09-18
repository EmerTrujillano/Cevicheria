"""
Rutas para el sistema QR único del restaurante
"""
from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from services.restaurant_qr_service import restaurant_qr_service
from models import Table
from config.extensions import db

restaurant_qr_bp = Blueprint('restaurant_qr', __name__, url_prefix='/restaurant')


@restaurant_qr_bp.route('/')
def restaurant_home():
    """Página principal accedida desde QR único"""
    return render_template('restaurant/welcome.html')


@restaurant_qr_bp.route('/tables')
def select_table():
    """Página para seleccionar mesa"""
    tables_result = restaurant_qr_service.get_available_tables()
    
    if not tables_result['success']:
        return render_template('restaurant/error.html', 
                             error=tables_result['error'])
    
    return render_template('restaurant/select_table.html', 
                         tables=tables_result['tables'])


@restaurant_qr_bp.route('/api/tables')
def api_get_tables():
    """API para obtener mesas disponibles"""
    return jsonify(restaurant_qr_service.get_available_tables())


@restaurant_qr_bp.route('/api/select-table', methods=['POST'])
def api_select_table():
    """API para seleccionar una mesa"""
    data = request.get_json()
    
    table_number = data.get('table_number')
    customer_name = data.get('customer_name', '')
    
    if not table_number:
        return jsonify({
            'success': False,
            'error': 'Número de mesa requerido'
        }), 400
    
    result = restaurant_qr_service.select_table(table_number, customer_name)
    
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400


@restaurant_qr_bp.route('/table/<int:table_number>')
def table_menu(table_number):
    """Menú para una mesa específica seleccionada"""
    table = Table.query.filter_by(numero=table_number).first()
    
    if not table:
        return render_template('restaurant/error.html', 
                             error='Mesa no encontrada')
    
    if table.status != 'temp_occupied':
        return redirect(url_for('restaurant_qr.select_table'))
    
    # Verificar que la sesión QR aún esté activa
    if not table.is_qr_session_active():
        # Liberar la mesa si la sesión expiró
        table.status = 'available'
        table.qr_session_id = None
        table.qr_expires_at = None
        table.customer_name = None
        db.session.commit()
        
        return render_template('restaurant/session_expired.html')
    
    return render_template('restaurant/menu.html', 
                         table=table,
                         table_number=table_number)


@restaurant_qr_bp.route('/admin/qr')
def admin_generate_qr():
    """Generar QR único para el restaurante (solo admin)"""
    qr_result = restaurant_qr_service.generate_restaurant_qr()
    
    return render_template('restaurant/admin_qr.html', 
                         qr_data=qr_result)


@restaurant_qr_bp.route('/api/generate-qr')
def api_generate_qr():
    """API para generar QR único"""
    return jsonify(restaurant_qr_service.generate_restaurant_qr())


@restaurant_qr_bp.route('/api/table/<int:table_number>/status')
def api_table_status(table_number):
    """Verificar estado de una mesa específica"""
    table = Table.query.filter_by(numero=table_number).first()
    
    if not table:
        return jsonify({
            'success': False,
            'error': 'Mesa no encontrada'
        }), 404
    
    return jsonify({
        'success': True,
        'table_number': table.numero,
        'status': table.status,
        'qr_session_active': table.is_qr_session_active() if hasattr(table, 'is_qr_session_active') else False,
        'time_remaining': table.get_qr_time_remaining() if hasattr(table, 'get_qr_time_remaining') else 0,
        'customer_name': table.customer_name
    })


@restaurant_qr_bp.route('/api/table/<int:table_number>/extend', methods=['POST'])
def api_extend_table_session(table_number):
    """Extender sesión de mesa"""
    table = Table.query.filter_by(numero=table_number).first()
    
    if not table:
        return jsonify({
            'success': False,
            'error': 'Mesa no encontrada'
        }), 404
    
    if table.status != 'temp_occupied':
        return jsonify({
            'success': False,
            'error': 'Mesa no está en uso'
        }), 400
    
    try:
        # Extender por 10 minutos más
        from datetime import datetime, timedelta
        table.qr_expires_at = datetime.utcnow() + timedelta(minutes=10)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sesión extendida por 10 minutos',
            'new_expires_at': table.qr_expires_at.isoformat(),
            'time_remaining': table.get_qr_time_remaining()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Error extendiendo sesión: {str(e)}'
        }), 500