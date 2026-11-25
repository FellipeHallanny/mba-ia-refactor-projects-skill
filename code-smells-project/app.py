import os
import sys

# Garante que o diretório raiz do projeto esteja no PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask
from flask_cors import CORS
from src.config.settings import Config
from src.database.connection import init_db, close_db
from src.middlewares.error_handler import register_error_handlers
from src.routes.produto_routes import produto_bp
from src.routes.usuario_routes import usuario_bp
from src.routes.pedido_routes import pedido_bp
from src.routes.relatorio_routes import relatorio_bp
from src.routes.health_routes import health_bp

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["DEBUG"] = Config.DEBUG

    CORS(app)

    # Registrar teardown do banco de dados
    app.teardown_appcontext(close_db)

    # Registrar middlewares e tratadores de erro
    register_error_handlers(app)

    # Registrar rotas por domínio
    app.register_blueprint(health_bp)
    app.register_blueprint(produto_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(pedido_bp)
    app.register_blueprint(relatorio_bp)

    return app

app = create_app()

if __name__ == "__main__":
    init_db()
    print("=" * 50)
    print("SERVIDOR INICIADO (MVC Refatorado)")
    print(f"Rodando em http://{Config.HOST}:{Config.PORT}")
    print("=" * 50)
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
