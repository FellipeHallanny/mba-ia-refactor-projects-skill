# Shim de retrocompatibilidade para rotas ou testes que importam diretamente models
from src.models.produto_model import ProdutoModel
from src.models.usuario_model import UsuarioModel
from src.models.pedido_model import PedidoModel
from src.models.relatorio_model import RelatorioModel

get_todos_produtos = ProdutoModel.listar_todos
get_produto_por_id = ProdutoModel.buscar_por_id
criar_produto = ProdutoModel.criar
atualizar_produto = ProdutoModel.atualizar
deletar_produto = ProdutoModel.deletar
buscar_produtos = ProdutoModel.buscar

get_todos_usuarios = UsuarioModel.listar_todos
get_usuario_por_id = UsuarioModel.buscar_por_id
criar_usuario = UsuarioModel.criar
login_usuario = UsuarioModel.autenticar

criar_pedido = PedidoModel.criar_pedido
get_todos_pedidos = PedidoModel.listar_todos
get_pedidos_usuario = PedidoModel.listar_por_usuario
atualizar_status_pedido = PedidoModel.atualizar_status

relatorio_vendas = RelatorioModel.relatorio_vendas
