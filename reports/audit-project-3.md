================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask (Flask-SQLAlchemy)
Files:   12 analyzed | ~1050 lines of code

## Summary
CRITICAL: 3 | HIGH: 2 | MEDIUM: 3 | LOW: 2

## Findings

### [CRITICAL] Hashing Obsoleto (MD5) e Vazamento de Senha na Serialização
File: models/user.py:21, 29, 32
Description: O método `set_password` utiliza o algoritmo `MD5` (`hashlib.md5(pwd.encode()).hexdigest()`), que é vulnerável a ataques de colisão e quebra instantânea por rainbow tables. Adicionalmente, o método `to_dict()` expõe o hash da senha diretamente no payload JSON retornado nas consultas de usuários (`'password': self.password`).
Impact: Comprometimento crítico de senhas de usuários e vazamento de hashes sensíveis em APIs públicas.
Recommendation: Migrar para hashing moderno com salt (PBKDF2/SHA-256 ou bcrypt) e remover o campo `password` da serialização `to_dict()`.

### [CRITICAL] Credenciais SMTP em Hardcode no Código-Fonte
File: services/notification_service.py:7-10
Description: Configurações de autenticação de e-mail com host, porta e credenciais reais (`self.email_user = 'taskmanager@gmail.com'`, `self.email_password = 'senha123'`) estão declaradas diretamente no construtor do serviço.
Impact: Exposição de credenciais de e-mail corporativo em repositórios de código.
Recommendation: Mover todas as credenciais SMTP para variáveis de ambiente carregadas via `config/settings.py`, com fallback vazio e desativação por padrão (JAMAIS manter a senha vazada 'senha123' como default no código). Fornecer arquivo `.env.example`.

### [CRITICAL] Hardcoded SECRET_KEY e Configurações de Banco
File: app.py:11-13
Description: `app.config['SECRET_KEY'] = 'super-secret-key-123'` e `app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'` estão fixados no código-fonte do entrypoint.
Impact: Insegurança na assinatura de cookies de sessão e impossibilidade de configurar bancos de dados diferentes entre ambientes (dev, staging, prod).
Recommendation: Centralizar as configurações em classe `Config` com leitura via `os.getenv()`, utilizando chave dummy inofensiva de desenvolvimento (JAMAIS manter 'super-secret-key-123' como default). Fornecer arquivo `.env.example`.

### [HIGH] Fat Routes / Ausência da Camada de Controllers
File: routes/task_routes.py:11-299; routes/user_routes.py:10-211; routes/report_routes.py:12-220
Description: Embora o projeto possua separação em pastas, as rotas funcionam como "Fat Routes", concentrando validações complexas, regras de negócio, manipulação de transações do banco (`db.session.add`, `db.session.commit`) e formatação de resposta. Não existe camada de Controllers.
Impact: Forte violação do Princípio de Responsabilidade Única (SRP), impossibilidade de reaproveitar lógicas de negócio e alta dificuldade de escrita de testes automatizados.
Recommendation: Introduzir a camada de `controllers/` (`task_controller.py`, `user_controller.py`, `report_controller.py`) para coordenar o fluxo entre requisições HTTP e os Models/Services.

### [HIGH] I/O Bloqueante Síncrono no Ciclo da Requisição HTTP
File: services/notification_service.py:12-25; routes/task_routes.py:128
Description: O envio de e-mails via `smtplib.SMTP` é síncrono e bloqueante. Ao criar ou atribuir uma tarefa, a requisição HTTP do usuário fica congelada aguardando o handshake TLS e resposta do servidor SMTP.
Impact: Degradação severa de tempo de resposta e travamento do servidor em picos de requisições ou instabilidades de rede SMTP.
Recommendation: Desacoplar notificações para execução em background ou permitir modo simulado/mock não bloqueante em ambiente síncrono.

### [MEDIUM] N+1 Query Problem no Relatório e na Listagem de Tarefas
File: routes/report_routes.py:33-43, 53-68; routes/task_routes.py:41-58
Description: A rota `/tasks` busca todas as tarefas e, dentro de um laço `for`, executa queries individuais para buscar `User.query.get(t.user_id)` e `Category.query.get(t.category_id)`. Similarmente, o relatório `/reports/summary` itera sobre todos os usuários executando `Task.query.filter_by(user_id=u.id).all()` para cada um.
Impact: Explosão de queries desnecessárias causando latência e degradação de throughput no banco.
Recommendation: Utilizar `joinedload` do SQLAlchemy ou consultas de agregação agrupadas (`GROUP BY`) para trazer os dados em lote.

### [MEDIUM] Uso de APIs Deprecated (datetime.utcnow e Model.query.get)
File: models/user.py:14; models/task.py:15-16; models/category.py:11; routes/report_routes.py:35, 42, 45, 71; routes/user_routes.py:29, 94; routes/task_routes.py:31, 42, 51, 67, 72
Description: O método `datetime.utcnow()` é utilizado amplamente para datas padrão e checagem de prazos, sendo formalmente depreciado a partir do Python 3.12 (com recomendação oficial de substituição por `datetime.now(timezone.utc)`). Além disso, a sintaxe legada `Model.query.get(id)` do SQLAlchemy 1.x é utilizada em vez de `db.session.get(Model, id)`.
Impact: Avisos de depreciação (`DeprecationWarning`) e risco de incompatibilidade futura com versões recentes de Python e SQLAlchemy.
Recommendation: Substituir todas as ocorrências por `datetime.now(timezone.utc)` e `db.session.get(Model, id)`.

### [MEDIUM] Tratamento Genérico Silencioso de Exceções (Swallowed Exceptions)
File: routes/task_routes.py:62-63
Description: O bloco `try ... except:` na listagem de tarefas captura qualquer exceção sem tipagem (`except:`) e retorna `{"error": "Erro interno"}` sem registrar log do stack trace.
Impact: Mascaramento de erros de banco, sintaxe ou tipagem, impossibilitando depuração em caso de falha.
Recommendation: Capturar classes de exceção específicas (`Exception as e`), registrar log estruturado do erro e padronizar o payload de resposta.

### [LOW] Funções Redundantes e Inconsistências em Helpers
File: utils/helpers.py:31-34, 43-50
Description: Funções auxiliares como `generate_id()` utilizam `uuid.uuid4()` que nunca é consumido pelo sistema, e `parse_date()` possui múltiplos blocos `try/except` aninhados sem documentação de formato padrão.
Impact: Código morto e complexidade ciclomática desnecessária em utilitários.
Recommendation: Limpar código morto e consolidar validações de data de forma determinística.

### [LOW] Logging Desestruturado via print()
File: routes/user_routes.py:83, 89; services/notification_service.py:21, 24; utils/helpers.py:39-41
Description: Mensagens de depuração e erros são impressas via `print()` diretamente no console sem timestamp ISO ou nível de severidade.
Impact: Falta de rastreabilidade de eventos em ambientes de produção.
Recommendation: Substituir chamadas de `print()` por instâncias do módulo padrão `logging`.

================================
Total: 10 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
