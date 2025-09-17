def validate_required_fields(data, required_fields):
    """Validar que todos los campos requeridos estén presentes"""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)
    return missing_fields

def validate_user_role(role):
    """Validar que el rol sea válido"""
    valid_roles = ['user', 'admin', 'superadmin']
    return role in valid_roles

def validate_rating(rating):
    """Validar que el rating esté entre 1 y 5"""
    try:
        rating = int(rating)
        return 1 <= rating <= 5
    except (ValueError, TypeError):
        return False

def validate_positive_number(value):
    """Validar que un valor sea un número positivo"""
    try:
        num = float(value)
        return num >= 0
    except (ValueError, TypeError):
        return False

def validate_duration_unit(unit):
    """Validar unidad de tiempo para permisos temporales"""
    valid_units = ['minutes', 'hours', 'days']
    return unit in valid_units
