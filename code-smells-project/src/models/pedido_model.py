from src.database.connection import get_db

class PedidoModel:
    @staticmethod
    def criar_pedido(usuario_id: int, itens: list):
        db = get_db()
        cursor = db.cursor()

        try:
            total = 0.0
            itens_processados = []

            for item in itens:
                produto_id = item.get("produto_id")
                quantidade = item.get("quantidade", 1)

                cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
                produto = cursor.fetchone()
                if produto is None:
                    return {"erro": f"Produto {produto_id} não encontrado"}
                if produto["estoque"] < quantidade:
                    return {"erro": f"Estoque insuficiente para {produto['nome']}"}

                preco_unitario = produto["preco"]
                total += preco_unitario * quantidade
                itens_processados.append({
                    "produto_id": produto_id,
                    "quantidade": quantidade,
                    "preco_unitario": preco_unitario
                })

            cursor.execute(
                "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
                (usuario_id, total)
            )
            pedido_id = cursor.lastrowid

            for item in itens_processados:
                cursor.execute(
                    "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                    (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"])
                )
                cursor.execute(
                    "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                    (item["quantidade"], item["produto_id"])
                )

            db.commit()
            return {"pedido_id": pedido_id, "total": round(total, 2)}
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def _agrupar_pedidos_com_itens(cursor):
        rows = cursor.fetchall()
        pedidos_dict = {}

        for row in rows:
            pid = row["pedido_id"]
            if pid not in pedidos_dict:
                pedidos_dict[pid] = {
                    "id": pid,
                    "usuario_id": row["usuario_id"],
                    "status": row["status"],
                    "total": row["total"],
                    "criado_em": row["criado_em"],
                    "itens": []
                }
            if row["item_id"]:
                pedidos_dict[pid]["itens"].append({
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"] or "Desconhecido",
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"]
                })

        return list(pedidos_dict.values())

    @staticmethod
    def listar_todos():
        db = get_db()
        cursor = db.cursor()
        query = """
            SELECT 
                p.id AS pedido_id, p.usuario_id, p.status, p.total, p.criado_em,
                ip.id AS item_id, ip.produto_id, ip.quantidade, ip.preco_unitario,
                pr.nome AS produto_nome
            FROM pedidos p
            LEFT JOIN itens_pedido ip ON p.id = ip.pedido_id
            LEFT JOIN produtos pr ON ip.produto_id = pr.id
            ORDER BY p.id DESC
        """
        cursor.execute(query)
        return PedidoModel._agrupar_pedidos_com_itens(cursor)

    @staticmethod
    def listar_por_usuario(usuario_id: int):
        db = get_db()
        cursor = db.cursor()
        query = """
            SELECT 
                p.id AS pedido_id, p.usuario_id, p.status, p.total, p.criado_em,
                ip.id AS item_id, ip.produto_id, ip.quantidade, ip.preco_unitario,
                pr.nome AS produto_nome
            FROM pedidos p
            LEFT JOIN itens_pedido ip ON p.id = ip.pedido_id
            LEFT JOIN produtos pr ON ip.produto_id = pr.id
            WHERE p.usuario_id = ?
            ORDER BY p.id DESC
        """
        cursor.execute(query, (usuario_id,))
        return PedidoModel._agrupar_pedidos_com_itens(cursor)

    @staticmethod
    def atualizar_status(pedido_id: int, novo_status: str):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
        db.commit()
        return cursor.rowcount > 0
