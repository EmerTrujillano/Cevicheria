from flask import Blueprint, render_template, redirect, url_for, jsonify, current_app, request
from models import Table
from config.extensions import db
from datetime import datetime, timedelta
from services.table_service import TableService

main_bp = Blueprint('main', __name__)

@main_bp.route('/login', methods=['GET'])
def login_page():
    """Renderiza el formulario de login"""
    return render_template('login.html')

@main_bp.route('/')
def index():
    return redirect(url_for('main.login_page'))


@main_bp.route('/test-login')
def test_login_page():
    return render_template('test_login.html')

# RUTAS COMENTADAS - DASHBOARD ELIMINADO PARA REDISEÑO
# Las vistas específicas de roles se crearán posteriormente

# RUTAS COMENTADAS - CONFLICTAN CON BLUEPRINTS ESPECÍFICOS
# @main_bp.route('/admin')
# def admin_panel():
#     return render_template('admin.html')

@main_bp.route('/superadmin')
def superadmin_panel():
    return render_template('superadmin.html')

@main_bp.route('/api/temporary-permissions')
def temporary_permissions_compatibility():
    """Endpoint de compatibilidad para templates antiguos"""
    return jsonify({
        'temporary_permissions': [],
        'message': 'Sistema actualizado: usar /api/permissions/temporary-permissions'
    }), 200

@main_bp.route('/api/tables/occupy-temporarily', methods=['POST'])
def occupy_table_temporarily():
    """Marcar una mesa como temporalmente ocupada por escaneo de QR"""
    try:
        data = request.get_json()
        table_id = data.get('table_id')
        
        if not table_id:
            return jsonify({
                'success': False,
                'message': 'ID de mesa requerido'
            }), 400
            
        table = Table.query.get(table_id)
        if not table:
            return jsonify({
                'success': False,
                'message': 'Mesa no encontrada'
            }), 404
            
        # Solo iniciar sesión QR si está disponible
        if table.status == 'available':
            session_id = table.start_qr_session(session_duration_minutes=10)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Mesa marcada como temporalmente ocupada',
                'data': {
                    'table_id': table.id,
                    'status': table.status,
                    'session_id': session_id,
                    'expires_at': table.qr_expires_at.isoformat() if table.qr_expires_at else None,
                    'time_remaining': table.get_qr_time_remaining()
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': f'La mesa está {table.status}',
                'data': {
                    'table_id': table.id,
                    'status': table.status,
                    'is_qr_active': table.is_qr_session_active(),
                    'time_remaining': table.get_qr_time_remaining()
                }
            })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error al marcar mesa: {str(e)}'
        }), 500

@main_bp.route('/api/tables/cleanup-expired', methods=['POST'])
def cleanup_expired_tables():
    """Limpiar mesas con sesiones QR expiradas"""
    try:
        cleaned_count = TableService.cleanup_expired_qr_sessions()
        
        return jsonify({
            'success': True,
            'message': f'Se limpiaron {cleaned_count} mesas expiradas',
            'data': {
                'cleaned_count': cleaned_count
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al limpiar mesas: {str(e)}'
        }), 500
