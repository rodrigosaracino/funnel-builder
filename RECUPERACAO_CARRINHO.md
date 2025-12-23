# 🛒 Recuperação de Carrinho Abandonado

## 📋 Visão Geral

O elemento **Recuperação de Carrinho** foi criado especialmente para planejar estratégias de recuperação de pessoas que **NÃO compraram** (abandonaram o carrinho/checkout).

## 🎯 Como Funciona

### Lógica Especial

Similar ao Downsell, a Recuperação de Carrinho recebe as pessoas que **NÃO converteram**:

```
Checkout: 1000 visitantes, 5% conversão = 50 vendas
Recuperação recebe: 950 pessoas (95% que não compraram)
```

### Exemplo de Funil Completo

```
[Tráfego Pago] → [Landing Page] → [Checkout]
                                       ↓ (95% não converteu)
                                  [Recuperação de Carrinho]
                                       ↓
                                  [Checkout Final]
```

## 📊 Benchmarks de Mercado

| Taxa de Recuperação | Classificação |
|---------------------|---------------|
| 5-10% | Taxa típica |
| 10-20% | Boa campanha |
| 20%+ | Excelente! |

## 💡 Melhores Práticas

### 1. Sequência de Emails

**Recomendado: 3-5 emails em 7-14 dias**

- **Email 1 (1h depois):** Lembrete amigável
  - "Você esqueceu algo no carrinho 🛒"
  - Taxa de conversão: 30-40% do total

- **Email 2 (24h depois):** Urgência
  - "Última chance! Vagas limitadas ⏰"
  - Taxa de conversão: 25-30% do total

- **Email 3 (48h depois):** Desconto progressivo
  - "10% OFF especial para você 🎁"
  - Taxa de conversão: 20-25% do total

- **Email 4 (7 dias):** Última tentativa
  - "Sentiremos sua falta... 😢"
  - Taxa de conversão: 10-15% do total

- **Email 5 (14 dias):** Reengajamento
  - "Voltamos com uma oferta especial!"
  - Taxa de conversão: 5-10% do total

### 2. Canais Múltiplos

Combine diferentes canais para melhor resultado:

```
[Checkout Abandonado]
    ↓
[Recuperação Email] (70% de alcance)
    ↓
[Recuperação WhatsApp] (40% de alcance)
    ↓
[Retargeting Facebook] (60% de alcance)
    ↓
[Checkout Final]
```

### 3. Elementos de Urgência

- ⏰ Countdown timer (24-72h)
- 🎁 Desconto progressivo (5% → 10% → 15%)
- 🔥 Escassez ("Só restam 3 vagas!")
- 💰 Bônus exclusivo

### 4. Segmentação

**Personalize a recuperação baseado em:**

- Quanto tempo ficou no checkout
- Valor do produto abandonado
- Quantas vezes visitou
- Origem do tráfego

## 🔧 Como Configurar no Funnel Builder

### Passo 1: Adicione o elemento

1. Arraste "Recuperação de Carrinho" da biblioteca
2. Posicione após o Checkout

### Passo 2: Conecte ao Checkout

1. Conecte Checkout → Recuperação de Carrinho
2. Configure a taxa de conversão da conexão:
   - **100%** = Todos os não-compradores entram na sequência
   - **50%** = Metade dos não-compradores (ex: só quem deu email)

### Passo 3: Configure o elemento

**Campos importantes:**

- **Taxa de Conversão:** % de recuperação esperada (5-20%)
- **Tipo de Recuperação:** Email, WhatsApp, Retargeting, Multi-canal
- **Tempo de Ação:** Quantos dias a sequência dura
- **Custo Adicional:** Investimento extra (ex: desconto oferecido)

### Passo 4: Conecte ao Checkout Final

1. Conecte Recuperação → Checkout (ou elemento de venda)
2. As pessoas recuperadas voltam ao processo de compra

## 📈 Exemplos Práticos

### Exemplo 1: Recuperação Simples (Email)

