#!/usr/bin/env python3
"""
Funnel Builder - Sistema completo de construção de funis com drag & drop
Autor: Sistema de Funnel Builder
Versão: 1.0
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser
import threading

HTML_CONTENT = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Funnel Builder</title>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f7fa;
            overflow: hidden;
        }

        #root {
            width: 100vw;
            height: 100vh;
        }

        .app {
            display: flex;
            flex-direction: column;
            height: 100%;
        }

        .dashboard {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 30px;
            display: flex;
            justify-content: space-around;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .metric {
            text-align: center;
        }

        .metric-label {
            font-size: 12px;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }

        .metric-value {
            font-size: 28px;
            font-weight: bold;
        }

        .main-content {
            display: flex;
            flex: 1;
            overflow: hidden;
        }

        .sidebar {
            width: 280px;
            background: white;
            border-right: 1px solid #e2e8f0;
            padding: 20px;
            overflow-y: auto;
        }

        .sidebar h3 {
            margin-bottom: 15px;
            color: #2d3748;
            font-size: 16px;
        }

        .element-library {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .library-element {
            padding: 12px;
            border-radius: 8px;
            cursor: move;
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 14px;
            font-weight: 500;
            transition: transform 0.2s, box-shadow 0.2s;
            border: 2px solid transparent;
        }

        .library-element:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .library-element:active {
            transform: scale(0.98);
        }

        .element-icon {
            font-size: 20px;
        }

        .canvas-container {
            flex: 1;
            position: relative;
            overflow: hidden;
            background-color: #f8fafc;
            background-image:
                linear-gradient(rgba(0, 0, 0, 0.05) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 0, 0, 0.05) 1px, transparent 1px);
            background-size: 20px 20px;
        }

        .canvas {
            width: 100%;
            height: 100%;
            position: relative;
        }

        .funnel-element {
            position: absolute;
            width: 200px;
            padding: 15px;
            border-radius: 12px;
            cursor: move;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.3);
            transition: box-shadow 0.2s, transform 0.2s;
        }

        .funnel-element:hover {
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
            transform: translateY(-2px);
        }

        .funnel-element.selected {
            box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.5);
        }

        .funnel-element.dragging {
            opacity: 0.7;
            cursor: grabbing;
        }

        .element-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
            color: white;
        }

        .element-title {
            font-weight: 600;
            font-size: 14px;
            flex: 1;
        }

        .element-actions {
            display: flex;
            gap: 5px;
        }

        .element-btn {
            width: 24px;
            height: 24px;
            border: none;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 4px;
            cursor: pointer;
            color: white;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }

        .element-btn:hover {
            background: rgba(255, 255, 255, 0.5);
        }

        .element-metrics {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 6px;
            padding: 8px;
            font-size: 11px;
            color: white;
        }

        .metric-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 4px;
        }

        .metric-row:last-child {
            margin-bottom: 0;
        }

        .connection-point {
            position: absolute;
            width: 16px;
            height: 16px;
            background: white;
            border: 3px solid #4299e1;
            border-radius: 50%;
            cursor: pointer;
            z-index: 100;
            transition: all 0.2s;
        }

        .connection-point.top {
            top: -8px;
            left: 50%;
            transform: translateX(-50%);
        }

        .connection-point.bottom {
            bottom: -8px;
            left: 50%;
            transform: translateX(-50%);
        }

        .connection-point:hover {
            background: #4299e1;
            transform: translateX(-50%) scale(1.4);
            box-shadow: 0 0 10px rgba(66, 153, 225, 0.5);
        }

        .connection-point.connecting {
            background: #f56565;
            border-color: #f56565;
            animation: pulse 0.8s infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: translateX(-50%) scale(1); }
            50% { transform: translateX(-50%) scale(1.3); }
        }

        svg.connections {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        }

        .connection-line {
            stroke: #4299e1;
            stroke-width: 3;
            fill: none;
            marker-end: url(#arrowhead);
            cursor: pointer;
            pointer-events: stroke;
            transition: stroke-width 0.2s;
        }

        .connection-line:hover {
            stroke: #2c5282;
            stroke-width: 5;
        }

        .connection-line.selected {
            stroke: #f56565;
            stroke-width: 4;
        }

        .connection-label {
            font-size: 12px;
            font-weight: 600;
            fill: white;
            pointer-events: none;
            text-anchor: middle;
        }

        .connection-label-bg {
            fill: #4299e1;
            rx: 4;
            pointer-events: none;
        }

        .properties-panel {
            width: 320px;
            background: white;
            border-left: 1px solid #e2e8f0;
            padding: 20px;
            overflow-y: auto;
        }

        .properties-panel h3 {
            margin-bottom: 20px;
            color: #2d3748;
            font-size: 16px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-label {
            display: block;
            margin-bottom: 8px;
            font-size: 13px;
            font-weight: 600;
            color: #4a5568;
        }

        .form-input {
            width: 100%;
            padding: 10px;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.2s;
        }

        .form-input:focus {
            outline: none;
            border-color: #4299e1;
        }

        .form-checkbox {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px;
            background: #f7fafc;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s;
        }

        .form-checkbox:hover {
            background: #edf2f7;
        }

        .form-checkbox input[type="checkbox"] {
            width: 18px;
            height: 18px;
            cursor: pointer;
        }

        .form-checkbox label {
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            color: #4a5568;
            margin: 0;
        }

        .empty-state {
            color: #a0aec0;
            text-align: center;
            padding: 40px 20px;
            font-size: 14px;
        }

        .color-trafego { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .color-landing { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        .color-email { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
        .color-video { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
        .color-webinar { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
        .color-checkout { background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); }
        .color-upsell { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #2d3748; }
        .color-obrigado { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); color: #2d3748; }

        /* Login Screen Styles */
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }

        .login-card {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 50px 40px;
            width: 100%;
            max-width: 420px;
            animation: slideUp 0.5s ease-out;
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .login-header {
            text-align: center;
            margin-bottom: 40px;
        }

        .login-logo {
            font-size: 48px;
            margin-bottom: 15px;
        }

        .login-title {
            font-size: 28px;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 8px;
        }

        .login-subtitle {
            font-size: 14px;
            color: #718096;
        }

        .login-form {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .login-input-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .login-label {
            font-size: 14px;
            font-weight: 600;
            color: #4a5568;
        }

        .login-input {
            padding: 14px 16px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-size: 15px;
            transition: all 0.2s;
        }

        .login-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .login-button {
            padding: 14px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-top: 10px;
        }

        .login-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        }

        .login-button:active {
            transform: translateY(0);
        }

        .login-footer {
            text-align: center;
            margin-top: 30px;
            font-size: 13px;
            color: #718096;
        }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useRef, useEffect } = React;

        const ELEMENT_TYPES = [
            { type: 'trafego', name: 'Tráfego', icon: '🎯', color: 'color-trafego' },
            { type: 'landing', name: 'Landing Page', icon: '📄', color: 'color-landing' },
            { type: 'email', name: 'Email', icon: '✉️', color: 'color-email' },
            { type: 'video', name: 'Vídeo', icon: '🎬', color: 'color-video' },
            { type: 'webinar', name: 'Webinar', icon: '🎥', color: 'color-webinar' },
            { type: 'checkout', name: 'Checkout', icon: '💳', color: 'color-checkout' },
            { type: 'upsell', name: 'Upsell', icon: '⬆️', color: 'color-upsell' },
            { type: 'obrigado', name: 'Obrigado', icon: '🎉', color: 'color-obrigado' }
        ];

        function LoginScreen({ onLogin }) {
            const [email, setEmail] = useState('');
            const [password, setPassword] = useState('');

            const handleSubmit = (e) => {
                e.preventDefault();
                onLogin();
            };

            return (
                <div className="login-container">
                    <div className="login-card">
                        <div className="login-header">
                            <div className="login-logo">🚀</div>
                            <h1 className="login-title">Funnel Builder</h1>
                            <p className="login-subtitle">Construa funis de vendas de alta conversão</p>
                        </div>
                        <form className="login-form" onSubmit={handleSubmit}>
                            <div className="login-input-group">
                                <label className="login-label" htmlFor="email">Email</label>
                                <input
                                    id="email"
                                    type="email"
                                    className="login-input"
                                    placeholder="seu@email.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="login-input-group">
                                <label className="login-label" htmlFor="password">Senha</label>
                                <input
                                    id="password"
                                    type="password"
                                    className="login-input"
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </div>
                            <button type="submit" className="login-button">
                                Acessar Sistema
                            </button>
                        </form>
                        <div className="login-footer">
                            Versão 1.0 - Sistema de Funis de Vendas
                        </div>
                    </div>
                </div>
            );
        }

        function FunnelBuilder() {
            const [elements, setElements] = useState([]);
            const [connections, setConnections] = useState([]);
            const [selectedElement, setSelectedElement] = useState(null);
            const [selectedConnection, setSelectedConnection] = useState(null);
            const [draggingElement, setDraggingElement] = useState(null);
            const [connectingFrom, setConnectingFrom] = useState(null);
            const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
            const [isDragging, setIsDragging] = useState(false);
            const [mouseDownPos, setMouseDownPos] = useState({ x: 0, y: 0 });
            const canvasRef = useRef(null);

            const calculateMetrics = () => {
                const elementMap = {};
                elements.forEach(el => {
                    elementMap[el.id] = { ...el, childConnections: [] };
                });

                // Mapeia conexões com suas taxas de conversão
                connections.forEach(conn => {
                    if (elementMap[conn.from]) {
                        elementMap[conn.from].childConnections.push(conn);
                    }
                });

                const calculateForElement = (id, inputTraffic = null, parentInvestment = 0) => {
                    const element = elementMap[id];
                    if (!element) return null;

                    let visits = 0;  // Pessoas que chegaram
                    let pageViews = 0;  // Pessoas que visualizaram a página
                    let leads = 0;  // Pessoas convertidas
                    let investment = 0;
                    let cpm = 0;
                    let ctr = 0;
                    let costPerLead = 0;

                    // Se é elemento raiz (sem inputTraffic), calcula a partir de impressões/cliques
                    if (inputTraffic === null) {
                        investment = element.investment || 0;
                        const impressions = element.impressions || 0;
                        const clicks = element.clicks || 0;

                        visits = clicks; // Visitas = número de cliques
                        pageViews = clicks; // No elemento raiz, visitas = pageViews
                        leads = clicks; // No elemento raiz, todos são leads potenciais

                        // Calcula CPM (Custo por Mil Impressões)
                        cpm = impressions > 0 ? (investment / impressions) * 1000 : 0;

                        // Calcula CTR (Click Through Rate)
                        ctr = impressions > 0 ? (clicks / impressions) * 100 : 0;

                        // Calcula Custo por Lead/Clique
                        costPerLead = clicks > 0 ? investment / clicks : 0;
                    } else {
                        // Se recebe tráfego de um elemento pai
                        visits = inputTraffic;
                        investment = parentInvestment;

                        // Aplica taxa de visualização de página
                        const pageViewRate = element.pageViewRate || 100;
                        pageViews = Math.round(visits * (pageViewRate / 100));

                        // Aplica taxa de conversão do elemento
                        const conversionRate = element.conversionRate || 0;
                        leads = Math.round(pageViews * (conversionRate / 100));
                    }

                    const price = element.price || 0;

                    // Só gera receita se o elemento tiver a flag generatesRevenue ativada
                    const revenue = element.generatesRevenue ? (leads * price) : 0;

                    // Custo total é o investimento inicial (apenas para elementos raiz)
                    const totalCost = inputTraffic === null ? investment : 0;
                    const profit = revenue - totalCost;

                    element.calculatedMetrics = {
                        visits,
                        pageViews,
                        leads,
                        revenue,
                        profit,
                        cost: totalCost,
                        investment,
                        cpm,
                        ctr,
                        costPerLead
                    };

                    // Propaga para elementos filhos usando a taxa de conversão da conexão
                    element.childConnections.forEach(conn => {
                        const conversionRate = conn.conversion || 0;
                        const childTraffic = Math.round(leads * (conversionRate / 100));
                        calculateForElement(conn.to, childTraffic, investment);
                    });
                };

                // Começa pelos elementos raiz (sem pais)
                elements.forEach(el => {
                    const hasParent = connections.some(conn => conn.to === el.id);
                    if (!hasParent) {
                        calculateForElement(el.id);
                    }
                });

                return elementMap;
            };

            const getDashboardMetrics = () => {
                const metricsMap = calculateMetrics();
                let totalRevenue = 0;
                let totalProfit = 0;
                let totalSales = 0;
                let totalInvestment = 0;

                Object.values(metricsMap).forEach(el => {
                    if (el.calculatedMetrics) {
                        totalRevenue += el.calculatedMetrics.revenue;
                        totalSales += el.calculatedMetrics.leads;

                        // Soma investimento apenas dos elementos raiz
                        if (el.calculatedMetrics.cost > 0) {
                            totalInvestment += el.calculatedMetrics.cost;
                        }
                    }
                });

                totalProfit = totalRevenue - totalInvestment;
                const roi = totalInvestment > 0 ? ((totalProfit / totalInvestment) * 100) : 0;

                return {
                    revenue: totalRevenue,
                    profit: totalProfit,
                    roi: roi,
                    sales: totalSales,
                    investment: totalInvestment
                };
            };

            const handleDragFromLibrary = (e, elementType) => {
                e.preventDefault();
                const rect = canvasRef.current.getBoundingClientRect();
                const x = e.clientX - rect.left - 100;
                const y = e.clientY - rect.top - 50;

                const newElement = {
                    id: Date.now(),
                    type: elementType.type,
                    name: elementType.name,
                    icon: elementType.icon,
                    color: elementType.color,
                    x: Math.max(0, x),
                    y: Math.max(0, y),
                    investment: 10000,
                    impressions: 100000,
                    clicks: 2000,
                    pageViewRate: 100,
                    conversionRate: 50,
                    price: 100,
                    url: '',
                    description: '',
                    generatesRevenue: false
                };

                setElements([...elements, newElement]);
            };

            const handleElementClick = (e, element) => {
                e.stopPropagation();
                setSelectedElement(element.id);
            };

            const handleElementMouseDown = (e, element) => {
                if (e.target.classList.contains('connection-point') ||
                    e.target.classList.contains('element-btn')) {
                    return;
                }

                e.stopPropagation();
                setSelectedElement(element.id);
                setDraggingElement(element.id);
                setIsDragging(false);
                setMouseDownPos({ x: e.clientX, y: e.clientY });

                const rect = e.currentTarget.getBoundingClientRect();
                setDragOffset({
                    x: e.clientX - rect.left,
                    y: e.clientY - rect.top
                });
            };

            const handleMouseMove = (e) => {
                if (!draggingElement) return;

                // Só começa a arrastar se mover mais de 5 pixels
                const deltaX = Math.abs(e.clientX - mouseDownPos.x);
                const deltaY = Math.abs(e.clientY - mouseDownPos.y);

                if (!isDragging && (deltaX > 5 || deltaY > 5)) {
                    setIsDragging(true);
                }

                if (isDragging) {
                    const rect = canvasRef.current.getBoundingClientRect();
                    const x = e.clientX - rect.left - dragOffset.x;
                    const y = e.clientY - rect.top - dragOffset.y;

                    setElements(elements.map(el =>
                        el.id === draggingElement
                            ? { ...el, x: Math.max(0, x), y: Math.max(0, y) }
                            : el
                    ));
                }
            };

            const handleMouseUp = () => {
                setDraggingElement(null);
                setIsDragging(false);
            };

            const handleCanvasClick = (e) => {
                // Só desseleciona se clicar diretamente no canvas ou canvas-container
                if (e.target === e.currentTarget ||
                    e.target.classList.contains('canvas') ||
                    e.target.classList.contains('canvas-container')) {
                    setSelectedElement(null);
                    setSelectedConnection(null);
                }
            };

            const handleConnectionClick = (e, connection) => {
                e.stopPropagation();
                setSelectedConnection(connection.id);
                setSelectedElement(null);
            };

            const handleConnectionStart = (e, elementId) => {
                e.stopPropagation();
                e.preventDefault();
                if (connectingFrom === elementId) {
                    // Se clicar no mesmo elemento, cancela a conexão
                    setConnectingFrom(null);
                } else if (connectingFrom) {
                    // Se já está conectando, finaliza a conexão
                    const connectionExists = connections.some(
                        conn => conn.from === connectingFrom && conn.to === elementId
                    );
                    if (!connectionExists) {
                        setConnections([...connections, {
                            id: Date.now(),
                            from: connectingFrom,
                            to: elementId,
                            conversion: 10
                        }]);
                    }
                    setConnectingFrom(null);
                } else {
                    // Inicia nova conexão
                    setConnectingFrom(elementId);
                }
            };

            const handleConnectionEnd = (e, elementId) => {
                e.stopPropagation();
                e.preventDefault();
                if (connectingFrom && connectingFrom !== elementId) {
                    const connectionExists = connections.some(
                        conn => conn.from === connectingFrom && conn.to === elementId
                    );

                    if (!connectionExists) {
                        setConnections([...connections, {
                            id: Date.now(),
                            from: connectingFrom,
                            to: elementId,
                            conversion: 10
                        }]);
                    }
                }
                setConnectingFrom(null);
            };

            const handleDeleteElement = (e, elementId) => {
                e.stopPropagation();
                setElements(elements.filter(el => el.id !== elementId));
                setConnections(connections.filter(conn =>
                    conn.from !== elementId && conn.to !== elementId
                ));
                if (selectedElement === elementId) {
                    setSelectedElement(null);
                }
            };

            const updateElementProperty = (property, value) => {
                setElements(elements.map(el => {
                    if (el.id === selectedElement) {
                        // Se for um campo numérico, converte para número
                        if (['investment', 'impressions', 'clicks', 'pageViewRate', 'conversionRate', 'price'].includes(property)) {
                            return { ...el, [property]: parseFloat(value) || 0 };
                        }
                        // Se for booleano, mantém como está
                        if (property === 'generatesRevenue') {
                            return { ...el, [property]: value };
                        }
                        // Caso contrário, mantém como string
                        return { ...el, [property]: value };
                    }
                    return el;
                }));
            };

            const updateConnectionProperty = (property, value) => {
                setConnections(connections.map(conn => {
                    if (conn.id === selectedConnection) {
                        if (property === 'conversion') {
                            return { ...conn, [property]: parseFloat(value) || 0 };
                        }
                        return { ...conn, [property]: value };
                    }
                    return conn;
                }));
            };

            const getConnectionPath = (fromId, toId) => {
                const fromEl = elements.find(el => el.id === fromId);
                const toEl = elements.find(el => el.id === toId);

                if (!fromEl || !toEl) return '';

                const fromX = fromEl.x + 100;
                const fromY = fromEl.y + 100;
                const toX = toEl.x + 100;
                const toY = toEl.y;

                const midY = (fromY + toY) / 2;

                return `M ${fromX} ${fromY} C ${fromX} ${midY}, ${toX} ${midY}, ${toX} ${toY}`;
            };

            const dashboardMetrics = getDashboardMetrics();
            const metricsMap = calculateMetrics();
            const selectedElementData = elements.find(el => el.id === selectedElement);

            return (
                <div className="app">
                    <div className="dashboard">
                        <div className="metric">
                            <div className="metric-label">Investimento</div>
                            <div className="metric-value">
                                R$ {dashboardMetrics.investment.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                            </div>
                        </div>
                        <div className="metric">
                            <div className="metric-label">Receita Total</div>
                            <div className="metric-value">
                                R$ {dashboardMetrics.revenue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                            </div>
                        </div>
                        <div className="metric">
                            <div className="metric-label">Lucro Total</div>
                            <div className="metric-value">
                                R$ {dashboardMetrics.profit.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                            </div>
                        </div>
                        <div className="metric">
                            <div className="metric-label">ROI</div>
                            <div className="metric-value">
                                {dashboardMetrics.roi.toFixed(1)}%
                            </div>
                        </div>
                        <div className="metric">
                            <div className="metric-label">Total de Vendas</div>
                            <div className="metric-value">
                                {dashboardMetrics.sales.toLocaleString('pt-BR')}
                            </div>
                        </div>
                    </div>

                    <div className="main-content">
                        <div className="sidebar">
                            <h3>Elementos do Funil</h3>
                            <div className="element-library">
                                {ELEMENT_TYPES.map(type => (
                                    <div
                                        key={type.type}
                                        className={`library-element ${type.color}`}
                                        draggable
                                        onDragEnd={(e) => handleDragFromLibrary(e, type)}
                                    >
                                        <span className="element-icon">{type.icon}</span>
                                        <span>{type.name}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div
                            className="canvas-container"
                            ref={canvasRef}
                            onMouseMove={handleMouseMove}
                            onMouseUp={handleMouseUp}
                            onClick={handleCanvasClick}
                        >
                            <svg className="connections">
                                <defs>
                                    <marker
                                        id="arrowhead"
                                        markerWidth="10"
                                        markerHeight="10"
                                        refX="9"
                                        refY="3"
                                        orient="auto"
                                    >
                                        <polygon points="0 0, 10 3, 0 6" fill="#4299e1" />
                                    </marker>
                                </defs>
                                {connections.map((conn, idx) => {
                                    const fromEl = elements.find(el => el.id === conn.from);
                                    const toEl = elements.find(el => el.id === conn.to);
                                    if (!fromEl || !toEl) return null;

                                    const midX = (fromEl.x + toEl.x) / 2 + 100;
                                    const midY = (fromEl.y + toEl.y) / 2 + 50;

                                    return (
                                        <g key={conn.id || idx}>
                                            <path
                                                className={`connection-line ${selectedConnection === conn.id ? 'selected' : ''}`}
                                                d={getConnectionPath(conn.from, conn.to)}
                                                onClick={(e) => handleConnectionClick(e, conn)}
                                            />
                                            <rect
                                                className="connection-label-bg"
                                                x={midX - 20}
                                                y={midY - 10}
                                                width="40"
                                                height="20"
                                            />
                                            <text
                                                className="connection-label"
                                                x={midX}
                                                y={midY + 4}
                                            >
                                                {conn.conversion || 0}%
                                            </text>
                                        </g>
                                    );
                                })}
                            </svg>

                            <div className="canvas">
                                {elements.map(element => {
                                    const metrics = metricsMap[element.id]?.calculatedMetrics || {};
                                    return (
                                        <div
                                            key={element.id}
                                            className={`funnel-element ${element.color} ${
                                                selectedElement === element.id ? 'selected' : ''
                                            } ${isDragging && draggingElement === element.id ? 'dragging' : ''}`}
                                            style={{
                                                left: element.x,
                                                top: element.y
                                            }}
                                            onClick={(e) => handleElementClick(e, element)}
                                            onMouseDown={(e) => handleElementMouseDown(e, element)}
                                        >
                                            <div
                                                className={`connection-point top ${connectingFrom === element.id ? 'connecting' : ''}`}
                                                onClick={(e) => handleConnectionStart(e, element.id)}
                                                title="Clique para conectar"
                                            />

                                            <div className="element-header">
                                                <span className="element-icon">{element.icon}</span>
                                                <span className="element-title">{element.name}</span>
                                                <div className="element-actions">
                                                    <button
                                                        className="element-btn"
                                                        onClick={(e) => handleConnectionStart(e, element.id)}
                                                        title={connectingFrom ? "Clique aqui ou em um ponto de conexão" : "Modo de conexão"}
                                                    >
                                                        {connectingFrom === element.id ? '⏸️' : '🔗'}
                                                    </button>
                                                    <button
                                                        className="element-btn"
                                                        onClick={(e) => handleDeleteElement(e, element.id)}
                                                        title="Deletar"
                                                    >
                                                        🗑️
                                                    </button>
                                                </div>
                                            </div>

                                            <div className="element-metrics">
                                                {element.type === 'trafego' ? (
                                                    // Métricas para Tráfego
                                                    <>
                                                        <div className="metric-row">
                                                            <span>💰 Investimento:</span>
                                                            <strong>R$ {(metrics.investment || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</strong>
                                                        </div>
                                                        <div className="metric-row">
                                                            <span>📊 CPM:</span>
                                                            <strong>R$ {(metrics.cpm || 0).toFixed(2)}</strong>
                                                        </div>
                                                        <div className="metric-row">
                                                            <span>💵 Custo/Lead:</span>
                                                            <strong>R$ {(metrics.costPerLead || 0).toFixed(2)}</strong>
                                                        </div>
                                                    </>
                                                ) : element.type === 'landing' ? (
                                                    // Métricas para Landing Page
                                                    <>
                                                        <div className="metric-row">
                                                            <span>👥 Visitas:</span>
                                                            <strong>{metrics.visits?.toLocaleString('pt-BR') || 0}</strong>
                                                        </div>
                                                        <div className="metric-row">
                                                            <span>✅ Leads:</span>
                                                            <strong>{metrics.leads?.toLocaleString('pt-BR') || 0}</strong>
                                                        </div>
                                                    </>
                                                ) : (
                                                    // Métricas para outros elementos
                                                    <>
                                                        <div className="metric-row">
                                                            <span>👥 Visitas:</span>
                                                            <strong>{metrics.visits?.toLocaleString('pt-BR') || 0}</strong>
                                                        </div>
                                                        <div className="metric-row">
                                                            <span>✅ Leads:</span>
                                                            <strong>{metrics.leads?.toLocaleString('pt-BR') || 0}</strong>
                                                        </div>
                                                        {metrics.revenue > 0 && (
                                                            <div className="metric-row">
                                                                <span>💰 Receita:</span>
                                                                <strong>R$ {(metrics.revenue || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</strong>
                                                            </div>
                                                        )}
                                                    </>
                                                )}
                                            </div>

                                            <div
                                                className={`connection-point bottom ${connectingFrom === element.id ? 'connecting' : ''}`}
                                                onClick={(e) => handleConnectionStart(e, element.id)}
                                                title="Clique para conectar"
                                            />
                                        </div>
                                    );
                                })}
                            </div>
                        </div>

                        <div className="properties-panel">
                            <h3>Propriedades</h3>
                            {selectedElementData ? (
                                <div>
                                    <div className="form-group">
                                        <label className="form-label">Nome do Elemento</label>
                                        <input
                                            type="text"
                                            className="form-input"
                                            value={selectedElementData.name || ''}
                                            onChange={(e) => updateElementProperty('name', e.target.value)}
                                            placeholder="Digite o nome..."
                                        />
                                    </div>

                                    {/* Campos específicos para TRÁFEGO */}
                                    {selectedElementData.type === 'trafego' && !connections.some(conn => conn.to === selectedElementData.id) && (
                                        <>
                                            <div className="form-group">
                                                <label className="form-label">💰 Investimento em Tráfego (R$)</label>
                                                <input
                                                    type="number"
                                                    className="form-input"
                                                    value={selectedElementData.investment || 0}
                                                    onChange={(e) => updateElementProperty('investment', e.target.value)}
                                                    placeholder="Ex: 10000"
                                                />
                                            </div>
                                            <div className="form-group">
                                                <label className="form-label">👁️ Impressões</label>
                                                <input
                                                    type="number"
                                                    className="form-input"
                                                    value={selectedElementData.impressions || 0}
                                                    onChange={(e) => updateElementProperty('impressions', e.target.value)}
                                                    placeholder="Ex: 100000"
                                                />
                                            </div>
                                            <div className="form-group">
                                                <label className="form-label">👆 Cliques</label>
                                                <input
                                                    type="number"
                                                    className="form-input"
                                                    value={selectedElementData.clicks || 0}
                                                    onChange={(e) => updateElementProperty('clicks', e.target.value)}
                                                    placeholder="Ex: 2000"
                                                />
                                            </div>
                                            {(() => {
                                                const metrics = calculateMetrics()[selectedElementData.id]?.calculatedMetrics;
                                                return metrics && (
                                                    <div className="form-group">
                                                        <div style={{
                                                            background: '#f7fafc',
                                                            padding: '12px',
                                                            borderRadius: '8px',
                                                            fontSize: '13px'
                                                        }}>
                                                            <div style={{marginBottom: '8px'}}>
                                                                <strong>📊 CPM:</strong> R$ {metrics.cpm.toFixed(2)}
                                                            </div>
                                                            <div style={{marginBottom: '8px'}}>
                                                                <strong>📈 CTR:</strong> {metrics.ctr.toFixed(2)}%
                                                            </div>
                                                            <div>
                                                                <strong>💵 Custo/Clique:</strong> R$ {metrics.costPerLead.toFixed(2)}
                                                            </div>
                                                        </div>
                                                    </div>
                                                );
                                            })()}
                                        </>
                                    )}

                                    {/* Campos específicos para LANDING PAGE */}
                                    {selectedElementData.type === 'landing' && (
                                        <>
                                            <div className="form-group">
                                                <label className="form-label">🔗 URL da Landing Page</label>
                                                <input
                                                    type="text"
                                                    className="form-input"
                                                    value={selectedElementData.url || ''}
                                                    onChange={(e) => updateElementProperty('url', e.target.value)}
                                                    placeholder="https://..."
                                                />
                                            </div>
                                            <div className="form-group">
                                                <label className="form-label">📝 Descrição</label>
                                                <input
                                                    type="text"
                                                    className="form-input"
                                                    value={selectedElementData.description || ''}
                                                    onChange={(e) => updateElementProperty('description', e.target.value)}
                                                    placeholder="Descrição da landing page..."
                                                />
                                            </div>
                                            <div className="form-group">
                                                <label className="form-label">👁️ % Visualização de Página</label>
                                                <input
                                                    type="number"
                                                    className="form-input"
                                                    value={selectedElementData.pageViewRate || 100}
                                                    onChange={(e) => updateElementProperty('pageViewRate', e.target.value)}
                                                    min="0"
                                                    max="100"
                                                    step="0.1"
                                                    placeholder="Ex: 85"
                                                />
                                                <small style={{fontSize: '11px', color: '#718096', marginTop: '4px', display: 'block'}}>
                                                    % de visitantes que carregam a página completamente
                                                </small>
                                            </div>
                                            <div className="form-group">
                                                <label className="form-label">✅ % Taxa de Conversão</label>
                                                <input
                                                    type="number"
                                                    className="form-input"
                                                    value={selectedElementData.conversionRate || 0}
                                                    onChange={(e) => updateElementProperty('conversionRate', e.target.value)}
                                                    min="0"
                                                    max="100"
                                                    step="0.1"
                                                    placeholder="Ex: 10"
                                                />
                                                <small style={{fontSize: '11px', color: '#718096', marginTop: '4px', display: 'block'}}>
                                                    % de pessoas que visualizaram e converteram
                                                </small>
                                            </div>
                                        </>
                                    )}

                                    {/* Campos para outros elementos (Email, Video, Webinar, etc) */}
                                    {selectedElementData.type !== 'trafego' && selectedElementData.type !== 'landing' && (
                                        <>
                                            <div className="form-group">
                                                <label className="form-label">🔗 URL</label>
                                                <input
                                                    type="text"
                                                    className="form-input"
                                                    value={selectedElementData.url || ''}
                                                    onChange={(e) => updateElementProperty('url', e.target.value)}
                                                    placeholder="https://..."
                                                />
                                            </div>
                                            <div className="form-group">
                                                <label className="form-label">📝 Descrição</label>
                                                <input
                                                    type="text"
                                                    className="form-input"
                                                    value={selectedElementData.description || ''}
                                                    onChange={(e) => updateElementProperty('description', e.target.value)}
                                                    placeholder="Descrição..."
                                                />
                                            </div>
                                            <div className="form-group">
                                                <label className="form-label">👁️ % Visualização de Página</label>
                                                <input
                                                    type="number"
                                                    className="form-input"
                                                    value={selectedElementData.pageViewRate || 100}
                                                    onChange={(e) => updateElementProperty('pageViewRate', e.target.value)}
                                                    min="0"
                                                    max="100"
                                                    step="0.1"
                                                    placeholder="Ex: 85"
                                                />
                                            </div>
                                            <div className="form-group">
                                                <label className="form-label">✅ % Taxa de Conversão</label>
                                                <input
                                                    type="number"
                                                    className="form-input"
                                                    value={selectedElementData.conversionRate || 0}
                                                    onChange={(e) => updateElementProperty('conversionRate', e.target.value)}
                                                    min="0"
                                                    max="100"
                                                    step="0.1"
                                                    placeholder="Ex: 10"
                                                />
                                            </div>
                                            <div className="form-group">
                                                <div className="form-checkbox">
                                                    <input
                                                        type="checkbox"
                                                        id="generates-revenue"
                                                        checked={selectedElementData.generatesRevenue || false}
                                                        onChange={(e) => updateElementProperty('generatesRevenue', e.target.checked)}
                                                    />
                                                    <label htmlFor="generates-revenue">💰 Este elemento gera receita (vendas)</label>
                                                </div>
                                            </div>
                                            {selectedElementData.generatesRevenue && (
                                                <div className="form-group">
                                                    <label className="form-label">💵 Valor da Venda (R$)</label>
                                                    <input
                                                        type="number"
                                                        className="form-input"
                                                        value={selectedElementData.price}
                                                        onChange={(e) => updateElementProperty('price', e.target.value)}
                                                        step="0.01"
                                                        placeholder="Ex: 197.00"
                                                    />
                                                </div>
                                            )}
                                        </>
                                    )}
                                </div>
                            ) : selectedConnection ? (
                                <div>
                                    <div className="form-group">
                                        <label className="form-label">Taxa de Conversão (%)</label>
                                        <input
                                            type="number"
                                            className="form-input"
                                            value={connections.find(c => c.id === selectedConnection)?.conversion || 0}
                                            onChange={(e) => updateConnectionProperty('conversion', e.target.value)}
                                            step="0.1"
                                        />
                                    </div>
                                    <div className="empty-state" style={{marginTop: '20px'}}>
                                        Esta é uma conexão entre elementos. Ajuste a taxa de conversão acima.
                                    </div>
                                </div>
                            ) : (
                                <div className="empty-state">
                                    Selecione um elemento ou conexão no canvas para editar suas propriedades
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            );
        }

        function App() {
            // Login desativado - vai direto para o app
            return <FunnelBuilder />;
        }

        ReactDOM.render(<App />, document.getElementById('root'));
    </script>
</body>
</html>"""


