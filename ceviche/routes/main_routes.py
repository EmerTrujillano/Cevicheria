from flask import Blueprint, render_template, redirect, url_for, jsonify, current_app

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return redirect(url_for('main.login_page'))

@main_bp.route('/login')
def login_page():
    return render_template('login.html')

@main_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main_bp.route('/admin')
def admin_panel():
    return render_template('admin.html')

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
