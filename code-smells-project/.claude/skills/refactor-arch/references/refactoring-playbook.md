# Playbook de Refatoração: Padrões de Transformação (Phase 3)

Este playbook reúne no mínimo 8 padrões concretos de transformação com exemplos de código **Antes (Before)** e **Depois (After)**, demonstrando como converter código legado e vulnerável em código limpo, seguro e aderente ao padrão MVC.

---

## Padrão 1: God Class / God File -> Separação Model / Controller / Route

### Problema:
Um único arquivo ou classe concentra DDL do banco de dados, queries SQL, regras de negócio, manipulação de rotas e formatação de resposta.

### Antes (Python):
```python
# models.py (God File)
def get_produtos(): ...
def criar_pedido(usuario_id, itens): ... # Lógica de estoque + DML misturados
def login_usuario(email, senha): ...
def relatorio_vendas(): ...
```

### Depois (Python - MVC):
```python
# models/produto_model.py
class ProdutoModel:
    @staticmethod
    def buscar_por_id(produto_id): ...

# models/pedido_model.py
class PedidoModel:
    @staticmethod
    def criar_pedido_com_estoque(usuario_id, itens): ...

# controllers/pedido_controller.py
class PedidoController:
    @staticmethod
    def criar_pedido():
        dados = request.get_json()
        resultado = PedidoModel.criar_pedido_com_estoque(dados["usuario_id"], dados["itens"])
        return jsonify({"dados": resultado}), 201

# routes/pedido_routes.py
pedido_bp = Blueprint("pedidos", __name__)
pedido_bp.route("/pedidos", methods=["POST"])(PedidoController.criar_pedido)
```

---

## Padrão 2: SQL Injection -> Consultas Parametrizadas (Bind Variables)

### Problema:
Interpolação de parâmetros não sanitizados direto na query SQL.

### Antes:
```python
# Python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute("INSERT INTO usuarios (nome, email) VALUES ('" + nome + "', '" + email + "')")
```
```javascript
// Node.js
db.run("DELETE FROM users WHERE id = " + id);
```

### Depois:
```python
# Python (SQLite com ?)
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute("INSERT INTO usuarios (nome, email) VALUES (?, ?)", (nome, email))
```
```javascript
// Node.js (SQLite com ?)
db.run("DELETE FROM users WHERE id = ?", [id], callback);
```

---

## Padrão 3: Hardcoded Secrets -> Módulo de Configuração e Variáveis de Ambiente

### Problema:
Chaves e senhas confidenciais salvas diretamente no código.

### Antes:
```python
# app.py
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
```
```javascript
// utils.js
const config = {
    paymentGatewayKey: "pk_live_1234567890abcdef",
    dbPass: "senha_super_secreta_prod_123"
};
```

### Depois:
```python
# config/settings.py
import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-fallback-key-do-not-use-in-prod")
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    DB_PATH = os.getenv("DB_PATH", "loja.db")
```
```javascript
// src/config/settings.js
module.exports = {
    port: process.env.PORT || 3000,
    dbPass: process.env.DB_PASS || "dev_default_pass",
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "dev_gateway_key",
    smtpUser: process.env.SMTP_USER || "no-reply@dev.local"
};
```

---

## Padrão 4: Criptografia Fraca / Insegura -> Hashing Seguro de Senhas

### Problema:
Armazenamento de senhas em texto claro, MD5 simples ou cifra customizada insegura.

### Antes:
```python
# models/user.py
self.password = hashlib.md5(pwd.encode()).hexdigest()
```
```javascript
// utils.js
function badCrypto(pwd) {
    let hash = "";
    for(let i = 0; i < 10000; i++) hash += Buffer.from(pwd).toString('base64').substring(0, 2);
    return hash.substring(0, 10);
}
```

### Depois:
```python
# models/user.py (com hash seguro via hashlib PBKDF2 ou SHA256 com salt)
import hashlib, os, hmac

def hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{hashed}"

def verify_password(stored_hash: str, password: str) -> bool:
    if ":" not in stored_hash:
        # Suporte retrocompatível para transição suave de dados legados
        return stored_hash == hashlib.md5(password.encode()).hexdigest() or stored_hash == password
    salt, original_hash = stored_hash.split(":", 1)
    new_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return hmac.compare_digest(original_hash, new_hash)
```
```javascript
// src/utils/crypto.js
const crypto = require('crypto');

function hashPassword(password) {
    const salt = crypto.randomBytes(16).toString('hex');
    const hash = crypto.pbkdf2Sync(password, salt, 1000, 32, 'sha256').toString('hex');
    return `${salt}:${hash}`;
}

function verifyPassword(stored, password) {
    if (!stored || !stored.includes(':')) {
        // Suporte retrocompatível com legados
        return stored === password;
    }
    const [salt, hash] = stored.split(':');
    const checkHash = crypto.pbkdf2Sync(password, salt, 1000, 32, 'sha256').toString('hex');
    return crypto.timingSafeEqual(Buffer.from(hash), Buffer.from(checkHash));
}
```