class FunnelBuilderHandler(BaseHTTPRequestHandler):
    """Handler HTTP para servir a aplicação Funnel Builder"""

    def do_GET(self):
        """Responde a requisições GET com a página HTML"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML_CONTENT.encode('utf-8'))

    def log_message(self, format, *args):
        """Sobrescreve o log padrão para mensagens customizadas"""
        print(f"[Funnel Builder] {format % args}")


def open_browser(port):
    """Abre o navegador após um pequeno delay"""
    import time
    time.sleep(1)
    webbrowser.open(f'http://localhost:{port}')


def run_server(port=8000):
    """Inicia o servidor HTTP"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, FunnelBuilderHandler)

    print("=" * 70)
    print("🚀 FUNNEL BUILDER - Sistema de Construção de Funis")
    print("=" * 70)
    print(f"\n✅ Servidor iniciado com sucesso!")
    print(f"🌐 Acesse: http://localhost:{port}")
    print(f"\n📖 Como usar:")
    print("   1. Arraste elementos da barra lateral para o canvas")
    print("   2. Clique no botão 🔗 para conectar elementos")
    print("   3. Clique em um elemento para editar suas propriedades")
    print("   4. Use o botão 🗑️ para deletar elementos")
    print(f"\n⚠️  Pressione Ctrl+C para parar o servidor\n")
    print("=" * 70)

    # Abre o navegador em uma thread separada
    browser_thread = threading.Thread(target=open_browser, args=(port,))
    browser_thread.daemon = True
    browser_thread.start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor encerrado pelo usuário")
        httpd.server_close()


if __name__ == '__main__':
    run_server()
