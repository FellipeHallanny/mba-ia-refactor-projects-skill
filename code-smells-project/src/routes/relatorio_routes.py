from flask import Blueprint
from src.controllers.relatorio_controller import RelatorioController

relatorio_bp = Blueprint("relatorios", __name__)

relatorio_bp.route("/relatorios/vendas", methods=["GET"])(RelatorioController.relatorio_vendas)
