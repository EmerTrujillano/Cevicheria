"""
Servicio de limpieza automática de sesiones inactivas
"""
import threading
import time
from datetime import datetime
from services.session_service import SessionService

class InactivityService:
    def __init__(self):
        self.running = False
        self.thread = None
        self.app_context = None
    
    def start(self, app):
        """Iniciar el servicio de limpieza de sesiones inactivas"""
        if self.running:
            return
        
        self.app_context = app.app_context()
        self.running = True
        self.thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.thread.start()
        print("[INACTIVITY_SERVICE] Servicio de auto-logout iniciado (5 min de inactividad)")
    
    def stop(self):
        """Detener el servicio"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("[INACTIVITY_SERVICE] Servicio de auto-logout detenido")
    
    def _cleanup_loop(self):
        """Loop principal que ejecuta la limpieza cada minuto"""
        while self.running:
            try:
                with self.app_context:
                    # Limpiar sesiones inactivas (5 minutos)
                    cleaned = SessionService.cleanup_inactive_sessions(inactivity_minutes=5)
                    
                    # También limpiar sesiones expiradas
                    SessionService.cleanup_expired_sessions()
                    
                    if cleaned > 0:
                        print(f"[INACTIVITY_SERVICE] {cleaned} usuarios desconectados por inactividad")
                
            except Exception as e:
                print(f"[INACTIVITY_SERVICE] Error en limpieza: {str(e)}")
            
            # Esperar 60 segundos antes de la siguiente limpieza
            time.sleep(60)

# Instancia global del servicio
inactivity_service = InactivityService()