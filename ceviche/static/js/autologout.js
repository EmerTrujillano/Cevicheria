// Sistema de autologout automático
class AutoLogoutManager {
    constructor() {
        this.checkInterval = 30000; // Verificar cada 30 segundos
        this.isActive = false;
        this.timeoutId = null;
    }

    start() {
        if (this.isActive) return;
        
        this.isActive = true;
        this.scheduleCheck();
        console.log('💫 AutoLogout activado - verificando cada 30s');
    }

    stop() {
        this.isActive = false;
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
            this.timeoutId = null;
        }
        console.log('⏹️ AutoLogout desactivado');
    }

    scheduleCheck() {
        if (!this.isActive) return;
        
        this.timeoutId = setTimeout(() => {
            this.checkSession();
        }, this.checkInterval);
    }

    async checkSession() {
        if (!this.isActive) return;

        try {
            const response = await fetch('/api/auth/verify-session', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });

            if (!response.ok || response.status === 401) {
                console.log('🚪 Sesión cerrada por administrador - redirigiendo al login');
                this.performLogout();
                return;
            }

            const data = await response.json();
            if (!data.success || !data.sessionActive) {
                console.log('🚪 Sesión inactiva - redirigiendo al login');
                this.performLogout();
                return;
            }

            // Programar próxima verificación
            this.scheduleCheck();

        } catch (error) {
            console.error('❌ Error verificando sesión:', error);
            // En caso de error, seguir verificando
            this.scheduleCheck();
        }
    }

    performLogout() {
        this.stop();
        
        // Limpiar datos locales
        localStorage.removeItem('authToken');
        localStorage.removeItem('currentUser');
        
        // Mostrar mensaje
        if (typeof showAlert === 'function') {
            showAlert('Tu sesión ha sido cerrada por el administrador', 'warning');
        }
        
        // Redirigir al login después de un momento
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
    }
}

// Inicializar autologout automáticamente si hay token
document.addEventListener('DOMContentLoaded', function() {
    const authToken = localStorage.getItem('authToken');
    if (authToken && window.location.pathname !== '/login') {
        window.autoLogoutManager = new AutoLogoutManager();
        window.autoLogoutManager.start();
    }
});