# API de Gerenciamento de Marketing Digital

Documentação completa dos endpoints de Marketing Digital do Funnel Builder.

## Índice
- [Visão Geral](#visão-geral)
- [Autenticação](#autenticação)
- [Páginas](#páginas)
- [Testes de Página](#testes-de-página)
- [Métricas](#métricas)
- [UTMs](#utms)

---

## Visão Geral

A API de Marketing Digital permite gerenciar:
- **Páginas**: Cadastro e gerenciamento de landing pages, VSLs, checkouts, etc.
- **Testes A/B**: Histórico de alterações e testes realizados em cada página
- **Métricas**: Impressões, cliques, conversões e analytics de cada página
- **UTMs**: Criação e gerenciamento de parâmetros UTM para rastreamento de campanhas

Base URL: `http://localhost:8000/api`

---

## Autenticação

Todos os endpoints requerem autenticação via token JWT no header:

```
Authorization: Bearer {seu_token}
```

---

## Páginas

### Listar Páginas

Retorna todas as páginas do usuário.

**Endpoint:** `GET /pages`

**Query Parameters:**
- `category` (opcional): Filtrar por categoria (landing, vsl, checkout, etc.)
- `status` (opcional): Filtrar por status (active, testing, paused, archived)

**Exemplo de Requisição:**
```bash
curl -X GET \
  -H "Authorization: Bearer {token}" \
  "http://localhost:8000/api/pages?category=landing&status=active"
```

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "pages": [
    {
      "id": 1,
      "user_id": 1,
      "name": "Landing Page - Curso Marketing Digital",
      "url": "https://exemplo.com/curso-marketing",
      "category": "landing",
      "description": "Landing page principal do curso",
      "tags": ["curso", "marketing-digital"],
      "status": "active",
      "thumbnail_url": null,
      "created_at": "2024-12-23 10:00:00",
      "updated_at": "2024-12-23 10:00:00"
    }
  ],
  "total": 1
}
```

---

### Criar Página

Cria uma nova página.

**Endpoint:** `POST /pages`

**Body (JSON):**
```json
{
  "name": "Landing Page - Curso Marketing Digital",
  "url": "https://exemplo.com/curso-marketing",
  "category": "landing",
  "description": "Landing page principal do curso de marketing digital",
  "tags": ["curso", "marketing-digital", "lancamento"],
  "status": "active",
  "thumbnail_url": "https://exemplo.com/thumb.jpg"
}
```

**Campos Obrigatórios:**
- `name`: Nome da página
- `url`: URL completa da página

**Campos Opcionais:**
- `category`: Categoria da página (padrão: "landing")
  - Opções: landing, vsl, checkout, thankyou, webinar, blog, etc.
- `description`: Descrição detalhada
- `tags`: Array de tags para organização
- `status`: Status atual (padrão: "active")
  - Opções: active, testing, paused, archived
- `thumbnail_url`: URL da thumbnail/screenshot

**Resposta de Sucesso (201):**
```json
{
  "success": true,
  "message": "Página criada com sucesso",
  "page": {
    "id": 1,
    "name": "Landing Page - Curso Marketing Digital",
    "url": "https://exemplo.com/curso-marketing",
    ...
  }
}
```

**Erros Possíveis:**
- `400`: Nome ou URL faltando / URL inválida
- `401`: Não autenticado
- `500`: Erro no servidor

---

### Buscar Página

Retorna detalhes de uma página específica, incluindo testes e métricas.

**Endpoint:** `GET /pages/{id}`

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "page": {
    "id": 1,
    "name": "Landing Page - Curso Marketing Digital",
    ...
  },
  "tests": [
    {
      "id": 1,
      "page_id": 1,
      "date": "2024-12-20",
      "title": "Teste de headline",
      "description": "Alterado headline de \"Aprenda\" para \"Domine\"",
      "test_type": "ab_test",
      "results": "Aumento de 32% na conversão",
      "metrics": {
        "conversion_before": 2.5,
        "conversion_after": 3.3
      }
    }
  ],
  "metrics": [
    {
      "id": 1,
      "page_id": 1,
      "date": "2024-12-23",
      "impressions": 50000,
      "clicks": 2500,
      "conversions": 125,
      "ctr": 5.0,
      "conversion_rate": 5.0,
      ...
    }
  ]
}
```

**Erros Possíveis:**
- `404`: Página não encontrada
- `401`: Não autenticado

---

### Atualizar Página

Atualiza dados de uma página existente.

**Endpoint:** `PUT /pages/{id}`

**Body (JSON):**
```json
{
  "name": "Novo Nome da Página",
  "description": "Nova descrição",
  "status": "testing",
  "tags": ["nova-tag", "teste"]
}
```

**Nota:** Envie apenas os campos que deseja atualizar.

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "message": "Página atualizada com sucesso",
  "page": { ... }
}
```

**Erros Possíveis:**
- `400`: Nenhum dado para atualizar / URL inválida
- `404`: Página não encontrada
- `401`: Não autenticado

---

### Deletar Página

Deleta uma página e todos os seus dados relacionados (testes e métricas).

**Endpoint:** `DELETE /pages/{id}`

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "message": "Página deletada com sucesso"
}
```

**Erros Possíveis:**
- `404`: Página não encontrada
- `401`: Não autenticado

---

## Testes de Página

### Adicionar Teste

Adiciona um teste A/B ou registro de alteração a uma página.

**Endpoint:** `POST /pages/{page_id}/tests`

**Body (JSON):**
```json
{
  "date": "2024-12-23",
  "title": "Teste de headline",
  "description": "Alterado headline de \"Aprenda Marketing\" para \"Domine Marketing Digital em 30 Dias\"",
  "test_type": "ab_test",
  "results": "Aumento de 32% na conversão",
  "metrics": {
    "conversion_before": 2.5,
    "conversion_after": 3.3,
    "sample_size": 1000,
    "confidence": 95
  }
}
```

**Campos Obrigatórios:**
- `date`: Data do teste (formato: YYYY-MM-DD)
- `title`: Título curto do teste
- `description`: Descrição detalhada do que foi alterado

**Campos Opcionais:**
- `test_type`: Tipo de teste (padrão: "ab_test")
  - Opções: ab_test, design_change, copy_change, layout_change, etc.
- `results`: Resultados observados (texto)
- `metrics`: Objeto com métricas do teste (formato livre)

**Resposta de Sucesso (201):**
```json
{
  "success": true,
  "message": "Teste adicionado com sucesso",
  "test": { ... }
}
```

**Erros Possíveis:**
- `400`: Campos obrigatórios faltando
- `404`: Página não encontrada
- `401`: Não autenticado

---

### Deletar Teste

Remove um teste de página.

**Endpoint:** `DELETE /pages/tests/{test_id}`

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "message": "Teste deletado com sucesso"
}
```

---

## Métricas

### Adicionar Métricas

Registra métricas de performance de uma página.

**Endpoint:** `POST /pages/{page_id}/metrics`

**Body (JSON):**
```json
{
  "date": "2024-12-23",
  "impressions": 50000,
  "clicks": 2500,
  "conversions": 125,
  "avg_time_on_page": 180,
  "bounce_rate": 45.5,
  "utm_id": 1,
  "notes": "Campanha de lançamento - Dia 1"
}
```

**Campos Obrigatórios:**
- `date`: Data das métricas (formato: YYYY-MM-DD)

**Campos Opcionais:**
- `impressions`: Número de impressões
- `clicks`: Número de cliques
- `conversions`: Número de conversões
- `avg_time_on_page`: Tempo médio na página (segundos)
- `bounce_rate`: Taxa de rejeição (porcentagem)
- `utm_id`: ID da UTM relacionada
- `notes`: Observações

**Resposta de Sucesso (201):**
```json
{
  "success": true,
  "message": "Métricas adicionadas com sucesso",
  "metric": {
    "id": 1,
    "page_id": 1,
    "date": "2024-12-23",
    "impressions": 50000,
    "clicks": 2500,
    "conversions": 125,
    "ctr": 5.0,
    "conversion_rate": 5.0,
    ...
  }
}
```

**Nota:** Os campos `ctr` e `conversion_rate` são calculados automaticamente.

---

### Listar Métricas

Lista todas as métricas de uma página.

**Endpoint:** `GET /pages/{page_id}/metrics`

**Query Parameters:**
- `start_date` (opcional): Data inicial (formato: YYYY-MM-DD)
- `end_date` (opcional): Data final (formato: YYYY-MM-DD)

**Exemplo:**
```bash
curl -X GET \
  -H "Authorization: Bearer {token}" \
  "http://localhost:8000/api/pages/1/metrics?start_date=2024-12-01&end_date=2024-12-31"
```

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "metrics": [ ... ],
  "total": 30,
  "summary": {
    "total_impressions": 1500000,
    "total_clicks": 75000,
    "total_conversions": 3750,
    "avg_ctr": 5.0,
    "avg_conversion_rate": 5.0
  }
}
```

---

### Deletar Métrica

Remove um registro de métrica.

**Endpoint:** `DELETE /metrics/{metric_id}`

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "message": "Métrica deletada com sucesso"
}
```

---

## UTMs

### Listar UTMs

Retorna todas as UTMs do usuário.

**Endpoint:** `GET /utms`

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "utms": [
    {
      "id": 1,
      "user_id": 1,
      "name": "Campanha Black Friday - Facebook Ads",
      "utm_source": "facebook",
      "utm_medium": "cpc",
      "utm_campaign": "black_friday_2024",
      "utm_content": "video_ad_headline_test",
      "utm_term": "marketing_digital",
      "tags": ["black-friday", "facebook"],
      "notes": "Campanha principal de Black Friday",
      "created_at": "2024-11-01 10:00:00",
      "updated_at": "2024-11-01 10:00:00"
    }
  ],
  "total": 1
}
```

---

### Criar UTM

Cria um novo conjunto de parâmetros UTM.

**Endpoint:** `POST /utms`

**Body (JSON):**
```json
{
  "name": "Campanha Black Friday - Facebook Ads",
  "utm_source": "facebook",
  "utm_medium": "cpc",
  "utm_campaign": "black_friday_2024",
  "utm_content": "video_ad_headline_test",
  "utm_term": "marketing_digital",
  "tags": ["black-friday", "facebook", "video"],
  "notes": "Campanha principal de Black Friday com teste de headline"
}
```

**Campos Obrigatórios:**
- `name`: Nome descritivo da UTM
- `utm_source`: Fonte do tráfego (ex: facebook, google, instagram)
- `utm_medium`: Meio/canal (ex: cpc, email, social, organic)
- `utm_campaign`: Nome da campanha

**Campos Opcionais:**
- `utm_content`: Identificador de conteúdo/versão do anúncio
- `utm_term`: Palavra-chave (geralmente para Google Ads)
- `tags`: Array de tags para organização
- `notes`: Observações sobre a campanha

**Resposta de Sucesso (201):**
```json
{
  "success": true,
  "message": "UTM criada com sucesso",
  "utm": { ... },
  "preview_url": "https://exemplo.com?utm_source=facebook&utm_medium=cpc&utm_campaign=black_friday_2024&utm_content=video_ad_headline_test&utm_term=marketing_digital"
}
```

**Erros Possíveis:**
- `400`: Campos obrigatórios faltando
- `401`: Não autenticado

---

### Buscar UTM

Retorna detalhes de uma UTM específica.

**Endpoint:** `GET /utms/{id}`

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "utm": { ... }
}
```

---

### Atualizar UTM

Atualiza uma UTM existente.

**Endpoint:** `PUT /utms/{id}`

**Body (JSON):**
```json
{
  "name": "Novo nome da campanha",
  "notes": "Novas observações",
  "tags": ["nova-tag"]
}
```

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "message": "UTM atualizada com sucesso",
  "utm": { ... }
}
```

---

### Gerar URL com UTM

Gera uma URL completa com os parâmetros UTM.

**Endpoint:** `POST /utms/{id}/generate`

**Body (JSON):**
```json
{
  "base_url": "https://exemplo.com/curso-marketing"
}
```

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "generated_url": "https://exemplo.com/curso-marketing?utm_source=facebook&utm_medium=cpc&utm_campaign=black_friday_2024&utm_content=video_ad_headline_test&utm_term=marketing_digital",
  "utm_params": {
    "utm_source": "facebook",
    "utm_medium": "cpc",
    "utm_campaign": "black_friday_2024",
    "utm_content": "video_ad_headline_test",
    "utm_term": "marketing_digital"
  }
}
```

**Erros Possíveis:**
- `400`: URL base faltando ou inválida
- `404`: UTM não encontrada

---

### Deletar UTM

Remove uma UTM.

**Endpoint:** `DELETE /utms/{id}`

**Resposta de Sucesso (200):**
```json
{
  "success": true,
  "message": "UTM deletada com sucesso"
}
```

---

## Categorias de Página

Categorias sugeridas para organização:

- `landing`: Landing Pages
- `vsl`: Video Sales Letters
- `checkout`: Páginas de checkout/pagamento
- `thankyou`: Páginas de agradecimento
- `webinar`: Páginas de webinar
- `blog`: Posts de blog
- `lead_magnet`: Iscas digitais
- `sales_page`: Páginas de vendas longas
- `squeeze_page`: Páginas de captura simples
- `other`: Outras

## Tipos de Teste

Tipos sugeridos para testes A/B:

- `ab_test`: Teste A/B tradicional
- `design_change`: Mudança de design
- `copy_change`: Mudança de copy/texto
- `layout_change`: Mudança de layout
- `cta_change`: Mudança de call-to-action
- `color_change`: Mudança de cores
- `image_change`: Mudança de imagens
- `price_change`: Mudança de preço
- `form_change`: Mudança de formulário
- `other`: Outro tipo

## Status de Página

- `active`: Página ativa e funcionando
- `testing`: Página em teste A/B
- `paused`: Página pausada temporariamente
- `archived`: Página arquivada

---

## Exemplo de Fluxo Completo

```bash
# 1. Login
TOKEN=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"usuario@exemplo.com","password":"senha123"}' \
  http://localhost:8000/api/login | jq -r '.token')

# 2. Criar página
PAGE_ID=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Landing Page Teste","url":"https://exemplo.com/teste"}' \
  http://localhost:8000/api/pages | jq -r '.page.id')

# 3. Criar UTM
UTM_ID=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Campanha Teste","utm_source":"google","utm_medium":"cpc","utm_campaign":"teste_2024"}' \
  http://localhost:8000/api/utms | jq -r '.utm.id')

# 4. Adicionar métricas
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"date":"2024-12-23","impressions":10000,"clicks":500,"conversions":25,"utm_id":'$UTM_ID'}' \
  http://localhost:8000/api/pages/$PAGE_ID/metrics

# 5. Ver estatísticas
curl -s -X GET \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/pages/$PAGE_ID/metrics | jq '.summary'
```

---

## Rate Limiting

- Operações de escrita (POST, PUT, DELETE): 100 requisições por 10 minutos por IP
- Operações de leitura (GET): Sem limite

## Códigos de Status HTTP

- `200`: Sucesso
- `201`: Recurso criado com sucesso
- `400`: Requisição inválida
- `401`: Não autenticado
- `404`: Recurso não encontrado
- `429`: Rate limit excedido
- `500`: Erro no servidor
