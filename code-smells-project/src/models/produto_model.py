from src.database.connection import get_db

class ProdutoModel:
    @staticmethod
    def listar_todos():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM produtos")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def buscar_por_id(produto_id: int):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    @staticmethod
    def criar(nome: str, descricao: str, preco: float, estoque: int, categoria: str):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def atualizar(produto_id: int, nome: str, descricao: str, preco: float, estoque: int, categoria: str):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id)
        )
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def deletar(produto_id: int):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def buscar(termo: str = None, categoria: str = None, preco_min: float = None, preco_max: float = None):
        db = get_db()
        cursor = db.cursor()
        query = "SELECT * FROM produtos WHERE 1=1"
        params = []

        if termo:
            query += " AND (nome LIKE ? OR descricao LIKE ?)"
            params.extend([f"%{termo}%", f"%{termo}%"])
        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)
        if preco_min is not None:
            query += " AND preco >= ?"
            params.append(preco_min)
        if preco_max is not None:
            query += " AND preco <= ?"
            params.append(preco_max)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
