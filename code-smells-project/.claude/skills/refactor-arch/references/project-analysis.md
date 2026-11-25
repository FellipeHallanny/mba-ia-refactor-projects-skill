# Heurísticas de Análise de Projeto (Phase 1)

Este guia fornece heurísticas determinísticas para detecção da stack tecnológica, do domínio de negócio e da topologia arquitetural existente em qualquer projeto de backend.

---

## 1. Detecção de Linguagem e Framework

| Linguagem | Arquivos Indicadores | Frameworks Web e Heurísticas |
|---|---|---|
| **Python** | `requirements.txt`, `Pipfile`, `pyproject.toml`, `setup.py`, arquivos `.py` | - **Flask**: Presença de `flask`, `Flask(__name__)`, `Blueprint`, `app.route`<br>- **FastAPI**: Presença de `fastapi`, `FastAPI()`, `APIRouter`<br>- **Django**: Presença de `manage.py`, `django`, `settings.py`, `models.py` |
| **JavaScript / TypeScript** | `package.json`, `tsconfig.json`, arquivos `.js`, `.mjs`, `.ts` | - **Express**: Presença de `"express"` em `dependencies`, `express()`<br>- **NestJS**: Presença de `@nestjs/core`, decorators `@Controller`, `@Injectable`<br>- **Fastify**: Presença de `"fastify"`, `fastify()` |
| **Go** | `go.mod`, `go.sum`, arquivos `.go` | - **Gin**: `github.com/gin-gonic/gin`<br>- **Echo**: `github.com/labstack/echo`<br>- **Fiber**: `github.com/gofiber/fiber` |
| **Java / Kotlin** | `pom.xml`, `build.gradle`, `.java`, `.kt` | - **Spring Boot**: `org.springframework.boot` |

---

## 2. Detecção de Mecanismo de Persistência (Banco de Dados)

1. **SQLite**:
   - Python: `import sqlite3`, `sqlite3.connect()`, arquivos `.db`, `.sqlite`.
   - Node.js: `sqlite3`, `better-sqlite3`, `new sqlite3.Database()`.
2. **PostgreSQL / MySQL / MariaDB**:
   - Python: `psycopg2`, `asyncpg`, `mysql-connector-python`, `PyMySQL`.
   - Node.js: `pg`, `mysql2`, `typeorm`, `prisma`, `knex`, `sequelize`.
3. **ORMs e Abstrações**:
   - `SQLAlchemy` / `flask_sqlalchemy`: `db.Model`, `db.Column()`, `db.session`.
   - `Prisma`, `Mongoose` (`mongoose.model`), `TypeORM`.

---

## 3. Identificação do Domínio de Negócio

Para determinar o domínio da aplicação:
1. Examine os nomes das tabelas criadas em DDLs (`CREATE TABLE ...`) ou migrations.
2. Analise os prefixos das rotas HTTP declaradas:
   - `/produtos`, `/pedidos`, `/checkout`, `/carrinho` -> **E-commerce / Varejo**.
   - `/cursos`, `/aulas`, `/matriculas`, `/students`, `/enrollments` -> **LMS / Educação online**.
   - `/tasks`, `/tarefas`, `/projetos`, `/categorias` -> **Gerenciador de Tarefas (Task Manager)**.
   - `/usuarios`, `/auth`, `/login`, `/perfis` -> **Módulo de Identidade & Acesso**.

---

## 4. Classificação da Topologia Arquitetural Atual

- **Monolito Desestruturado (Spaghetti / Tudo em 1-4 arquivos)**:
  Toda a regra de negócio, SQL queries, DDLs, inicialização de servidor e manipulação de HTTP residem no mesmo arquivo ou distribuídos arbitrariamente sem separação de responsabilidades (ex: `app.py`, `models.py`, `controllers.py` com tudo misturado, ou um arquivo monolítico central como `AppManager.js`).
- **Arquitetura em Camadas Parcial (Semi-estruturado)**:
  O projeto possui pastas como `models/`, `routes/`, `services/`, porém:
  - As rotas contêm lógica de negócio pesada sem uma camada de `controllers` dedicada;
  - Regras de domínio estão espalhadas em helpers ou serviços fortemente acoplados;
  - Conexões e queries não possuem abstração padronizada.
- **Padrão Alvo MVC (Model-View-Controller)**:
  Separação explícita em camadas:
  - `config`: isolamento de credenciais e parâmetros de ambiente;
  - `models`: persistência, regras de entidade e contratos de dados;
  - `controllers`: orquestração do fluxo de requisições e regras de aplicação;
  - `views/routes`: mapeamento de rotas e formatação de resposta;
  - `middlewares`: tratamento centralizado de erros e filtros transversais;
  - `app`: composição e inicialização limpa.
