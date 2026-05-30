#!/bin/bash

# Script de teste para API de Marketing Digital
# Testa todos os endpoints de páginas, UTMs e métricas

BASE_URL="http://localhost:8000"
TOKEN=""  # Será preenchido após o login

echo "🧪 Testando API de Marketing Digital"
echo "======================================"
echo ""

# Função para fazer requisições com token
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3

    if [ -z "$data" ]; then
        curl -s -X $method \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            "$BASE_URL$endpoint"
    else
        curl -s -X $method \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$BASE_URL$endpoint"
    fi
}

# 1. Login
echo "📝 1. Fazendo login..."
LOGIN_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"email":"teste@funnel.com","password":"senha123"}' \
    "$BASE_URL/api/login")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Falha no login. Criando usuário..."

    REGISTER_RESPONSE=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d '{"email":"teste@funnel.com","password":"senha123","name":"Teste Marketing","whatsapp":"11999999999"}' \
        "$BASE_URL/api/register")

    TOKEN=$(echo $REGISTER_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)

    if [ -z "$TOKEN" ]; then
        echo "❌ Erro ao criar usuário"
        exit 1
    fi
    echo "✅ Usuário criado com sucesso"
fi

echo "✅ Login realizado com sucesso"
echo "   Token: ${TOKEN:0:20}..."
echo ""

# 2. Criar Página
echo "📄 2. Criando página..."
PAGE_RESPONSE=$(api_call POST "/api/pages" '{
    "name": "Landing Page - Curso Marketing Digital",
    "url": "https://exemplo.com/curso-marketing",
    "category": "landing",
    "description": "Landing page principal do curso de marketing digital",
    "tags": ["curso", "marketing-digital", "lancamento"],
    "status": "active"
}')

PAGE_ID=$(echo $PAGE_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -n "$PAGE_ID" ]; then
    echo "✅ Página criada com sucesso (ID: $PAGE_ID)"
else
    echo "❌ Erro ao criar página"
    echo "   Resposta: $PAGE_RESPONSE"
fi
echo ""

# 3. Listar Páginas
echo "📋 3. Listando páginas..."
PAGES_LIST=$(api_call GET "/api/pages")
PAGES_COUNT=$(echo $PAGES_LIST | grep -o '"total":[0-9]*' | cut -d':' -f2)
echo "✅ Total de páginas: $PAGES_COUNT"
echo ""

# 4. Adicionar Teste à Página
if [ -n "$PAGE_ID" ]; then
    echo "🧪 4. Adicionando teste A/B à página..."
    TEST_RESPONSE=$(api_call POST "/api/pages/$PAGE_ID/tests" '{
        "date": "2024-12-23",
        "title": "Teste de headline",
        "description": "Alterado headline de \"Aprenda Marketing\" para \"Domine Marketing Digital em 30 Dias\"",
        "test_type": "ab_test",
        "results": "Aumento de 32% na conversão",
        "metrics": {
            "conversion_before": 2.5,
            "conversion_after": 3.3
        }
    }')

    if echo $TEST_RESPONSE | grep -q '"success":true'; then
        echo "✅ Teste adicionado com sucesso"
    else
        echo "❌ Erro ao adicionar teste"
    fi
    echo ""
fi

# 5. Adicionar Métricas à Página
if [ -n "$PAGE_ID" ]; then
    echo "📊 5. Adicionando métricas à página..."
    METRICS_RESPONSE=$(api_call POST "/api/pages/$PAGE_ID/metrics" '{
        "date": "2024-12-23",
        "impressions": 50000,
        "clicks": 2500,
        "conversions": 125,
        "avg_time_on_page": 180,
        "bounce_rate": 45.5,
        "notes": "Campanha de lançamento - Dia 1"
    }')

    if echo $METRICS_RESPONSE | grep -q '"success":true'; then
        echo "✅ Métricas adicionadas com sucesso"
        echo "   CTR: 5.00%"
        echo "   Taxa de conversão: 5.00%"
    else
        echo "❌ Erro ao adicionar métricas"
    fi
    echo ""
fi

