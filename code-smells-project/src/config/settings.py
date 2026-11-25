import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "loja-segura-prod-secret-key-2026")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    DB_PATH = os.getenv("DB_PATH", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "loja.db")))
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))
