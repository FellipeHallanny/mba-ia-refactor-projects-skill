from flask import jsonify
from src.database.connection import get_db

class HealthController:
    @staticmethod
    def health_check():
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT 1")
            cursor.execute("SELECT COUNT(*) FROM produtos")
            produtos = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            usuarios = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM pedidos")
            pedidos = cursor.fetchone()[0]

            # Retorno saneado sem expor secret_key ou caminhos internos
            return jsonify({
                "status": "ok",
                "database": "connected",
                "counts": {
                    "produtos": produtos,
                    "usuarios": usuarios,
                    "pedidos": pedidos
                },
                "versao": "1.0.0"
            }), 200
        except Exception as e:
            return jsonify({"status": "erro", "detalhes": str(e)}), 500
