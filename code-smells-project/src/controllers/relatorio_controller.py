from flask import jsonify
from src.models.relatorio_model import RelatorioModel

class RelatorioController:
    @staticmethod
    def relatorio_vendas():
        try:
            relatorio = RelatorioModel.relatorio_vendas()
            return jsonify({"dados": relatorio, "sucesso": True}), 200
        except Exception as e:
            return jsonify({"erro": str(e)}), 500
