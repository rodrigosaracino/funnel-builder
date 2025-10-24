# 🚀 Funnel Builder - Sistema de Construção de Funis de Vendas

Sistema completo e interativo para construção, visualização e análise de funis de vendas digitais com interface drag & drop.

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Características](#-características)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [Tipos de Elementos](#-tipos-de-elementos)
- [Templates Prontos](#-templates-prontos)
- [Métricas e Cálculos](#-métricas-e-cálculos)
- [Funcionalidades Avançadas](#-funcionalidades-avançadas)
- [Tecnologias](#-tecnologias)

---

## 🎯 Visão Geral

O **Funnel Builder** é uma ferramenta visual para profissionais de marketing digital criarem, planejarem e analisarem funis de vendas completos. Com interface intuitiva de arrastar e soltar, permite simular diferentes estratégias de conversão e prever resultados financeiros.

### Principais Benefícios:
- ✅ Visualização clara do fluxo de conversão
- ✅ Cálculo automático de métricas e ROI
- ✅ Templates prontos baseados em estratégias comprovadas
- ✅ Simulação de diferentes cenários
- ✅ Auto-save automático
- ✅ Gerenciamento de múltiplos funis

---

## ✨ Características

### 🎨 Interface Visual
- **Drag & Drop**: Arraste elementos da biblioteca para o canvas
- **Conexões Visuais**: Conecte elementos com setas que mostram taxa de conversão
- **Canvas Infinito**: Zoom e pan ilimitados
- **Design Moderno**: Interface gradiente com cores categorizadas

### 📊 Dashboard Inicial
- **Templates Prontos**: 3 modelos profissionais (VSL, Webinar, Tripwire)
- **Criar do Zero**: Opção para funis personalizados
- **Meus Funis**: Lista todos os funis criados
- **Ações Rápidas**: Editar, duplicar ou deletar funis

### 💾 Persistência
- **Auto-Save**: Salva automaticamente todas as alterações
- **LocalStorage**: Dados persistem entre sessões
- **Múltiplos Funis**: Gerencie quantos funis quiser

### 📈 Métricas em Tempo Real
- Visitantes iniciais
- Investimento total
- Conversões esperadas
- Receita projetada
- ROI projetado (com indicadores visuais)

---

## 🚀 Instalação

### Requisitos
- Python 3.6 ou superior
- Navegador web moderno (Chrome, Firefox, Safari, Edge)

### Passos

1. **Clone o repositório:**
```bash
git clone https://github.com/rodrigosaracino/funnel-builder.git
cd funnel-builder
```

2. **Execute o servidor:**
```bash
python3 funnel_builder.py
```

3. **Acesse no navegador:**
```
http://localhost:8000
```

O navegador abrirá automaticamente!

---

## 📖 Como Usar

### 1️⃣ Dashboard Inicial

Ao abrir o sistema, você verá:
- **Templates Prontos**: Clique para criar um funil instantaneamente
- **Criar do Zero**: Para começar com canvas vazio
- **Meus Funis**: Lista de funis já criados

### 2️⃣ Escolhendo um Template

Clique em qualquer template para criar um funil pré-configurado:
- **VSL Simples**: Funil com vídeo de vendas
- **Webinar**: Funil de webinar completo
- **Tripwire**: Oferta de baixo valor com upsells

### 3️⃣ Criando Funil do Zero

1. Clique em "**Criar do Zero**"
2. Digite o nome do funil
3. Clique em "**Criar**"
4. Comece a arrastar elementos para o canvas

### 4️⃣ Construindo o Funil

**Adicionar Elementos:**
1. Arraste um elemento da biblioteca (lateral esquerda)
2. Solte no canvas
3. Configure as propriedades (painel direito)

**Conectar Elementos:**
1. Clique no ponto de conexão direito (bolinha azul) do elemento origem
2. Arraste até o ponto esquerdo do elemento destino
3. Configure a taxa de conversão da conexão

**Editar Propriedades:**
1. Clique em um elemento
2. Painel direito mostra todas as propriedades
3. Ajuste valores conforme necessário
4. Mudanças são salvas automaticamente

### 5️⃣ Analisando Resultados

- **Dashboard Superior**: Mostra métricas consolidadas
- **Cada Elemento**: Exibe métricas individuais
- **Conexões**: Mostram taxa de conversão entre elementos

---

## 🧩 Tipos de Elementos

### 📢 Tráfego
**Fonte inicial de visitantes**
- **Modos**:
  - Métricas (CPM + CTR)
  - Absoluto (Cliques diretos)
- **Campos**: Investimento, impressões, cliques
- **Uso**: Facebook Ads, Google Ads, tráfego orgânico

### 📄 Landing Page
**Página de captura ou apresentação**
- **Campos**: Taxa de conversão, taxa de visualização
- **Uso**: Squeeze pages, páginas de vendas simples

### 📧 Captura / Squeeze
**Captura de emails**
- **Campos**: Taxa de conversão (30-50% típico)
- **Uso**: Lead magnets, webinars

### 🎬 VSL (Video Sales Letter)
**Vídeo de vendas**
- **Campos**: Taxa de conclusão, taxa de conversão
- **Uso**: Produtos digitais, cursos online

### 💳 Página de Vendas / Checkout
**Conversão final**
- **Campos**:
  - Taxa de conversão
  - Preço do produto
  - Gera receita: ✅/❌
- **Uso**: Todas as vendas principais

### ⬆️ Upsell
**Oferta adicional pós-compra**
- **Campos**: Taxa de conversão (20-40%), preço
- **Uso**: Order bumps, ofertas complementares

### ⬇️ Downsell
**Oferta para quem NÃO converteu**
- **Lógica Especial**: Recebe pessoas que não compraram
- **Campos**: Taxa de conversão (30-50%), preço menor
- **Uso**: Oferta alternativa de menor valor

### ✉️ Email / Automação
**Sequências de email**
- **Campos**: Taxa de abertura, taxa de clique
- **Uso**: Nutrição, recuperação de carrinho

### 💬 WhatsApp
**Mensagens diretas**
- **Campos**: Taxa de visualização, taxa de resposta
- **Uso**: Lembretes, urgência

### 🎓 Webinar
**Apresentação ao vivo/gravada**
- **Campos**: Taxa de comparecimento, conversão
- **Uso**: Vendas consultivas, alto ticket

### 📹 Vídeo
**Conteúdo em vídeo**
- **Campos**: Taxa de visualização, engajamento
- **Uso**: Conteúdo educativo, série de lançamento

### 🔄 Retargeting
**Anúncios para público aquecido**
- **Campos**: Nome do público, taxas de conversão
- **Uso**: Remarketing, recuperação

### 📱 Produto / Membership
**Produtos ou assinaturas**
- **Campos**: Retenção, LTV
- **Uso**: Produtos físicos, memberships

---

## 📦 Templates Prontos

### 🎬 VSL Simples
**Estrutura:**
```
Tráfego Pago (R$ 3.000)
    ↓ 100%
Landing Page (40% conversão)
    ↓ 100%
VSL (60% assistem)
    ↓ 100%
Checkout (3% conversão, R$ 497)
```

**Ideal para:**
- Infoprodutos
- Cursos online
- Produtos digitais

**ROI Estimado:** 120-150%

---

### 🎓 Webinar
**Estrutura:**
```
Tráfego Pago (R$ 4.000)
    ↓ 100%
Página de Inscrição (35% conversão)
    ↓ 100%
Email Confirmação (55% abertura)
    ↓ 100%
Webinar (40% comparecimento)
    ↓ 100%
Oferta (15% conversão, R$ 997)
```

**Ideal para:**
- Consultorias
- High ticket
- Produtos complexos

**ROI Estimado:** 150-200%

---

### 🎁 Tripwire
**Estrutura:**
```
Tráfego Pago (R$ 1.500)
    ↓ 100%
Landing Page (40% conversão)
    ↓ 100%
Tripwire R$ 27 (20% conversão)
    ↓ 100%
Upsell R$ 97 (30% conversão)
```

**Ideal para:**
- Construir lista
- Qualificar compradores
- Maximizar LTV

**ROI Estimado:** 200-300%

---

## 📐 Métricas e Cálculos

### Fórmulas Utilizadas

**Elementos Raiz (Tráfego):**
```
CPM = (Investimento / Impressões) × 1000
CTR = (Cliques / Impressões) × 100
Custo por Lead = Investimento / Cliques
```

**Elementos de Conversão:**
```
Visitantes = Tráfego de Entrada
Page Views = Visitantes × (Taxa de Visualização / 100)
Leads (Convertidos) = Page Views × (Taxa de Conversão / 100)
```

**Receita:**
```
Receita = Leads × Preço (se "Gera Receita" = true)
```

**ROI:**
```
Lucro = Receita Total - Investimento Total
ROI = (Lucro / Investimento) × 100
```

### Lógica Especial: Downsell

**Diferente de todos os outros elementos**, o Downsell recebe as pessoas que **NÃO converteram**:

```
Não Convertidos = Page Views - Leads
Tráfego para Downsell = Não Convertidos × (Taxa da Conexão / 100)
```

**Exemplo:**
- Checkout: 200 visitantes, 10% conversão = 20 vendas
- Downsell recebe: 180 pessoas (90% que não compraram)

---

## 🔥 Funcionalidades Avançadas

### 🎨 Personalização
- **Ícone do Elemento**: Adicione emoji personalizado
- **Nome do Público**: Campo específico para Retargeting
- **Cores por Categoria**: Identificação visual rápida

### 🔗 Múltiplas Conexões
- **Soma Automática**: Elemento com múltiplas entradas soma todo o tráfego
- **Taxa Individual**: Cada conexão tem sua própria taxa de conversão
- **Exemplo**: Tráfego Orgânico + Tráfego Pago → Landing Page

### 📊 Validação em Tempo Real
- **Alertas Visuais**:
  - ✅ Verde: Valores dentro do normal
  - ⚠️ Amarelo: Atenção necessária
  - ❌ Vermelho: Valores problemáticos
- **Benchmarks**: Cada elemento mostra taxas típicas do mercado

### 🎯 Zoom e Navegação
- **Zoom In/Out**: Botões + e -
- **Pan**: Arraste o canvas
- **100%**: Botão para resetar zoom

### 💾 Gerenciamento de Funis
- **Auto-Save**: Salvamento automático a cada mudança
- **Múltiplos Funis**: Sem limite de quantidade
- **Duplicar**: Clone funis existentes
- **Deletar**: Remove com confirmação

---

## 🛠 Tecnologias

### Backend
- **Python 3**: Servidor HTTP simples
- **Threading**: Abertura automática do navegador

### Frontend
- **React 18**: Interface reativa
- **Babel**: Transpilação JSX in-browser
- **Vanilla CSS**: Estilos puros sem frameworks
- **LocalStorage API**: Persistência de dados

### Arquitetura
- **SPA (Single Page Application)**: Navegação sem reload
- **Component-Based**: Componentes React reutilizáveis
- **State Management**: React Hooks (useState, useEffect)

---

## 📝 Estrutura do Código

```
funnel_builder.py          # Arquivo principal
├── HTTP Server            # Servidor Python
├── HTML/CSS              # Estrutura e estilos
└── JavaScript/React      # Lógica da aplicação
    ├── ELEMENT_CATEGORIES    # Definição de elementos
    ├── FUNNEL_TEMPLATES      # Templates prontos
    ├── FunnelBuilder()       # Editor principal
    ├── FunnelDashboard()     # Tela inicial
    └── App()                 # Componente raiz
```

---

## 🎓 Casos de Uso

### 1. Planejamento de Campanhas
- Simule funis antes de investir
- Compare diferentes estratégias
- Calcule ROI projetado

### 2. Apresentações para Clientes
- Visualize o funil completo
- Mostre métricas esperadas
- Justifique investimentos

### 3. Otimização de Funis Existentes
- Identifique gargalos
- Teste variações
- Melhore taxas de conversão

### 4. Treinamento de Equipes
- Ensine conceitos de funis
- Demonstre fluxos complexos
- Simule cenários reais

---

## 🐛 Solução de Problemas

### Servidor não inicia
```bash
# Verifique se a porta 8000 está livre
lsof -i :8000

# Mate processos na porta
kill -9 <PID>

# Reinicie o servidor
python3 funnel_builder.py
```

### Dados não salvam
- Verifique se o navegador permite localStorage
- Limpe o cache e tente novamente
- Use navegador em modo normal (não anônimo)

### Elementos não aparecem
- Recarregue a página (Ctrl/Cmd + Shift + R)
- Limpe o cache do navegador
- Verifique o console (F12) por erros

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

---

## 👨‍💻 Autor

**Rodrigo Saracino**
- GitHub: [@rodrigosaracino](https://github.com/rodrigosaracino)

---

## 🙏 Agradecimentos

- Inspirado em ferramentas como Funnelytics e ClickFunnels
- Desenvolvido com assistência de Claude Code
- Comunidade de marketing digital

---

## 📞 Suporte

Para dúvidas, sugestões ou reportar bugs:
- Abra uma [Issue](https://github.com/rodrigosaracino/funnel-builder/issues)
- Entre em contato via GitHub

---

## 🔮 Roadmap

### Versão 1.1 (Planejado)
- [ ] Export para PDF
- [ ] Compartilhamento de funis
- [ ] Mais templates (Lançamento PLF, Lead Magnet)
- [ ] Temas dark/light

### Versão 1.2 (Futuro)
- [ ] Integração com APIs (Facebook, Google)
- [ ] Relatórios avançados
- [ ] Colaboração em tempo real
- [ ] Mobile responsivo

---

## ⭐ Star o Projeto

Se este projeto foi útil para você, considere dar uma ⭐ no GitHub!

---

**Versão:** 1.0
**Última Atualização:** Outubro 2024
**Status:** ✅ Estável
