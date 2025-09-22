from models import Table
from config.extensions import db
from datetime import datetime
import threading
import time
from flask import current_app

class QRSessionService:
    """Servicio para gestión de sesiones QR y temporizadores"""
    
    _instance = None
    _running = False
    _cleanup_thread = None
    _app = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QRSessionService, cls).__new__(cls)
        return cls._instance
    
    def start_cleanup_service(self, app=None):
        """Iniciar el servicio de limpieza en background"""
        if app:
            self._app = app
        if not self._running:
            self._running = True
            self._cleanup_thread = threading.Thread(target=self._cleanup_expired_sessions, daemon=True)
            self._cleanup_thread.start()
    
    def stop_cleanup_service(self):
        """Detener el servicio de limpieza"""
        self._running = False
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)
    
    def _cleanup_expired_sessions(self):
        """Proceso en background para limpiar sesiones QR expiradas"""
        while self._running:
            try:
                if self._app:
                    with self._app.app_context():
                        # Buscar mesas con sesiones QR expiradas
                        expired_tables = Table.query.filter(
                            Table.status == 'temp_occupied',
                            Table.qr_expires_at <= datetime.utcnow()
                        ).all()
                        
                        for table in expired_tables:
                            print(f"Limpiando sesión QR expirada para mesa {table.number}")
                            table.end_qr_session()
                        
                        if expired_tables:
                            db.session.commit()
                            print(f"Se limpiaron {len(expired_tables)} sesiones QR expiradas")
                
            except Exception as e:
                print(f"Error en cleanup de sesiones QR: {e}")
                if self._app:
                    with self._app.app_context():
                        db.session.rollback()
            
            # Esperar 30 segundos antes del próximo cleanup
            time.sleep(30)
    
    @staticmethod
    def start_qr_session(table_id, duration_minutes=10):
        """
        Iniciar sesión QR para una mesa
        
        Args:
            table_id: ID de la mesa
            duration_minutes: Duración en minutos (default: 10)
        
        Returns:
            dict: Resultado con success, message y data/error
        """
        try:
            table = Table.query.get(table_id)
            if not table:
                return {
                    'success': False,
                    'message': 'Mesa no encontrada'
                }
            
            # Verificar que la mesa esté disponible
            if table.status not in ['available', 'temp_occupied']:
                return {
                    'success': False,
                    'message': f'Mesa no disponible. Estado actual: {table.status}'
                }
            
            # Si ya hay una sesión activa, extenderla
            if table.status == 'temp_occupied' and table.is_qr_session_active():
                from datetime import timedelta
                table.qr_expires_at = datetime.utcnow() + timedelta(minutes=duration_minutes)
                db.session.commit()
                
                return {
                    'success': True,
                    'message': 'Sesión QR extendida',
                    'data': {
                        'session_id': table.qr_session_id,
                        'expires_at': table.qr_expires_at.isoformat(),
                        'time_remaining': table.get_qr_time_remaining()
                    }
                }
            
            # Iniciar nueva sesión
            session_id = table.start_qr_session(duration_minutes)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Sesión QR iniciada',
                'data': {
                    'session_id': session_id,
                    'expires_at': table.qr_expires_at.isoformat(),
                    'time_remaining': table.get_qr_time_remaining()
                }
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error al iniciar sesión QR: {str(e)}'
            }
    
    @staticmethod
    def confirm_table_order(table_id, session_id=None):
        """
        Confirmar que se realizó un pedido en la mesa (desactiva temporizador)
        
        Args:
            table_id: ID de la mesa
            session_id: ID de sesión QR (opcional para validar)
        
        Returns:
            dict: Resultado con success, message y data/error
        """
        try:
            table = Table.query.get(table_id)
            if not table:
                return {
                    'success': False,
                    'message': 'Mesa no encontrada'
                }
            
            # Validar sesión si se proporciona
            if session_id and table.qr_session_id != session_id:
                return {
                    'success': False,
                    'message': 'Sesión QR no válida'
                }
            
            # Cambiar estado a ocupada permanentemente
            table.status = 'occupied'
            table.qr_scanned_at = None
            table.qr_expires_at = None
            table.qr_session_id = None
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Mesa confirmada como ocupada',
                'data': table.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error al confirmar mesa: {str(e)}'
            }
    
    @staticmethod
    def get_qr_session_status(table_id, session_id=None):
        """
        Obtener estado de sesión QR
        
        Args:
            table_id: ID de la mesa
            session_id: ID de sesión QR (opcional para validar)
        
        Returns:
            dict: Estado de la sesión
        """
        try:
            table = Table.query.get(table_id)
            if not table:
                return {
                    'success': False,
                    'message': 'Mesa no encontrada'
                }
            
            # Validar sesión si se proporciona
            if session_id and table.qr_session_id != session_id:
                return {
                    'success': False,
                    'message': 'Sesión QR no válida',
                    'data': {
                        'session_active': False,
                        'time_remaining': 0
                    }
                }
            
            return {
                'success': True,
                'data': {
                    'table_id': table.id,
                    'table_number': table.number,
                    'status': table.status,
                    'session_active': table.is_qr_session_active(),
                    'time_remaining': table.get_qr_time_remaining(),
                    'session_id': table.qr_session_id,
                    'scanned_at': table.qr_scanned_at.isoformat() if table.qr_scanned_at else None,
                    'expires_at': table.qr_expires_at.isoformat() if table.qr_expires_at else None
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al obtener estado de sesión: {str(e)}'
            }
    
    @staticmethod
    def extend_qr_session(table_id, session_id, additional_minutes=5):
        """
        Extender sesión QR por interacción del cliente
        
        Args:
            table_id: ID de la mesa
            session_id: ID de sesión QR
            additional_minutes: Minutos adicionales (default: 5)
        
        Returns:
            dict: Resultado con success, message y data/error
        """
        try:
            table = Table.query.get(table_id)
            if not table:
                return {
                    'success': False,
                    'message': 'Mesa no encontrada'
                }
            
            # Validar sesión
            if table.qr_session_id != session_id:
                return {
                    'success': False,
                    'message': 'Sesión QR no válida'
                }
            
            if not table.is_qr_session_active():
                return {
                    'success': False,
                    'message': 'Sesión QR expirada'
                }
            
            # Extender sesión
            from datetime import timedelta
            table.qr_expires_at = table.qr_expires_at + timedelta(minutes=additional_minutes)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Sesión extendida por {additional_minutes} minutos',
                'data': {
                    'new_expiry': table.qr_expires_at.isoformat(),
                    'time_remaining': table.get_qr_time_remaining()
                }
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Error al extender sesión: {str(e)}'
            }
    
    @staticmethod
    def get_active_qr_sessions():
        """
        Obtener todas las sesiones QR activas
        
        Returns:
            list: Lista de sesiones QR activas
        """
        try:
            active_tables = Table.query.filter(
                Table.status == 'temp_occupied',
                Table.qr_expires_at > datetime.utcnow()
            ).all()
            
            sessions = []
            for table in active_tables:
                sessions.append({
                    'table_id': table.id,
                    'table_number': table.number,
                    'zone_name': table.zone.name if table.zone else None,
                    'floor_name': table.zone.floor.name if table.zone and table.zone.floor else None,
                    'session_id': table.qr_session_id,
                    'scanned_at': table.qr_scanned_at.isoformat(),
                    'expires_at': table.qr_expires_at.isoformat(),
                    'time_remaining': table.get_qr_time_remaining()
                })
            
            return sessions
            
        except Exception as e:
            print(f"Error al obtener sesiones QR activas: {e}")
            return []

# Instancia global del servicio
qr_service = QRSessionService()