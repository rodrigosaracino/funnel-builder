# Prompt para Planejamento do Funnel Builder

## Contexto do Projeto

Sou o desenvolvedor do **Funnel Builder**, um sistema completo de construção e análise de funis de vendas com interface drag & drop. O projeto está em Python com servidor HTTP simples e frontend em React (via Babel no navegador).

---

## 📋 VISÃO GERAL DO SISTEMA

### Tecnologias Utilizadas
- **Backend**: Python 3 com http.server (HTTPServer)
- **Frontend**: React 18 + Babel Standalone
- **Persistência**: localStorage do navegador
- **Arquivo único**: `funnel_builder.py` (contém HTML, CSS, JavaScript/React embarcado)

### Arquitetura
- Aplicação single-page em um único arquivo Python
- Servidor roda em `http://127.0.0.1:7860`
- Todo o código frontend está embarcado como string Python
- Dados salvos localmente no navegador (funis, configurações)

---

## 🎯 FUNCIONALIDADES PRINCIPAIS IMPLEMENTADAS

### 1. Sistema de Autenticação (Tela de Login)
- Tela de login com email e senha
- Design moderno com gradiente roxo
- Animações de entrada

### 2. Dashboard de Funis
**Características:**
- Lista todos os funis criados pelo usuário
- Templates prontos para uso rápido:
  - VSL Simples (tráfego → VSL → checkout → obrigado)
  - Webinar (tráfego → captura → webinar → vendas → obrigado)
  - Tripwire (tráfego → captura → tripwire → upsell → obrigado)
- Botão "Criar do Zero" para funil customizado
- Botão "⚙️ Configurações" no canto superior direito
- Barra de rolagem vertical para visualizar todo conteúdo
- Cada funil mostra: ícone, nome, número de elementos
- Opção de deletar funis

### 3. Editor de Funil (Canvas Principal)
**Interface:**
- **Topo**: Dashboard com 6 métricas em tempo real:
  - 🎯 Visitantes Iniciais
  - 💰 Investimento Total
  - 📊 CAC (Custo por Cliente) - calculado apenas com vendas reais
  - 🛒 Conversões Esperadas
  - 💵 Receita Projetada
  - 📈 ROI Projetado (com indicadores coloridos ✅⚠️❌)

- **Lateral Esquerda**: Biblioteca de elementos organizados por categorias
- **Centro**: Canvas com grid para posicionar elementos
- **Lateral Direita**: Painel de propriedades do elemento selecionado
- **Canto inferior direito**: Controles de zoom (+, -, reset, nível)

**Funcionalidades do Canvas:**
- Drag & drop de elementos da biblioteca
- Movimentação livre de elementos
- Zoom (0.5x a 2x)
- Pan (arrastar o canvas com o mouse)
- Seleção de elementos (borda azul)
- Conexões entre elementos com curvas suaves
- Pontos de conexão nos 4 lados de cada elemento
- Labels de conversão nas conexões
- Validação visual de campos (verde/amarelo/vermelho)

### 4. Elementos do Funil

#### Categorias e Elementos:
**🎯 Tráfego**
- Tráfego Pago (ícone: 🎯)
- Retargeting (ícone: 🔄)

**📄 Páginas**
- Landing Page (ícone: 🚀)
- Página de Captura (ícone: 📝)
- VSL - Video Sales Letter (ícone: 🎬)
- Página de Vendas (ícone: 💎)
- Checkout (ícone: 💳)
- Página Obrigado (ícone: 🎉)
- Squeeze Page (ícone: 🎁)

**💬 Relacionamento**
- Email (ícone: ✉️)
- Sequência Email (ícone: 📧)
- WhatsApp (ícone: 📱)

**🎬 Engajamento**
- Quiz/Enquete (ícone: 📊)
- Vídeo (ícone: ▶️)
- Webinar (ícone: 🎥)
- Call/Consulta (ícone: 📞)

**💰 Conversão**
- Countdown (ícone: ⏰)
- Upsell (ícone: ⬆️)
- Downsell (ícone: ⬇️)

