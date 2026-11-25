# Criação de Skills — Refatoração Arquitetural Automatizada (`refactor-arch`)

Repositório desenvolvido como entrega do desafio do módulo **Desenvolvimento de Software e Aplicações com IA**. Contém a implementação da Custom Skill agnóstica de tecnologia `refactor-arch`, capaz de analisar, auditar e refatorar qualquer base de código backend para o padrão **MVC (Model-View-Controller)**, com eliminação de vulnerabilidades críticas, code smells e gargalos de performance.

---

## Sumário
1. [Análise Manual dos Projetos](#a-análise-manual-dos-projetos)
2. [Construção da Skill `refactor-arch`](#b-construção-da-skill-refactor-arch)
3. [Resultados e Validação](#c-resultados-e-validação)
4. [Como Executar](#d-como-executar)
5. [Estrutura do Repositório](#estrutura-do-repositório)

---

## A) Análise Manual dos Projetos

Antes do desenvolvimento da Skill, os três projetos legados foram analisados minuciosamente para compreender suas deficiências arquiteturais, de segurança e de manutenibilidade.

### 1. `code-smells-project` (Python / Flask — E-commerce API)

| Severidade | Problema Identificado | Localização | Justificativa de Relevância |
|---|---|---|---|
| **CRITICAL** | **SQL Injection Generalizado** | `models.py:28, 48, 58, 68, 109, 127, 140, 149...` | Parâmetros externos de requisições HTTP são concatenados diretamente em strings SQL (`"WHERE id = " + str(id)` e `"WHERE email = '" + email + "'"`), permitindo extração total do banco e bypass de autenticação (`' OR '1'='1`). |
| **CRITICAL** | **Backdoor Administrativo Inseguro** | `app.py:47-79` | Endpoints `/admin/query` e `/admin/reset-db` expõem execução de qualquer comando SQL arbitrário e deleção em massa de dados sem nenhuma camada de autenticação ou autorização. |
| **CRITICAL** | **Hardcoded Credentials & Vazamento** | `app.py:7`; `controllers.py:289` | Chave de segurança (`SECRET_KEY = "minha-chave-super-secreta-123"`) fixada no código e exposta abertamente no JSON de resposta do endpoint `/health`. |
| **HIGH** | **God File / Falha de Separação de Camadas** | `models.py:1-314` | Um único arquivo contém regras de negócio, persistência, controle de estoque, cálculo financeiro e manipulação de 4 domínios (Produtos, Usuários, Pedidos e Relatórios). |
| **HIGH** | **Conexão SQLite Global sem Proteção de Concorrência** | `database.py:4-13` | Variável global `db_connection` compartilhada com `check_same_thread=False` sem isolamento por thread/request, provocando race conditions e locks em requisições paralelas. |
| **MEDIUM** | **N+1 Query Problem em Pedidos** | `models.py:187-200, 219-232` | Ao listar pedidos, queries filhas individuais são executadas repetidamente dentro de laços `for` para cada item e para cada produto, gerando dezenas de acessos desnecessários ao banco. |
| **MEDIUM** | **Armazenamento de Senhas em Texto Puro** | `models.py:105-131`; `database.py:76-83` | Senhas inseridas e consultadas sem nenhum algoritmo de hashing (ex: `senha = 'admin123'`), violando requisitos de segurança e conformidade (LGPD). |
| **LOW** | **Magic Numbers em Regras de Desconto** | `models.py:257-262` | Valores numéricos literais soltos no código (`10000`, `5000`, `1000`, `0.1`, `0.05`) sem nomenclatura de constantes descritivas. |
| **LOW** | **Logging Desestruturado via `print()`** | `controllers.py:8, 57, 106, 179...` | Uso excessivo de `print()` sem timestamps, formato JSON ou níveis de severidade (`INFO`, `WARN`, `ERROR`). |

---

### 2. `ecommerce-api-legacy` (Node.js / Express — LMS com Checkout)

| Severidade | Problema Identificado | Localização | Justificativa de Relevância |
|---|---|---|---|
| **CRITICAL** | **God Class Anti-Pattern** | `src/AppManager.js:4-140` | A classe `AppManager` absorve DDL de tabelas, inserção de seeds, mapeamento de rotas Express, regras de checkout, simulação de pagamento, queries SQL e escrita em cache. |
| **CRITICAL** | **Credenciais de Produção em Hardcode** | `src/utils.js:1-7` | Chaves confidenciais expostas em texto plano: senha do banco (`dbPass`), usuário admin e chave live de gateway de pagamento (`pk_live_1234567890abcdef`). |
| **CRITICAL** | **Exposição de Cartão de Crédito em Log (PCI-DSS)** | `src/AppManager.js:45` | O número completo do cartão (`cc`) é impresso diretamente no stdout junto com a chave secreta do gateway de pagamento, violando padrões internacionais de segurança. |
| **CRITICAL** | **Criptografia Quebrada (`badCrypto`)** | `src/utils.js:17-23` | Cifra caseira insegura construída concatenando substrings de Base64 em loop arbitrário de 10.000 iterações truncado em 10 caracteres, suscetível a colisões imediatas. |
| **HIGH** | **Callback Hell / Pirâmide da Morte** | `src/AppManager.js:37-77, 83-128` | Operações assíncronas aninhadas em 5 níveis de profundidade com callbacks sem promises ou `async/await`, dificultando o tratamento de erros e gerando memory leaks. |
| **HIGH** | **Estado Global Mutável Descontrolado** | `src/utils.js:9-10`; `src/AppManager.js:59` | Objetos globais `globalCache` e `totalRevenue` sofrem mutação concorrente sem sincronização, impedindo escalabilidade horizontal da aplicação. |
| **MEDIUM** | **N+1 Query Cascade no Relatório Financeiro** | `src/AppManager.js:80-128` | Laço forEach aninhado: para cada curso consulta matrículas; para cada matrícula busca aluno; e para cada aluno busca pagamentos. |
| **MEDIUM** | **Violação de Integridade Referencial na Deleção** | `src/AppManager.js:131-137` | `DELETE /api/users/:id` remove o usuário mas deixa registros órfãos em `enrollments` e `payments`, corrompendo a consistência dos relatórios contábeis. |
| **LOW** | **Nomenclatura Críptica de Variáveis** | `src/AppManager.js:29-33` | Variáveis `u`, `e`, `p`, `cid`, `cc`, `c`, `enr` que obscurecem o domínio de negócio e degradam a manutenibilidade. |
| **LOW** | **Respostas de Erro com Texto Puro** | `src/AppManager.js:35, 48, 51, 55` | Respostas `res.status(500).send("Erro DB")` sem serialização JSON padronizada ou middleware centralizado. |

---

### 3. `task-manager-api` (Python / Flask com Flask-SQLAlchemy)

| Severidade | Problema Identificado | Localização | Justificativa de Relevância |
|---|---|---|---|
| **CRITICAL** | **Hashing Obsoleto (MD5) e Vazamento de Senha** | `models/user.py:21, 29, 32` | Senhas salvas com hash `MD5` fraco (sujeito a colisões e rainbow tables) e expostas no dicionário de serialização `to_dict()`, permitindo que qualquer listagem de usuários vaze os hashes. |
| **CRITICAL** | **Credenciais SMTP em Texto Puro** | `services/notification_service.py:7-10` | Usuário (`taskmanager@gmail.com`) e senha de e-mail corporativo (`senha123`) fixados diretamente no construtor da classe. |
| **CRITICAL** | **Configuração e Segredos Fixados no Entrypoint** | `app.py:11-13` | `SECRET_KEY = 'super-secret-key-123'` e `SQLALCHEMY_DATABASE_URI = 'sqlite:///tasks.db'` hardcoded no arquivo principal. |
| **HIGH** | **Fat Routes / Ausência da Camada de Controllers** | `routes/task_routes.py`, `routes/user_routes.py` | Apesar de ter pastas separadas, as funções de rota executam regras de negócio, validações profundas e transações `db.session`, ausentando a camada de Controllers. |
| **HIGH** | **I/O Bloqueante Síncrono no Request Cycle** | `services/notification_service.py:12-25` | Envio de e-mail síncrono via `smtplib.SMTP` disparado inline no fluxo de criação de tarefas, travando a thread HTTP do servidor. |
| **MEDIUM** | **N+1 Query Problem em Listagem e Relatório** | `routes/report_routes.py:33-43, 53-68`; `routes/task_routes.py:41-58` | Loop em tarefas disparando `User.query.get(t.user_id)` individualmente, e loop em usuários consultando tarefas de cada um no relatório de produtividade. |
| **MEDIUM** | **Uso de APIs Deprecated (`datetime.utcnow` e `Model.query.get`)** | `models/`, `routes/`, `services/`, `utils/helpers.py` | `datetime.utcnow()` depreciado no Python 3.12+ (recomendado `datetime.now(timezone.utc)`) e `Model.query.get(id)` depreciado no SQLAlchemy 2.0 (recomendado `db.session.get`). |
| **LOW** | **Tratamento Genérico Silencioso de Exceções** | `routes/task_routes.py:62-63` | Bloco `try ... except:` captura todas as falhas sem tipagem e devolve erro 500 genérico sem registrar log do stack trace. |
| **LOW** | **Código Morto e Inconsistências em Helpers** | `utils/helpers.py:31-34, 43-50` | Função `generate_id` com UUID nunca é chamada, e múltiplos blocos `try/except` desnecessários para parsing de data. |

---

## B) Construção da Skill `refactor-arch`

### 1. Decisões de Design e Estrutura

A Skill foi desenhada com separação estrita entre o **orquestrador de fluxo** (`SKILL.md`) e os **arquivos de conhecimento de domínio** (`references/`):

```
.claude/skills/refactor-arch/
├── SKILL.md                          # Orquestrador sequencial das 3 fases
└── references/
    ├── project-analysis.md           # Heurísticas de detecção de linguagem, framework e arquitetura
    ├── anti-patterns.md              # Catálogo com 13 anti-patterns detalhados por severidade
    ├── report-template.md            # Template padronizado de saída para a Fase 2
    ├── mvc-guidelines.md             # Diretrizes arquiteturais para o padrão MVC alvo
    └── refactoring-playbook.md       # 9 padrões concretos de transformação com exemplos Antes/Depois
```

- **Fase 1 (Project Analysis)**: Varre manifestos (`requirements.txt`, `package.json`, `*.csproj`), detecta dependências, entidades e padrão atual, exibindo o banner padronizado de análise.
- **Fase 2 (Architecture Audit)**: Cruza o código contra o catálogo de anti-patterns, detecta APIs deprecated, ordena os findings por severidade (`CRITICAL` -> `HIGH` -> `MEDIUM` -> `LOW`) e **obrigatoriamente pausa** para confirmação humana (`Proceed with refactoring (Phase 3)? [y/n]`).
- **Fase 3 (Refactoring Complete)**: Cria a estrutura de diretórios MVC, extrai configurações, parametriza queries, substitui criptografia fraca, resolve N+1 e valida boot e integridade dos endpoints.

### 2. Catálogo de Anti-Patterns Incluídos

O catálogo foi estruturado com base nas vulnerabilidades e falhas reais observadas:
1. `God Class / God File` (CRITICAL) — Violação severa de SRP e acoplamento máximo.
2. `SQL Injection & Unsanitized Queries` (CRITICAL) — Concatenação de strings em queries.
3. `Hardcoded Secrets & Credential Exposure` (CRITICAL) — Chaves privadas e senhas em código.
4. `Broken Cryptography / Insecure Password Storage` (CRITICAL) — Senhas em texto puro, MD5 e algoritmos caseiros.
5. `Plaintext Sensitive Data in Logs` (CRITICAL) — Números de cartão e tokens confidenciais em logs.
6. `Insecure Administrative Backdoors` (CRITICAL) — Endpoints que executam DDL/DML sem autenticação.
7. `Fat Routes / Missing Controller Layer` (HIGH) — Rotas acumulando lógica de negócio e banco.
8. `Callback Hell & Unhandled Promises` (HIGH) — Pirâmide da morte e concorrência assíncrona instável.
9. `Global Mutable State & Unsafe Concurrency` (HIGH) — Caches e conexões mutáveis em memória.
10. `Synchronous Blocking I/O in Request Cycle` (HIGH) — Conexões SMTP/rede travando threads HTTP.
11. `N+1 Query Problem` (MEDIUM) — Queries repetitivas em loops.
12. `Deprecated APIs Usage` (MEDIUM) — `datetime.utcnow()` e `Model.query.get()`.
13. `Swallowed / Bare Exception Handling` (MEDIUM) — Captura silenciosa de falhas.
14. `Magic Numbers & Unnamed Constants` (LOW) — Literais numéricos sem contexto.
15. `Cryptic Variable Naming` (LOW) — Identificadores de 1 a 2 letras.
16. `Unstructured Console Output` (LOW) — Prints diretos sem formato e sem nível de log.

### 3. Garantia de Agnosticismo Tecnológico

Para funcionar em Python (Flask/SQLAlchemy), Node.js (Express), C# (.NET / ASP.NET Core) ou qualquer outra stack:
- As heurísticas analisam **conceitos arquiteturais**, não apenas palavras-chave de uma única sintaxe.
- O catálogo avalia responsabilidades de camadas (ex: rota chamando banco diretamente é um anti-pattern em qualquer linguagem).
- O playbook contém exemplos concretos e idiomáticos para **Python**, **Node.js/JavaScript** e **C# / .NET** (ASP.NET Core Controllers, Entity Framework Core, Dapper, PBKDF2), permitindo que o agente aplique a transformação correta de acordo com a stack detectada na Fase 1.

### 4. Desafios Encontrados e Soluções

1. **Retrocompatibilidade de Dados Existentes no SQLite**:
   - *Desafio*: Ao migrar senhas em texto puro ou MD5 para hashing seguro (PBKDF2/SHA256 com salt), logins de usuários pré-seedados falhariam.
   - *Solução*: Implementação de verificação de senha retrocompatível: se o hash armazenado não possui salt formatado (`salt:hash`), o sistema valida com a regra legada no primeiro login, permitindo re-hashing transparente.
2. **Eliminação de N+1 Queries sem Quebrar Contratos**:
   - *Desafio*: Consultas com `LEFT JOIN` trazem linhas duplicadas para relacionamentos 1:N (pedidos e itens, cursos e matrículas).
   - *Solução*: Algoritmos eficientes de agrupamento em memória em complexidade $O(N)$, reconstruindo a estrutura aninhada esperada pelos clientes da API sem disparar queries adicionais.
3. **Múltiplos Níveis de Organização Inicial dos Projetos**:
   - *Desafio*: O `code-smells-project` era um monolito de 4 arquivos misturados, enquanto o `task-manager-api` já possuía pastas `models/` e `routes/`, mas carecia de `controllers/`.
   - *Solução*: A Skill avalia a topologia atual e aplica a refatoração incremental necessária: nos monolitos ela cria toda a árvore MVC; no projeto parcialmente organizado ela introduz a camada faltante (`controllers/`), move a orquestração e refatora os modelos sem destruir a estrutura existente.

---

## C) Resultados e Validação

### 1. Resumo dos Relatórios de Auditoria

| Projeto | Stack | Arquivos | Linhas | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|---|---|---|
| `code-smells-project` | Python / Flask | 4 | ~780 | 5 | 2 | 3 | 2 | **12** |
| `ecommerce-api-legacy` | Node.js / Express | 3 | ~180 | 4 | 2 | 2 | 2 | **10** |
| `task-manager-api` | Python / Flask | 12 | ~1050 | 3 | 2 | 3 | 2 | **10** |

*Os relatórios completos da Fase 2 de cada projeto estão arquivados em `reports/audit-project-1.md`, `reports/audit-project-2.md` e `reports/audit-project-3.md`.*

---

### 2. Comparação de Estrutura Antes / Depois

#### Projeto 1: `code-smells-project`

```
ANTES:
code-smells-project/
├── app.py              # Monolítico: rotas, backdoors e inicialização
├── controllers.py      # Lógica de negócio pesada, prints, validações
├── database.py         # Conexão global compartilhada com check_same_thread=False e DDL
├── models.py           # God File: 4 domínios, SQL Injection generalizado, senhas planas
└── requirements.txt

DEPOIS (MVC):
code-smells-project/
├── .claude/skills/refactor-arch/  # Skill completa
├── src/
│   ├── config/settings.py        # Configurações centralizadas via os.getenv
│   ├── database/connection.py    # Conexão segura com teardown por request e DDL isolado
│   ├── models/
│   │   ├── produto_model.py      # Queries parametrizadas com bind variables
│   │   ├── usuario_model.py      # Hashing seguro com salt e auth protegida
│   │   ├── pedido_model.py       # Transações atômicas e consultas com JOIN (sem N+1)
│   │   └── relatorio_model.py    # Cálculos desacoplados com constantes nomeadas
│   ├── controllers/
│   │   ├── produto_controller.py
│   │   ├── usuario_controller.py
│   │   ├── pedido_controller.py
│   │   ├── relatorio_controller.py
│   │   └── health_controller.py  # Health check seguro e saneado
│   ├── routes/
│   │   ├── produto_routes.py     # Blueprints dedicados
│   │   ├── usuario_routes.py
│   │   ├── pedido_routes.py
│   │   ├── relatorio_routes.py
│   │   └── health_routes.py
│   └── middlewares/
│       └── error_handler.py      # Tratamento centralizado de exceções HTTP
├── app.py                        # Composition root limpo
├── database.py / models.py / controllers.py (Shims retrocompatíveis)
└── requirements.txt
```

#### Projeto 2: `ecommerce-api-legacy`

```
ANTES:
ecommerce-api-legacy/
├── src/
│   ├── app.js            # Instancia AppManager diretamente
│   ├── AppManager.js     # God Class: DDL, seeds, rotas, checkout, callbacks aninhados
│   └── utils.js          # Credenciais em hardcode, badCrypto e estado global mutável
├── api.http
└── package.json

DEPOIS (MVC):
ecommerce-api-legacy/
├── .claude/skills/refactor-arch/  # Skill completa
├── src/
│   ├── config/settings.js        # Configurações via process.env
│   ├── database/connection.js    # Conexão SQLite promisificada (async/await)
│   ├── models/
│   │   ├── UserModel.js          # Hashing pbkdf2 seguro e deleção em cascata
│   │   ├── CourseModel.js        # Queries de cursos e relatórios com JOIN otimizado
│   │   ├── EnrollmentModel.js    # Gestão de matrículas
│   │   ├── PaymentModel.js       # Gestão de pagamentos e auditoria
│   │   └── AuditLogModel.js      # Logs estruturados no banco
│   ├── controllers/
│   │   ├── CheckoutController.js # Checkout com máscara de cartão e tratamento de erro
│   │   ├── ReportController.js   # Relatório financeiro sem N+1
│   │   └── UserController.js     # Deleção de usuário com integridade referencial
│   ├── routes/
│   │   ├── checkoutRoutes.js
│   │   ├── reportRoutes.js
│   │   └── userRoutes.js
│   ├── middlewares/
│   │   └── errorHandler.js       # Middleware de erro centralizado do Express
│   ├── utils/crypto.js           # Funções seguras de hash, verificação e máscara
│   └── app.js                    # Entrypoint desacoplado e startServer assíncrono
├── api.http
└── package.json
```

#### Projeto 3: `task-manager-api`

```
ANTES:
task-manager-api/
├── app.py                        # Hardcoded SECRET_KEY e database URI
├── models/user.py                # MD5 fraco e vazamento de senha em to_dict()
├── models/task.py                # datetime.utcnow() deprecated
├── routes/                       # Fat Routes sem Controllers (regras e transações)
├── services/notification_service.py # Credenciais SMTP em texto puro e I/O bloqueante
└── utils/helpers.py

DEPOIS (MVC):
task-manager-api/
├── .claude/skills/refactor-arch/  # Skill completa
├── config/settings.py            # Centralização de configurações e credenciais SMTP
├── models/
│   ├── user.py                   # Hashing SHA256 com salt; senha removida de to_dict()
│   ├── task.py                   # datetime.now(timezone.utc) e comparação segura
│   └── category.py               # datetime moderno e serialização limpa
├── controllers/                  # Camada de Controllers criada
│   ├── user_controller.py        # Orquestração de usuários e autenticação
│   ├── task_controller.py        # CRUD de tarefas, busca e estatísticas com joinedload
│   └── report_controller.py      # Relatório com agregação SQL direta (sem N+1)
├── routes/
│   ├── user_routes.py            # Rotas enxutas delegando aos controllers
│   ├── task_routes.py            # Rotas enxutas delegando aos controllers
│   └── report_routes.py          # Rotas enxutas delegando aos controllers
├── services/notification_service.py # Timeout seguro e fallbacks não bloqueantes
├── app.py                        # Inicialização limpa via factory
└── seed.py / requirements.txt
```

---

### 3. Checklist de Validação Preenchido

#### Checklist — `code-smells-project` (Python/Flask)
- [x] **Fase 1 — Análise**
  - [x] Linguagem detectada corretamente (Python)
  - [x] Framework detectado corretamente (Flask 3.1.1)
  - [x] Domínio da aplicação descrito corretamente (E-commerce API)
  - [x] Número de arquivos analisados condiz com a realidade (4 arquivos)
- [x] **Fase 2 — Auditoria**
  - [x] Relatório segue o template definido nos arquivos de referência
  - [x] Cada finding tem arquivo e linhas exatos
  - [x] Findings ordenados por severidade (CRITICAL → LOW)
  - [x] Mínimo de 5 findings identificados (12 identificados)
  - [x] Detecção de APIs deprecated incluída
  - [x] Skill pausa e pede confirmação antes da Fase 3
- [x] **Fase 3 — Refatoração**
  - [x] Estrutura de diretórios segue padrão MVC (`src/config`, `models`, `controllers`, `routes`)
  - [x] Configuração extraída para módulo de config (sem hardcoded)
  - [x] Models criados para abstrair dados
  - [x] Views/Routes separadas para visualização ou roteamento
  - [x] Controllers concentram o fluxo da aplicação
  - [x] Error handling centralizado
  - [x] Entry point claro (`app.py` com factory)
  - [x] Aplicação inicia sem erros
  - [x] Endpoints originais respondem corretamente

#### Checklist — `ecommerce-api-legacy` (Node.js/Express)
- [x] **Fase 1 — Análise**
  - [x] Linguagem detectada corretamente (Node.js / JavaScript)
  - [x] Framework detectado corretamente (Express 4.18.2)
  - [x] Domínio da aplicação descrito corretamente (LMS API com checkout)
  - [x] Número de arquivos analisados condiz com a realidade (3 arquivos)
- [x] **Fase 2 — Auditoria**
  - [x] Relatório segue o template definido nos arquivos de referência
  - [x] Cada finding tem arquivo e linhas exatos
  - [x] Findings ordenados por severidade (CRITICAL → LOW)
  - [x] Mínimo de 5 findings identificados (10 identificados)
  - [x] Detecção de APIs deprecated incluída
  - [x] Skill pausa e pede confirmação antes da Fase 3
- [x] **Fase 3 — Refatoração**
  - [x] Estrutura de diretórios segue padrão MVC (`src/config`, `models`, `controllers`, `routes`)
  - [x] Configuração extraída para módulo de config (sem hardcoded)
  - [x] Models criados para abstrair dados
  - [x] Views/Routes separadas para visualização ou roteamento
  - [x] Controllers concentram o fluxo da aplicação
  - [x] Error handling centralizado (`middlewares/errorHandler.js`)
  - [x] Entry point claro (`src/app.js` com `startServer`)
  - [x] Aplicação inicia sem erros
  - [x] Endpoints originais respondem corretamente

#### Checklist — `task-manager-api` (Python/Flask)
- [x] **Fase 1 — Análise**
  - [x] Linguagem detectada corretamente (Python)
  - [x] Framework detectado corretamente (Flask + Flask-SQLAlchemy)
  - [x] Domínio da aplicação descrito corretamente (Task Manager API)
  - [x] Número de arquivos analisados condiz com a realidade (12 arquivos)
- [x] **Fase 2 — Auditoria**
  - [x] Relatório segue o template definido nos arquivos de referência
  - [x] Cada finding tem arquivo e linhas exatos
  - [x] Findings ordenados por severidade (CRITICAL → LOW)
  - [x] Mínimo de 5 findings identificados (10 identificados)
  - [x] Detecção de APIs deprecated incluída (`datetime.utcnow()` e `Model.query.get()`)
  - [x] Skill pausa e pede confirmação antes da Fase 3
- [x] **Fase 3 — Refatoração**
  - [x] Estrutura de diretórios segue padrão MVC com adição da camada `controllers/`
  - [x] Configuração extraída para módulo de config (`config/settings.py`)
  - [x] Models criados e protegidos (senha removida do `to_dict()`)
  - [x] Views/Routes enxutas delegando aos controllers
  - [x] Controllers concentram o fluxo e regras da aplicação
  - [x] Error handling centralizado
  - [x] Entry point claro (`app.py` com factory)
  - [x] Aplicação inicia sem erros
  - [x] Endpoints originais respondem corretamente

---

### 4. Evidência de Execução dos Endpoints Refatorados

Log da suite de validação em execução real no projeto `ecommerce-api-legacy`:

```text
Server started successfully!
Frankenstein LMS refatorado rodando na porta 3000...
Financial report response status: 200
Financial report data: [{"course":"Clean Architecture","revenue":997,"students":[{"student":"Leonan","paid":997}]},{"course":"Docker","revenue":0,"students":[]}]
[INFO] Processando transação com cartão **** **** **** 4444 para o curso 2
Checkout success status: 200
Checkout response body: {"msg":"Sucesso","enrollment_id":2}
[INFO] Processando transação com cartão **** **** **** 4444 para o curso 1
Checkout denied status: 400
Checkout denied body: Pagamento recusado
Delete user status: 200
Delete user body: Usuário deletado com sucesso e integridade referencial mantida.
All tests passed! Server closed.
```

---

## D) Como Executar

### Pré-requisitos
- **Node.js** (v18+) e **npm** instalados;
- **Python** (3.10+) e **pip** instalados;
- Ferramenta agêntica com suporte a Custom Skills (ex: **Claude Code**, **Gemini CLI** ou **Antigravity**).

### Execução da Skill por Projeto

#### Projeto 1 — `code-smells-project`
```bash
cd code-smells-project
# Invocar a skill pelo comando registrado na ferramenta
claude "/refactor-arch"

# Para rodar a aplicação refatorada
pip install -r requirements.txt
python app.py
```
Acesse `http://localhost:5000/` ou teste os endpoints:
```bash
curl http://localhost:5000/produtos
curl http://localhost:5000/health
```

#### Projeto 2 — `ecommerce-api-legacy`
```bash
cd ecommerce-api-legacy
# Invocar a skill pelo comando registrado na ferramenta
claude "/refactor-arch"

# Para rodar a aplicação refatorada
npm install
npm start
```
Acesse `http://localhost:3000/` ou execute os testes via arquivo `api.http`.

#### Projeto 3 — `task-manager-api`
```bash
cd task-manager-api
# Invocar a skill pelo comando registrado na ferramenta
claude "/refactor-arch"

# Para rodar a aplicação refatorada
pip install -r requirements.txt
python seed.py
python app.py
```
Acesse `http://localhost:5000/` ou teste os endpoints:
```bash
curl http://localhost:5000/health
curl http://localhost:5000/tasks
curl http://localhost:5000/reports/summary
```

---

## Estrutura do Repositório

```
mba-ia-refactor-projects-skill/
├── .claude/
│   └── skills/
│       └── refactor-arch/             # Skill na raiz do repositório
│           ├── SKILL.md
│           └── references/
│               ├── anti-patterns.md
│               ├── mvc-guidelines.md
│               ├── project-analysis.md
│               ├── refactoring-playbook.md
│               └── report-template.md
├── reports/                           # Relatórios de auditoria gerados (Fase 2)
│   ├── audit-project-1.md
│   ├── audit-project-2.md
│   └── audit-project-3.md
├── code-smells-project/               # Projeto 1 — Python/Flask (Refatorado MVC)
│   ├── .claude/skills/refactor-arch/  # Cópia da skill
│   ├── src/                           # Camadas MVC desacopladas
│   ├── app.py
│   └── requirements.txt
├── ecommerce-api-legacy/              # Projeto 2 — Node.js/Express (Refatorado MVC)
│   ├── .claude/skills/refactor-arch/  # Cópia da skill
│   ├── src/                           # Camadas MVC desacopladas
│   ├── api.http
│   └── package.json
├── task-manager-api/                  # Projeto 3 — Python/Flask (Refatorado MVC)
│   ├── .claude/skills/refactor-arch/  # Cópia da skill
│   ├── config/
│   ├── controllers/                   # Nova camada de Controllers
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── app.py
│   ├── seed.py
│   └── requirements.txt
└── README.md                          # Esta documentação completa
```
