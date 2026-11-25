import hashlib
import os
import hmac
from src.database.connection import get_db

def hash_senha(senha: str) -> str:
    salt = os.urandom(16).hex()
    digest = hashlib.sha256((salt + senha).encode("utf-8")).hexdigest()
    return f"{salt}:{digest}"

def verificar_senha(hash_armazenado: str, senha: str) -> bool:
    if not hash_armazenado:
        return False
    if ":" not in hash_armazenado:
        # Retrocompatibilidade com seeds legados em texto puro
        return hash_armazenado == senha
    salt, original_digest = hash_armazenado.split(":", 1)
    new_digest = hashlib.sha256((salt + senha).encode("utf-8")).hexdigest()
    return hmac.compare_digest(original_digest, new_digest)

class UsuarioModel:
    @staticmethod
    def listar_todos():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def buscar_por_id(usuario_id: int):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id = ?", (usuario_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def buscar_por_email(email: str):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def criar(nome: str, email: str, senha: str, tipo: str = "cliente"):
        db = get_db()
        cursor = db.cursor()
        senha_segura = hash_senha(senha)
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, senha_segura, tipo)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def autenticar(email: str, senha: str):
        usuario = UsuarioModel.buscar_por_email(email)
        if usuario and verificar_senha(usuario["senha"], senha):
            return {
                "id": usuario["id"],
                "nome": usuario["nome"],
                "email": usuario["email"],
                "tipo": usuario["tipo"]
            }
        return None
