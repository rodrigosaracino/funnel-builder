# 🛒 Recuperação de Carrinho Abandonado - Estratégia Visual

## 📋 Visão Geral

O elemento **"Recuperação de Carrinho"** é um **ponto de entrada** especial que recebe as pessoas que **NÃO compraram** no checkout.

A partir dele, você monta uma **estratégia visual completa** conectando elementos em sequência (Email, WhatsApp, Ligações, Retargeting).

### 🎯 Diferencial: Totalmente Visual

Diferente de configurações abstratas, aqui você **VÊ TUDO** no canvas:
- ✅ Quantos emails serão enviados
- ✅ Quando cada um será enviado
- ✅ Quantas pessoas cada canal recupera
- ✅ O resultado final combinado

**Tudo visível. Tudo claro. Sem abstrações.**

---

## 🎯 Como Funciona

### Lógica Especial

O elemento "Recuperação de Carrinho" **recebe os NÃO-convertidos** do checkout:

```
Checkout: 1000 visitantes, 5% conversão = 50 vendas
         ↓
[950 pessoas NÃO compraram] → Vão para Recuperação
```

A partir daí, você conecta sua sequência de recuperação!

---

## 🔧 Como Montar sua Estratégia (Passo a Passo)

### Passo 1: Conecte o Checkout à Recuperação

```
[Checkout] ──100%──→ [🛒 Recuperação de Carrinho]
```

- Conecte com **100%** para todos não-compradores entrarem
- Ou **50%** se só quem deu email entra na sequência

### Passo 2: Monte a Sequência de Recuperação

Arraste elementos da biblioteca e conecte em sequência:

```
[🛒 Recuperação]
      ↓ 100%
[📧 Email 1h depois] (8% conversão)
      ↓ 100%
[📧 Email 24h depois] (6% conversão)
      ↓ 100%
[📱 WhatsApp 48h] (12% conversão)
      ↓ 100%
[🎯 Retargeting 7 dias] (5% conversão)
      ↓ 100%
[💳 Checkout Final]
```

### Passo 3: Configure Cada Elemento

**Para cada Email/WhatsApp:**
1. Clique no elemento
2. Configure **Taxa de Conversão** (% que recupera)
3. Opcionalmente, configure **Taxa de Visualização** (% que abre)

**Exemplo - Email 1h depois:**
- Nome: "Email 1h - Lembrete"
- Taxa de Visualização: 70% (70% abre o email)
- Taxa de Conversão: 8% (dos que abrem, 8% compram)

### Passo 4: Conecte Tudo ao Checkout Final

Cada elemento pode conectar ao checkout final:

```
[Email 1h] ────┐
               ├──→ [Checkout Final]
[Email 24h] ───┤
               │
[WhatsApp] ────┘
```

Ou em sequência linear (recomendado para visualização):

```
[Email 1h] → [Email 24h] → [WhatsApp] → [Checkout Final]
```

---

## 📊 Exemplo Completo Visual

### Funil Completo com Recuperação

```
[Tráfego: 10.000 pessoas] → [Landing: 40%] → [Checkout: 5%]
                                                   ↓
                                            [200 vendas]
                                            [3.800 NÃO compraram]
                                                   ↓
                                     [🛒 Recuperação de Carrinho]
                                                   ↓
                              ┌────────────────────┴────────────────────┐
                              ↓                                         ↓
                    [📧 Email 1h depois]                    [Análise de tráfego]
                    3.800 pessoas
                    70% abrem = 2.660
                    8% compram = 213 vendas ✅
                              ↓
                    [📧 Email 24h depois]
                    (3.800 - 213) = 3.587 pessoas
                    65% abrem = 2.332
                    6% compram = 140 vendas ✅
                              ↓
                    [📱 WhatsApp 48h]
                    (3.587 - 140) = 3.447 pessoas
                    40% alcance = 1.379
                    12% compram = 165 vendas ✅
                              ↓
                    [🎯 Retargeting 7 dias]
                    (3.447 - 165) = 3.282 pessoas
                    60% alcance = 1.969
                    5% compram = 98 vendas ✅
                              ↓
                         [💳 Checkout Final]
                         616 vendas recuperadas!

TOTAL: 200 (inicial) + 616 (recuperados) = 816 vendas
Aumento de 308%! 🚀
```

---

## 💡 Estratégias Recomendadas

### Estratégia 1: Email Simples (3 emails)

```
[Recuperação]
    ↓
[Email 1h] → "Você esqueceu algo no carrinho" (8%)
    ↓
[Email 24h] → "Última chance! 24h restantes" (6%)
    ↓
[Email 48h] → "10% OFF exclusivo pra você" (10%)
    ↓
[Checkout Final]

Resultado: ~24% de recuperação
```

### Estratégia 2: Multi-Canal (Email + WhatsApp)

