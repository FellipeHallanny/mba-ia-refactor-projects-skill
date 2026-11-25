from flask import request, jsonify
from src.models.usuario_model import UsuarioModel

class UsuarioController:
    @staticmethod
    def listar_usuarios():
        try:
            usuarios = UsuarioModel.listar_todos()
            return jsonify({"dados": usuarios, "sucesso": True}), 200
        except Exception as e:
            return jsonify({"erro": str(e)}), 500

    @staticmethod
    def buscar_usuario(id: int):
        try:
            usuario = UsuarioModel.buscar_por_id(id)
            if usuario:
                return jsonify({"dados": usuario, "sucesso": True}), 200
            return jsonify({"erro": "Usuário não encontrado"}), 404
        except Exception as e:
            return jsonify({"erro": str(e)}), 500

    @staticmethod
    def criar_usuario():
        try:
            dados = request.get_json()
            if not dados:
                return jsonify({"erro": "Dados inválidos"}), 400

            nome = dados.get("nome", "")
            email = dados.get("email", "")
            senha = dados.get("senha", "")
            tipo = dados.get("tipo", "cliente")

            if not nome or not email or not senha:
                return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400

            usuario_existente = UsuarioModel.buscar_por_email(email)
            if usuario_existente:
                return jsonify({"erro": "Email já cadastrado"}), 400

            user_id = UsuarioModel.criar(nome, email, senha, tipo)
            return jsonify({"dados": {"id": user_id}, "sucesso": True}), 201
        except Exception as e:
            return jsonify({"erro": str(e)}), 500

    @staticmethod
    def login():
        try:
            dados = request.get_json()
            if not dados:
                return jsonify({"erro": "Email e senha são obrigatórios"}), 400

            email = dados.get("email", "")
            senha = dados.get("senha", "")

            if not email or not senha:
                return jsonify({"erro": "Email e senha são obrigatórios"}), 400

            usuario = UsuarioModel.autenticar(email, senha)
            if usuario:
                return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
            return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401
        except Exception as e:
            return jsonify({"erro": str(e)}), 500