---

## Padrão 5: Callback Hell -> Funções Assíncronas com Async/Await e Promises

### Problema:
Callbacks aninhados profundamente (Pirâmide da Morte), dificultando tratamento de erros.

### Antes (Node.js):
```javascript
this.db.get("SELECT * FROM courses WHERE id = ?", [cid], (err, course) => {
    if (err || !course) return res.status(404).send(...);
    this.db.get("SELECT id FROM users WHERE email = ?", [e], (err, user) => {
        this.db.run("INSERT INTO enrollments...", (err) => {
            this.db.run("INSERT INTO payments...", (err) => {
                // 5+ níveis
            });
        });
    });
});
```

### Depois (Node.js - Async/Await):
```javascript
// Usando helper de promise no SQLite
const course = await db.getAsync("SELECT * FROM courses WHERE id = ? AND active = 1", [courseId]);
if (!course) return res.status(404).json({ error: "Curso não encontrado" });

let user = await db.getAsync("SELECT id FROM users WHERE email = ?", [email]);
if (!user) {
    const hash = hashPassword(password);
    const userResult = await db.runAsync("INSERT INTO users (name, email, pass) VALUES (?, ?, ?)", [name, email, hash]);
    user = { id: userResult.lastID };
}

const enrResult = await db.runAsync("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", [user.id, courseId]);
await db.runAsync("INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)", [enrResult.lastID, course.price, "PAID"]);
```

---

## Padrão 6: Problema de Queries N+1 -> JOINs ou Carregamento em Lote

### Problema:
Disparar queries adicionais dentro de um loop para cada registro retornado pela query pai.

### Antes:
```python
# Python
pedidos = cursor.execute("SELECT * FROM pedidos").fetchall()
for p in pedidos:
    itens = cursor.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(p["id"])).fetchall()
    for item in itens:
        prod = cursor.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"])).fetchone()
```

### Depois:
```python
# Python (Uma query agrupada com JOIN)
query = """
    SELECT p.id as pedido_id, p.usuario_id, p.status, p.total, p.criado_em,
           ip.produto_id, pr.nome as produto_nome, ip.quantidade, ip.preco_unitario
    FROM pedidos p
    LEFT JOIN itens_pedido ip ON p.id = ip.pedido_id
    LEFT JOIN produtos pr ON ip.produto_id = pr.id
    ORDER BY p.id
"""
rows = cursor.execute(query).fetchall()
# Agrupamento eficiente em memória em O(N)
pedidos_map = {}
for row in rows:
    pid = row["pedido_id"]
    if pid not in pedidos_map:
        pedidos_map[pid] = {
            "id": pid, "usuario_id": row["usuario_id"], "status": row["status"],
            "total": row["total"], "criado_em": row["criado_em"], "itens": []
        }
    if row["produto_id"]:
        pedidos_map[pid]["itens"].append({
            "produto_id": row["produto_id"], "produto_nome": row["produto_nome"],
            "quantidade": row["quantidade"], "preco_unitario": row["preco_unitario"]
        })
return list(pedidos_map.values())
```

---

## Padrão 7: Fat Routes -> Extração de Controllers e Separação de Rotas

### Problema:
Handlers de rota acumulam validação de entrada, instanciação de models, regras de negócio e manipulação de sessão.

### Antes:
```python
# routes/user_routes.py
@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    # 40 linhas de validações de regex, queries de verificação, manipulação de db.session
```

### Depois:
```python
# routes/user_routes.py
user_bp = Blueprint('users', __name__)
user_bp.route('/users', methods=['POST'])(UserController.create)

# controllers/user_controller.py
class UserController:
    @staticmethod
    def create():
        payload = request.get_json() or {}
        validated_data, error = validate_user_payload(payload)
        if error:
            return jsonify({'error': error}), 400
        user = UserModel.create_user(validated_data)
        return jsonify(user.to_dict()), 201
```

---

## Padrão 8: APIs Deprecated -> Substituição por APIs Modernas e Suportadas

### Problema:
Uso de métodos ou atributos depreciados pela linguagem ou bibliotecas de runtime.

### Antes:
```python
# Python 3.12+ deprecation: datetime.utcnow()
from datetime import datetime
created_at = datetime.utcnow()

# SQLAlchemy 2.0 deprecation: Model.query.get(id)
user = User.query.get(user_id)
```

### Depois:
```python
# Python moderno: datetime.now(timezone.utc)
from datetime import datetime, timezone
created_at = datetime.now(timezone.utc)

# SQLAlchemy moderno: db.session.get(Model, id)
user = db.session.get(User, user_id)
```

---

## Padrão 9: Vazamento de Dados Sensíveis em Logs -> Mascaramento / Sanitização

### Problema:
Logs contendo número de cartão de crédito e chaves confidenciais em texto plano.

### Antes:
```javascript
console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
```

### Depois:
```javascript
const maskedCard = cc ? `**** **** **** ${cc.slice(-4)}` : '****';
console.log(`[INFO] Processando transação com cartão final ${maskedCard}`);
```
