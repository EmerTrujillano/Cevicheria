from flask import Blueprint, jsonify, request
from utils.decorators import user_or_higher, get_user_permissions, has_area_access, SYSTEM_AREAS
from models import Product, Category, User, TemporaryPermission
from config.extensions import db
from datetime import datetime
import pytz

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/info', methods=['GET'])
@user_or_higher
def get_dashboard_info(current_user):
    """Información del dashboard según el rol del usuario"""
    try:
        # Obtener permisos del usuario
        user_permissions = []
        temp_permissions = []
        
        # Revisar todas las áreas del sistema
        for area, config in SYSTEM_AREAS.items():
            # Verificar acceso por defecto según el rol
            has_default_access = current_user.role in config['default_roles']
            
            # Verificar permisos temporales activos
            lima_tz = pytz.timezone('America/Lima')
            now_lima = datetime.now(lima_tz)
            now_utc = now_lima.astimezone(pytz.UTC).replace(tzinfo=None)
            
            temp_perm = TemporaryPermission.query.filter_by(
                user_id=current_user.id,
                area=area,
                is_active=True
            ).filter(TemporaryPermission.expires_at > now_utc).first()
            
            if has_default_access or temp_perm:
                user_permissions.append(area)
                
                if temp_perm:
                    expires_at_lima = pytz.UTC.localize(temp_perm.expires_at).astimezone(lima_tz)
                    time_remaining = str(expires_at_lima - now_lima).split('.')[0] if expires_at_lima > now_lima else 'Expirado'
                    
                    temp_permissions.append({
                        'area': area,
                        'expires_at': expires_at_lima.isoformat(),
                        'time_remaining': time_remaining,
                        'granted_by': User.query.get(temp_perm.granted_by).username if User.query.get(temp_perm.granted_by) else 'Desconocido'
                    })
        
        dashboard_data = {
            'user_info': {
                'id': current_user.id,
                'username': current_user.username,
                'role': current_user.role,
                'areas_allowed': user_permissions,
                'temporary_permissions': temp_permissions
            },
            'available_modules': {},
            'module_states': {}  # Para manejar estado de cards (expandido/colapsado)
        }
        
        # INVENTARIO - Todos pueden ver
        if 'inventario' in user_permissions:
            products_count = Product.query.count()
            dashboard_data['available_modules']['inventario'] = {
                'id': 'inventario',
                'name': 'Inventario',
                'description': 'Gestión de productos e inventario',
                'icon': 'inventory',
                'color': 'primary',
                'is_collapsible': True,
                'default_expanded': True,
                'access_type': 'default' if current_user.role in SYSTEM_AREAS['inventario']['default_roles'] else 'temporal',
                'stats': {
                    'total_products': products_count,
                    'products_with_stock': Product.query.filter(Product.stock > 0).count(),
                    'products_without_stock': Product.query.filter(Product.stock == 0).count(),
                    'can_modify': current_user.role in ['admin', 'superadmin']
                },
                'actions': [
                    {'name': 'Ver Productos', 'endpoint': '/api/products', 'method': 'GET', 'icon': 'visibility'},
                    {'name': 'Buscar Producto', 'endpoint': '/api/products/search', 'method': 'GET', 'icon': 'search'}
                ]
            }
            
            if current_user.role in ['admin', 'superadmin']:
                dashboard_data['available_modules']['inventario']['actions'].extend([
                    {'name': 'Agregar Producto', 'endpoint': '/api/products', 'method': 'POST', 'icon': 'add'},
                    {'name': 'Editar Producto', 'endpoint': '/api/products/<id>', 'method': 'PUT', 'icon': 'edit'},
                    {'name': 'Eliminar Producto', 'endpoint': '/api/products/<id>', 'method': 'DELETE', 'icon': 'delete'}
                ])
        
        # CATEGORÍAS - Solo admin y superadmin
        if 'categorias' in user_permissions:
            categories_count = Category.query.count()
            dashboard_data['available_modules']['categorias'] = {
                'id': 'categorias',
                'name': 'Categorías',
                'description': 'Gestión de categorías de productos',
                'icon': 'category',
                'color': 'secondary',
                'is_collapsible': True,
                'default_expanded': False,
                'access_type': 'default' if current_user.role in SYSTEM_AREAS['categorias']['default_roles'] else 'temporal',
                'stats': {
                    'total_categories': categories_count
                },
                'actions': [
                    {'name': 'Ver Categorías', 'endpoint': '/api/categories', 'method': 'GET', 'icon': 'visibility'},
                    {'name': 'Agregar Categoría', 'endpoint': '/api/categories', 'method': 'POST', 'icon': 'add'},
                    {'name': 'Editar Categoría', 'endpoint': '/api/categories/<id>', 'method': 'PUT', 'icon': 'edit'},
                    {'name': 'Eliminar Categoría', 'endpoint': '/api/categories/<id>', 'method': 'DELETE', 'icon': 'delete'}
                ]
            }
        
        # USUARIOS Y ROLES - Solo superadmin
        if 'usuarios' in user_permissions:
            users_count = User.query.count()
            dashboard_data['available_modules']['usuarios'] = {
                'id': 'usuarios',
                'name': 'Usuarios',
                'description': 'Gestión de usuarios del sistema',
                'icon': 'people',
                'color': 'success',
                'is_collapsible': True,
                'default_expanded': False,
                'access_type': 'default' if current_user.role in SYSTEM_AREAS['usuarios']['default_roles'] else 'temporal',
                'stats': {
                    'total_users': users_count,
                    'admins': User.query.filter_by(role='admin').count(),
                    'regular_users': User.query.filter_by(role='user').count(),
                    'superadmins': User.query.filter_by(role='superadmin').count()
                },
                'actions': [
                    {'name': 'Ver Usuarios', 'endpoint': '/api/users/list', 'method': 'GET', 'icon': 'visibility'},
                    {'name': 'Crear Usuario', 'endpoint': '/api/users', 'method': 'POST', 'icon': 'person_add'},
                    {'name': 'Cambiar Rol', 'endpoint': '/api/users/<id>/role', 'method': 'PUT', 'icon': 'security'},
                    {'name': 'Eliminar Usuario', 'endpoint': '/api/users/<id>', 'method': 'DELETE', 'icon': 'delete'}
                ]
            }
        
        if 'roles' in user_permissions:
            dashboard_data['available_modules']['permisos'] = {
                'id': 'permisos',
                'name': 'Permisos Temporales',
                'description': 'Gestión de permisos temporales',
                'icon': 'security',
                'color': 'warning',
                'is_collapsible': True,
                'default_expanded': False,
                'access_type': 'default' if current_user.role in SYSTEM_AREAS['roles']['default_roles'] else 'temporal',
                'actions': [
                    {'name': 'Ver Permisos Activos', 'endpoint': '/api/permissions/active', 'method': 'GET', 'icon': 'visibility'},
                    {'name': 'Otorgar Permiso', 'endpoint': '/api/permissions/grant-multiple', 'method': 'POST', 'icon': 'add_moderator'},
                    {'name': 'Revocar Permiso', 'endpoint': '/api/permissions/<id>', 'method': 'DELETE', 'icon': 'remove_moderator'}
                ]
            }
        
        # REPORTES - Admin y superadmin
        if 'reportes' in user_permissions:
            dashboard_data['available_modules']['reportes'] = {
                'id': 'reportes',
                'name': 'Reportes',
                'description': 'Reportes y estadísticas del sistema',
                'icon': 'analytics',
                'color': 'info',
                'is_collapsible': True,
                'default_expanded': False,
                'access_type': 'default' if current_user.role in SYSTEM_AREAS['reportes']['default_roles'] else 'temporal',
                'actions': [
                    {'name': 'Ver Estadísticas', 'endpoint': '/api/dashboard/stats', 'method': 'GET', 'icon': 'bar_chart'},
                    {'name': 'Exportar Datos', 'endpoint': '/api/dashboard/export', 'method': 'GET', 'icon': 'download'}
                ]
            }
        
        # CONFIGURACIÓN - Admin y superadmin
        if 'configuracion' in user_permissions:
            dashboard_data['available_modules']['configuracion'] = {
                'id': 'configuracion',
                'name': 'Configuración',
                'description': 'Configuración del sistema',
                'icon': 'settings',
                'color': 'dark',
                'is_collapsible': True,
                'default_expanded': False,
                'access_type': 'default' if current_user.role in SYSTEM_AREAS['configuracion']['default_roles'] else 'temporal',
                'actions': [
                    {'name': 'Ver Configuración', 'endpoint': '/api/config', 'method': 'GET', 'icon': 'visibility'},
                    {'name': 'Actualizar Config', 'endpoint': '/api/config', 'method': 'PUT', 'icon': 'update'}
                ]
            }
        
        return jsonify(dashboard_data), 200
        
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@dashboard_bp.route('/module-state', methods=['POST'])
@user_or_higher
def update_module_state(current_user):
    """Actualizar el estado de expansión/colapso de un módulo"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'Datos requeridos'}), 400
        
        module_id = data.get('module_id')
        is_expanded = data.get('is_expanded', True)
        
        if not module_id:
            return jsonify({'message': 'module_id es requerido'}), 400
        
        # Aquí podrías guardar el estado en la base de datos si quieres persistirlo
        # Por ahora, simplemente confirmamos que se recibió
        
        return jsonify({
            'message': 'Estado del módulo actualizado',
            'module_id': module_id,
            'is_expanded': is_expanded
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@dashboard_bp.route('/stats', methods=['GET'])
@user_or_higher
def get_dashboard_stats(current_user):
    """Estadísticas del sistema según permisos del usuario"""
    try:
        # Obtener permisos del usuario (similar a la función anterior)
        user_permissions = []
        
        for area, config in SYSTEM_AREAS.items():
            has_default_access = current_user.role in config['default_roles']
            
            lima_tz = pytz.timezone('America/Lima')
            now_lima = datetime.now(lima_tz)
            now_utc = now_lima.astimezone(pytz.UTC).replace(tzinfo=None)
            
            temp_perm = TemporaryPermission.query.filter_by(
                user_id=current_user.id,
                area=area,
                is_active=True
            ).filter(TemporaryPermission.expires_at > now_utc).first()
            
            if has_default_access or temp_perm:
                user_permissions.append(area)
        
        stats = {}
        
        # Estadísticas de inventario
        if 'inventario' in user_permissions:
            total_value = db.session.query(
                db.func.sum(Product.price * Product.stock)
            ).scalar() or 0
            
            stats['inventario'] = {
                'total_productos': Product.query.count(),
                'productos_con_stock': Product.query.filter(Product.stock > 0).count(),
                'productos_sin_stock': Product.query.filter(Product.stock == 0).count(),
                'valor_total_inventario': float(total_value),
                'producto_mas_caro': {
                    'name': Product.query.order_by(Product.price.desc()).first().name if Product.query.first() else 'N/A',
                    'price': float(Product.query.order_by(Product.price.desc()).first().price) if Product.query.first() else 0
                },
                'stock_promedio': float(db.session.query(db.func.avg(Product.stock)).scalar() or 0)
            }
        
        # Estadísticas de categorías (solo admin+)
        if 'categorias' in user_permissions:
            stats['categorias'] = {
                'total_categorias': Category.query.count(),
                'productos_por_categoria': [
                    {
                        'categoria': cat.name,
                        'productos': Product.query.filter_by(category_id=cat.id).count(),
                        'valor_total': float(db.session.query(
                            db.func.sum(Product.price * Product.stock)
                        ).filter_by(category_id=cat.id).scalar() or 0)
                    }
                    for cat in Category.query.all()
                ]
            }
        
        # Estadísticas de usuarios (solo superadmin)
        if 'usuarios' in user_permissions:
            stats['usuarios'] = {
                'total_usuarios': User.query.count(),
                'usuarios_por_rol': {
                    'superadmin': User.query.filter_by(role='superadmin').count(),
                    'admin': User.query.filter_by(role='admin').count(),
                    'user': User.query.filter_by(role='user').count()
                },
                'usuarios_activos': User.query.count()
            }
        
        return jsonify({
            'user_role': current_user.role,
            'stats': stats,
            'generated_at': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500
        return jsonify({'message': f'Error interno del servidor: {str(e)}'}), 500

@dashboard_bp.route('/permissions', methods=['GET'])
@user_or_higher
def get_user_dashboard_permissions(current_user):
    """Ver permisos detallados del usuario actual"""
    from utils.decorators import ROLE_PERMISSIONS, SYSTEM_AREAS
    
    user_permissions = ROLE_PERMISSIONS.get(current_user.role, {})
    
    return jsonify({
        'user': {
            'username': current_user.username,
            'role': current_user.role,
            'role_description': user_permissions.get('description', 'Sin descripción')
        },
        'permissions': {
            'areas_allowed': user_permissions.get('areas', []),
            'areas_description': {
                area: SYSTEM_AREAS.get(area, 'Sin descripción')
                for area in user_permissions.get('areas', [])
            }
        },
        'capabilities': {
            'can_view_inventory': 'inventario' in user_permissions.get('areas', []),
            'can_modify_inventory': current_user.role in ['admin', 'superadmin'],
            'can_manage_categories': 'categorias' in user_permissions.get('areas', []),
            'can_manage_users': 'usuarios' in user_permissions.get('areas', []),
            'can_manage_roles': 'roles' in user_permissions.get('areas', []),
            'can_view_reports': 'reportes' in user_permissions.get('areas', [])
        }
    }), 200
