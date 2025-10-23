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
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .metric-status {
            font-size: 20px;
        }

        .metric-positive {
            color: #48bb78;
        }

        .metric-negative {
            color: #f56565;
        }

        .metric-neutral {
            color: #ecc94b;
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
            margin-bottom: 20px;
            color: #2d3748;
            font-size: 18px;
            font-weight: 700;
        }

        .element-library {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .element-category {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .category-header {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 10px;
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            border-radius: 8px;
            margin-bottom: 4px;
            border-left: 4px solid #4299e1;
        }

        .category-icon {
            font-size: 18px;
        }

        .category-name {
            font-size: 13px;
            font-weight: 700;
            color: #2d3748;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .library-element {
            padding: 10px 12px;
            border-radius: 8px;
            cursor: move;
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.2s;
            border: 2px solid rgba(255, 255, 255, 0.3);
            position: relative;
            overflow: hidden;
        }

        .library-element::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, transparent 0%, rgba(255, 255, 255, 0.2) 100%);
            opacity: 0;
            transition: opacity 0.2s;
        }

        .library-element:hover::before {
            opacity: 1;
        }

        .library-element:hover {
            transform: translateX(4px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            border-color: rgba(255, 255, 255, 0.5);
        }

        .library-element:active {
            transform: scale(0.98) translateX(0);
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
            transform-origin: 0 0;
            transition: transform 0.2s ease-out;
        }

        .zoom-controls {
            position: absolute;
            bottom: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
            z-index: 1000;
        }

        .zoom-btn {
            width: 44px;
            height: 44px;
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: bold;
            color: #4a5568;
            transition: all 0.2s;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .zoom-btn:hover {
            background: #4299e1;
            color: white;
            border-color: #4299e1;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(66, 153, 225, 0.3);
        }

        .zoom-btn:active {
            transform: translateY(0);
        }

        .zoom-level {
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            padding: 0 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: 600;
            color: #4a5568;
            min-width: 70px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .connection-drag-line {
            stroke: #f56565;
            stroke-width: 3;
            fill: none;
            stroke-dasharray: 8, 4;
            animation: dash 0.5s linear infinite;
            pointer-events: none;
        }

        @keyframes dash {
            to {
                stroke-dashoffset: -12;
            }
        }

        .element-menu-popup {
            position: absolute;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            padding: 12px;
            z-index: 10000;
            max-height: 400px;
            overflow-y: auto;
            min-width: 220px;
            animation: popupAppear 0.2s ease-out;
        }

        @keyframes popupAppear {
            from {
                opacity: 0;
                transform: scale(0.9);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }

        .element-menu-popup h4 {
            font-size: 14px;
            color: #2d3748;
            margin-bottom: 12px;
            padding: 0 8px;
            font-weight: 700;
        }

        .popup-category {
            margin-bottom: 16px;
        }

        .popup-category:last-child {
            margin-bottom: 0;
        }

        .popup-category-header {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 6px 8px;
            background: #f7fafc;
            border-radius: 6px;
            margin-bottom: 6px;
        }

        .popup-category-icon {
            font-size: 14px;
        }

        .popup-category-name {
            font-size: 11px;
            font-weight: 700;
            color: #4a5568;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .popup-element-item {
            padding: 8px 10px;
            border-radius: 6px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.15s;
            margin-bottom: 3px;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }

        .popup-element-item:hover {
            transform: translateX(4px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-color: rgba(255, 255, 255, 0.5);
        }

        .funnel-element.drag-hover {
            box-shadow: 0 0 0 4px rgba(245, 101, 101, 0.5);
            transform: scale(1.02);
        }

        .funnel-element {
            position: absolute;
            width: 220px;
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

        .connection-point.left {
            left: -8px;
            top: 50%;
            transform: translateY(-50%);
        }

        .connection-point.right {
            right: -8px;
            top: 50%;
            transform: translateY(-50%);
        }

        .connection-point.left:hover {
            background: #4299e1;
            transform: translateY(-50%) scale(1.4);
            box-shadow: 0 0 10px rgba(66, 153, 225, 0.5);
        }

        .connection-point.right:hover {
            background: #4299e1;
            transform: translateY(-50%) scale(1.4);
            box-shadow: 0 0 10px rgba(66, 153, 225, 0.5);
        }

        .connection-point.connecting {
            background: #f56565;
            border-color: #f56565;
            animation: pulse 0.8s infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: translateY(-50%) scale(1); }
            50% { transform: translateY(-50%) scale(1.3); }
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

        .form-input.error {
            border-color: #f56565;
            background-color: #fff5f5;
        }

        .form-input.warning {
            border-color: #ecc94b;
            background-color: #fffff0;
        }

        .form-input.success {
            border-color: #48bb78;
            background-color: #f0fff4;
        }

        .form-help {
            display: block;
            font-size: 12px;
            color: #718096;
            margin-top: 4px;
            line-height: 1.4;
        }

        .form-help::before {
            content: "↳ ";
            color: #a0aec0;
        }

        .validation-message {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            margin-top: 6px;
            padding: 8px;
            border-radius: 4px;
        }

        .validation-message.error {
            color: #c53030;
            background-color: #fff5f5;
        }

        .validation-message.warning {
            color: #975a16;
            background-color: #fffff0;
        }

        .validation-message.success {
            color: #276749;
            background-color: #f0fff4;
        }

        .benchmark-box {
            background: #f7fafc;
            padding: 12px;
            border-radius: 8px;
            font-size: 12px;
            margin-top: 12px;
            border-left: 3px solid #4299e1;
        }

        .benchmark-box h4 {
            font-size: 13px;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 8px;
        }

        .benchmark-item {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 4px;
            color: #4a5568;
        }

        .benchmark-item:last-child {
            margin-bottom: 0;
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

        .traffic-mode-toggle {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            background: #f7fafc;
            padding: 8px;
            border-radius: 8px;
        }

        .mode-option {
            flex: 1;
            padding: 10px;
            border-radius: 6px;
            cursor: pointer;
            text-align: center;
            font-weight: 600;
            font-size: 13px;
            transition: all 0.2s;
            border: 2px solid transparent;
        }

        .mode-option:hover {
            transform: translateY(-1px);
        }

        .mode-option.active {
            background: white;
            border-color: #4299e1;
            color: #4299e1;
            box-shadow: 0 2px 8px rgba(66, 153, 225, 0.2);
        }

        .mode-option.inactive {
            background: transparent;
            color: #718096;
        }

        .empty-state {
            color: #a0aec0;
            text-align: center;
            padding: 40px 20px;
            font-size: 14px;
        }

        .color-trafego { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .color-retargeting { background: linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%); }
        .color-landing { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        .color-captura { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #2d3748; }
        .color-vsl { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
        .color-vendas { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
        .color-checkout { background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); }
        .color-obrigado { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); color: #2d3748; }
        .color-squeeze { background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%); color: #2d3748; }
        .color-email { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
        .color-sequencia { background: linear-gradient(135deg, #5f72bd 0%, #9b23ea 100%); }
        .color-whatsapp { background: linear-gradient(135deg, #25d366 0%, #128c7e 100%); }
        .color-quiz { background: linear-gradient(135deg, #ff9a56 0%, #ff6a88 100%); }
        .color-video { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
        .color-webinar { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
        .color-countdown { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); }
        .color-call { background: linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%); }
        .color-upsell { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #2d3748; }
        .color-downsell { background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%); color: #2d3748; }
        .color-membros { background: linear-gradient(135deg, #8e44ad 0%, #c0392b 100%); }

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

        const ELEMENT_CATEGORIES = [
            {
                name: 'Tráfego',
                icon: '🎯',
                elements: [
                    { type: 'trafego', name: 'Tráfego Pago', icon: '🎯', color: 'color-trafego' },
                    { type: 'retargeting', name: 'Retargeting', icon: '🔄', color: 'color-retargeting' }
                ]
            },
            {
                name: 'Páginas',
                icon: '📄',
                elements: [
                    { type: 'landing', name: 'Landing Page', icon: '🚀', color: 'color-landing' },
                    { type: 'captura', name: 'Página de Captura', icon: '📝', color: 'color-captura' },
                    { type: 'vsl', name: 'VSL (Video Sales Letter)', icon: '🎬', color: 'color-vsl' },
                    { type: 'vendas', name: 'Página de Vendas', icon: '💎', color: 'color-vendas' },
                    { type: 'checkout', name: 'Checkout', icon: '💳', color: 'color-checkout' },
                    { type: 'obrigado', name: 'Página Obrigado', icon: '🎉', color: 'color-obrigado' },
                    { type: 'squeeze', name: 'Squeeze Page', icon: '🎁', color: 'color-squeeze' }
                ]
            },
            {
                name: 'Relacionamento',
                icon: '💬',
                elements: [
                    { type: 'email', name: 'Email', icon: '✉️', color: 'color-email' },
                    { type: 'sequencia', name: 'Sequência Email', icon: '📧', color: 'color-sequencia' },
                    { type: 'whatsapp', name: 'WhatsApp', icon: '📱', color: 'color-whatsapp' }
                ]
            },
            {
                name: 'Engajamento',
                icon: '🎬',
                elements: [
                    { type: 'quiz', name: 'Quiz/Enquete', icon: '📊', color: 'color-quiz' },
                    { type: 'video', name: 'Vídeo', icon: '▶️', color: 'color-video' },
                    { type: 'webinar', name: 'Webinar', icon: '🎥', color: 'color-webinar' },
                    { type: 'call', name: 'Call/Consulta', icon: '📞', color: 'color-call' }
                ]
            },
            {
                name: 'Conversão',
                icon: '💰',
                elements: [
                    { type: 'countdown', name: 'Countdown', icon: '⏰', color: 'color-countdown' },
                    { type: 'upsell', name: 'Upsell', icon: '⬆️', color: 'color-upsell' },
                    { type: 'downsell', name: 'Downsell', icon: '⬇️', color: 'color-downsell' }
                ]
            },
            {
                name: 'Pós-Venda',
                icon: '🎁',
                elements: [
                    { type: 'membros', name: 'Área de Membros', icon: '📚', color: 'color-membros' }
                ]
            }
        ];

        const ELEMENT_TYPES = ELEMENT_CATEGORIES.flatMap(cat => cat.elements);

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
            const [zoomLevel, setZoomLevel] = useState(1);
            const [isDraggingConnection, setIsDraggingConnection] = useState(false);
            const [dragConnectionStart, setDragConnectionStart] = useState(null);
            const [dragConnectionEnd, setDragConnectionEnd] = useState(null);
            const [hoveredElement, setHoveredElement] = useState(null);
            const [showElementMenu, setShowElementMenu] = useState(false);
            const [elementMenuPosition, setElementMenuPosition] = useState({ x: 0, y: 0 });
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
                let totalVisitors = 0;

                Object.values(metricsMap).forEach(el => {
                    if (el.calculatedMetrics) {
                        totalRevenue += el.calculatedMetrics.revenue;
                        totalSales += el.calculatedMetrics.leads;

                        // Soma investimento apenas dos elementos raiz
                        if (el.calculatedMetrics.cost > 0) {
                            totalInvestment += el.calculatedMetrics.cost;
                        }

                        // Conta visitantes dos elementos de tráfego
                        if (el.type === 'trafego') {
                            totalVisitors += el.clicks || 0;
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
                    investment: totalInvestment,
                    visitors: totalVisitors
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
                    investment: 0,
                    impressions: 0,
                    clicks: 0,
                    ctr: 0,
                    cpm: 0,
                    trafficMode: 'absolute', // 'absolute' ou 'metrics'
                    pageViewRate: 100,
                    conversionRate: 0,
                    price: 0,
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
                // Arrasto de conexão
                if (isDraggingConnection) {
                    handleConnectionDragMove(e);
                    return;
                }

                // Arrasto de elemento
                if (!draggingElement) return;

                // Só começa a arrastar se mover mais de 5 pixels
                const deltaX = Math.abs(e.clientX - mouseDownPos.x);
                const deltaY = Math.abs(e.clientY - mouseDownPos.y);

                if (!isDragging && (deltaX > 5 || deltaY > 5)) {
                    setIsDragging(true);
                }

                if (isDragging) {
                    const rect = canvasRef.current.getBoundingClientRect();
                    const x = (e.clientX - rect.left) / zoomLevel - dragOffset.x;
                    const y = (e.clientY - rect.top) / zoomLevel - dragOffset.y;

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
                // Fecha o menu popup se estiver aberto
                if (showElementMenu) {
                    setShowElementMenu(false);
                    return;
                }

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

                const element = elements.find(el => el.id === elementId);
                if (!element) return;

                const rect = canvasRef.current.getBoundingClientRect();

                // Inicia o arrasto da conexão
                setIsDraggingConnection(true);
                setConnectingFrom(elementId);
                setDragConnectionStart({
                    x: element.x + 220, // direita do elemento
                    y: element.y + 60   // meio do elemento
                });
                setDragConnectionEnd({
                    x: (e.clientX - rect.left) / zoomLevel,
                    y: (e.clientY - rect.top) / zoomLevel
                });
            };

            const handleConnectionDragMove = (e) => {
                if (!isDraggingConnection) return;

                const rect = canvasRef.current.getBoundingClientRect();
                setDragConnectionEnd({
                    x: (e.clientX - rect.left) / zoomLevel,
                    y: (e.clientY - rect.top) / zoomLevel
                });
            };

            const handleConnectionDragEnd = (e) => {
                if (!isDraggingConnection) return;

                e.stopPropagation();

                // Se soltou sobre um elemento com hover, cria a conexão
                if (hoveredElement && hoveredElement !== connectingFrom) {
                    const connectionExists = connections.some(
                        conn => conn.from === connectingFrom && conn.to === hoveredElement
                    );

                    if (!connectionExists) {
                        setConnections([...connections, {
                            id: Date.now(),
                            from: connectingFrom,
                            to: hoveredElement,
                            conversion: 10
                        }]);
                    }

                    // Reset states
                    setIsDraggingConnection(false);
                    setDragConnectionStart(null);
                    setDragConnectionEnd(null);
                    setConnectingFrom(null);
                    setHoveredElement(null);
                } else {
                    // Se não soltou sobre um elemento, mostra o menu
                    const rect = canvasRef.current.getBoundingClientRect();
                    const menuX = (e.clientX - rect.left) / zoomLevel;
                    const menuY = (e.clientY - rect.top) / zoomLevel;

                    setElementMenuPosition({
                        x: menuX * zoomLevel,
                        y: menuY * zoomLevel
                    });
                    setShowElementMenu(true);

                    // Não reseta connectingFrom aqui, será resetado quando selecionar um elemento
                    setIsDraggingConnection(false);
                    setDragConnectionStart(null);
                    setDragConnectionEnd(null);
                    setHoveredElement(null);
                }
            };

            const handleElementHover = (elementId, isHovering) => {
                if (isDraggingConnection) {
                    setHoveredElement(isHovering ? elementId : null);
                }
            };

            const handleElementMenuSelect = (elementType) => {
                const newElement = {
                    id: Date.now(),
                    type: elementType.type,
                    name: elementType.name,
                    icon: elementType.icon,
                    color: elementType.color,
                    x: Math.max(0, elementMenuPosition.x / zoomLevel - 110),
                    y: Math.max(0, elementMenuPosition.y / zoomLevel - 60),
                    investment: 0,
                    impressions: 0,
                    clicks: 0,
                    ctr: 0,
                    cpm: 0,
                    trafficMode: 'absolute', // 'absolute' ou 'metrics'
                    pageViewRate: 100,
                    conversionRate: 0,
                    price: 0,
                    url: '',
                    description: '',
                    generatesRevenue: false
                };

                setElements([...elements, newElement]);

                // Cria a conexão com o novo elemento
                if (connectingFrom) {
                    setConnections([...connections, {
                        id: Date.now() + 1,
                        from: connectingFrom,
                        to: newElement.id,
                        conversion: 0
                    }]);
                }

                setShowElementMenu(false);
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

            const validateValue = (property, value) => {
                const numValue = parseFloat(value) || 0;

                // Validações para percentuais
                if (['conversionRate', 'pageViewRate'].includes(property)) {
                    if (numValue < 0) return { valid: false, type: 'error', message: '❌ O valor não pode ser negativo' };
                    if (numValue > 100) return { valid: false, type: 'error', message: '❌ O valor não pode ser maior que 100%' };

                    // Warnings para taxas de conversão
                    if (property === 'conversionRate') {
                        if (numValue < 1) return { valid: true, type: 'warning', message: '⚠️ Taxa muito baixa. Típico: 5-15%' };
                        if (numValue > 50) return { valid: true, type: 'warning', message: '⚠️ Taxa muito alta. Verifique se está correto' };
                        if (numValue >= 10 && numValue <= 30) return { valid: true, type: 'success', message: '✅ Ótima taxa de conversão!' };
                    }
                }

                // Validações para valores monetários
                if (['investment', 'price'].includes(property)) {
                    if (numValue < 0) return { valid: false, type: 'error', message: '❌ O valor não pode ser negativo' };
                    if (numValue > 1000000) return { valid: true, type: 'warning', message: '⚠️ Valor muito alto. Confirme se está correto' };
                }

                // Validações para impressões e cliques
                if (property === 'impressions' && numValue < 1) {
                    return { valid: true, type: 'warning', message: '⚠️ Configure as impressões esperadas' };
                }
                if (property === 'clicks' && numValue < 1) {
                    return { valid: true, type: 'warning', message: '⚠️ Configure os cliques esperados' };
                }

                return { valid: true, type: null, message: null };
            };

            const updateElementProperty = (property, value) => {
                setElements(elements.map(el => {
                    if (el.id === selectedElement) {
                        // Se for um campo numérico
                        if (['investment', 'impressions', 'clicks', 'pageViewRate', 'conversionRate', 'price', 'ctr', 'cpm'].includes(property)) {
                            // Se o valor estiver vazio, permite vazio (não força 0)
                            if (value === '' || value === null || value === undefined) {
                                return { ...el, [property]: 0 };
                            }
                            const numValue = parseFloat(value);
                            const updated = { ...el, [property]: numValue };

                            // Cálculos automáticos para modo de tráfego
                            if (el.type === 'trafego') {
                                if (el.trafficMode === 'metrics') {
                                    // Sempre recalcula impressões se temos CPM e investimento
                                    if (updated.cpm > 0 && updated.investment > 0) {
                                        updated.impressions = Math.round((updated.investment / updated.cpm) * 1000);
                                    }
                                    // Sempre recalcula cliques se temos CTR e impressões
                                    if (updated.ctr > 0 && updated.impressions > 0) {
                                        updated.clicks = Math.round((updated.impressions * updated.ctr) / 100);
                                    }
                                } else if (el.trafficMode === 'absolute') {
                                    // Calcula CTR automaticamente
                                    if (updated.impressions > 0 && updated.clicks >= 0) {
                                        updated.ctr = parseFloat(((updated.clicks / updated.impressions) * 100).toFixed(2));
                                    }
                                    // Calcula CPM automaticamente
                                    if (updated.impressions > 0 && updated.investment >= 0) {
                                        updated.cpm = parseFloat(((updated.investment / updated.impressions) * 1000).toFixed(2));
                                    }
                                }
                            }

                            return updated;
                        }
                        // Se mudou o modo de tráfego, recalcula tudo
                        if (property === 'trafficMode') {
                            const updated = { ...el, [property]: value };

                            if (value === 'metrics') {
                                // Recalcula com base nas métricas
                                if (updated.cpm > 0 && updated.investment > 0) {
                                    updated.impressions = Math.round((updated.investment / updated.cpm) * 1000);
                                }
                                if (updated.ctr > 0 && updated.impressions > 0) {
                                    updated.clicks = Math.round((updated.impressions * updated.ctr) / 100);
                                }
                            } else if (value === 'absolute') {
                                // Recalcula as métricas
                                if (updated.impressions > 0 && updated.clicks >= 0) {
                                    updated.ctr = parseFloat(((updated.clicks / updated.impressions) * 100).toFixed(2));
                                }
                                if (updated.impressions > 0 && updated.investment >= 0) {
                                    updated.cpm = parseFloat(((updated.investment / updated.impressions) * 1000).toFixed(2));
                                }
                            }

                            return updated;
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
                            // Se o valor estiver vazio, permite vazio (converte para 0)
                            if (value === '' || value === null || value === undefined) {
                                return { ...conn, [property]: 0 };
                            }
                            return { ...conn, [property]: parseFloat(value) };
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

                // Elemento origem - saída pela direita
                const fromX = fromEl.x + 220; // largura do elemento
                const fromY = fromEl.y + 60; // meio do elemento

                // Elemento destino - entrada pela esquerda
                const toX = toEl.x;
                const toY = toEl.y + 60; // meio do elemento

                // Distância horizontal entre os elementos
                const midX = (fromX + toX) / 2;

                // Cria uma curva suave horizontal
                return `M ${fromX} ${fromY} C ${midX} ${fromY}, ${midX} ${toY}, ${toX} ${toY}`;
            };

            const handleZoomIn = () => {
                setZoomLevel(prev => Math.min(prev + 0.1, 2));
            };

            const handleZoomOut = () => {
                setZoomLevel(prev => Math.max(prev - 0.1, 0.5));
            };

            const handleZoomReset = () => {
                setZoomLevel(1);
            };

            const dashboardMetrics = getDashboardMetrics();
            const metricsMap = calculateMetrics();
            const selectedElementData = elements.find(el => el.id === selectedElement);

            return (
                <div className="app">
                    <div className="dashboard">
                        <div className="metric">
                            <div className="metric-label">🎯 Visitantes Iniciais</div>
                            <div className="metric-value">
                                {dashboardMetrics.visitors.toLocaleString('pt-BR')}
                            </div>
                        </div>
                        <div className="metric">
                            <div className="metric-label">💰 Investimento Total</div>
                            <div className="metric-value">
                                R$ {dashboardMetrics.investment.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                            </div>
                        </div>
                        <div className="metric">
                            <div className="metric-label">🛒 Conversões Esperadas</div>
                            <div className="metric-value">
                                {dashboardMetrics.sales.toLocaleString('pt-BR')}
                            </div>
                        </div>
                        <div className="metric">
                            <div className="metric-label">💵 Receita Projetada</div>
                            <div className="metric-value">
                                R$ {dashboardMetrics.revenue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                            </div>
                        </div>
                        <div className="metric">
                            <div className="metric-label">📈 ROI Projetado</div>
                            <div className="metric-value">
                                <span className={dashboardMetrics.roi >= 100 ? 'metric-positive' : dashboardMetrics.roi >= 0 ? 'metric-neutral' : 'metric-negative'}>
                                    {dashboardMetrics.roi >= 100 ? '✅' : dashboardMetrics.roi >= 0 ? '⚠️' : '❌'}
                                </span>
                                {dashboardMetrics.roi.toFixed(1)}%
                            </div>
                        </div>
                    </div>

                    <div className="main-content">
                        <div className="sidebar">
                            <h3>📦 Elementos do Funil</h3>
                            <div className="element-library">
                                {ELEMENT_CATEGORIES.map((category, idx) => (
                                    <div key={idx} className="element-category">
                                        <div className="category-header">
                                            <span className="category-icon">{category.icon}</span>
                                            <span className="category-name">{category.name}</span>
                                        </div>
                                        {category.elements.map(type => (
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
                                ))}
                            </div>
                        </div>

                        <div
                            className="canvas-container"
                            ref={canvasRef}
                            onMouseMove={handleMouseMove}
                            onMouseUp={(e) => {
                                if (isDraggingConnection) {
                                    handleConnectionDragEnd(e);
                                } else {
                                    handleMouseUp();
                                }
                            }}
                            onClick={handleCanvasClick}
                        >
                            <div className="zoom-controls">
                                <button className="zoom-btn" onClick={handleZoomOut} title="Diminuir zoom">−</button>
                                <div className="zoom-level">{Math.round(zoomLevel * 100)}%</div>
                                <button className="zoom-btn" onClick={handleZoomIn} title="Aumentar zoom">+</button>
                                <button className="zoom-btn" onClick={handleZoomReset} title="Resetar zoom">⊙</button>
                            </div>
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
                                <g transform={`scale(${zoomLevel})`}>
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
                                    {isDraggingConnection && dragConnectionStart && dragConnectionEnd && (
                                        <line
                                            className="connection-drag-line"
                                            x1={dragConnectionStart.x}
                                            y1={dragConnectionStart.y}
                                            x2={dragConnectionEnd.x}
                                            y2={dragConnectionEnd.y}
                                        />
                                    )}
                                </g>
                            </svg>

                            <div className="canvas" style={{ transform: `scale(${zoomLevel})` }}>
                                {elements.map(element => {
                                    const metrics = metricsMap[element.id]?.calculatedMetrics || {};
                                    return (
                                        <div
                                            key={element.id}
                                            className={`funnel-element ${element.color} ${
                                                selectedElement === element.id ? 'selected' : ''
                                            } ${isDragging && draggingElement === element.id ? 'dragging' : ''} ${
                                                hoveredElement === element.id ? 'drag-hover' : ''
                                            }`}
                                            style={{
                                                left: element.x,
                                                top: element.y
                                            }}
                                            onClick={(e) => handleElementClick(e, element)}
                                            onMouseDown={(e) => handleElementMouseDown(e, element)}
                                            onMouseEnter={() => handleElementHover(element.id, true)}
                                            onMouseLeave={() => handleElementHover(element.id, false)}
                                        >
                                            <div
                                                className={`connection-point left ${connectingFrom === element.id ? 'connecting' : ''}`}
                                                onMouseDown={(e) => {
                                                    e.stopPropagation();
                                                    e.preventDefault();
                                                }}
                                                title="Entrada - Arraste uma conexão até aqui"
                                            />

                                            <div className="element-header">
                                                <span className="element-icon">{element.icon}</span>
                                                <span className="element-title">{element.name}</span>
                                                <div className="element-actions">
                                                    <button
                                                        className="element-btn"
                                                        onMouseDown={(e) => handleConnectionStart(e, element.id)}
                                                        title="Segurar e arrastar para conectar"
                                                    >
                                                        🔗
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
                                                            <span>👁️ {(element.impressions || 0).toLocaleString('pt-BR')} impressões</span>
                                                        </div>
                                                        <div className="metric-row">
                                                            <span>👆 {(element.clicks || 0).toLocaleString('pt-BR')} cliques ({element.impressions > 0 ? ((element.clicks / element.impressions) * 100).toFixed(1) : 0}%)</span>
                                                        </div>
                                                        <div style={{borderTop: '1px solid rgba(255,255,255,0.2)', margin: '6px 0', paddingTop: '6px'}}>
                                                            <div className="metric-row">
                                                                <span>💰 R$ {(metrics.investment || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
                                                            </div>
                                                            <div className="metric-row">
                                                                <span>💵 R$ {(metrics.costPerLead || 0).toFixed(2)}/clique</span>
                                                            </div>
                                                        </div>
                                                    </>
                                                ) : element.type === 'landing' ? (
                                                    // Métricas para Landing Page
                                                    <>
                                                        <div className="metric-row">
                                                            <span>👥 {metrics.visits?.toLocaleString('pt-BR') || 0} visitantes</span>
                                                        </div>
                                                        <div className="metric-row">
                                                            <span>✅ {metrics.leads?.toLocaleString('pt-BR') || 0} conversões ({element.conversionRate || 0}%)</span>
                                                        </div>
                                                        <div style={{borderTop: '1px solid rgba(255,255,255,0.2)', margin: '6px 0', paddingTop: '6px'}}>
                                                            <div className="metric-row">
                                                                <span>📊 Taxa: {element.conversionRate || 0}%</span>
                                                            </div>
                                                        </div>
                                                    </>
                                                ) : (
                                                    // Métricas para outros elementos
                                                    <>
                                                        <div className="metric-row">
                                                            <span>👥 {metrics.visits?.toLocaleString('pt-BR') || 0} pessoas</span>
                                                        </div>
                                                        <div className="metric-row">
                                                            <span>{metrics.revenue > 0 ? '🛒' : '✅'} {metrics.leads?.toLocaleString('pt-BR') || 0} {metrics.revenue > 0 ? 'vendas' : 'conversões'} ({element.conversionRate || 0}%)</span>
                                                        </div>
                                                        {metrics.revenue > 0 && (
                                                            <div style={{borderTop: '1px solid rgba(255,255,255,0.2)', margin: '6px 0', paddingTop: '6px'}}>
                                                                <div className="metric-row">
                                                                    <span>💰 R$ {element.price?.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) || '0,00'} cada</span>
                                                                </div>
                                                                <div className="metric-row">
                                                                    <span>💵 R$ {(metrics.revenue || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })} total</span>
                                                                </div>
                                                            </div>
                                                        )}
                                                    </>
                                                )}
                                            </div>

                                            <div
                                                className={`connection-point right ${connectingFrom === element.id ? 'connecting' : ''}`}
                                                onMouseDown={(e) => handleConnectionStart(e, element.id)}
                                                title="Saída - Segurar e arrastar para conectar"
                                            />
                                        </div>
                                    );
                                })}
                            </div>

                            {showElementMenu && (
                                <div
                                    className="element-menu-popup"
                                    style={{
                                        left: elementMenuPosition.x,
                                        top: elementMenuPosition.y,
                                        transform: `scale(${1 / zoomLevel})`
                                    }}
                                    onClick={(e) => e.stopPropagation()}
                                >
                                    <h4>➕ Adicionar Elemento</h4>
                                    {ELEMENT_CATEGORIES.map((category, idx) => (
                                        <div key={idx} className="popup-category">
                                            <div className="popup-category-header">
                                                <span className="popup-category-icon">{category.icon}</span>
                                                <span className="popup-category-name">{category.name}</span>
                                            </div>
                                            {category.elements.map(type => (
                                                <div
                                                    key={type.type}
                                                    className={`popup-element-item ${type.color}`}
                                                    onClick={() => handleElementMenuSelect(type)}
                                                >
                                                    <span className="element-icon">{type.icon}</span>
                                                    <span>{type.name}</span>
                                                </div>
                                            ))}
                                        </div>
                                    ))}
                                </div>
                            )}
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
                                            <div className="traffic-mode-toggle">
                                                <div
                                                    className={`mode-option ${selectedElementData.trafficMode === 'absolute' ? 'active' : 'inactive'}`}
                                                    onClick={() => updateElementProperty('trafficMode', 'absolute')}
                                                >
                                                    📊 Números Absolutos
                                                </div>
                                                <div
                                                    className={`mode-option ${selectedElementData.trafficMode === 'metrics' ? 'active' : 'inactive'}`}
                                                    onClick={() => updateElementProperty('trafficMode', 'metrics')}
                                                >
                                                    📈 CTR & CPM
                                                </div>
                                            </div>

                                            <div className="form-group">
                                                <label className="form-label">💰 Investimento Planejado (R$)</label>
                                                <input
                                                    type="number"
                                                    className={`form-input ${validateValue('investment', selectedElementData.investment).type || ''}`}
                                                    value={selectedElementData.investment === 0 ? '' : selectedElementData.investment}
                                                    onChange={(e) => updateElementProperty('investment', e.target.value)}
                                                    placeholder="Ex: 10000"
                                                    step="0.01"
                                                />
                                                <small className="form-help">Quanto você pretende investir em anúncios?</small>
                                                {validateValue('investment', selectedElementData.investment).message && (
                                                    <div className={`validation-message ${validateValue('investment', selectedElementData.investment).type}`}>
                                                        {validateValue('investment', selectedElementData.investment).message}
                                                    </div>
                                                )}
                                            </div>

                                            {selectedElementData.trafficMode === 'absolute' ? (
                                                <>
                                                    <div className="form-group">
                                                        <label className="form-label">👁️ Impressões Esperadas</label>
                                                        <input
                                                            type="number"
                                                            className={`form-input ${validateValue('impressions', selectedElementData.impressions).type || ''}`}
                                                            value={selectedElementData.impressions === 0 ? '' : selectedElementData.impressions}
                                                            onChange={(e) => updateElementProperty('impressions', e.target.value)}
                                                            placeholder="Ex: 100000"
                                                        />
                                                        <small className="form-help">Quantas pessoas verão seu anúncio?</small>
                                                    </div>
                                                    <div className="form-group">
                                                        <label className="form-label">👆 Cliques Esperados</label>
                                                        <input
                                                            type="number"
                                                            className={`form-input ${validateValue('clicks', selectedElementData.clicks).type || ''}`}
                                                            value={selectedElementData.clicks === 0 ? '' : selectedElementData.clicks}
                                                            onChange={(e) => updateElementProperty('clicks', e.target.value)}
                                                            placeholder="Ex: 2000"
                                                        />
                                                        <small className="form-help">Quantas pessoas clicarão? (CTR calculado: {selectedElementData.ctr}%)</small>
                                                    </div>
                                                </>
                                            ) : (
                                                <>
                                                    <div className="form-group">
                                                        <label className="form-label">💵 CPM - Custo por Mil (R$)</label>
                                                        <input
                                                            type="number"
                                                            className="form-input"
                                                            value={selectedElementData.cpm === 0 ? '' : selectedElementData.cpm}
                                                            onChange={(e) => updateElementProperty('cpm', e.target.value)}
                                                            placeholder="Ex: 25"
                                                            step="0.01"
                                                        />
                                                        <small className="form-help">Quanto custa 1000 impressões? (Impressões calculadas: {selectedElementData.impressions.toLocaleString('pt-BR')})</small>
                                                    </div>
                                                    <div className="form-group">
                                                        <label className="form-label">📊 CTR - Taxa de Cliques (%)</label>
                                                        <input
                                                            type="number"
                                                            className="form-input"
                                                            value={selectedElementData.ctr === 0 ? '' : selectedElementData.ctr}
                                                            onChange={(e) => updateElementProperty('ctr', e.target.value)}
                                                            placeholder="Ex: 2"
                                                            step="0.01"
                                                        />
                                                        <small className="form-help">% de pessoas que clicam no anúncio (Cliques calculados: {selectedElementData.clicks.toLocaleString('pt-BR')})</small>
                                                    </div>
                                                </>
                                            )}

                                            {selectedElementData.clicks > 0 && (
                                                <div className="benchmark-box" style={{background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', border: 'none'}}>
                                                    <h4 style={{color: 'white'}}>👥 TRÁFEGO PARA PRÓXIMA ETAPA</h4>
                                                    <div className="benchmark-item" style={{fontSize: '16px', fontWeight: 'bold'}}>
                                                        <span>• {selectedElementData.clicks.toLocaleString('pt-BR')} pessoas chegarão na próxima página</span>
                                                    </div>
                                                    {selectedElementData.impressions > 0 && (
                                                        <>
                                                            <div className="benchmark-item">
                                                                <span>• CTR: {selectedElementData.ctr > 0 ? selectedElementData.ctr : ((selectedElementData.clicks / selectedElementData.impressions) * 100).toFixed(2)}%</span>
                                                            </div>
                                                            <div className="benchmark-item">
                                                                <span>• CPM: R$ {selectedElementData.cpm > 0 ? selectedElementData.cpm.toFixed(2) : ((selectedElementData.investment / selectedElementData.impressions) * 1000).toFixed(2)}</span>
                                                            </div>
                                                            <div className="benchmark-item">
                                                                <span>• CPC: R$ {(selectedElementData.investment / selectedElementData.clicks).toFixed(2)}</span>
                                                            </div>
                                                        </>
                                                    )}
                                                </div>
                                            )}

                                            {(() => {
                                                const metrics = calculateMetrics()[selectedElementData.id]?.calculatedMetrics;
                                                return metrics && (
                                                    <div className="benchmark-box">
                                                        <h4>📊 MÉTRICAS CALCULADAS</h4>
                                                        <div className="benchmark-item">
                                                            <span>• CPM: R$ {metrics.cpm.toFixed(2)}</span>
                                                        </div>
                                                        <div className="benchmark-item">
                                                            <span>• Custo/Clique: R$ {metrics.costPerLead.toFixed(2)}</span>
                                                        </div>
                                                        <div className="benchmark-item">
                                                            <span>• CTR: {metrics.ctr.toFixed(2)}%</span>
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
                                                <label className="form-label">🔗 URL da Landing Page (opcional)</label>
                                                <input
                                                    type="text"
                                                    className="form-input"
                                                    value={selectedElementData.url || ''}
                                                    onChange={(e) => updateElementProperty('url', e.target.value)}
                                                    placeholder="https://meusite.com/cadastro"
                                                />
                                                <small className="form-help">URL da sua página de captura</small>
                                            </div>
                                            <div className="form-group">
                                                <label className="form-label">📝 Descrição (opcional)</label>
                                                <input
                                                    type="text"
                                                    className="form-input"
                                                    value={selectedElementData.description || ''}
                                                    onChange={(e) => updateElementProperty('description', e.target.value)}
                                                    placeholder="Ex: Página de cadastro para webinar gratuito"
                                                />
                                                <small className="form-help">Descreva o objetivo desta página</small>
                                            </div>
                                            <div className="form-group">
                                                <label className="form-label">✅ Taxa de Conversão (%)</label>
                                                <input
                                                    type="number"
                                                    className={`form-input ${validateValue('conversionRate', selectedElementData.conversionRate).type || ''}`}
                                                    value={selectedElementData.conversionRate === 0 ? '' : selectedElementData.conversionRate}
                                                    onChange={(e) => updateElementProperty('conversionRate', e.target.value)}
                                                    min="0"
                                                    max="100"
                                                    step="0.1"
                                                    placeholder="Ex: 15"
                                                />
                                                <small className="form-help">% de visitantes que preencherão o formulário</small>
                                                {validateValue('conversionRate', selectedElementData.conversionRate).message && (
                                                    <div className={`validation-message ${validateValue('conversionRate', selectedElementData.conversionRate).type}`}>
                                                        {validateValue('conversionRate', selectedElementData.conversionRate).message}
                                                    </div>
                                                )}
                                            </div>
                                            <div className="benchmark-box">
                                                <h4>📋 BENCHMARKS DO MERCADO</h4>
                                                <div className="benchmark-item">
                                                    <span>• 5-15%: Bom para captura de leads</span>
                                                </div>
                                                <div className="benchmark-item">
                                                    <span>• 15-30%: Excelente conversão!</span>
                                                </div>
                                                <div className="benchmark-item">
                                                    <span>• 30%+: Landing otimizada profissionalmente</span>
                                                </div>
                                            </div>
                                        </>
                                    )}

                                    {/* Campos para outros elementos (Email, Video, Webinar, etc) */}
                                    {selectedElementData.type !== 'trafego' && selectedElementData.type !== 'landing' && (
                                        <>
                                            <div className="form-group">
                                                <label className="form-label">🔗 URL (opcional)</label>
                                                <input
                                                    type="text"
                                                    className="form-input"
                                                    value={selectedElementData.url || ''}
                                                    onChange={(e) => updateElementProperty('url', e.target.value)}
                                                    placeholder="https://meusite.com/checkout"
                                                />
                                                <small className="form-help">Link da página deste elemento</small>
                                            </div>
                                            <div className="form-group">
                                                <label className="form-label">📝 Descrição (opcional)</label>
                                                <input
                                                    type="text"
                                                    className="form-input"
                                                    value={selectedElementData.description || ''}
                                                    onChange={(e) => updateElementProperty('description', e.target.value)}
                                                    placeholder="Ex: Página de vendas do produto principal"
                                                />
                                                <small className="form-help">Descreva este elemento do funil</small>
                                            </div>
                                            <div className="form-group">
                                                <label className="form-label">✅ Taxa de Conversão (%)</label>
                                                <input
                                                    type="number"
                                                    className={`form-input ${validateValue('conversionRate', selectedElementData.conversionRate).type || ''}`}
                                                    value={selectedElementData.conversionRate === 0 ? '' : selectedElementData.conversionRate}
                                                    onChange={(e) => updateElementProperty('conversionRate', e.target.value)}
                                                    min="0"
                                                    max="100"
                                                    step="0.1"
                                                    placeholder="Ex: 10"
                                                />
                                                <small className="form-help">% de pessoas que completarão a ação desejada</small>
                                                {validateValue('conversionRate', selectedElementData.conversionRate).message && (
                                                    <div className={`validation-message ${validateValue('conversionRate', selectedElementData.conversionRate).type}`}>
                                                        {validateValue('conversionRate', selectedElementData.conversionRate).message}
                                                    </div>
                                                )}
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
                                                <>
                                                    <div className="form-group">
                                                        <label className="form-label">💵 Preço do Produto (R$)</label>
                                                        <input
                                                            type="number"
                                                            className={`form-input ${validateValue('price', selectedElementData.price).type || ''}`}
                                                            value={selectedElementData.price === 0 ? '' : selectedElementData.price}
                                                            onChange={(e) => updateElementProperty('price', e.target.value)}
                                                            step="0.01"
                                                            placeholder="Ex: 197.00"
                                                        />
                                                        <small className="form-help">Valor que será cobrado por venda</small>
                                                        {validateValue('price', selectedElementData.price).message && (
                                                            <div className={`validation-message ${validateValue('price', selectedElementData.price).type}`}>
                                                                {validateValue('price', selectedElementData.price).message}
                                                            </div>
                                                        )}
                                                    </div>
                                                    {(() => {
                                                        const metrics = calculateMetrics()[selectedElementData.id]?.calculatedMetrics;
                                                        return metrics && metrics.revenue > 0 && (
                                                            <div className="benchmark-box">
                                                                <h4>📊 PREVISÃO DE VENDAS</h4>
                                                                <div className="benchmark-item">
                                                                    <span>• Visitantes: {metrics.visits?.toLocaleString('pt-BR') || 0}</span>
                                                                </div>
                                                                <div className="benchmark-item">
                                                                    <span>• Vendas: {metrics.leads?.toLocaleString('pt-BR') || 0} ({selectedElementData.conversionRate || 0}%)</span>
                                                                </div>
                                                                <div className="benchmark-item">
                                                                    <span>• Receita: R$ {metrics.revenue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
                                                                </div>
                                                            </div>
                                                        );
                                                    })()}
                                                </>
                                            )}
                                            {selectedElementData.type === 'captura' && (
                                                <div className="benchmark-box">
                                                    <h4>📋 BENCHMARKS - PÁGINA DE CAPTURA</h4>
                                                    <div className="benchmark-item">
                                                        <span>• 20-40%: Taxa típica de conversão</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 40-60%: Muito boa!</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 60%+: Excepcional!</span>
                                                    </div>
                                                </div>
                                            )}
                                            {selectedElementData.type === 'vsl' && (
                                                <div className="benchmark-box">
                                                    <h4>📋 BENCHMARKS - VSL</h4>
                                                    <div className="benchmark-item">
                                                        <span>• 40-60%: Taxa de play</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 30-50%: Assistem até o final</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 5-15%: Conversão típica de VSL</span>
                                                    </div>
                                                </div>
                                            )}
                                            {selectedElementData.type === 'vendas' && (
                                                <div className="benchmark-box">
                                                    <h4>📋 BENCHMARKS - PÁGINA DE VENDAS</h4>
                                                    <div className="benchmark-item">
                                                        <span>• 2-5%: Tráfego frio</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 5-15%: Tráfego qualificado</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 15%+: Tráfego ultra-qualificado</span>
                                                    </div>
                                                </div>
                                            )}
                                            {selectedElementData.type === 'squeeze' && (
                                                <div className="benchmark-box">
                                                    <h4>📋 BENCHMARKS - SQUEEZE PAGE</h4>
                                                    <div className="benchmark-item">
                                                        <span>• 30-50%: Taxa típica</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 50-70%: Muito boa!</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 70%+: Squeeze page otimizada!</span>
                                                    </div>
                                                </div>
                                            )}
                                            {selectedElementData.type === 'checkout' && (
                                                <div className="benchmark-box">
                                                    <h4>📋 BENCHMARKS - CHECKOUT</h4>
                                                    <div className="benchmark-item">
                                                        <span>• 1-3%: Típico e-commerce</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 5-10%: Checkout otimizado</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 20%+: Tráfego ultra-qualificado</span>
                                                    </div>
                                                </div>
                                            )}
                                            {selectedElementData.type === 'upsell' && (
                                                <div className="benchmark-box">
                                                    <h4>📋 BENCHMARKS - UPSELL</h4>
                                                    <div className="benchmark-item">
                                                        <span>• 10-20%: Taxa típica de aceitação</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 20-40%: Oferta bem alinhada</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 40%+: Upsell irresistível!</span>
                                                    </div>
                                                </div>
                                            )}
                                            {selectedElementData.type === 'downsell' && (
                                                <div className="benchmark-box">
                                                    <h4>📋 BENCHMARKS - DOWNSELL</h4>
                                                    <div className="benchmark-item">
                                                        <span>• 20-30%: Taxa típica de aceitação</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 30-50%: Boa oferta alternativa</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 50%+: Downsell muito atrativo!</span>
                                                    </div>
                                                </div>
                                            )}
                                            {selectedElementData.type === 'whatsapp' && (
                                                <div className="benchmark-box">
                                                    <h4>📋 BENCHMARKS - WHATSAPP</h4>
                                                    <div className="benchmark-item">
                                                        <span>• 40-60%: Taxa de abertura</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 15-25%: Taxa de resposta</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 60%+: Excelente engajamento!</span>
                                                    </div>
                                                </div>
                                            )}
                                            {selectedElementData.type === 'sequencia' && (
                                                <div className="benchmark-box">
                                                    <h4>📋 BENCHMARKS - SEQUÊNCIA EMAIL</h4>
                                                    <div className="benchmark-item">
                                                        <span>• 15-25%: Taxa de abertura</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 2-5%: Taxa de clique</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 10-20%: Conversão final da sequência</span>
                                                    </div>
                                                </div>
                                            )}
                                            {selectedElementData.type === 'quiz' && (
                                                <div className="benchmark-box">
                                                    <h4>📋 BENCHMARKS - QUIZ</h4>
                                                    <div className="benchmark-item">
                                                        <span>• 30-50%: Taxa de conclusão do quiz</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 50-70%: Taxa de captura de email</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• Aumenta engajamento em 2-3x</span>
                                                    </div>
                                                </div>
                                            )}
                                            {selectedElementData.type === 'video' && (
                                                <div className="benchmark-box">
                                                    <h4>📋 BENCHMARKS - VÍDEO/VSL</h4>
                                                    <div className="benchmark-item">
                                                        <span>• 40-60%: Taxa de play</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 30-50%: Assistem até o final</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 5-15%: Conversão típica de VSL</span>
                                                    </div>
                                                </div>
                                            )}
                                            {selectedElementData.type === 'webinar' && (
                                                <div className="benchmark-box">
                                                    <h4>📋 BENCHMARKS - WEBINAR</h4>
                                                    <div className="benchmark-item">
                                                        <span>• 30-50%: Taxa de comparecimento</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 10-25%: Conversão em vendas</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 40%+: Webinars de alta conversão</span>
                                                    </div>
                                                </div>
                                            )}
                                            {selectedElementData.type === 'countdown' && (
                                                <div className="benchmark-box">
                                                    <h4>📋 BENCHMARKS - COUNTDOWN</h4>
                                                    <div className="benchmark-item">
                                                        <span>• Aumenta conversão em 20-40%</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• Reduz tempo de decisão em 60%</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• Ideal: 24-72h de urgência</span>
                                                    </div>
                                                </div>
                                            )}
                                            {selectedElementData.type === 'call' && (
                                                <div className="benchmark-box">
                                                    <h4>📋 BENCHMARKS - CALL/CONSULTA</h4>
                                                    <div className="benchmark-item">
                                                        <span>• 20-40%: Taxa de agendamento</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 60-80%: Comparecimento na call</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 30-50%: Fechamento na call</span>
                                                    </div>
                                                </div>
                                            )}
                                            {selectedElementData.type === 'membros' && (
                                                <div className="benchmark-box">
                                                    <h4>📋 BENCHMARKS - ÁREA MEMBROS</h4>
                                                    <div className="benchmark-item">
                                                        <span>• 70-90%: Taxa de acesso inicial</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 40-60%: Conclusão do conteúdo</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 80-95%: Retenção mensal</span>
                                                    </div>
                                                </div>
                                            )}
                                            {selectedElementData.type === 'retargeting' && (
                                                <div className="benchmark-box">
                                                    <h4>📋 BENCHMARKS - RETARGETING</h4>
                                                    <div className="benchmark-item">
                                                        <span>• 2-5%: CTR típico de anúncios</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 10-30%: Conversão de retargeting</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• CPC 50-70% menor que cold traffic</span>
                                                    </div>
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
                                            value={connections.find(c => c.id === selectedConnection)?.conversion === 0 ? '' : connections.find(c => c.id === selectedConnection)?.conversion}
                                            onChange={(e) => updateConnectionProperty('conversion', e.target.value)}
                                            step="0.1"
                                            placeholder="Ex: 10"
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
