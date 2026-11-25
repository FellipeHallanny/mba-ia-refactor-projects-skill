================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 5 | HIGH: 2 | MEDIUM: 3 | LOW: 2

## Findings

### [CRITICAL] SQL Injection & Unsanitized Query String Concatenation
File: models.py:28, 48-50, 58-61, 68, 109-111, 127-129, 140, 149-151, 158-160, 164-166, 174, 280-282, 291-298
Description: Consultas SQL são construídas via concatenação direta de strings com parâmetros recebidos de requisições HTTP (`"SELECT * FROM produtos WHERE id = " + str(id)`, `"WHERE email = '" + email + "' AND senha = '" + senha + "'"`).
Impact: Permite que invasores executem SQL arbitrário, burlem a autenticação com bypass `' OR '1'='1`, extraiam dados sigilosos e excluam tabelas inteiras.
Recommendation: Migrar todas as consultas para queries parametrizadas usando placeholders (`?`) com passagem de tuplas de parâmetros no SQLite.

### [CRITICAL] God File / Falha Total de Separação de Camadas
File: models.py:1-314
Description: Arquivo único concentra regras de negócio, persistência, controle de estoque, cálculo de faturamento, validações e manipulação de 4 domínios distintos (Produtos, Usuários, Pedidos e Relatórios).
Impact: Alto acoplamento, impossibilidade de testes unitários isolados e elevado risco de regressão a cada modificação.
Recommendation: Decompor o arquivo em models especializados por domínio (`ProdutoModel`, `UsuarioModel`, `PedidoModel`) e mover regras de fluxo para a camada de controllers.

### [CRITICAL] Backdoors Administrativos Inseguros sem Autenticação
File: app.py:47-79
Description: Os endpoints `/admin/query` e `/admin/reset-db` aceitam qualquer requisição POST sem autenticação ou autorização, executando instruções SQL arbitrárias fornecidas pelo cliente ou limpando todas as tabelas do sistema.
Impact: Qualquer usuário não autenticado na rede pode destruir ou manipular a base de dados de produção.
Recommendation: Remover os endpoints backdoor ou restringi-los a ambiente de teste/desenvolvimento com proteção de autenticação e RBAC.

### [CRITICAL] Hardcoded Credentials & Exposição de Segredos
File: app.py:7; controllers.py:289
Description: A chave de segurança da aplicação (`SECRET_KEY = "minha-chave-super-secreta-123"`) está fixada no código-fonte e é exposta abertamente no JSON de resposta do endpoint `/health`.
Impact: Quebra do segredo criptográfico de sessão e assinatura de tokens da aplicação.
Recommendation: Mover segredos para variáveis de ambiente (`os.getenv`) carregadas centralizadamente em `config/settings.py` e sanear a resposta do `/health`.

### [CRITICAL] Armazenamento de Senha em Texto Claro
File: models.py:105-120, 122-131; database.py:76-83
Description: Senhas de usuários são inseridas, salvas e consultadas em texto plano (`senha = 'admin123'`), sem qualquer função de hash criptográfico ou salting.
Impact: Vazamento imediato de credenciais de todos os usuários em caso de leitura não autorizada do banco de dados (violação grave de LGPD/GDPR).
Recommendation: Implementar hashing seguro de senhas com salting (PBKDF2/SHA-256) na criação/atualização e comparação segura no login, mantendo verificação retrocompatível.

### [HIGH] Fat Controllers & Mistura de Regras de Negócio com Camada HTTP
File: controllers.py:24-63, 188-221, 237-256
Description: As funções de controle manipulam validações manuais de regras de negócio de estoque, formatação de status de pedidos e regras de envio de e-mail/SMS acopladas à lógica de requisição/resposta HTTP.
Impact: Duplicação de código, dificuldade de manutenção e quebra do Princípio da Responsabilidade Única (SRP).
Recommendation: Isolar a validação de dados e orquestração de domínio em serviços/models, mantendo os controllers estritamente focados no protocolo HTTP.

### [HIGH] Conexão Global com Banco de Dados sem Proteção de Concorrência
File: database.py:4-13
Description: Uso de uma variável global `db_connection` compartilhada por todas as threads de requisição com `check_same_thread=False` no SQLite.
Impact: Risco crítico de race conditions, bloqueios de escrita e corrupção de memória durante requisições simultâneas.
Recommendation: Gerenciar conexões por requisição (ex: usando `g` do Flask ou context managers dedicados com fechamento adequado).

### [MEDIUM] N+1 Query Problem na Listagem de Pedidos
File: models.py:187-200, 219-232
Description: As funções `get_pedidos_usuario` e `get_todos_pedidos` realizam uma query inicial para buscar os pedidos e, em loops aninhados subsequentes, executam queries individuais para cada item do pedido e para cada produto.
Impact: Explosão de queries ao banco de dados com degradação exponencial de latência conforme o volume de pedidos cresce.
Recommendation: Reescrever as consultas utilizando `LEFT JOIN` unificado entre pedidos, itens e produtos, agrupando o resultado em memória.

### [MEDIUM] Vazamento de Dados Sensíveis no Health Check
File: controllers.py:264-291
Description: O endpoint `/health` expõe informações de infraestrutura interna como caminho do banco SQLite (`db_path`), status de debug ativo e o valor literal da `SECRET_KEY`.
Impact: Reconhecimento e exploração facilitada de infraestrutura por atacantes.
Recommendation: Limitar a resposta do health check a status de conectividade operacional (`{"status": "ok", "database": "connected"}`).

### [MEDIUM] DDL e Carga Inicial (Seeds) Acopladas à Conexão do Banco
File: database.py:14-85
Description: A função `get_db()` cria tabelas e insere dados padrão toda vez que é chamada sem uma conexão prévia, misturando inicialização de schema com obtenção de conexão.
Impact: Operações redundantes e lentidão nas primeiras requisições.
Recommendation: Separar a inicialização do schema e seeds em comando/função de inicialização explícita (`init_db`).

### [LOW] Magic Numbers em Regras de Desconto do Relatório
File: models.py:257-262
Description: Faixas de faturamento (`10000`, `5000`, `1000`) e alíquotas de desconto (`0.1`, `0.05`, `0.02`) aparecem diretamente como literais no código.
Impact: Dificuldade de parametrização e pouca legibilidade das regras de negócio financeiras.
Recommendation: Definir constantes nomeadas ou parâmetros configuráveis para as regras de desconto.

### [LOW] Logging Desestruturado via print()
File: controllers.py:8, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250; app.py:56, 83-86
Description: Uso extensivo de `print()` com concatenação de strings para registrar ações e erros diretamente no stdout.
Impact: Falta de níveis de log (DEBUG, INFO, ERROR), timestamps padronizados e incapacidade de filtragem em produção.
Recommendation: Substituir por módulo padrão `logging` estruturado.

================================
Total: 12 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