```
[Recuperação]
    ↓
[Email 1h] → 8%
    ↓
[Email 24h] → 6%
    ↓
[WhatsApp] → "Oi! Vi que você quase comprou..." (12%)
    ↓
[Checkout Final]

Resultado: ~26% de recuperação
```

### Estratégia 3: Agressiva (Email + WhatsApp + Ligação)

```
[Recuperação]
    ↓
[Email 1h] → 8%
    ↓
[Email 24h] → 6%
    ↓
[WhatsApp 48h] → 12%
    ↓
[Ligação 72h] → "Posso ajudar?" (25%)
    ↓
[Checkout Final]

Resultado: ~51% de recuperação (alto ticket)
```

### Estratégia 4: Long Tail (14 dias)

```
[Recuperação]
    ↓
[Email 1h] → 8%
    ↓
[Email 24h] → 6%
    ↓
[Email 3d] → 5%
    ↓
[WhatsApp 7d] → 10%
    ↓
[Retargeting 14d] → 5%
    ↓
[Checkout Final]

Resultado: ~34% de recuperação
```

---

## 📋 Benchmarks por Canal

### 📧 Email

| Timing | Taxa de Abertura | Taxa de Conversão |
|--------|------------------|-------------------|
| 1 hora | 60-80% | 6-10% |
| 24 horas | 50-70% | 4-8% |
| 48 horas | 40-60% | 3-6% |
| 7 dias | 30-50% | 2-5% |

### 📱 WhatsApp

| Timing | Taxa de Alcance | Taxa de Conversão |
|--------|-----------------|-------------------|
| 48 horas | 30-50% | 10-15% |
| 72 horas | 30-50% | 8-12% |
| 7 dias | 25-40% | 5-10% |

### 📞 Ligação

| Contexto | Taxa de Atendimento | Taxa de Conversão |
|----------|---------------------|-------------------|
| High Ticket | 10-20% | 20-30% |
| Mid Ticket | 5-15% | 15-25% |

### 🎯 Retargeting

| Timing | Taxa de Alcance | Taxa de Conversão |
|--------|-----------------|-------------------|
| 7 dias | 50-70% | 3-7% |
| 14 dias | 40-60% | 2-5% |
| 30 dias | 30-50% | 1-3% |

---

## 🎨 Dicas de Visualização no Canvas

### 1. Use Cores Diferentes

- Email 1: 📧 Azul claro
- Email 2: 📧 Azul médio
- WhatsApp: 📱 Verde
- Ligação: 📞 Amarelo
- Retargeting: 🎯 Roxo

### 2. Nomeie Claramente

Bons nomes:
- ✅ "Email 1h - Lembrete"
- ✅ "Email 24h - Urgência"
- ✅ "WhatsApp 48h - 10% OFF"

Nomes ruins:
- ❌ "Email 1"
- ❌ "Email 2"
- ❌ "WhatsApp"

### 3. Organize Verticalmente

```
[Recuperação]
      ↓
   [Email 1]
      ↓
   [Email 2]
      ↓
   [WhatsApp]
      ↓
   [Checkout]
```

Mais fácil de ler que horizontal!

---

## ⚠️ Erros Comuns

### ❌ ERRO 1: Não configurar taxa de conversão

```
[Recuperação] → [Email] → [Checkout]
                  ↑
            (0% conversão!)
```

**Solução:** Sempre configure a taxa de conversão de cada elemento!

### ❌ ERRO 2: Conectar direto ao Checkout original

```
[Checkout Original] → [Recuperação] → [Checkout Original]
                                            ↑
                                    (NÃO FAÇA ISSO!)
```

**Solução:** Crie um "Checkout Final" separado para receber as recuperações.

### ❌ ERRO 3: Muitos emails muito rápido

```
[Recuperação]
    ↓
[Email 1h] → [Email 2h] → [Email 3h] → [Email 4h]
                        (SPAM!)
```

**Solução:** Espaçe os emails (1h → 24h → 48h → 7d)

---

## 🚀 Começando Agora

1. **Abra seu funil** no Funnel Builder
2. **Conecte Checkout → Recuperação** (100%)
3. **Arraste 2-3 elementos de Email** para o canvas
4. **Conecte em sequência**: Recuperação → Email 1 → Email 2 → Checkout Final
5. **Configure taxa de conversão** de cada email (6-10%)
6. **Veja os resultados** calculados automaticamente!

---

**Agora sua estratégia de recuperação está 100% VISUAL!** 🎨

Você vê exatamente:
- ✅ Quantos emails
- ✅ Quando cada um é enviado
- ✅ Quantas pessoas cada um recupera
- ✅ O resultado total

**Sem abstrações. Só clareza.** ✨

---

**Versão:** 2.0 - Visual
**Data:** Dezembro 2024
