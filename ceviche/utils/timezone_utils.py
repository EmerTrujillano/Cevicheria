"""
Utilidades para manejo de fechas con zona horaria de Lima
"""
from datetime import datetime
import pytz
from flask import current_app

def lima_now():
    """Obtener la fecha/hora actual en zona horaria de Lima"""
    lima_tz = pytz.timezone('America/Lima')
    utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    return utc_now.astimezone(lima_tz)

def lima_datetime_naive():
    """Obtener datetime naive (sin timezone) en hora de Lima para BD"""
    return lima_now().replace(tzinfo=None)

def format_lima_datetime(dt):
    """Formatear datetime para mostrar en zona horaria de Lima"""
    if dt is None:
        return None
    
    # Si el datetime es naive, asumimos que está en UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=pytz.UTC)
    
    lima_tz = pytz.timezone('America/Lima')
    lima_dt = dt.astimezone(lima_tz)
    return lima_dt.strftime('%Y-%m-%d %H:%M:%S')

def utc_to_lima_naive(utc_dt):
    """Convertir UTC datetime a Lima datetime naive para BD"""
    if utc_dt is None:
        return None
    
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=pytz.UTC)
    
    lima_tz = pytz.timezone('America/Lima')
    lima_dt = utc_dt.astimezone(lima_tz)
    return lima_dt.replace(tzinfo=None)