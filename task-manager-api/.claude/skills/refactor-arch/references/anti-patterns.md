# Catálogo de Anti-Patterns e Sinais de Detecção (Phase 2)

Classificação oficial de anti-patterns arquiteturais, code smells e vulnerabilidades com base nos princípios **MVC**, **SOLID** e boas práticas de segurança (OWASP).

---

## 1. Classificação por Severidade

### [CRITICAL]
Falhas graves de arquitetura ou segurança que expõem a aplicação a comprometimento, vazam credenciais/dados sensíveis ou colapsam completamente o isolamento de camadas.

1. **God Class / God File**:
   - **Sinais**: Arquivo ou classe única que assume múltiplas responsabilidades vitais (DDL do banco, queries SQL diretas, regras de negócio de múltiplos domínios, manipulação de HTTP, formatação de respostas e agendamento). Ex: `AppManager.js` com rotas, DB, pagamentos e logs; ou `models.py` contendo lógica de produtos, usuários, pedidos e relatórios juntos.
   - **Impacto**: Impossibilidade de testes unitários, altíssimo risco de regressão, forte acoplamento.
2. **SQL Injection & Unsanitized Queries**:
   - **Sinais**: Concatenação direta de strings ou interpolação com dados de requisições HTTP em queries SQL:
     - Python: `"SELECT * FROM produtos WHERE id = " + str(id)` ou `f"WHERE email = '{email}'"`
     - Node.js: `"SELECT * FROM users WHERE email = '" + req.body.email + "'"`
     - C# / .NET: `_context.Database.SqlQueryRaw($"SELECT * FROM Users WHERE Id = {id}")`, `FromSqlRaw($"... {id}")` ou Dapper `conn.Query($"SELECT * FROM Users WHERE Email = '{email}'")` sem objeto anônimo de parâmetros.
   - **Impacto**: Risco total de exfiltração, adulteração ou destruição do banco de dados.
3. **Hardcoded Secrets & Credential Exposure**:
   - **Sinais**: Chaves de criptografia (`SECRET_KEY`), senhas de banco (`dbPass`), chaves de gateway de pagamento (`paymentGatewayKey = "pk_live_..."`) ou credenciais SMTP gravadas no código-fonte.
   - **Impacto**: Comprometimento direto em repositórios e ambientes compartilhados.
4. **Broken Cryptography & Insecure Password Storage**:
   - **Sinais**: Senhas armazenadas em texto puro, funções de cifra customizadas e fracas (ex: loops de Base64) ou algoritmos criptograficamente quebrados (MD5, SHA-1).
   - **Impacto**: Quebra imediata de credenciais de usuários e violação de conformidade (LGPD/GDPR).
5. **Backdoors Administrativos Inseguros**:
   - **Sinais**: Rotas públicas de administração (`/admin/query`, `/admin/reset-db`) que executam SQL arbitrário fornecido pelo cliente ou resetam dados sem autenticação.
   - **Impacto**: Acesso irrestrito ao sistema por qualquer ator não autenticado.
6. **Plaintext Sensitive Data in Logs (PCI-DSS / Privacy Breach)**:
   - **Sinais**: `console.log` ou `print` gravando números completos de cartão de crédito (`card`) ou senhas no stdout/logs.
   - **Impacto**: Violação de normas de conformidade de pagamento e vazamento de dados de cartão.

---

### [HIGH]
Fortes violações do padrão MVC ou princípios SOLID que dificultam severamente a manutenção, a extensibilidade e a confiabilidade.

7. **Fat Routes / Missing Controller Layer**:
   - **Sinais**: Funções de rota (handlers de rotas ou blueprints) executando diretamente transações no banco, validações complexas de dados e orquestração de serviços, sem uma camada de Controllers dedicada.
   - **Impacto**: Inviolabilidade do princípio de responsabilidade única (SRP), duplicação de regras e impossibilidade de reaproveitamento de fluxo.
8. **Callback Hell / Unhandled Asynchronous Flow**:
   - **Sinais**: Encadeamento piramidal de callbacks em Node.js (5+ níveis de profundidade com `this.db.get`, `this.db.run`) sem promises ou `async/await`.
   - **Impacto**: Ilegibilidade crítica, propensão a memory leaks e perda de rastreabilidade de erros.