```
Checkout: 1000 visitantes, 5% conversão = 50 vendas
Não compraram: 950 pessoas

Recuperação Email: 950 pessoas, 10% conversão
Vendas recuperadas: 95 vendas

TOTAL: 145 vendas (aumento de 190%!)
```

### Exemplo 2: Recuperação Multi-canal

```
Checkout: 2000 visitantes, 3% conversão = 60 vendas
Não compraram: 1940 pessoas

Email (100% alcance): 1940 pessoas, 8% = 155 vendas
WhatsApp (50% alcance): 970 pessoas, 12% = 116 vendas
Retargeting (70% alcance): 1358 pessoas, 5% = 68 vendas

TOTAL: 399 vendas (aumento de 565%!)
```

### Exemplo 3: Com Desconto Progressivo

```
Checkout Original: R$ 497, 1000 visitantes, 5% = 50 vendas
Receita: R$ 24.850

Recuperação com desconto:
- Email 1 (sem desconto): 40 vendas × R$ 497 = R$ 19.880
- Email 2 (10% OFF): 30 vendas × R$ 447 = R$ 13.410
- Email 3 (15% OFF): 25 vendas × R$ 422 = R$ 10.550

TOTAL: 145 vendas, R$ 68.690 (aumento de 176%)
```

## ⚠️ Cuidados Importantes

### 1. Não Canibalizar Vendas Principais

❌ **Errado:** Oferecer desconto logo na primeira hora
- Pessoas podem abandonar de propósito esperando desconto

✅ **Certo:** Primeiros emails sem desconto
- Desconto apenas após 48-72h
- Desconto progressivo (aumenta com o tempo)

### 2. Respeitar a Jornada

❌ **Errado:** Enviar 10 emails em 3 dias
- Spam, irritação, descadastro

✅ **Certo:** Espaçar bem os contatos
- 3-5 emails em 7-14 dias
- Combinar com outros canais

### 3. Testar e Otimizar

**Teste A/B:**
- Headlines diferentes
- Ofertas diferentes (desconto vs bônus)
- Timing (1h vs 24h para primeiro email)
- Quantidade de emails (3 vs 5)

## 🎯 Casos de Uso

### 1. E-commerce

```
[Produto] → [Carrinho] → [Checkout]
                             ↓ (abandonou)
                        [Email 1h] → [Email 24h] → [Email 48h + 10% OFF]
                             ↓           ↓              ↓
                        [Checkout Recuperado]
```

### 2. Infoproduto

```
[VSL] → [Checkout R$ 497]
             ↓ (não comprou)
        [Email Urgência] → [WhatsApp] → [Retargeting]
             ↓                 ↓             ↓
        [Checkout Final]
```

### 3. High Ticket

```
[Webinar] → [Checkout R$ 5.000]
                ↓ (não comprou)
           [Email Sequência] → [Call de Recuperação]
                ↓                      ↓
           [Checkout Recuperado]
```

## 📊 Métricas para Acompanhar

1. **Taxa de Abertura dos Emails** (25-35% é bom)
2. **Taxa de Clique** (5-10% é bom)
3. **Taxa de Conversão por Email** (varia conforme sequência)
4. **Taxa de Recuperação Total** (5-20%)
5. **ROI da Campanha** (Receita recuperada - Custo)
6. **Tempo Médio até Conversão** (otimizar sequência)

## 🚀 Próximos Passos

1. Arraste o elemento "Recuperação de Carrinho" para seu funil
2. Configure a sequência de recuperação
3. Teste diferentes estratégias
4. Analise os resultados
5. Otimize baseado nos dados

---

## 💡 Dica de Ouro

> "A melhor recuperação de carrinho é aquela que nunca precisou acontecer."
>
> Otimize primeiro seu checkout para reduzir abandono:
> - Processo simples (poucos campos)
> - Múltiplos métodos de pagamento
> - Prova social e garantia visíveis
> - Checkout rápido (sem distrações)
>
> A recuperação deve ser o **plano B**, não o plano principal!

---

**Versão:** 1.0
**Data:** Dezembro 2024
