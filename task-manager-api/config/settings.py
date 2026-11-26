import os

class Config:
    # Chave dummy explícita para desenvolvimento local. NUNCA a chave 'super-secret-key-123' auditada.
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-taskmanager-key-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///tasks.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

    # SMTP Settings — Segredos e credenciais exigem injeção via ambiente. NUNCA 'senha123' como fallback.
    SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_ENABLED = os.getenv("SMTP_ENABLED", "0") == "1"
