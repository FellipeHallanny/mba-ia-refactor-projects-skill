---
name: refactor-arch
description: Analisa código, audita anti-patterns arquiteturais e de segurança, gera relatório e refatora a aplicação para o padrão MVC de forma agnóstica de tecnologia.
---

# Skill: refactor-arch

Esta skill executa uma auditoria e refatoração arquitetural automatizada em qualquer codebase backend, guiando o projeto para o padrão **MVC (Model-View-Controller)** de forma desacoplada, segura e sustentável.

A execução é estritamente dividida em **3 fases sequenciais**:

---

## FASE 1: PROJECT ANALYSIS (Análise de Projeto)

O objetivo desta fase é mapear a stack tecnológica, o domínio de negócio e a topologia arquitetural existente sem realizar nenhuma alteração de arquivos.

### Passos de Execução:
1. Ler os manifestos de dependências presentes (`package.json`, `requirements.txt`, `pyproject.toml`, `*.csproj`, `*.sln`, `go.mod`, `pom.xml`, etc.).
2. Identificar:
   - **Linguagem**: Python, JavaScript/Node.js, TypeScript, C# (.NET), etc.
   - **Framework Web**: Flask, Express, FastAPI, Django, NestJS, ASP.NET Core (Controllers / Minimal APIs), etc., com versão.
   - **Dependências Principais**: ORMs, drivers de banco, bibliotecas de autenticação/utilitários.
   - **Domínio**: Entidades principais identificadas nos nomes de arquivos, tabelas e rotas (ex: E-commerce, LMS/Cursos, Task Manager).
   - **Arquitetura Atual**: Monolítica desestruturada, código espaguete, arquitetura em camadas parcial, etc.
   - **Arquivos Fonte**: Quantidade e lista dos arquivos analisados.
   - **Tabelas do Banco de Dados**: Tabelas identificadas via DDL SQL ou models existentes.
3. Consultar as heurísticas detalhadas em:
   - `references/project-analysis.md`
4. Exibir obrigatoriamente no terminal o resumo no seguinte formato padronizado:

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <Linguagem detectada>
Framework:     <Framework e versão>
Dependencies:  <Dependências principais>
Domain:        <Domínio da aplicação>
Architecture:  <Descrição da arquitetura atual>
Source files:  <Quantidade de arquivos analisados>
DB tables:     <Tabelas identificadas>
================================
```

---

## FASE 2: ARCHITECTURE AUDIT (Auditoria Arquitetural)

O objetivo desta fase é cruzar todo o código-fonte contra o catálogo de anti-patterns e vulnerabilidades, mapeando cada ocorrência com arquivo e linha exatos.

### Passos de Execução:
1. Carregar as regras e critérios dos arquivos de referência:
   - `references/anti-patterns.md` (Catálogo de anti-patterns, sinais de detecção e classificação de severidade)
   - `references/report-template.md` (Template padronizado de saída)
2. Fazer varredura de código inspecionando todos os arquivos-fonte do projeto em busca de:
   - **CRITICAL**: Falhas de segurança (SQL Injection, credenciais hardcoded, endpoints backdoor sem autenticação, criptografia quebrada/MD5, vazamento de credenciais ou cartões em logs) ou God Classes / God Files que violem totalmente a separação de responsabilidades.
   - **HIGH**: Violações fortes de MVC/SOLID (lógica de negócio pesada em controllers/rotas, ausência de camada de controller, forte acoplamento, estado global mutável, callback hell).
   - **MEDIUM**: Problemas de persistência ou performance (Queries N+1, uso de APIs deprecated como `datetime.utcnow()` ou métodos obsoletos de ORM, tratamentos genéricos silenciosos de exceção, ausência de validação em rotas).
   - **LOW**: Falhas de legibilidade, má nomenclatura de variáveis, magic numbers, prints desestruturados no stdout.
3. Ordenar obrigatoriamente os findings por severidade decrescente: `CRITICAL` -> `HIGH` -> `MEDIUM` -> `LOW`.
4. Incluir detecção de APIs deprecated e recomendar a substituição moderna equivalente.
5. Exibir o relatório completo na tela seguindo fielmente o formato do template.
6. **PAUSA OBRIGATÓRIA**: Parar a execução e solicitar confirmação do usuário antes de realizar qualquer alteração em arquivos:

```text
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Apenas após resposta afirmativa (`y` ou `yes`), prosseguir para a Fase 3.

---

## FASE 3: REFACTORING (Refatoração para MVC)

O objetivo desta fase é reestruturar o projeto no padrão **MVC (Model-View-Controller)**, eliminando os anti-patterns identificados na Fase 2 e mantendo total compatibilidade comportamental com os contratos de rotas existentes.

### Passos de Execução:
1. Carregar os padrões e diretrizes de:
   - `references/mvc-guidelines.md` (Estrutura e responsabilidade de cada camada)
   - `references/refactoring-playbook.md` (Transformações concretas antes/depois)
2. Criar a estrutura limpa de diretórios:
   - `config/` (ou `src/config/`): Configurações centralizadas e leitura de variáveis de ambiente com defaults seguros (proibido manter senhas ou secrets como valor default; nenhum segredo auditado pode virar fallback). Criação de `.env.example`.
   - `models/` (ou `src/models/`): Entidades de dados isoladas por domínio, abstração de acesso ao banco com queries parametrizadas (eliminando SQL Injection), sanitização e hashes seguros.
   - `controllers/` (ou `src/controllers/`): Orquestradores de requisição/resposta, validação de payload e coordenação dos models, isolando a regra de negócio das rotas HTTP.
   - `views/` ou `routes/` (ou `src/routes/`): Definição estrita de endpoints, métodos HTTP e mapeamento para seus respectivos controllers.
   - `middlewares/` (ou `src/middlewares/`): Tratamento centralizado de erros e filtros de requisição.
   - Entrypoint principal (`app.py`, `src/app.js` ou `Program.cs`): Composition root limpo, registrando middlewares, rotas/endpoints e inicializando o servidor.
3. Aplicar as transformações do playbook:
   - Eliminar God Classes e separar responsabilidades por entidade/domínio.
   - Substituir concatenações SQL por consultas parametrizadas com bind variables.
   - Eliminar credenciais hardcoded e backdoors administrativos inseguros, garantindo que nenhum segredo auditado seja mantido como valor default no código.
   - Substituir algoritmos obsoletos de hashing (MD5, SHA1 ou cifras manuais) por padrões seguros.
   - Resolver Queries N+1 utilizando queries com JOIN, subconsultas ou carregamento em lote.
   - Transformar Callback Hell em funções assíncronas limpas com `async/await` e tratamento de erros com `try/catch`.
   - Substituir APIs deprecated pelas suas versões modernas suportadas.
   - Remover vazamento de dados confidenciais (números de cartão, senhas, chaves privadas) de logs e respostas `/health`.
4. **Validação do Resultado**:
   - Garantir que a aplicação sobe sem erros de sintaxe ou dependência.
   - Garantir que todos os endpoints públicos originais continuam acessíveis e respondendo os mesmos contratos de dados esperados pelos clientes.
5. Imprimir o banner de conclusão da Fase 3:

```text
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<Árvore do novo diretório>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```
