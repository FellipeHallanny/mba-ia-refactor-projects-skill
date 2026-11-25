from src.database.connection import get_db

TIER_HIGH_THRESHOLD = 10000
TIER_MEDIUM_THRESHOLD = 5000
TIER_LOW_THRESHOLD = 1000

DISCOUNT_HIGH = 0.10
DISCOUNT_MEDIUM = 0.05
DISCOUNT_LOW = 0.02

class RelatorioModel:
    @staticmethod
    def relatorio_vendas():
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT COUNT(*) FROM pedidos")
        total_pedidos = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(total) FROM pedidos")
        faturamento = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'")
        pendentes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'")
        aprovados = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'")
        cancelados = cursor.fetchone()[0]

        desconto = 0.0
        if faturamento > TIER_HIGH_THRESHOLD:
            desconto = faturamento * DISCOUNT_HIGH
        elif faturamento > TIER_MEDIUM_THRESHOLD:
            desconto = faturamento * DISCOUNT_MEDIUM
        elif faturamento > TIER_LOW_THRESHOLD:
            desconto = faturamento * DISCOUNT_LOW

        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": round(desconto, 2),
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": pendentes,
            "pedidos_aprovados": aprovados,
            "pedidos_cancelados": cancelados,
            "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0
        }
