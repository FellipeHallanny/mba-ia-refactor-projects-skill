import os
import sys

# Garante que o diretório raiz esteja no PATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS
from database import db
from config.settings import Config
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from routes.report_routes import report_bp
from datetime import datetime, timezone

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SECRET_KEY'] = Config.SECRET_KEY

    CORS(app)
    db.init_app(app)

    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)

    @app.route('/health')
    def health():
        return jsonify({'status': 'ok', 'timestamp': str(datetime.now(timezone.utc))}), 200

    @app.route('/')
    def index():
        return jsonify({'message': 'Task Manager API (Refatorado MVC)', 'version': '1.0.0'}), 200

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
