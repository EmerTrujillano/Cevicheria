from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

# Inicializar extensiones
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

# Lista negra para tokens invalidados
blacklisted_tokens = set()

def init_extensions(app):
    """Inicializa las extensiones con la aplicación Flask"""
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return jwt_payload['jti'] in blacklisted_tokens