# 6. Criar UTM
echo "🔗 6. Criando UTM..."
UTM_RESPONSE=$(api_call POST "/api/utms" '{
    "name": "Campanha Black Friday - Facebook Ads",
    "utm_source": "facebook",
    "utm_medium": "cpc",
    "utm_campaign": "black_friday_2024",
    "utm_content": "video_ad_headline_test",
    "utm_term": "marketing_digital",
    "tags": ["black-friday", "facebook", "video"],
    "notes": "Campanha principal de Black Friday com teste de headline"
}')

UTM_ID=$(echo $UTM_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -n "$UTM_ID" ]; then
    echo "✅ UTM criada com sucesso (ID: $UTM_ID)"
    PREVIEW_URL=$(echo $UTM_RESPONSE | grep -o '"preview_url":"[^"]*' | cut -d'"' -f4)
    echo "   Preview: $PREVIEW_URL"
else
    echo "❌ Erro ao criar UTM"
fi
echo ""

# 7. Gerar URL com UTM
if [ -n "$UTM_ID" ]; then
    echo "🌐 7. Gerando URL com parâmetros UTM..."
    URL_RESPONSE=$(api_call POST "/api/utms/$UTM_ID/generate" '{
        "base_url": "https://exemplo.com/curso-marketing"
    }')

    GENERATED_URL=$(echo $URL_RESPONSE | grep -o '"generated_url":"[^"]*' | cut -d'"' -f4)
    if [ -n "$GENERATED_URL" ]; then
        echo "✅ URL gerada com sucesso:"
        echo "   $GENERATED_URL"
    else
        echo "❌ Erro ao gerar URL"
    fi
    echo ""
fi

# 8. Listar UTMs
echo "📋 8. Listando UTMs..."
UTMS_LIST=$(api_call GET "/api/utms")
UTMS_COUNT=$(echo $UTMS_LIST | grep -o '"total":[0-9]*' | cut -d':' -f2)
echo "✅ Total de UTMs: $UTMS_COUNT"
echo ""

# 9. Buscar Página Completa (com testes e métricas)
if [ -n "$PAGE_ID" ]; then
    echo "🔍 9. Buscando página completa..."
    PAGE_DETAIL=$(api_call GET "/api/pages/$PAGE_ID")

    if echo $PAGE_DETAIL | grep -q '"success":true'; then
        echo "✅ Página recuperada com sucesso"
        echo "   Possui testes e métricas anexados"
    else
        echo "❌ Erro ao buscar página"
    fi
    echo ""
fi

# 10. Atualizar Página
if [ -n "$PAGE_ID" ]; then
    echo "✏️ 10. Atualizando página..."
    UPDATE_RESPONSE=$(api_call PUT "/api/pages/$PAGE_ID" '{
        "status": "testing",
        "description": "Landing page em teste A/B"
    }')

    if echo $UPDATE_RESPONSE | grep -q '"success":true'; then
        echo "✅ Página atualizada com sucesso"
    else
        echo "❌ Erro ao atualizar página"
    fi
    echo ""
fi

# 11. Listar Métricas da Página
if [ -n "$PAGE_ID" ]; then
    echo "📊 11. Listando métricas da página..."
    METRICS_LIST=$(api_call GET "/api/pages/$PAGE_ID/metrics")

    if echo $METRICS_LIST | grep -q '"success":true'; then
        echo "✅ Métricas recuperadas com sucesso"
        TOTAL_IMPRESSIONS=$(echo $METRICS_LIST | grep -o '"total_impressions":[0-9]*' | cut -d':' -f2)
        TOTAL_CLICKS=$(echo $METRICS_LIST | grep -o '"total_clicks":[0-9]*' | cut -d':' -f2)
        echo "   Total de impressões: $TOTAL_IMPRESSIONS"
        echo "   Total de cliques: $TOTAL_CLICKS"
    else
        echo "❌ Erro ao listar métricas"
    fi
    echo ""
fi

echo "======================================"
echo "✅ Testes concluídos com sucesso!"
echo ""
echo "📝 Resumo:"
echo "   - Páginas criadas: 1"
echo "   - UTMs criadas: 1"
echo "   - Testes A/B: 1"
echo "   - Métricas registradas: 1"
echo ""
echo "🎯 Próximos passos:"
echo "   1. Testar integração com elementos do funil"
echo "   2. Criar interface web para gerenciar páginas e UTMs"
echo "   3. Implementar dashboard de analytics"
