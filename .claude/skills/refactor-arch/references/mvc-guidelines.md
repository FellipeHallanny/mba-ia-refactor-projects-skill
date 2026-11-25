# Diretrizes do Padrão Arquitetural MVC (Phase 3)

Este documento define as regras e responsabilidades de cada camada no padrão **Model-View-Controller (MVC)** para projetos de backend refatorados pela skill `refactor-arch`.

---

## 1. Princípios Gerais do MVC em APIs

No contexto de APIs RESTful e serviços backend:
- O **Model** é dono dos dados, da persistência e das regras de domínio.
- O **Controller** orquestra a execução da requisição HTTP, aciona os Models/Services e determina o status de resposta.
- A **View / Route** é responsável estritamente por definir o mapeamento das rotas HTTP (URLs, verbos) e serializar/formatar a resposta ao cliente.
- A **Configuração** é apartada do código de negócio e injetada por variáveis de ambiente.

---

## 2. Camadas e Responsabilidades

### `config/` (Camada de Configuração)
- **Responsabilidade**: Centralizar todas as configurações da aplicação, portas, chaves secretas e credenciais de banco ou APIs externas.
- **Regras**:
  - Proibido manter senhas ou secrets em texto puro no código.
  - Carregar valores de variáveis de ambiente (`os.getenv()` em Python, `process.env` em Node.js, `IConfiguration` / `appsettings.json` com variáveis de ambiente no C#/.NET) com fallbacks seguros para desenvolvimento.
  - Exportar um objeto, classe ou Options Pattern unificado (`IOptions<T>` no .NET).

### `models/` (Camada de Modelos e Dados)
- **Responsabilidade**: Abstrair o acesso a dados e encapsular entidades de negócio.
- **Regras**:
  - Cada entidade ou domínio deve ter seu próprio Model (ex: `UserModel`, `ProductModel`, `OrderModel`, classes POCO / `EntityTypeConfiguration` no C#).
  - Todas as queries SQL devem ser estritamente parametrizadas (proibido interpolação/concatenação de strings).
  - Encapsular hashing e verificação segura de senhas dentro do domínio do usuário (ex: `IPasswordHasher<T>` no .NET).
  - Isolar transações de banco (commit/rollback ou `IDbContextTransaction`) de forma que falhas parciais não corrompam os dados.

### `controllers/` (Camada de Controladores)
- **Responsabilidade**: Receber parâmetros da requisição, validar payloads de entrada, invocar métodos de domínio dos Models/Services e definir a resposta HTTP.
- **Regras**:
  - Não executa queries SQL diretamente (delega para os Models/Repositories/Services).
  - Em C#/.NET: herda de `ControllerBase` com anotação `[ApiController]`, retornando `ActionResult<T>` ou `IActionResult` assíncrono (`async Task<IActionResult>`).
  - Trata fluxos de exceção e retorna códigos de status HTTP semânticos (200, 201, 400, 404, 409, 500).
  - Não vaza stack traces ou detalhes internos sensíveis na resposta.

### `views/` ou `routes/` (Camada de Rotas / Visão)
- **Responsabilidade**: Mapear endpoints (URLs) e métodos HTTP (GET, POST, PUT, DELETE) para os métodos correspondentes dos Controllers.
- **Regras**:
  - Não deve conter regras de negócio nem manipulação direta de banco.
  - Organizado por módulos de domínio via Blueprints (Flask), Routers (`express.Router()`) ou Attributes Routing (`[Route("api/[controller]")]`) no C#/.NET.

### `middlewares/` (Camada de Interceptadores e Handlers Globais)
- **Responsabilidade**: Tratar erros não capturados, aplicar headers de segurança, CORS e logging estruturado.
- **Regras**:
  - Em C#/.NET: implementado via `app.UseExceptionHandler()`, `app.UseCors()` ou classes customizadas com `IMiddleware` / `InvokeAsync(HttpContext context)`.
  - Evitar que erros 500 derrubem o servidor ou exponham dados de infraestrutura.

### `app` (Composition Root / Entry Point)
- **Responsabilidade**: Ponto de entrada da aplicação (`app.py`, `src/app.js` ou `Program.cs`).
- **Regras**:
  - Instancia o framework web (Flask, Express ou `WebApplication.CreateBuilder(args)` no C#/.NET).
  - Registra a injeção de dependência (`builder.Services.AddScoped<...>()` no .NET).
  - Inicializa conexões e middlewares (`app.Use...()`).
  - Registra as rotas/controllers (`app.MapControllers()`).
  - Inicializa o servidor HTTP na porta configurada (`app.Run()`).
