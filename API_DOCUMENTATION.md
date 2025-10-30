# 📚 Documentação da API REST - Funnel Builder

## Base URL
```
http://localhost:8000
```

## Autenticação
A API usa **Bearer Token** no header `Authorization`:
```
Authorization: Bearer SEU_TOKEN_AQUI
```

---

## 📋 Endpoints

### 1. Registro de Usuário
**POST** `/api/register`

Cadastra um novo usuário no sistema.

**Body (JSON):**
```json
{
  "email": "usuario@email.com",
  "password": "senha123",
  "name": "Nome do Usuário"  // opcional
}
```

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "message": "Usuário cadastrado com sucesso",
  "token": "abc123xyz...",
  "user": {
    "id": 1,
    "email": "usuario@email.com",
    "name": "Nome do Usuário",
    "created_at": "2025-10-30T12:00:00"
  }
}
```

**Resposta de Erro (400):**
```json
{
  "success": false,
  "message": "Email já cadastrado"
}
```

---

### 2. Login
**POST** `/api/login`

Autentica um usuário existente.

**Body (JSON):**
```json
{
  "email": "usuario@email.com",
  "password": "senha123"
}
```

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "message": "Login realizado com sucesso",
  "token": "xyz789abc...",
  "user": {
    "id": 1,
    "email": "usuario@email.com",
    "name": "Nome do Usuário",
    "created_at": "2025-10-30T12:00:00"
  }
}
```

**Resposta de Erro (401):**
```json
{
  "success": false,
  "message": "Email ou senha incorretos"
}
```

---

### 3. Logout
**DELETE** `/api/logout`

Encerra a sessão do usuário.

**Headers:**
```
Authorization: Bearer SEU_TOKEN
```

**Resposta (200):**
```json
{
  "success": true,
  "message": "Logout realizado"
}
```

---

### 4. Listar Funis
**GET** `/api/funnels`

Retorna todos os funis do usuário autenticado.

**Headers:**
```
Authorization: Bearer SEU_TOKEN
```

**Resposta (200):**
```json
{
  "funnels": [
    {
      "id": 1,
      "name": "Funil VSL",
      "icon": "🎬",
      "elements": [...],
      "connections": [...],
      "createdAt": "2025-10-30T12:00:00",
      "updatedAt": "2025-10-30T14:30:00"
    },
    ...
  ]
}
```

**Resposta de Erro (401):**
```json
{
  "error": "Não autenticado"
}
```

---

### 5. Buscar Funil Específico
**GET** `/api/funnels/:id`

Retorna um funil específico do usuário.

**Headers:**
```
Authorization: Bearer SEU_TOKEN
```

**Exemplo:**
```
GET /api/funnels/1
```

**Resposta (200):**
```json
{
  "funnel": {
    "id": 1,
    "name": "Funil VSL",
    "icon": "🎬",
    "elements": [
      {
        "id": 1,
        "type": "trafego",
        "name": "Tráfego Pago",
        "x": 100,
        "y": 150,
        ...
      }
    ],
    "connections": [
      {
        "id": "c1",
        "from": 1,
        "to": 2,
        "conversion": 50
      }
    ],
    "createdAt": "2025-10-30T12:00:00",
    "updatedAt": "2025-10-30T14:30:00"
  }
}
```

**Resposta de Erro (404):**
```json
{
  "error": "Funil não encontrado"
}
```

---

### 6. Criar Funil
**POST** `/api/funnels`

Cria um novo funil para o usuário autenticado.

**Headers:**
```
Authorization: Bearer SEU_TOKEN
```

**Body (JSON):**
```json
{
  "name": "Meu Novo Funil",
  "icon": "🚀",
  "elements": [],
  "connections": []
}
```

**Resposta (201):**
```json
{
  "success": true,
  "funnel": {
    "id": 5,
    "name": "Meu Novo Funil",
    "icon": "🚀",
    "elements": [],
    "connections": [],
    "createdAt": "2025-10-30T15:00:00",
    "updatedAt": "2025-10-30T15:00:00"
  }
}
```

---

### 7. Atualizar Funil
**PUT** `/api/funnels/:id`

Atualiza um funil existente.

**Headers:**
```
Authorization: Bearer SEU_TOKEN
```

**Body (JSON):**
```json
{
  "name": "Nome Atualizado",
  "icon": "🎯",
  "elements": [...],
  "connections": [...]
}
```

Obs: Todos os campos são opcionais. Envie apenas o que deseja atualizar.

**Resposta (200):**
```json
{
  "success": true,
  "funnel": {
    "id": 1,
    "name": "Nome Atualizado",
    "icon": "🎯",
    ...
  }
}
```

**Resposta de Erro (404):**
```json
{
  "error": "Funil não encontrado"
}
```

---

### 8. Deletar Funil
**DELETE** `/api/funnels/:id`

Remove um funil permanentemente.

**Headers:**
```
Authorization: Bearer SEU_TOKEN
```

**Exemplo:**
```
DELETE /api/funnels/1
```

**Resposta (200):**
```json
{
  "success": true,
  "message": "Funil deletado"
}
```

**Resposta de Erro (404):**
```json
{
  "error": "Funil não encontrado"
}
```

---

## 🔒 Códigos de Status HTTP

| Código | Significado |
|--------|------------|
| 200 | OK - Sucesso |
| 201 | Created - Recurso criado |
| 400 | Bad Request - Dados inválidos |
| 401 | Unauthorized - Não autenticado |
| 404 | Not Found - Recurso não encontrado |
| 500 | Internal Server Error - Erro no servidor |

---

## 💡 Exemplos de Uso

### Exemplo com cURL

**Registrar:**
```bash
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@email.com","password":"senha123","name":"Teste"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@email.com","password":"senha123"}'
```

**Listar Funis:**
```bash
curl http://localhost:8000/api/funnels \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

### Exemplo com JavaScript (Fetch)

```javascript
// Login
const login = async () => {
  const response = await fetch('http://localhost:8000/api/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      email: 'teste@email.com',
      password: 'senha123'
    })
  });

  const data = await response.json();
  if (data.success) {
    localStorage.setItem('token', data.token);
    console.log('Login realizado!', data.user);
  }
};

// Listar funis
const getFunnels = async () => {
  const token = localStorage.getItem('token');

  const response = await fetch('http://localhost:8000/api/funnels', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  const data = await response.json();
  console.log('Funis:', data.funnels);
};
```

---

## 🎯 Próximos Passos

Agora você pode:

1. **Atualizar o Frontend** para usar essas APIs em vez do localStorage
2. **Testar os endpoints** com ferramentas como Postman ou Insomnia
3. **Implementar features adicionais** como compartilhamento de funis, templates, etc.

---

## 📝 Notas Importantes

- ⚠️ As sessões são armazenadas em memória. Reiniciar o servidor invalida todos os tokens.
- 🔒 Em produção, use HTTPS e armazene senhas com salt único por usuário.
- 💾 O banco de dados SQLite está em `funnel_builder.db`
- 🧪 Para testes, use `test_funnel.db` executando os módulos individuais.