9. **Global Mutable State & Unsafe Concurrency**:
   - **Sinais**: Variáveis globais mutáveis no módulo (ex: `let globalCache = {}`, `let totalRevenue = 0` ou conexão global `db_connection` com `check_same_thread=False` em Python).
   - **Impacto**: Condições de corrida (race conditions), inconsistência entre requisições concorrentes e comportamento não idempotente.
10. **Synchronous Blocking I/O & Sync-Over-Async**:
    - **Sinais**:
      - Conexões síncronas bloqueantes de rede ou disco durante a requisição HTTP (ex: `smtplib.SMTP` direto em Python).
      - C# / .NET: Padrão **Sync-over-Async** bloqueando threads com `.Result`, `.Wait()` ou `.GetAwaiter().GetResult()` sobre `Task` assíncrona, provocando thread pool starvation e deadlocks no ASP.NET.
    - **Impacto**: Esgotamento do pool de threads, contenção de conexões e travamento da aplicação sob concorrência.

---

### [MEDIUM]
Problemas de padronização, duplicação de código, gargalos de performance e uso de tecnologias descontinuadas.

11. **N+1 Query Problem**:
    - **Sinais**: Laço de repetição (`for` ou `forEach`) realizando uma query SQL para cada registro obtido em uma query anterior (ex: loop em pedidos executando query para cada item, ou loop em cursos buscando matrículas, alunos e pagamentos um a um).
    - **Impacto**: Degradação exponencial de tempo de resposta e sobrecarga no banco de dados.
12. **Deprecated APIs Usage**:
    - **Sinais**:
      - Python: Uso de `datetime.utcnow()` (deprecated desde Python 3.12 em prol de `datetime.now(timezone.utc)`).
      - SQLAlchemy / Flask-SQLAlchemy: Uso do padrão de consulta legado `Model.query.get(id)` (descontinuado no SQLAlchemy 2.0 em favor de `db.session.get(Model, id)`).
      - Node.js: Uso de métodos obsoletos de buffer (`new Buffer()`) ou padrões legados sem tratamento assíncrono.
      - C# / .NET:
        - `BinaryFormatter` (inseguro e obsoleto com `SYSLIB0011` no .NET 7/8/9 em favor de `System.Text.Json`).
        - `MD5CryptoServiceProvider` / `SHA1Managed` (obsoletos em prol de `SHA256.HashData` ou `Rfc2898DeriveBytes`).
        - `app.UseEndpoints(endpoints => ...)` e `IHostingEnvironment` (obsoletos no ASP.NET Core moderno em prol de top-level route mapping e `IWebHostEnvironment`).
    - **Impacto**: Quebra de compatibilidade em upgrades de versão de bibliotecas e runtime.
13. **Swallowed / Bare Exception Handling**:
    - **Sinais**: Blocos `except:` sem especificar a classe de exceção, ou `try/catch` que apenas retornam uma mensagem genérica sem registrar o stack trace.
    - **Impacto**: Ocultação de bugs graves e impossibilidade de observabilidade em produção.
14. **Lack of Input Validation**:
    - **Sinais**: Rotas que aceitam dados do corpo da requisição sem validação de tipos, faixas ou presença de campos obrigatórios.
    - **Impacto**: Inconsistências de dados e respostas de erro 500 inesperadas.

---

### [LOW]
Problemas de legibilidade, estilo de código, manutenibilidade e ruído operacional.

15. **Magic Numbers & Unnamed Constants**:
    - **Sinais**: Valores literais soltos no meio do código (ex: `10000`, `5000`, `0.1`, `997.00`, limites fixos numéricos) sem nomeação descritiva.
    - **Impacto**: Dificuldade para entender o significado do cálculo ou alterar regras no futuro.
16. **Cryptic Variable Naming**:
    - **Sinais**: Variáveis com 1 ou 2 caracteres (`u`, `e`, `p`, `cid`, `cc`, `c`, `enr`, `p1`, `p2`) que não comunicam seu propósito.
    - **Impacto**: Baixa legibilidade e esforço cognitivo desnecessário para entendimento.
17. **Unstructured Console Logging**:
    - **Sinais**: Uso de `print()` ou `console.log()` direto no código com strings concatenadas, em vez de um mecanismo padronizado de logging com níveis (`INFO`, `WARN`, `ERROR`).
    - **Impacto**: Poluição do stdout sem controle de nível de log e sem formato estruturado (JSON).
