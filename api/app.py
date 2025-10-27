from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from api.config import Config
import os

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # CORS configuration
    CORS(app, resources={
        r"/api/*": {
            "origins": [app.config['FRONTEND_URL']],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Ensure data directories exist
    data_path = app.config['DATA_PATH']
    os.makedirs(f"{data_path}/productos/etiquetas_qr", exist_ok=True)
    os.makedirs(f"{data_path}/productos/imagenes", exist_ok=True)
    os.makedirs(f"{data_path}/manifiestos/en_proceso", exist_ok=True)
    os.makedirs(f"{data_path}/manifiestos/finalizados", exist_ok=True)
    os.makedirs(f"{data_path}/reportes/movimientos", exist_ok=True)
    os.makedirs(f"{data_path}/reportes/entregas", exist_ok=True)
    os.makedirs(f"{data_path}/respaldos/db", exist_ok=True)
    os.makedirs(f"{data_path}/respaldos/logs", exist_ok=True)

    # Register blueprints
    from api.routes import auth, productos, movimientos, manifiestos, clientes, categorias, reportes, usuarios, files

    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(productos.bp, url_prefix='/api/productos')
    app.register_blueprint(movimientos.bp, url_prefix='/api/movimientos')
    app.register_blueprint(manifiestos.bp, url_prefix='/api/manifiestos')
    app.register_blueprint(clientes.bp, url_prefix='/api/clientes')
    app.register_blueprint(categorias.bp, url_prefix='/api/categorias')
    app.register_blueprint(reportes.bp, url_prefix='/api/reportes')
    app.register_blueprint(usuarios.bp, url_prefix='/api/usuarios')
    app.register_blueprint(files.bp, url_prefix='/api/files')

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({"status": "ok", "message": "Sistema de Inventario Web - Nova is running"}), 200

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Recurso no encontrado"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({"error": "Error interno del servidor"}), 500

    return app

# Create app instance for direct execution
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
