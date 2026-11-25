from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"erro": "Requisição inválida", "detalhes": str(error)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"erro": "Recurso não encontrado"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"erro": "Erro interno do servidor"}), 500
