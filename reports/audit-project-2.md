================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express 4.18.2
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 4 | HIGH: 2 | MEDIUM: 2 | LOW: 2

## Findings

### [CRITICAL] God Class Anti-Pattern (`AppManager`)
File: src/AppManager.js:4-140
Description: A classe `AppManager` atua como um "God Object", centralizando a instanciação do banco de dados SQLite em memória, DDLs (`CREATE TABLE`), inserção de seeds, mapeamento de rotas Express, regras de checkout, integração simulada de pagamento, geração de relatórios e manipulação de cache.
Impact: Quebra total do princípio de responsabilidade única (SRP), impossibilidade de testes em isolamento e acoplamento máximo de todos os domínios (Cursos, Usuários, Matrículas, Pagamentos).
Recommendation: Decompor o monólito em camadas MVC: `config/`, `database/`, `models/` (User, Course, Enrollment, Payment), `controllers/` (Checkout, Report, User) e `routes/`.

### [CRITICAL] Vazamento de Dados Sensíveis de Cartão e Chave Privada em Logs (PCI-DSS)
File: src/AppManager.js:45
Description: O número completo do cartão de crédito (`cc`) e a chave privada do gateway (`config.paymentGatewayKey`) são impressos diretamente no console via `console.log`.
Impact: Violação frontal de normas internacionais de segurança e conformidade de pagamentos (PCI-DSS) e privacidade (LGPD), permitindo que qualquer pessoa com acesso aos logs intercepte números de cartão válidos.
Recommendation: Mascarar o número do cartão (`**** **** **** 1234`) e nunca exibir segredos ou tokens de gateways nos logs.

### [CRITICAL] Criptografia Customizada Insegura (`badCrypto`)
File: src/utils.js:17-23
Description: Função de hash customizada que executa um laço de 10.000 iterações truncando substrings Base64 para gerar uma senha de apenas 10 caracteres.
Impact: Altíssima previsibilidade, colisões imediatas e quebra trivial por força bruta ou rainbow tables.
Recommendation: Substituir pelo módulo nativo `crypto` do Node.js utilizando `crypto.pbkdf2Sync` ou `crypto.scryptSync` com salt criptográfico de 16 bytes.

### [CRITICAL] Hardcoded Secrets & Credenciais de Produção no Código
File: src/utils.js:1-7
Description: Configurações sensíveis (`dbUser: "admin_master"`, `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"`) estão inseridas estaticamente em código versionável.
Impact: Exposição irreversível de credenciais em repositórios de código.
Recommendation: Extrair parâmetros para variáveis de ambiente lidas através de `process.env` em `src/config/settings.js`.

### [HIGH] Callback Hell / Pirâmide da Morte Assíncrona
File: src/AppManager.js:37-77, 83-128
Description: Operações de banco com o driver `sqlite3` utilizam callbacks profundamente aninhados (até 5 níveis no checkout e no relatório), com controle manual de flags pendentes (`coursesPending`, `enrPending`).
Impact: Código ilegível, alta propensão a memory leaks, dificuldade em capturar erros e impossibilidade de composição assíncrona.
Recommendation: Promisificar as chamadas de banco (`db.getAsync`, `db.runAsync`, `db.allAsync`) e adotar `async/await` com blocos estruturados de `try/catch`.

### [HIGH] Estado Global Mutável & Cache Compartilhado sem Isolamento
File: src/utils.js:9-10; src/AppManager.js:59
Description: Variáveis globais mutáveis (`let globalCache = {}`, `let totalRevenue = 0`) mantêm estado em memória no escopo do módulo sem thread-safety ou controle de expiração (TTL).
Impact: Risco de vazamento de memória não controlada (memory leak) e inconsistência entre requisições concorrentes.
Recommendation: Mover o armazenamento para serviço de cache dedicado ou isolar no contexto adequado.

### [MEDIUM] N+1 Query Cascade no Relatório Financeiro
File: src/AppManager.js:89-125
Description: O endpoint `/api/admin/financial-report` busca todos os cursos e, para cada curso, dispara uma query para enrollments, e para cada enrollment dispara queries individuais para users e payments.
Impact: Para uma base com 10 cursos e 100 matrículas, são disparadas centenas de queries individuais síncronas/em cascata, derrubando o desempenho da API.
Recommendation: Consolidar a extração em consultas agregadas com `LEFT JOIN` ou pré-carregamento com agrupamento eficiente em memória.

### [MEDIUM] Violação de Integridade Referencial na Exclusão de Usuários
File: src/AppManager.js:131-137
Description: Ao deletar um usuário em `/api/users/:id`, apenas o registro da tabela `users` é removido, deixando registros órfãos nas tabelas `enrollments` e `payments`. O próprio código admite: *"Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco"*.
Impact: Corrupção da integridade de dados e geração de inconsistências cadastrais e financeiras.
Recommendation: Implementar exclusão em cascata (ou transação com remoção coordenada de matrículas e logs do usuário).

### [LOW] Nomenclatura Críptica de Variáveis
File: src/AppManager.js:29-33, 89-93
Description: Utilização sistemática de identificadores monossilábicos sem semântica (`let u`, `let e`, `let p`, `let cid`, `let cc`, `c`, `enr`).
Impact: Redução drástica da legibilidade e aumento da carga cognitiva para leitura e manutenção do código.
Recommendation: Renomear variáveis para termos descritivos (`name`, `email`, `password`, `courseId`, `creditCard`).

### [LOW] Logging Desestruturado via console.log()
File: src/utils.js:13; src/AppManager.js:45; src/app.js:13
Description: Mensagens de log e debug impressas diretamente com `console.log` sem identificadores de nível ou timestamp padronizado.
Impact: Dificuldade de auditoria e monitoramento em ambientes de produção.
Recommendation: Estruturar logs com níveis semânticos (`[INFO]`, `[ERROR]`, `[WARN]`).

================================
Total: 10 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