**🎁 Pós-Venda**
- Área de Membros (ícone: 📚)

### 5. Sistema de Cores

#### Cores Padrão por Tipo (Gradientes CSS):
- Cada tipo de elemento tem uma cor padrão única
- Exemplos:
  - Tráfego: Gradiente roxo (#667eea → #764ba2)
  - Landing Page: Rosa/vermelho (#f093fb → #f5576c)
  - Checkout: Ciano/roxo escuro (#30cfd0 → #330867)
  - WhatsApp: Verde característico (#25d366 → #128c7e)

#### Personalização de Cores:
- Seletor de cor nativo HTML5 para customização
- Botão "🔄 Restaurar Padrão" para voltar à cor original
- Cores salvas automaticamente no funil

### 6. Propriedades dos Elementos

#### Campos Comuns a Todos:
- Nome do Elemento
- 🎨 Cor do Elemento (personalizável)
- URL da Página
- Descrição (opcional)
- Taxa de Conversão (%)

#### Tráfego Pago - Campos Especiais:
**Dois Modos de Configuração:**

**Modo 1: Números Absolutos**
- 💰 Investimento Planejado (R$)
- 👁️ Impressões Esperadas
- 👆 Cliques Esperados
- CTR calculado automaticamente

**Modo 2: CTR & CPM**
- 💰 Investimento Planejado (R$)
- 💵 CPM - Custo por Mil (R$)
- 📊 CTR - Taxa de Cliques (%)
- Impressões e Cliques calculados automaticamente

**Validações em Tempo Real:**
- Verde: Valores dentro do esperado
- Amarelo: Atenção necessária
- Vermelho: Valores fora do padrão

**Benchmarks Exibidos:**
- CTR de 1-3%: Bom desempenho
- CPM de R$ 15-40: Faixa comum
- E outros indicadores por tipo

#### Elementos de Conversão:
- ✅ Checkbox: "💰 Este elemento gera receita"
- 💵 Preço do Produto (se gera receita)
- 📦 Order Bump (checkbox)
  - Preço do Order Bump
  - Taxa de Conversão do Order Bump

#### Retargeting:
- Campo: "Nome do Público" (ex: "Visualizou VSL mas não comprou")

### 7. Sistema de Cálculos

#### Propagação de Métricas:
- Tráfego flui do elemento inicial (tráfego pago) até o final
- Cada conexão tem uma taxa de conversão
- Cálculos automáticos em cascata:
  - Visitantes → Pageviews → Leads → Vendas
  - Investimento propagado do início
  - CPL (Custo por Lead) calculado
  - ROI calculado automaticamente

#### Lógica Especial - Downsell:
- Recebe pessoas que **NÃO converteram** no elemento anterior
- Exemplo: Se 100 pessoas chegaram no checkout e 20 compraram, o Downsell recebe 80 pessoas (os não-convertidos)

#### Métricas Exibidas em Cada Elemento:
- 👥 Visitantes/Pessoas
- ✅ Conversões (número + percentual)
- 💰 Investimento acumulado
- 💵 CPL ou Receita Total

### 8. Painel de Configurações do Sistema

Acessível via botão "⚙️ Configurações" no dashboard.

**Modal com 2 Seções:**

#### 📁 Categorias de Elementos:
- Editar ícone da categoria (emoji)
- Editar nome da categoria
- Para cada elemento:
  - Editar ícone (emoji)
  - Editar nome de exibição

#### 🏷️ Labels dos Campos:
- Customizar todos os rótulos dos campos do formulário
- Exemplos editáveis:
  - "Investimento Planejado"
  - "Impressões Esperadas"
  - "Taxa de Conversão"
  - etc.

**Controles:**
- 💾 Salvar Alterações (recarrega página para aplicar)
- 🔄 Restaurar Padrões (remove todas customizações)
- Cancelar (fecha sem salvar)

**Persistência:**
- Configurações salvas em `localStorage` → chave `systemConfig`
- Carregadas automaticamente ao iniciar

### 9. Validação e UX

#### Validação Visual:
- Campos numéricos validados em tempo real
- Mensagens contextuais de ajuda
- Cores indicativas (verde/amarelo/vermelho)
- Benchmarks do mercado exibidos

#### Feedback Visual:
- Hover effects em todos os botões
- Animações suaves (fade in, slide up)
- Indicadores de estado (selecionado, arrastando, conectando)
- Zoom controls com feedback visual

#### Auto-Save:
- Funis salvos automaticamente ao modificar
- Sem necessidade de botão "Salvar"
- Dados persistem entre sessões

---

## 🗂️ ESTRUTURA DE DADOS

### Estrutura de um Funil:
```json
{
  "id": "timestamp único",
  "name": "Nome do Funil",
  "icon": "🚀",
  "createdAt": "ISO date",
  "elements": [...],
  "connections": [...]
}
```

### Estrutura de um Elemento:
```json
{
  "id": "elemento_timestamp",
  "type": "trafego|landing|checkout|...",
  "name": "Nome customizado",
  "icon": "🎯",
  "color": "color-trafego",
  "customColor": "linear-gradient(...)", // opcional
  "customColorPicker": "#667eea", // opcional
  "x": 100,
  "y": 150,
  "investment": 10000,
  "impressions": 100000,
  "clicks": 2000,
  "ctr": 2,
  "cpm": 25,
  "trafficMode": "absolute|metrics",
  "conversionRate": 15,
  "generatesRevenue": true,
  "price": 197,
  "hasOrderBump": false,
  "orderBumpPrice": 0,
  "orderBumpConversion": 0,
  "url": "https://...",
  "description": "..."
}
```

### Estrutura de uma Conexão:
```json
{
  "id": "conexao_timestamp",
  "from": "elemento_id_origem",
  "to": "elemento_id_destino",
  "fromSide": "right|left|top|bottom",
  "toSide": "left|right|top|bottom",
  "conversion": 50,
  "label": "50%"
}
```

---

## 🎨 DESIGN SYSTEM

### Paleta de Cores Principal:
- Gradiente principal: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- Branco: `#ffffff`
- Cinza claro: `#f7fafc`
- Cinza médio: `#e2e8f0`
- Cinza texto: `#4a5568`
- Texto escuro: `#2d3748`

### Indicadores de Status:
- ✅ Verde (#48bb78): Positivo/Excelente
- ⚠️ Amarelo (#ecc94b): Atenção/Moderado
- ❌ Vermelho (#f56565): Negativo/Crítico

### Tipografia:
- Font: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto
- Títulos: 700 (bold)
- Texto normal: 400-600

### Espaçamentos:
- Padding cards: 20px
- Gap grids: 20px
- Border radius: 8-16px
- Sombras: 0 4px 12px rgba(0, 0, 0, 0.1)

---

## 🔧 COMPONENTES REACT PRINCIPAIS

### Hierarquia de Componentes:
```
App
├── LoginScreen (tela inicial)
├── FunnelDashboard (lista de funis)
│   └── SettingsPanel (modal de configurações)
├── FunnelBuilder (editor principal)
│   ├── Dashboard (métricas do topo)
│   ├── Sidebar (biblioteca de elementos)
│   ├── Canvas (área de trabalho)
│   │   ├── Element (cada elemento)
│   │   └── Connection (linhas de conexão)
│   └── PropertiesPanel (painel lateral direito)
└── SettingsPanel (configurações do sistema)
```

### Hooks Utilizados:
- `useState`: Gerenciamento de estado local
- `useRef`: Referência ao canvas para cálculos
- `useEffect`: Auto-save e carregamento de dados

---

## 📊 FLUXO DE DADOS

### 1. Carregamento Inicial:
```
localStorage → systemConfig (configurações)
localStorage → funnels (lista de funis)
```

### 2. Edição de Funil:
```
Usuário modifica elemento
→ updateElementProperty()
→ setElements() atualiza estado
→ calculateMetrics() recalcula tudo
→ useEffect() salva no localStorage
→ Canvas re-renderiza
```

### 3. Propagação de Métricas:
```
Elemento Tráfego (raiz)
→ calculateForElement() recursivo
→ Para cada conexão:
  → Aplica taxa de conversão
  → Propaga para elemento filho
  → Calcula métricas acumuladas
→ Retorna mapa completo de métricas
```

---

## 🐛 PROBLEMAS CONHECIDOS

### 1. Seletor de Cores
- **Status**: Parcialmente funcional
- **Problema**: Paleta de cores prontas removida temporariamente
- **Funcionando**: Seletor de cor personalizado + restaurar padrão
- **Logs adicionados**: console.log para debug de atualização

### 2. Performance
- **Atenção**: Babel transpiling no navegador (desenvolvimento)
- **Aviso**: "You are using the in-browser Babel transformer"
- **Recomendação futura**: Pré-compilar scripts para produção

---

## 📁 ESTRUTURA DO PROJETO

```
Funnel Builder/
├── funnel_builder.py          (arquivo único com tudo)
├── DOCUMENTACAO.md             (documentação completa)
├── README.md                   (instruções de uso)
└── PROMPT_PROJETO.md          (este arquivo)
```

---

## 🚀 COMO EXECUTAR

```bash
cd "/Users/rodrigosaracino/Downloads/Funnel Builder"
python3 funnel_builder.py
```

Acesse: `http://127.0.0.1:7860`

---

## 💡 POSSÍVEIS MELHORIAS FUTURAS

### Funcionalidades:
1. Exportar funil como imagem (PNG/SVG)
2. Exportar dados para CSV/Excel
3. Integração com APIs de marketing (Facebook Ads, Google Ads)
4. Comparação entre funis (A/B testing)
5. Templates salvos personalizados
6. Colaboração em tempo real
7. Histórico de versões do funil
8. Duplicar elementos
9. Atalhos de teclado
10. Modo escuro

### Técnicas:
1. Separar frontend e backend
2. Usar framework (Next.js ou Vite)
3. TypeScript para type safety
4. Banco de dados real (PostgreSQL)
5. Autenticação real (JWT)
6. Deploy em produção (Vercel/Railway)
7. Testes automatizados
8. CI/CD pipeline

### UX:
1. Tutorial interativo na primeira vez
2. Tooltips mais explicativos
3. Undo/Redo
4. Alinhamento automático de elementos
5. Snap to grid
6. Minimap do canvas
7. Busca de elementos
8. Favoritos/elementos recentes

---

## 🎯 COMO USAR ESTE PROMPT

**Para planejamento estratégico:**
> "Com base no projeto Funnel Builder descrito acima, preciso [objetivo específico]. Considere as funcionalidades atuais e sugira a melhor abordagem."

**Para resolver bugs:**
> "No Funnel Builder, estou tendo o seguinte problema: [descrição]. Considerando a arquitetura atual (React + Python server), como posso resolver?"

**Para adicionar features:**
> "Quero adicionar [nova funcionalidade] ao Funnel Builder. Como isso se integraria com o sistema atual de [componente relacionado]?"

**Para refatoração:**
> "Preciso refatorar [componente/função] do Funnel Builder. Qual a melhor forma de fazer isso mantendo compatibilidade com o resto do sistema?"

**Para otimização:**
> "Como posso otimizar [aspecto específico] do Funnel Builder considerando que usa [tecnologia/padrão atual]?"

---

## 📝 NOTAS IMPORTANTES

1. **Arquivo Único**: Todo o código está em um único arquivo Python por simplicidade
2. **localStorage**: Todos os dados ficam no navegador do usuário
3. **Sem Backend Real**: Servidor apenas serve o HTML, sem API
4. **React In-Browser**: Babel transforma JSX no navegador (dev only)
5. **Auto-Save**: Mudanças são salvas automaticamente
6. **Responsivo**: Layout se adapta mas é otimizado para desktop

---

## 🔍 CONTEXTO TÉCNICO ADICIONAL

- Python 3.13
- React 18.x
- Babel Standalone
- Sin dependências npm/package.json
- Porta padrão: 7860
- SO de desenvolvimento: macOS (Darwin 25.0.0)

---

Última atualização: 28 de outubro de 2025
