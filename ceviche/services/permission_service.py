from datetime import datetime, timedelta
from config.extensions import db
from models import TemporaryPermission, User
from utils.decorators import SYSTEM_AREAS
from utils.validators import validate_duration_unit

class PermissionService:
    @staticmethod
    def grant_temporary_permission(user_id, area, hours, granted_by_id, reason=None):
        """Otorgar permiso temporal"""
        # Validar área
        if area not in SYSTEM_AREAS:
            return None, 'Área inválida'
        
        # Verificar usuarios
        user = User.query.get(user_id)
        granter = User.query.get(granted_by_id)
        
        if not user:
            return None, 'Usuario no encontrado'
        if not granter:
            return None, 'Usuario que otorga el permiso no encontrado'
        
        # Verificar si ya tiene acceso por defecto
        if user.role in SYSTEM_AREAS[area]['default_roles']:
            return None, f'El usuario ya tiene acceso por defecto al área {area}'
        
        # Desactivar permisos temporales anteriores para esta área
        TemporaryPermission.query.filter_by(
            user_id=user_id,
            area=area,
            is_active=True
        ).update({'is_active': False})
        
        # Crear nuevo permiso temporal
        from datetime import timezone, timedelta as td
        import pytz
        
        # Usar zona horaria de Lima, Peru
        lima_tz = pytz.timezone('America/Lima')
        now_lima = datetime.now(lima_tz)
        expires_at = now_lima + timedelta(hours=hours)
        
        # Convertir a UTC para almacenar en la base de datos
        expires_at_utc = expires_at.astimezone(pytz.UTC).replace(tzinfo=None)
        
        temp_permission = TemporaryPermission(
            user_id=user_id,
            granted_by=granted_by_id,
            area=area,
            expires_at=expires_at_utc,
            reason=reason
        )
        
        db.session.add(temp_permission)
        db.session.commit()
        
        return temp_permission, None

    @staticmethod
    def revoke_temporary_permission(user_id, area):
        """Revocar permiso temporal"""
        updated_count = TemporaryPermission.query.filter_by(
            user_id=user_id,
            area=area,
            is_active=True
        ).update({'is_active': False})
        
        db.session.commit()
        
        if updated_count > 0:
            user = User.query.get(user_id)
            return True, f'Permiso temporal revocado para {user.username} en {area}'
        else:
            return False, 'No se encontraron permisos temporales activos'

    @staticmethod
    def get_active_permissions():
        """Obtener todos los permisos temporales activos"""
        import pytz
        
        lima_tz = pytz.timezone('America/Lima')
        now_lima = datetime.now(lima_tz)
        now_utc = now_lima.astimezone(pytz.UTC).replace(tzinfo=None)
        
        active_permissions = TemporaryPermission.query.filter(
            TemporaryPermission.is_active == True,
            TemporaryPermission.expires_at > now_utc
        ).all()
        
        return [perm.to_dict() for perm in active_permissions]

    @staticmethod
    def get_user_permissions(user_id):
        """Obtener permisos específicos de un usuario"""
        user = User.query.get(user_id)
        if not user:
            return None, 'Usuario no encontrado'
        
        areas_info = []
        for area, config in SYSTEM_AREAS.items():
            has_default_access = user.role in config['default_roles']
            temp_permission = None
            
            # Buscar permisos temporales activos
            import pytz
            lima_tz = pytz.timezone('America/Lima')
            now_lima = datetime.now(lima_tz)
            now_utc = now_lima.astimezone(pytz.UTC).replace(tzinfo=None)
            
            temp_perm = TemporaryPermission.query.filter_by(
                user_id=user.id,
                area=area,
                is_active=True
            ).filter(TemporaryPermission.expires_at > now_utc).first()
            
            if temp_perm:
                temp_permission = temp_perm.to_dict()
            
            # El usuario tiene acceso si tiene acceso por defecto O un permiso temporal activo
            has_access = has_default_access or (temp_perm is not None)
            
            areas_info.append({
                'name': area,
                'description': config['description'],
                'default_roles': config['default_roles'],
                'has_default_access': has_default_access,
                'has_temp_access': temp_perm is not None,
                'has_access': has_access,
                'temporary_permission': temp_permission
            })
        
        return areas_info, None

    @staticmethod
    def cleanup_expired_permissions():
        """Limpiar permisos temporales expirados"""
        import pytz
        
        lima_tz = pytz.timezone('America/Lima')
        now_lima = datetime.now(lima_tz)
        now_utc = now_lima.astimezone(pytz.UTC).replace(tzinfo=None)
        
        expired_count = TemporaryPermission.query.filter(
            TemporaryPermission.is_active == True,
            TemporaryPermission.expires_at <= now_utc
        ).update({'is_active': False})
        
        db.session.commit()
        return expired_count

    @staticmethod
    def grant_multiple_temporary_permissions(user_id, areas, hours, granted_by_id, reason=None):
        """Otorgar permisos temporales a múltiples áreas"""
        if not areas or not isinstance(areas, list):
            return None, 'Se debe proporcionar una lista de áreas'
        
        # Validar todas las áreas primero
        invalid_areas = [area for area in areas if area not in SYSTEM_AREAS]
        if invalid_areas:
            return None, f'Áreas inválidas: {", ".join(invalid_areas)}'
        
        # Verificar usuarios
        user = User.query.get(user_id)
        granter = User.query.get(granted_by_id)
        
        if not user:
            return None, 'Usuario no encontrado'
        if not granter:
            return None, 'Usuario que otorga el permiso no encontrado'
        
        # Filtrar áreas que ya tiene por defecto
        areas_to_grant = []
        areas_already_have = []
        
        for area in areas:
            if user.role in SYSTEM_AREAS[area]['default_roles']:
                areas_already_have.append(area)
            else:
                areas_to_grant.append(area)
        
        if not areas_to_grant:
            already_msg = f"El usuario ya tiene acceso por defecto a: {', '.join(areas_already_have)}"
            return None, already_msg
        
        # Crear permisos temporales para las áreas que no tiene
        created_permissions = []
        
        try:
            from datetime import timezone, timedelta as td
            import pytz
            
            # Usar zona horaria de Lima, Peru
            lima_tz = pytz.timezone('America/Lima')
            now_lima = datetime.now(lima_tz)
            expires_at = now_lima + timedelta(hours=hours)
            
            # Convertir a UTC para almacenar en la base de datos
            expires_at_utc = expires_at.astimezone(pytz.UTC).replace(tzinfo=None)
            
            for area in areas_to_grant:
                # Desactivar permisos temporales anteriores para esta área
                TemporaryPermission.query.filter_by(
                    user_id=user_id,
                    area=area,
                    is_active=True
                ).update({'is_active': False})
                
                # Crear nuevo permiso temporal
                temp_permission = TemporaryPermission(
                    user_id=user_id,
                    granted_by=granted_by_id,
                    area=area,
                    expires_at=expires_at_utc,
                    reason=reason,
                    is_active=True
                )
                
                db.session.add(temp_permission)
                created_permissions.append(temp_permission)
            
            db.session.commit()
            
            result_msg = f"Permisos otorgados a: {', '.join(areas_to_grant)}"
            if areas_already_have:
                result_msg += f". Ya tenía acceso a: {', '.join(areas_already_have)}"
            
            return created_permissions, result_msg
            
        except Exception as e:
            db.session.rollback()
            return None, f'Error al crear permisos temporales: {str(e)}'
