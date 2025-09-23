"""
Servicio para gestionar QR único del restaurante
"""
import qrcode
import io
import base64
from datetime import datetime, timedelta
from models import Table
from config.extensions import db


class RestaurantQRService:
    """Servicio para QR único del restaurante"""
    
    def __init__(self):
        self.restaurant_url = "https://tu-dominio.com/restaurant"  # URL base del restaurante
    
    def generate_restaurant_qr(self):
        """
        Generar QR único para el restaurante
        """
        try:
            # Crear objeto QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            # Agregar datos del restaurante
            qr.add_data(self.restaurant_url)
            qr.make(fit=True)
            
            # Crear imagen
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir a base64 para mostrar en web
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                'success': True,
                'qr_image': f"data:image/png;base64,{img_str}",
                'url': self.restaurant_url,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error generando QR: {str(e)}"
            }
    
    def get_available_tables(self):
        """
        Obtener mesas disponibles para selección del cliente
        """
        try:
            tables = Table.query.filter_by(status='available').all()
            
            tables_data = []
            for table in tables:
                tables_data.append({
                    'id': table.id,
                    'numero': table.numero,
                    'capacidad': table.capacidad,
                    'status': table.status
                })
            
            return {
                'success': True,
                'tables': tables_data,
                'total_available': len(tables_data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error obteniendo mesas: {str(e)}"
            }
    
    def select_table(self, table_number, customer_name=None):
        """
        Seleccionar una mesa específica desde el QR único
        """
        try:
            table = Table.query.filter_by(numero=table_number).first()
            
            if not table:
                return {
                    'success': False,
                    'error': 'Mesa no encontrada'
                }
            
            if table.status != 'available':
                return {
                    'success': False,
                    'error': 'Mesa no disponible'
                }
            
            # Marcar mesa como temporalmente ocupada
            table.status = 'temp_occupied'
            table.qr_session_id = f"single_qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{table_number}"
            table.qr_expires_at = datetime.utcnow() + timedelta(minutes=15)  # 15 minutos para ordenar
            
            if customer_name:
                table.customer_name = customer_name
            
            db.session.commit()
            
            return {
                'success': True,
                'table_id': table.id,
                'table_number': table.numero,
                'session_id': table.qr_session_id,
                'expires_at': table.qr_expires_at.isoformat(),
                'message': f'Mesa {table_number} seleccionada exitosamente'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f"Error seleccionando mesa: {str(e)}"
            }


# Instancia global del servicio
restaurant_qr_service = RestaurantQRService()