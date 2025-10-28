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
            min-width: 3000px;
            min-height: 3000px;
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

        .connection-point.top {
            top: -8px;
            left: 50%;
            transform: translateX(-50%);
        }

        .connection-point.right {
            right: -8px;
            top: 50%;
            transform: translateY(-50%);
        }

        .connection-point.bottom {
            bottom: -8px;
            left: 50%;
            transform: translateX(-50%);
        }

        .connection-point.left {
            left: -8px;
            top: 50%;
            transform: translateY(-50%);
        }

        .connection-point.top:hover {
            background: #4299e1;
            transform: translateX(-50%) scale(1.4);
            box-shadow: 0 0 10px rgba(66, 153, 225, 0.5);
        }

        .connection-point.right:hover {
            background: #4299e1;
            transform: translateY(-50%) scale(1.4);
            box-shadow: 0 0 10px rgba(66, 153, 225, 0.5);
        }

        .connection-point.bottom:hover {
            background: #4299e1;
            transform: translateX(-50%) scale(1.4);
            box-shadow: 0 0 10px rgba(66, 153, 225, 0.5);
        }

        .connection-point.left:hover {
            background: #4299e1;
            transform: translateY(-50%) scale(1.4);
            box-shadow: 0 0 10px rgba(66, 153, 225, 0.5);
        }

        .connection-point.connecting.top,
        .connection-point.connecting.bottom {
            background: #f56565;
            border-color: #f56565;
            animation: pulseHorizontal 0.8s infinite;
        }

        .connection-point.connecting.left,
        .connection-point.connecting.right {
            background: #f56565;
            border-color: #f56565;
            animation: pulseVertical 0.8s infinite;
        }

        @keyframes pulseVertical {
            0%, 100% { transform: translateY(-50%) scale(1); }
            50% { transform: translateY(-50%) scale(1.3); }
        }

        @keyframes pulseHorizontal {
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
        .color-ecommerce { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
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

        /* Settings Panel Styles */
        .settings-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
            animation: fadeIn 0.2s;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .settings-panel {
            background: white;
            border-radius: 16px;
            width: 90%;
            max-width: 1200px;
            max-height: 90vh;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            animation: slideInUp 0.3s ease-out;
        }

        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .settings-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 24px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .settings-header h2 {
            font-size: 24px;
            font-weight: 700;
            margin: 0;
        }

        .settings-close-btn {
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            font-size: 24px;
            width: 40px;
            height: 40px;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }

        .settings-close-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: scale(1.05);
        }

        .settings-content {
            flex: 1;
            overflow-y: auto;
            padding: 30px;
        }

        .settings-section {
            margin-bottom: 40px;
        }

        .settings-section:last-child {
            margin-bottom: 0;
        }

        .settings-section-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e2e8f0;
        }

        .settings-section-icon {
            font-size: 28px;
        }

        .settings-section-title {
            font-size: 20px;
            font-weight: 700;
            color: #2d3748;
        }

        .settings-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }

        .settings-card {
            background: #f7fafc;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            transition: all 0.2s;
        }

        .settings-card:hover {
            border-color: #cbd5e0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }

        .settings-card-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 16px;
        }

        .settings-card-icon {
            font-size: 24px;
        }

        .settings-card-title {
            font-size: 16px;
            font-weight: 700;
            color: #2d3748;
            margin: 0;
        }

        .settings-input-group {
            margin-bottom: 16px;
        }

        .settings-input-group:last-child {
            margin-bottom: 0;
        }

        .settings-label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 6px;
        }

        .settings-input {
            width: 100%;
            padding: 10px 12px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.2s;
        }

        .settings-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .settings-footer {
            padding: 20px 30px;
            border-top: 2px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #f7fafc;
        }

        .settings-btn {
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            border: none;
        }

        .settings-btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .settings-btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }

        .settings-btn-secondary {
            background: #e2e8f0;
            color: #4a5568;
        }

        .settings-btn-secondary:hover {
            background: #cbd5e0;
        }

        .settings-icon-btn {
            background: transparent;
            border: none;
            cursor: pointer;
            font-size: 20px;
            padding: 8px;
            border-radius: 6px;
            transition: all 0.2s;
        }

        .settings-icon-btn:hover {
            background: rgba(102, 126, 234, 0.1);
        }

        .category-editor {
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .category-editor-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 16px;
        }

        .color-palette {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 8px;
            margin-top: 10px;
            margin-bottom: 15px;
        }

        .color-palette-item {
            width: 100%;
            height: 40px;
            border-radius: 8px;
            cursor: pointer;
            border: 3px solid transparent;
            transition: all 0.2s;
            position: relative;
        }

        .color-palette-item:hover {
            transform: scale(1.1);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }

        .color-palette-item.selected {
            border-color: #2d3748;
            box-shadow: 0 0 0 2px white, 0 0 0 4px #2d3748;
        }

        .color-picker-section {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .color-picker-label {
            font-size: 13px;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 4px;
        }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useRef, useEffect } = React;

        // Função para carregar configurações do sistema
        const loadSystemConfig = () => {
            const saved = localStorage.getItem('systemConfig');
            if (saved) {
                return JSON.parse(saved);
            }
            return null;
        };

        // Carrega configurações ou usa padrão
        const systemConfig = loadSystemConfig();

        const ELEMENT_CATEGORIES_DEFAULT = [
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
                    { type: 'squeeze', name: 'Squeeze Page', icon: '🎁', color: 'color-squeeze' },
                    { type: 'ecommerce', name: 'E-commerce', icon: '🛒', color: 'color-ecommerce' }
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

        // Usa configurações personalizadas se existirem, senão usa padrão
        const ELEMENT_CATEGORIES = systemConfig?.categories || ELEMENT_CATEGORIES_DEFAULT;
        const ELEMENT_TYPES = ELEMENT_CATEGORIES.flatMap(cat => cat.elements);

        // Mapeamento de cores padrão para cada tipo de elemento
        const DEFAULT_COLORS = {
            // Tráfego - Roxo/Gradiente
            'trafego': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'retargeting': 'linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%)',

            // Páginas - Tons variados
            'landing': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            'captura': 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
            'vsl': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
            'vendas': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            'checkout': 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
            'obrigado': 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
            'squeeze': 'linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%)',
            'ecommerce': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',

            // Relacionamento - Azul/Roxo
            'email': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            'sequencia': 'linear-gradient(135deg, #5f72bd 0%, #9b23ea 100%)',
            'whatsapp': 'linear-gradient(135deg, #25d366 0%, #128c7e 100%)',

            // Engajamento - Laranja/Amarelo
            'quiz': 'linear-gradient(135deg, #ff9a56 0%, #ff6a88 100%)',
            'video': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
            'webinar': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            'call': 'linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%)',

            // Conversão - Verde/Amarelo
            'countdown': 'linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%)',
            'upsell': 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
            'downsell': 'linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%)',

            // Pós-Venda - Roxo escuro
            'membros': 'linear-gradient(135deg, #8e44ad 0%, #c0392b 100%)'
        };

        // Verifica se o texto é claro ou escuro para contraste
        const needsDarkText = (color) => {
            const lightBackgrounds = ['captura', 'obrigado', 'squeeze', 'upsell', 'downsell'];
            return lightBackgrounds.includes(color);
        };

        // Paleta de cores predefinidas para seleção rápida
        const COLOR_PALETTE = [
            { name: 'Roxo Imperial', gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
            { name: 'Laranja Quente', gradient: 'linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%)' },
            { name: 'Rosa Vibrante', gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
            { name: 'Ciano Suave', gradient: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)' },
            { name: 'Verde Menta', gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' },
            { name: 'Dourado Solar', gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' },
            { name: 'Azul Oceano', gradient: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)' },
            { name: 'Pêssego', gradient: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)' },
            { name: 'Amarelo Brilhante', gradient: 'linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%)' },
            { name: 'Azul Claro', gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
            { name: 'Roxo Místico', gradient: 'linear-gradient(135deg, #5f72bd 0%, #9b23ea 100%)' },
            { name: 'Verde WhatsApp', gradient: 'linear-gradient(135deg, #25d366 0%, #128c7e 100%)' },
            { name: 'Coral Tropical', gradient: 'linear-gradient(135deg, #ff9a56 0%, #ff6a88 100%)' },
            { name: 'Azul Turquesa', gradient: 'linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%)' },
            { name: 'Vermelho Intenso', gradient: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%)' },
            { name: 'Roxo Escuro', gradient: 'linear-gradient(135deg, #8e44ad 0%, #c0392b 100%)' },
            { name: 'Verde Esmeralda', gradient: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)' },
            { name: 'Azul Índigo', gradient: 'linear-gradient(135deg, #4e54c8 0%, #8f94fb 100%)' }
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

        function FunnelBuilder({ funnelId, onBack }) {
            const [elements, setElements] = useState([]);
            const [connections, setConnections] = useState([]);
            const [currentFunnel, setCurrentFunnel] = useState(null);

            // Carrega o funil específico
            React.useEffect(() => {
                if (funnelId) {
                    const funnels = JSON.parse(localStorage.getItem('funnels') || '[]');
                    const funnel = funnels.find(f => f.id === funnelId);
                    if (funnel) {
                        setCurrentFunnel(funnel);
                        setElements(funnel.elements || []);
                        setConnections(funnel.connections || []);
                    }
                }
            }, [funnelId]);

            // Auto-salva quando elementos ou conexões mudam
            React.useEffect(() => {
                if (funnelId && currentFunnel) {
                    const funnels = JSON.parse(localStorage.getItem('funnels') || '[]');
                    const updated = funnels.map(f => {
                        if (f.id === funnelId) {
                            return { ...f, elements, connections };
                        }
                        return f;
                    });
                    localStorage.setItem('funnels', JSON.stringify(updated));
                }
            }, [elements, connections, funnelId, currentFunnel]);
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
            const [connectionFromSide, setConnectionFromSide] = useState(null);
            const [hoveredElement, setHoveredElement] = useState(null);
            const [showElementMenu, setShowElementMenu] = useState(false);
            const [elementMenuPosition, setElementMenuPosition] = useState({ x: 0, y: 0 });
            const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
            const [isPanning, setIsPanning] = useState(false);
            const [panStart, setPanStart] = useState({ x: 0, y: 0 });
            const canvasRef = useRef(null);

            const calculateMetrics = () => {
                const elementMap = {};
                elements.forEach(el => {
                    elementMap[el.id] = {
                        ...el,
                        childConnections: [],
                        incomingTraffic: [] // Array para acumular tráfego de múltiplas fontes
                    };
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

                    // Retargeting com métricas próprias ignora tráfego de entrada (funciona como fonte independente)
                    const isRetargetingWithMetrics = element.type === 'retargeting' && element.clicks > 0;

                    // Se recebe tráfego de entrada E não é retargeting com métricas, acumula no array
                    if (inputTraffic !== null && !isRetargetingWithMetrics) {
                        element.incomingTraffic.push({
                            traffic: inputTraffic,
                            investment: parentInvestment
                        });
                        // Não calcula ainda, apenas acumula
                        return;
                    }

                    let visits = 0;  // Pessoas que chegaram
                    let pageViews = 0;  // Pessoas que visualizaram a página
                    let leads = 0;  // Pessoas convertidas
                    let investment = 0;
                    let cpm = 0;
                    let ctr = 0;
                    let costPerLead = 0;

                    // Se é elemento raiz (sem inputTraffic), calcula a partir de impressões/cliques
                    if ((element.type === 'trafego' || element.type === 'retargeting') && element.clicks > 0) {
                        // Para retargeting, usa investment ou retargetingInvestment
                        investment = element.type === 'retargeting'
                            ? (element.investment || element.retargetingInvestment || 0)
                            : (element.investment || 0);

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
                    } else if (element.incomingTraffic.length > 0) {
                        // Se recebe tráfego de múltiplas fontes, soma tudo
                        visits = element.incomingTraffic.reduce((sum, t) => sum + t.traffic, 0);
                        investment = element.incomingTraffic.reduce((sum, t) => sum + t.investment, 0);

                        // Aplica taxa de visualização de página
                        const pageViewRate = element.pageViewRate || 100;
                        pageViews = Math.round(visits * (pageViewRate / 100));

                        // Aplica taxa de conversão do elemento
                        const conversionRate = element.conversionRate || 0;
                        leads = Math.round(pageViews * (conversionRate / 100));
                    }

                    const price = element.price || 0;

                    // Só gera receita se o elemento tiver a flag generatesRevenue ativada
                    let revenue = element.generatesRevenue ? (leads * price) : 0;

                    // Adiciona receita do Order Bump se estiver habilitado
                    let orderBumpRevenue = 0;
                    let orderBumpSales = 0;
                    if (element.hasOrderBump && element.generatesRevenue) {
                        const orderBumpPrice = element.orderBumpPrice || 0;
                        const orderBumpConversion = element.orderBumpConversion || 0;
                        orderBumpSales = Math.round(leads * (orderBumpConversion / 100));
                        orderBumpRevenue = orderBumpSales * orderBumpPrice;
                        revenue += orderBumpRevenue;
                    }

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
                        costPerLead,
                        orderBumpSales,
                        orderBumpRevenue
                    };

                    // Propaga para elementos filhos usando a taxa de conversão da conexão
                    element.childConnections.forEach(conn => {
                        const childElement = elementMap[conn.to];
                        const conversionRate = conn.conversion || 0;
                        let childTraffic = 0;

                        // Se o elemento filho é um Downsell, envia os NÃO convertidos
                        if (childElement && childElement.type === 'downsell') {
                            // Downsell recebe quem NÃO converteu (pageViews - leads)
                            const nonConverted = pageViews - leads;
                            childTraffic = Math.round(nonConverted * (conversionRate / 100));
                        } else {
                            // Elementos normais recebem os convertidos (leads)
                            childTraffic = Math.round(leads * (conversionRate / 100));
                        }

                        calculateForElement(conn.to, childTraffic, investment);
                    });
                };

                // FASE 1: Propaga o tráfego dos elementos raiz
                elements.forEach(el => {
                    const hasParent = connections.some(conn => conn.to === el.id);
                    // Retargeting com métricas próprias (clicks > 0) funciona como raiz, mesmo com conexões de entrada
                    const isRetargetingWithMetrics = el.type === 'retargeting' && el.clicks > 0;

                    if (!hasParent || isRetargetingWithMetrics) {
                        calculateForElement(el.id);
                    }
                });

                // FASE 2: Calcula métricas para todos os elementos que receberam tráfego
                Object.values(elementMap).forEach(element => {
                    if (element.incomingTraffic.length > 0 && !element.calculatedMetrics) {
                        // Soma todo o tráfego recebido
                        const totalVisits = element.incomingTraffic.reduce((sum, t) => sum + t.traffic, 0);
                        const totalInvestment = element.incomingTraffic.reduce((sum, t) => sum + t.investment, 0);

                        // Aplica taxa de visualização de página
                        const pageViewRate = element.pageViewRate || 100;
                        const pageViews = Math.round(totalVisits * (pageViewRate / 100));

                        // Aplica taxa de conversão do elemento
                        const conversionRate = element.conversionRate || 0;
                        const leads = Math.round(pageViews * (conversionRate / 100));

                        const price = element.price || 0;

                        // Só gera receita se o elemento tiver a flag generatesRevenue ativada
                        let revenue = element.generatesRevenue ? (leads * price) : 0;

                        // Adiciona receita do Order Bump se estiver habilitado
                        let orderBumpRevenue = 0;
                        let orderBumpSales = 0;
                        if (element.hasOrderBump && element.generatesRevenue) {
                            const orderBumpPrice = element.orderBumpPrice || 0;
                            const orderBumpConversion = element.orderBumpConversion || 0;
                            orderBumpSales = Math.round(leads * (orderBumpConversion / 100));
                            orderBumpRevenue = orderBumpSales * orderBumpPrice;
                            revenue += orderBumpRevenue;
                        }

                        element.calculatedMetrics = {
                            visits: totalVisits,
                            pageViews,
                            leads,
                            revenue,
                            profit: revenue,
                            cost: 0,
                            investment: totalInvestment,
                            cpm: 0,
                            ctr: 0,
                            costPerLead: 0,
                            orderBumpSales,
                            orderBumpRevenue
                        };

                        // Propaga para elementos filhos
                        element.childConnections.forEach(conn => {
                            const childElement = elementMap[conn.to];
                            const conversionRate = conn.conversion || 0;
                            let childTraffic = 0;

                            // Se o elemento filho é um Downsell, envia os NÃO convertidos
                            if (childElement && childElement.type === 'downsell') {
                                const nonConverted = pageViews - leads;
                                childTraffic = Math.round(nonConverted * (conversionRate / 100));
                            } else {
                                childTraffic = Math.round(leads * (conversionRate / 100));
                            }

                            if (childTraffic > 0) {
                                if (!childElement.incomingTraffic) {
                                    childElement.incomingTraffic = [];
                                }
                                childElement.incomingTraffic.push({
                                    traffic: childTraffic,
                                    investment: totalInvestment
                                });
                            }
                        });
                    }
                });

                // FASE 3: Processa elementos que ainda não foram calculados (podem ter recebido tráfego na fase 2)
                let maxIterations = 10; // Previne loop infinito
                let hasUncalculated = true;

                while (hasUncalculated && maxIterations > 0) {
                    hasUncalculated = false;
                    maxIterations--;

                    Object.values(elementMap).forEach(element => {
                        if (element.incomingTraffic.length > 0 && !element.calculatedMetrics) {
                            hasUncalculated = true;

                            // Copia a lógica de cálculo
                            const totalVisits = element.incomingTraffic.reduce((sum, t) => sum + t.traffic, 0);
                            const totalInvestment = element.incomingTraffic.reduce((sum, t) => sum + t.investment, 0);
                            const pageViewRate = element.pageViewRate || 100;
                            const pageViews = Math.round(totalVisits * (pageViewRate / 100));
                            const conversionRate = element.conversionRate || 0;
                            const leads = Math.round(pageViews * (conversionRate / 100));
                            const price = element.price || 0;
                            let revenue = element.generatesRevenue ? (leads * price) : 0;
                            let orderBumpRevenue = 0;
                            let orderBumpSales = 0;

                            if (element.hasOrderBump && element.generatesRevenue) {
                                const orderBumpPrice = element.orderBumpPrice || 0;
                                const orderBumpConversion = element.orderBumpConversion || 0;
                                orderBumpSales = Math.round(leads * (orderBumpConversion / 100));
                                orderBumpRevenue = orderBumpSales * orderBumpPrice;
                                revenue += orderBumpRevenue;
                            }

                            element.calculatedMetrics = {
                                visits: totalVisits,
                                pageViews,
                                leads,
                                revenue,
                                profit: revenue,
                                cost: 0,
                                investment: totalInvestment,
                                cpm: 0,
                                ctr: 0,
                                costPerLead: 0,
                                orderBumpSales,
                                orderBumpRevenue
                            };

                            // Propaga para elementos filhos
                            element.childConnections.forEach(conn => {
                                const childElement = elementMap[conn.to];
                                const childConversionRate = conn.conversion || 0;
                                let childTraffic = 0;

                                if (childElement && childElement.type === 'downsell') {
                                    const nonConverted = pageViews - leads;
                                    childTraffic = Math.round(nonConverted * (childConversionRate / 100));
                                } else {
                                    childTraffic = Math.round(leads * (childConversionRate / 100));
                                }

                                if (childTraffic > 0) {
                                    if (!childElement.incomingTraffic) {
                                        childElement.incomingTraffic = [];
                                    }
                                    childElement.incomingTraffic.push({
                                        traffic: childTraffic,
                                        investment: totalInvestment
                                    });
                                }
                            });
                        }
                    });
                }

                return elementMap;
            };

            const getDashboardMetrics = () => {
                const metricsMap = calculateMetrics();
                let totalRevenue = 0;
                let totalProfit = 0;
                let totalSales = 0;
                let totalActualSales = 0; // Vendas reais (apenas elementos que geram receita)
                let totalInvestment = 0;
                let totalVisitors = 0;

                Object.values(metricsMap).forEach(el => {
                    if (el.calculatedMetrics) {
                        totalRevenue += el.calculatedMetrics.revenue;
                        totalSales += el.calculatedMetrics.leads;

                        // Conta vendas apenas de elementos que geram receita
                        if (el.generatesRevenue && el.calculatedMetrics.leads > 0) {
                            totalActualSales += el.calculatedMetrics.leads;
                        }

                        // Soma investimento apenas dos elementos raiz
                        if (el.calculatedMetrics.cost > 0) {
                            totalInvestment += el.calculatedMetrics.cost;
                        }

                        // Soma investimento de retargeting
                        if (el.type === 'retargeting' && el.retargetingInvestment > 0) {
                            totalInvestment += el.retargetingInvestment;
                        }

                        // Conta visitantes dos elementos de tráfego
                        if (el.type === 'trafego') {
                            totalVisitors += el.clicks || 0;
                        }
                    }
                });

                totalProfit = totalRevenue - totalInvestment;
                const roi = totalInvestment > 0 ? ((totalProfit / totalInvestment) * 100) : 0;
                // CAC baseado apenas em vendas reais (elementos que geram receita)
                const cac = totalActualSales > 0 ? (totalInvestment / totalActualSales) : 0;

                return {
                    revenue: totalRevenue,
                    profit: totalProfit,
                    cac: cac,
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
                // Pan do canvas
                if (isPanning) {
                    const deltaX = e.clientX - panStart.x;
                    const deltaY = e.clientY - panStart.y;
                    setPanOffset({
                        x: panOffset.x + deltaX,
                        y: panOffset.y + deltaY
                    });
                    setPanStart({ x: e.clientX, y: e.clientY });
                    return;
                }

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
                    const x = (e.clientX - rect.left - panOffset.x) / zoomLevel - dragOffset.x;
                    const y = (e.clientY - rect.top - panOffset.y) / zoomLevel - dragOffset.y;

                    setElements(elements.map(el =>
                        el.id === draggingElement
                            ? { ...el, x: x, y: y }
                            : el
                    ));
                }
            };

            const handleMouseUp = () => {
                setDraggingElement(null);
                setIsDragging(false);
                setIsPanning(false);
            };

            const handleCanvasMouseDown = (e) => {
                // Se clicar diretamente no canvas-container (fundo), inicia o pan
                if (e.target === e.currentTarget ||
                    e.target.classList.contains('canvas') ||
                    e.target.classList.contains('connections')) {
                    setIsPanning(true);
                    setPanStart({ x: e.clientX, y: e.clientY });
                }
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

            // Função helper para calcular posição do ponto de conexão
            const getConnectionPointPosition = (element, side) => {
                const width = 220;  // largura do elemento
                const height = 120; // altura aproximada do elemento

                switch(side) {
                    case 'top':
                        return { x: element.x + width / 2, y: element.y };
                    case 'right':
                        return { x: element.x + width, y: element.y + height / 2 };
                    case 'bottom':
                        return { x: element.x + width / 2, y: element.y + height };
                    case 'left':
                        return { x: element.x, y: element.y + height / 2 };
                    default:
                        return { x: element.x + width, y: element.y + height / 2 };
                }
            };

            const handleConnectionStart = (e, elementId, side = 'right') => {
                e.stopPropagation();
                e.preventDefault();

                const element = elements.find(el => el.id === elementId);
                if (!element) return;

                const rect = canvasRef.current.getBoundingClientRect();
                const startPos = getConnectionPointPosition(element, side);

                // Inicia o arrasto da conexão
                setIsDraggingConnection(true);
                setConnectingFrom(elementId);
                setConnectionFromSide(side);
                setDragConnectionStart(startPos);
                setDragConnectionEnd({
                    x: (e.clientX - rect.left - panOffset.x) / zoomLevel,
                    y: (e.clientY - rect.top - panOffset.y) / zoomLevel
                });
            };

            const handleConnectionDragMove = (e) => {
                if (!isDraggingConnection) return;

                const rect = canvasRef.current.getBoundingClientRect();
                setDragConnectionEnd({
                    x: (e.clientX - rect.left - panOffset.x) / zoomLevel,
                    y: (e.clientY - rect.top - panOffset.y) / zoomLevel
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
                        // Encontra o elemento de destino para calcular qual lado está mais próximo
                        const toElement = elements.find(el => el.id === hoveredElement);
                        let toSide = 'left'; // padrão

                        if (toElement && dragConnectionEnd) {
                            // Calcula qual lado está mais próximo do ponto onde o mouse está
                            const width = 220;
                            const height = 120;
                            const centerX = toElement.x + width / 2;
                            const centerY = toElement.y + height / 2;
                            const dx = dragConnectionEnd.x - centerX;
                            const dy = dragConnectionEnd.y - centerY;

                            // Determina o lado mais próximo baseado em qual direção predomina
                            if (Math.abs(dx) > Math.abs(dy)) {
                                toSide = dx > 0 ? 'right' : 'left';
                            } else {
                                toSide = dy > 0 ? 'bottom' : 'top';
                            }
                        }

                        setConnections([...connections, {
                            id: Date.now(),
                            from: connectingFrom,
                            to: hoveredElement,
                            fromSide: connectionFromSide,
                            toSide: toSide,
                            conversion: 10
                        }]);
                    }

                    // Reset states
                    setIsDraggingConnection(false);
                    setDragConnectionStart(null);
                    setDragConnectionEnd(null);
                    setConnectingFrom(null);
                    setConnectionFromSide(null);
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
                    x: elementMenuPosition.x / zoomLevel - 110,
                    y: elementMenuPosition.y / zoomLevel - 60,
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
                console.log('updateElementProperty chamada:', property, value, 'elemento:', selectedElement);
                setElements(elements.map(el => {
                    if (el.id === selectedElement) {
                        console.log('Atualizando elemento:', el.id, property, value);
                        // Se for um campo numérico
                        if (['investment', 'impressions', 'clicks', 'pageViewRate', 'conversionRate', 'price', 'ctr', 'cpm', 'orderBumpPrice', 'orderBumpConversion', 'addToCartRate', 'retargetingInvestment'].includes(property)) {
                            // Se o valor estiver vazio, permite vazio (não força 0)
                            if (value === '' || value === null || value === undefined) {
                                return { ...el, [property]: 0 };
                            }
                            const numValue = parseFloat(value);
                            const updated = { ...el, [property]: numValue };

                            // Cálculos automáticos para modo de tráfego (trafego e retargeting)
                            if (el.type === 'trafego' || el.type === 'retargeting') {
                                // Para retargeting, usa investment ou retargetingInvestment
                                const inv = el.type === 'retargeting' ? (updated.investment || updated.retargetingInvestment) : updated.investment;

                                if (el.trafficMode === 'metrics') {
                                    // Sempre recalcula impressões se temos CPM e investimento
                                    if (updated.cpm > 0 && inv > 0) {
                                        updated.impressions = Math.round((inv / updated.cpm) * 1000);
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
                                    if (updated.impressions > 0 && inv >= 0) {
                                        updated.cpm = parseFloat(((inv / updated.impressions) * 1000).toFixed(2));
                                    }
                                }
                            }

                            return updated;
                        }
                        // Se mudou o modo de tráfego, recalcula tudo
                        if (property === 'trafficMode') {
                            const updated = { ...el, [property]: value };

                            // Para retargeting, usa investment ou retargetingInvestment
                            const inv = el.type === 'retargeting' ? (updated.investment || updated.retargetingInvestment) : updated.investment;

                            if (value === 'metrics') {
                                // Recalcula com base nas métricas
                                if (updated.cpm > 0 && inv > 0) {
                                    updated.impressions = Math.round((inv / updated.cpm) * 1000);
                                }
                                if (updated.ctr > 0 && updated.impressions > 0) {
                                    updated.clicks = Math.round((updated.impressions * updated.ctr) / 100);
                                }
                            } else if (value === 'absolute') {
                                // Recalcula as métricas
                                if (updated.impressions > 0 && updated.clicks >= 0) {
                                    updated.ctr = parseFloat(((updated.clicks / updated.impressions) * 100).toFixed(2));
                                }
                                if (updated.impressions > 0 && inv >= 0) {
                                    updated.cpm = parseFloat(((inv / updated.impressions) * 1000).toFixed(2));
                                }
                            }

                            return updated;
                        }
                        // Se for booleano, mantém como está
                        if (property === 'generatesRevenue' || property === 'hasOrderBump') {
                            return { ...el, [property]: value };
                        }
                        // Caso contrário, mantém como string
                        const updated = { ...el, [property]: value };
                        console.log('Elemento atualizado:', updated);
                        return updated;
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

            const deleteConnection = (connectionId) => {
                if (confirm('Tem certeza que deseja deletar esta conexão?')) {
                    setConnections(connections.filter(conn => conn.id !== connectionId));
                    setSelectedConnection(null); // Deseleciona após deletar
                }
            };

            const getConnectionPath = (fromId, toId, fromSide = 'right', toSide = 'left') => {
                const fromEl = elements.find(el => el.id === fromId);
                const toEl = elements.find(el => el.id === toId);

                if (!fromEl || !toEl) return '';

                // Calcula posição do ponto de saída
                const fromPos = getConnectionPointPosition(fromEl, fromSide);
                const fromX = fromPos.x;
                const fromY = fromPos.y;

                // Calcula posição do ponto de entrada
                const toPos = getConnectionPointPosition(toEl, toSide);
                const toX = toPos.x;
                const toY = toPos.y;

                // Cria curva suave baseada na direção da conexão
                const dx = toX - fromX;
                const dy = toY - fromY;
                const absDx = Math.abs(dx);
                const absDy = Math.abs(dy);

                // Define o tamanho da curva baseado na distância
                const curveOffset = Math.min(50, Math.max(absDx, absDy) / 4);

                // Pontos de controle baseados nos lados
                let cp1x = fromX, cp1y = fromY;
                let cp2x = toX, cp2y = toY;

                // Ajusta pontos de controle baseado no lado de saída
                if (fromSide === 'right') cp1x = fromX + curveOffset;
                else if (fromSide === 'left') cp1x = fromX - curveOffset;
                else if (fromSide === 'top') cp1y = fromY - curveOffset;
                else if (fromSide === 'bottom') cp1y = fromY + curveOffset;

                // Ajusta pontos de controle baseado no lado de entrada
                if (toSide === 'right') cp2x = toX + curveOffset;
                else if (toSide === 'left') cp2x = toX - curveOffset;
                else if (toSide === 'top') cp2y = toY - curveOffset;
                else if (toSide === 'bottom') cp2y = toY + curveOffset;

                // Cria uma curva suave
                return `M ${fromX} ${fromY} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${toX} ${toY}`;
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
                        {onBack && (
                            <button onClick={onBack} style={{ padding: '10px 20px', backgroundColor: 'rgba(255,255,255,0.2)', color: 'white', border: '1px solid rgba(255,255,255,0.3)', borderRadius: '8px', cursor: 'pointer', fontWeight: '600' }}>
                                ← Voltar
                            </button>
                        )}
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
                            <div className="metric-label">📊 CAC (Custo por Cliente)</div>
                            <div className="metric-value">
                                <span className={dashboardMetrics.cac < 50 ? 'metric-positive' : dashboardMetrics.cac < 150 ? 'metric-neutral' : 'metric-negative'}>
                                    {dashboardMetrics.cac < 50 ? '✅' : dashboardMetrics.cac < 150 ? '⚠️' : '❌'}
                                </span>
                                R$ {dashboardMetrics.cac.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
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
                            onMouseDown={handleCanvasMouseDown}
                            onMouseMove={handleMouseMove}
                            onMouseUp={(e) => {
                                if (isDraggingConnection) {
                                    handleConnectionDragEnd(e);
                                } else {
                                    handleMouseUp();
                                }
                            }}
                            onClick={handleCanvasClick}
                            style={{ cursor: isPanning ? 'grabbing' : 'default' }}
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
                                <g transform={`translate(${panOffset.x}, ${panOffset.y}) scale(${zoomLevel})`}>
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
                                                    d={getConnectionPath(conn.from, conn.to, conn.fromSide || 'right', conn.toSide || 'left')}
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

                            <div className="canvas" style={{ transform: `translate(${panOffset.x}px, ${panOffset.y}px) scale(${zoomLevel})` }}>
                                {elements.map(element => {
                                    const metrics = metricsMap[element.id]?.calculatedMetrics || {};
                                    // Se tem cor customizada, usa ela; senão usa a padrão do tipo
                                    const elementColor = element.customColor || DEFAULT_COLORS[element.type];
                                    // Determina cor do texto baseado no tipo (alguns fundos claros precisam texto escuro)
                                    const textColor = needsDarkText(element.type) ? '#2d3748' : 'white';

                                    return (
                                        <div
                                            key={element.id}
                                            className={`funnel-element ${
                                                selectedElement === element.id ? 'selected' : ''
                                            } ${isDragging && draggingElement === element.id ? 'dragging' : ''} ${
                                                hoveredElement === element.id ? 'drag-hover' : ''
                                            }`}
                                            style={{
                                                left: element.x,
                                                top: element.y,
                                                background: elementColor,
                                                color: textColor
                                            }}
                                            onClick={(e) => handleElementClick(e, element)}
                                            onMouseDown={(e) => handleElementMouseDown(e, element)}
                                            onMouseEnter={() => handleElementHover(element.id, true)}
                                            onMouseLeave={() => handleElementHover(element.id, false)}
                                        >
                                            {/* Pontos de conexão nos 4 lados */}
                                            <div
                                                className={`connection-point top ${connectingFrom === element.id ? 'connecting' : ''}`}
                                                onMouseDown={(e) => handleConnectionStart(e, element.id, 'top')}
                                                title="Conectar do topo"
                                            />
                                            <div
                                                className={`connection-point right ${connectingFrom === element.id ? 'connecting' : ''}`}
                                                onMouseDown={(e) => handleConnectionStart(e, element.id, 'right')}
                                                title="Conectar da direita"
                                            />
                                            <div
                                                className={`connection-point bottom ${connectingFrom === element.id ? 'connecting' : ''}`}
                                                onMouseDown={(e) => handleConnectionStart(e, element.id, 'bottom')}
                                                title="Conectar de baixo"
                                            />
                                            <div
                                                className={`connection-point left ${connectingFrom === element.id ? 'connecting' : ''}`}
                                                onMouseDown={(e) => handleConnectionStart(e, element.id, 'left')}
                                                title="Conectar da esquerda"
                                            />

                                            <div className="element-header">
                                                <span className="element-icon">{element.icon}</span>
                                                <span className="element-title">{element.name}</span>
                                                <div className="element-actions">
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
                                                ) : element.type === 'retargeting' && element.clicks > 0 ? (
                                                    // Métricas para Retargeting como fonte de tráfego
                                                    <>
                                                        <div className="metric-row">
                                                            <span>👁️ {(element.impressions || 0).toLocaleString('pt-BR')} impressões</span>
                                                        </div>
                                                        <div className="metric-row">
                                                            <span>👆 {(element.clicks || 0).toLocaleString('pt-BR')} cliques ({element.impressions > 0 ? ((element.clicks / element.impressions) * 100).toFixed(1) : 0}%)</span>
                                                        </div>
                                                        <div style={{borderTop: '1px solid rgba(255,255,255,0.2)', margin: '6px 0', paddingTop: '6px'}}>
                                                            <div className="metric-row">
                                                                <span>💰 R$ {((element.investment || element.retargetingInvestment) || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
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
                                                        {/* Retargeting sem métricas de tráfego mostra apenas investimento se configurado */}
                                                        {element.type === 'retargeting' && element.clicks === 0 && element.retargetingInvestment > 0 && (
                                                            <div style={{borderTop: '1px solid rgba(255,255,255,0.2)', margin: '6px 0', paddingTop: '6px'}}>
                                                                <div className="metric-row">
                                                                    <span>💰 R$ {(element.retargetingInvestment || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })} investido</span>
                                                                </div>
                                                            </div>
                                                        )}
                                                        {metrics.revenue > 0 && (
                                                            <div style={{borderTop: '1px solid rgba(255,255,255,0.2)', margin: '6px 0', paddingTop: '6px'}}>
                                                                <div className="metric-row">
                                                                    <span>💰 R$ {element.price?.toLocaleString('pt-BR', { minimumFractionDigits: 2 }) || '0,00'} cada</span>
                                                                </div>
                                                                {element.hasOrderBump && metrics.orderBumpSales > 0 && (
                                                                    <div className="metric-row">
                                                                        <span>🎁 {metrics.orderBumpSales} bumps (R$ {(metrics.orderBumpRevenue || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })})</span>
                                                                    </div>
                                                                )}
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

                                    <div className="form-group">
                                        <label className="form-label">🎨 Cor do Elemento</label>
                                        <div style={{display: 'flex', gap: '10px', alignItems: 'center'}}>
                                            <input
                                                type="color"
                                                style={{
                                                    width: '60px',
                                                    height: '40px',
                                                    border: '2px solid #e2e8f0',
                                                    borderRadius: '8px',
                                                    cursor: 'pointer'
                                                }}
                                                value={selectedElementData.customColorPicker || '#667eea'}
                                                onChange={(e) => {
                                                    const color = e.target.value;
                                                    updateElementProperty('customColorPicker', color);
                                                    updateElementProperty('customColor', `linear-gradient(135deg, ${color} 0%, ${color} 100%)`);
                                                }}
                                            />
                                            <button
                                                className="form-button"
                                                style={{
                                                    padding: '8px 16px',
                                                    background: '#e2e8f0',
                                                    border: 'none',
                                                    borderRadius: '6px',
                                                    cursor: 'pointer',
                                                    fontWeight: '600',
                                                    fontSize: '13px',
                                                    color: '#4a5568'
                                                }}
                                                onClick={() => {
                                                    updateElementProperty('customColor', null);
                                                    updateElementProperty('customColorPicker', null);
                                                }}
                                            >
                                                🔄 Restaurar Padrão
                                            </button>
                                        </div>
                                        <small className="form-help">Personalize a cor deste elemento ou use a cor padrão</small>
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
                                            {/* Taxa de conversão não é necessária para Retargeting com métricas de tráfego */}
                                            {!(selectedElementData.type === 'retargeting' && selectedElementData.clicks > 0) && (
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
                                            )}
                                            {/* Campo específico para E-commerce: Taxa de Add to Cart */}
                                            {selectedElementData.type === 'ecommerce' && (
                                                <div className="form-group">
                                                    <label className="form-label">🛒 Taxa de Adicionar ao Carrinho (%)</label>
                                                    <input
                                                        type="number"
                                                        className={`form-input ${validateValue('addToCartRate', selectedElementData.addToCartRate).type || ''}`}
                                                        value={selectedElementData.addToCartRate === 0 ? '' : selectedElementData.addToCartRate || ''}
                                                        onChange={(e) => updateElementProperty('addToCartRate', e.target.value)}
                                                        min="0"
                                                        max="100"
                                                        step="0.1"
                                                        placeholder="Ex: 20"
                                                    />
                                                    <small className="form-help">% de visitantes que adicionam produto ao carrinho</small>
                                                    {validateValue('addToCartRate', selectedElementData.addToCartRate).message && (
                                                        <div className={`validation-message ${validateValue('addToCartRate', selectedElementData.addToCartRate).type}`}>
                                                            {validateValue('addToCartRate', selectedElementData.addToCartRate).message}
                                                        </div>
                                                    )}
                                                </div>
                                            )}

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

                                                    <div className="form-group">
                                                        <div className="form-checkbox">
                                                            <input
                                                                type="checkbox"
                                                                id="has-orderbump"
                                                                checked={selectedElementData.hasOrderBump || false}
                                                                onChange={(e) => updateElementProperty('hasOrderBump', e.target.checked)}
                                                            />
                                                            <label htmlFor="has-orderbump">🎁 Possui Order Bump</label>
                                                        </div>
                                                    </div>

                                                    {selectedElementData.hasOrderBump && (
                                                        <>
                                                            <div className="form-group">
                                                                <label className="form-label">💰 Valor do Order Bump (R$)</label>
                                                                <input
                                                                    type="number"
                                                                    className="form-input"
                                                                    value={selectedElementData.orderBumpPrice === 0 ? '' : selectedElementData.orderBumpPrice || ''}
                                                                    onChange={(e) => updateElementProperty('orderBumpPrice', e.target.value)}
                                                                    step="0.01"
                                                                    placeholder="Ex: 47.00"
                                                                />
                                                                <small className="form-help">Valor adicional do order bump</small>
                                                            </div>
                                                            <div className="form-group">
                                                                <label className="form-label">📊 Taxa de Conversão do Order Bump (%)</label>
                                                                <input
                                                                    type="number"
                                                                    className="form-input"
                                                                    value={selectedElementData.orderBumpConversion === 0 ? '' : selectedElementData.orderBumpConversion || ''}
                                                                    onChange={(e) => updateElementProperty('orderBumpConversion', e.target.value)}
                                                                    min="0"
                                                                    max="100"
                                                                    step="1"
                                                                    placeholder="Ex: 30"
                                                                />
                                                                <small className="form-help">% de compradores que aceitam o order bump (típico: 20-40%)</small>
                                                            </div>
                                                        </>
                                                    )}
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
                                                                {selectedElementData.hasOrderBump && metrics.orderBumpSales > 0 && (
                                                                    <>
                                                                        <div className="benchmark-item">
                                                                            <span>• Order Bumps: {metrics.orderBumpSales?.toLocaleString('pt-BR') || 0} ({selectedElementData.orderBumpConversion || 0}%)</span>
                                                                        </div>
                                                                        <div className="benchmark-item">
                                                                            <span>• Receita Bump: R$ {(metrics.orderBumpRevenue || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
                                                                        </div>
                                                                    </>
                                                                )}
                                                                <div className="benchmark-item">
                                                                    <span>• Receita Total: R$ {metrics.revenue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
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
                                            {selectedElementData.type === 'ecommerce' && (
                                                <div className="benchmark-box">
                                                    <h4>📋 BENCHMARKS - E-COMMERCE</h4>
                                                    <div className="benchmark-item">
                                                        <span>• 15-25%: Taxa de Add to Cart</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 2-5%: Conversão em vendas</span>
                                                    </div>
                                                    <div className="benchmark-item">
                                                        <span>• 50-70%: Abandono de carrinho típico</span>
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
                                            {/* Campos específicos para RETARGETING */}
                                            {selectedElementData.type === 'retargeting' && (
                                                <>
                                                    <div className="form-group">
                                                        <label className="form-label">📝 Nome do Público</label>
                                                        <input
                                                            type="text"
                                                            className="form-input"
                                                            value={selectedElementData.audienceName || ''}
                                                            onChange={(e) => updateElementProperty('audienceName', e.target.value)}
                                                            placeholder="Ex: Visualizou VSL mas não comprou"
                                                        />
                                                        <small className="form-help">Identifique qual público será impactado neste retargeting</small>
                                                    </div>

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
                                                        <label className="form-label">💰 Investimento em Retargeting (R$)</label>
                                                        <input
                                                            type="number"
                                                            className={`form-input ${validateValue('investment', selectedElementData.investment || selectedElementData.retargetingInvestment).type || ''}`}
                                                            value={selectedElementData.investment || selectedElementData.retargetingInvestment || ''}
                                                            onChange={(e) => {
                                                                updateElementProperty('investment', e.target.value);
                                                                updateElementProperty('retargetingInvestment', e.target.value);
                                                            }}
                                                            placeholder="Ex: 2000"
                                                            step="0.01"
                                                        />
                                                        <small className="form-help">Investimento adicional em campanhas de retargeting</small>
                                                        {validateValue('investment', selectedElementData.investment || selectedElementData.retargetingInvestment).message && (
                                                            <div className={`validation-message ${validateValue('investment', selectedElementData.investment || selectedElementData.retargetingInvestment).type}`}>
                                                                {validateValue('investment', selectedElementData.investment || selectedElementData.retargetingInvestment).message}
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
                                                                    placeholder="Ex: 50000"
                                                                />
                                                                <small className="form-help">Quantas pessoas do público verão o anúncio de retargeting?</small>
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
                                                                    placeholder="Ex: 15"
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
                                                                    placeholder="Ex: 4"
                                                                    step="0.01"
                                                                />
                                                                <small className="form-help">% de pessoas que clicam no anúncio (Cliques calculados: {selectedElementData.clicks.toLocaleString('pt-BR')})</small>
                                                            </div>
                                                        </>
                                                    )}

                                                    {selectedElementData.clicks > 0 && (
                                                        <div className="benchmark-box" style={{background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white', border: 'none'}}>
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
                                                                        <span>• CPM: R$ {selectedElementData.cpm > 0 ? selectedElementData.cpm.toFixed(2) : (((selectedElementData.investment || selectedElementData.retargetingInvestment) / selectedElementData.impressions) * 1000).toFixed(2)}</span>
                                                                    </div>
                                                                    <div className="benchmark-item">
                                                                        <span>• CPC: R$ {((selectedElementData.investment || selectedElementData.retargetingInvestment) / selectedElementData.clicks).toFixed(2)}</span>
                                                                    </div>
                                                                </>
                                                            )}
                                                        </div>
                                                    )}

                                                    <div className="benchmark-box">
                                                        <h4>📋 BENCHMARKS - RETARGETING</h4>
                                                        <div className="benchmark-item">
                                                            <span>• 3-8%: CTR típico (melhor que cold traffic)</span>
                                                        </div>
                                                        <div className="benchmark-item">
                                                            <span>• CPM 30-50% menor que tráfego frio</span>
                                                        </div>
                                                        <div className="benchmark-item">
                                                            <span>• 10-30%: Conversão de retargeting</span>
                                                        </div>
                                                        <div className="benchmark-item">
                                                            <span>• CPC 50-70% menor que cold traffic</span>
                                                        </div>
                                                    </div>
                                                </>
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
                                    <button
                                        onClick={() => deleteConnection(selectedConnection)}
                                        style={{
                                            width: '100%',
                                            padding: '12px',
                                            marginTop: '20px',
                                            background: 'linear-gradient(135deg, #f56565 0%, #c53030 100%)',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '8px',
                                            cursor: 'pointer',
                                            fontWeight: '600',
                                            fontSize: '14px',
                                            transition: 'opacity 0.2s'
                                        }}
                                        onMouseEnter={(e) => e.target.style.opacity = '0.9'}
                                        onMouseLeave={(e) => e.target.style.opacity = '1'}
                                    >
                                        🗑️ Deletar Conexão
                                    </button>
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

        // Templates de Funis Prontos
        const FUNNEL_TEMPLATES = [
            {
                id: 'vsl-simples',
                name: 'VSL Simples',
                icon: '🎬',
                description: 'Tráfego → Landing → VSL → Checkout',
                elements: [
                    { id: 1, type: 'trafego', name: 'Tráfego Pago', icon: '🎯', color: 'color-trafego', x: 100, y: 150, trafficMode: 'absolute', investment: 3000, impressions: 150000, clicks: 5000 },
                    { id: 2, type: 'landing', name: 'Landing Page', icon: '📄', color: 'color-landing', x: 350, y: 150, conversionRate: 40, pageViewRate: 95 },
                    { id: 3, type: 'vsl', name: 'VSL', icon: '🎥', color: 'color-vsl', x: 600, y: 150, conversionRate: 60, pageViewRate: 85 },
                    { id: 4, type: 'vendas', name: 'Checkout', icon: '💳', color: 'color-vendas', x: 850, y: 150, conversionRate: 3, pageViewRate: 95, generatesRevenue: true, price: 497 }
                ],
                connections: [
                    { id: 'c1', from: 1, to: 2, conversion: 100, fromSide: 'right', toSide: 'left' },
                    { id: 'c2', from: 2, to: 3, conversion: 100, fromSide: 'right', toSide: 'left' },
                    { id: 'c3', from: 3, to: 4, conversion: 100, fromSide: 'right', toSide: 'left' }
                ]
            },
            {
                id: 'webinar',
                name: 'Webinar',
                icon: '🎓',
                description: 'Captura → Email → Webinar → Oferta',
                elements: [
                    { id: 1, type: 'trafego', name: 'Tráfego Pago', icon: '🎯', color: 'color-trafego', x: 100, y: 150, trafficMode: 'absolute', investment: 4000, impressions: 160000, clicks: 4000 },
                    { id: 2, type: 'landing', name: 'Inscrição', icon: '📄', color: 'color-landing', x: 350, y: 150, conversionRate: 35, pageViewRate: 95 },
                    { id: 3, type: 'email', name: 'Email Confirmação', icon: '✉️', color: 'color-email', x: 600, y: 150, conversionRate: 100, pageViewRate: 55 },
                    { id: 4, type: 'webinar', name: 'Webinar', icon: '🎓', color: 'color-webinar', x: 850, y: 150, conversionRate: 40, pageViewRate: 40 },
                    { id: 5, type: 'vendas', name: 'Oferta', icon: '💳', color: 'color-vendas', x: 1100, y: 150, conversionRate: 15, pageViewRate: 100, generatesRevenue: true, price: 997 }
                ],
                connections: [
                    { id: 'c1', from: 1, to: 2, conversion: 100, fromSide: 'right', toSide: 'left' },
                    { id: 'c2', from: 2, to: 3, conversion: 100, fromSide: 'right', toSide: 'left' },
                    { id: 'c3', from: 3, to: 4, conversion: 100, fromSide: 'right', toSide: 'left' },
                    { id: 'c4', from: 4, to: 5, conversion: 100, fromSide: 'right', toSide: 'left' }
                ]
            },
            {
                id: 'tripwire',
                name: 'Tripwire',
                icon: '🎁',
                description: 'Landing → Oferta Baixa → Upsells',
                elements: [
                    { id: 1, type: 'trafego', name: 'Tráfego Pago', icon: '🎯', color: 'color-trafego', x: 100, y: 150, trafficMode: 'absolute', investment: 1500, impressions: 75000, clicks: 3000 },
                    { id: 2, type: 'landing', name: 'Landing Page', icon: '📄', color: 'color-landing', x: 350, y: 150, conversionRate: 40, pageViewRate: 95 },
                    { id: 3, type: 'vendas', name: 'Tripwire R$ 27', icon: '🎁', color: 'color-vendas', x: 600, y: 150, conversionRate: 20, pageViewRate: 100, generatesRevenue: true, price: 27 },
                    { id: 4, type: 'upsell', name: 'Upsell R$ 97', icon: '⬆️', color: 'color-upsell', x: 850, y: 150, conversionRate: 30, pageViewRate: 100, generatesRevenue: true, price: 97 }
                ],
                connections: [
                    { id: 'c1', from: 1, to: 2, conversion: 100, fromSide: 'right', toSide: 'left' },
                    { id: 'c2', from: 2, to: 3, conversion: 100, fromSide: 'right', toSide: 'left' },
                    { id: 'c3', from: 3, to: 4, conversion: 100, fromSide: 'right', toSide: 'left' }
                ]
            }
        ];

        function FunnelDashboard({ onSelectFunnel, onCreateBlank, onOpenSettings }) {
            const [funnels, setFunnels] = React.useState([]);
            const [showNewModal, setShowNewModal] = React.useState(false);
            const [newName, setNewName] = React.useState('');

            React.useEffect(() => {
                const saved = JSON.parse(localStorage.getItem('funnels') || '[]');
                setFunnels(saved);
            }, []);

            const createFromTemplate = (template) => {
                const newFunnel = {
                    id: Date.now().toString(),
                    name: template.name,
                    icon: template.icon,
                    createdAt: new Date().toISOString(),
                    elements: template.elements,
                    connections: template.connections
                };
                const updated = [...funnels, newFunnel];
                localStorage.setItem('funnels', JSON.stringify(updated));
                setFunnels(updated);
                onSelectFunnel(newFunnel.id);
            };

            const createBlank = () => {
                if (!newName.trim()) {
                    alert('Digite um nome para o funil');
                    return;
                }
                const newFunnel = {
                    id: Date.now().toString(),
                    name: newName,
                    icon: '🎯',
                    createdAt: new Date().toISOString(),
                    elements: [],
                    connections: []
                };
                const updated = [...funnels, newFunnel];
                localStorage.setItem('funnels', JSON.stringify(updated));
                setFunnels(updated);
                setShowNewModal(false);
                setNewName('');
                onSelectFunnel(newFunnel.id);
            };

            const deleteFunnel = (id, e) => {
                e.stopPropagation();
                if (confirm('Deletar este funil?')) {
                    const updated = funnels.filter(f => f.id !== id);
                    localStorage.setItem('funnels', JSON.stringify(updated));
                    setFunnels(updated);
                }
            };

            return (
                <div style={{ minHeight: '100vh', maxHeight: '100vh', overflow: 'auto', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '40px 20px', position: 'relative' }}>
                    <button
                        onClick={onOpenSettings}
                        style={{
                            position: 'fixed',
                            top: '20px',
                            right: '20px',
                            zIndex: '1000',
                            padding: '12px 20px',
                            background: 'rgba(255,255,255,0.2)',
                            border: '2px solid rgba(255,255,255,0.3)',
                            borderRadius: '12px',
                            color: 'white',
                            fontSize: '16px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.2s',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                        }}
                        onMouseOver={(e) => { e.currentTarget.style.background = 'rgba(255,255,255,0.3)'; e.currentTarget.style.transform = 'scale(1.05)'; }}
                        onMouseOut={(e) => { e.currentTarget.style.background = 'rgba(255,255,255,0.2)'; e.currentTarget.style.transform = 'scale(1)'; }}
                    >
                        ⚙️ Configurações
                    </button>
                    <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
                        <h1 style={{ color: 'white', fontSize: '48px', fontWeight: 'bold', marginBottom: '10px', textAlign: 'center' }}>🚀 Meus Funis</h1>
                        <p style={{ color: 'rgba(255,255,255,0.9)', fontSize: '18px', textAlign: 'center', marginBottom: '40px' }}>Escolha um template ou crie do zero</p>

                        <div style={{ backgroundColor: 'rgba(255,255,255,0.95)', borderRadius: '16px', padding: '30px', marginBottom: '30px' }}>
                            <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '20px' }}>✨ Templates Prontos</h2>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' }}>
                                {FUNNEL_TEMPLATES.map(t => (
                                    <div key={t.id} onClick={() => createFromTemplate(t)} style={{ backgroundColor: 'white', border: '2px solid #e5e7eb', borderRadius: '12px', padding: '24px', cursor: 'pointer', transition: 'all 0.3s' }}
                                        onMouseOver={(e) => { e.currentTarget.style.borderColor = '#667eea'; e.currentTarget.style.transform = 'translateY(-4px)'; }}
                                        onMouseOut={(e) => { e.currentTarget.style.borderColor = '#e5e7eb'; e.currentTarget.style.transform = 'translateY(0)'; }}>
                                        <div style={{ fontSize: '48px', textAlign: 'center', marginBottom: '12px' }}>{t.icon}</div>
                                        <h3 style={{ fontSize: '18px', fontWeight: 'bold', textAlign: 'center', marginBottom: '8px' }}>{t.name}</h3>
                                        <p style={{ fontSize: '13px', color: '#6b7280', textAlign: 'center' }}>{t.description}</p>
                                    </div>
                                ))}
                                <div onClick={() => setShowNewModal(true)} style={{ backgroundColor: 'white', border: '2px dashed #667eea', borderRadius: '12px', padding: '24px', cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '200px' }}>
                                    <div style={{ fontSize: '48px', marginBottom: '12px' }}>➕</div>
                                    <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#667eea' }}>Criar do Zero</h3>
                                </div>
                            </div>
                        </div>

                        {funnels.length > 0 && (
                            <div style={{ backgroundColor: 'rgba(255,255,255,0.95)', borderRadius: '16px', padding: '30px' }}>
                                <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '20px' }}>📊 Meus Funis</h2>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' }}>
                                    {funnels.map(f => (
                                        <div key={f.id} onClick={() => onSelectFunnel(f.id)} style={{ backgroundColor: 'white', border: '2px solid #e5e7eb', borderRadius: '12px', padding: '20px', cursor: 'pointer', position: 'relative' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                                                <span style={{ fontSize: '32px' }}>{f.icon}</span>
                                                <h3 style={{ fontSize: '18px', fontWeight: 'bold', flex: 1 }}>{f.name}</h3>
                                                <button onClick={(e) => deleteFunnel(f.id, e)} style={{ padding: '8px', backgroundColor: '#ef4444', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>🗑️</button>
                                            </div>
                                            <p style={{ fontSize: '12px', color: '#9ca3af' }}>{f.elements?.length || 0} elementos</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {showNewModal && (
                            <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 }} onClick={() => setShowNewModal(false)}>
                                <div onClick={(e) => e.stopPropagation()} style={{ backgroundColor: 'white', padding: '40px', borderRadius: '16px', maxWidth: '500px', width: '90%' }}>
                                    <h2 style={{ fontSize: '24px', marginBottom: '20px' }}>Criar Novo Funil</h2>
                                    <input type="text" value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="Nome do funil..."
                                        onKeyPress={(e) => { if (e.key === 'Enter') createBlank(); }}
                                        style={{ width: '100%', padding: '12px', fontSize: '16px', border: '2px solid #e5e7eb', borderRadius: '8px', marginBottom: '20px', boxSizing: 'border-box' }} autoFocus />
                                    <div style={{ display: 'flex', gap: '12px' }}>
                                        <button onClick={() => setShowNewModal(false)} style={{ flex: 1, padding: '12px', backgroundColor: '#e5e7eb', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '600' }}>Cancelar</button>
                                        <button onClick={createBlank} style={{ flex: 1, padding: '12px', backgroundColor: '#667eea', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '600' }}>Criar</button>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            );
        }

        function SettingsPanel({ onClose }) {
            // Carrega configurações do localStorage ou usa padrão
            const loadConfig = () => {
                const saved = localStorage.getItem('systemConfig');
                if (saved) {
                    return JSON.parse(saved);
                }
                return {
                    categories: ELEMENT_CATEGORIES,
                    fieldLabels: {
                        investment: 'Investimento Planejado',
                        impressions: 'Impressões Esperadas',
                        clicks: 'Cliques Esperados',
                        cpm: 'CPM - Custo por Mil',
                        ctr: 'CTR - Taxa de Cliques',
                        conversionRate: 'Taxa de Conversão',
                        price: 'Preço do Produto',
                        url: 'URL da Página',
                        description: 'Descrição',
                        name: 'Nome do Elemento',
                        orderBumpPrice: 'Preço do Order Bump',
                        orderBumpConversion: 'Taxa de Conversão do Order Bump'
                    }
                };
            };

            const [config, setConfig] = useState(loadConfig());
            const [hasChanges, setHasChanges] = useState(false);

            const updateCategoryName = (categoryIndex, newName) => {
                const newConfig = { ...config };
                newConfig.categories[categoryIndex].name = newName;
                setConfig(newConfig);
                setHasChanges(true);
            };

            const updateCategoryIcon = (categoryIndex, newIcon) => {
                const newConfig = { ...config };
                newConfig.categories[categoryIndex].icon = newIcon;
                setConfig(newConfig);
                setHasChanges(true);
            };

            const updateElementName = (categoryIndex, elementIndex, newName) => {
                const newConfig = { ...config };
                newConfig.categories[categoryIndex].elements[elementIndex].name = newName;
                setConfig(newConfig);
                setHasChanges(true);
            };

            const updateElementIcon = (categoryIndex, elementIndex, newIcon) => {
                const newConfig = { ...config };
                newConfig.categories[categoryIndex].elements[elementIndex].icon = newIcon;
                setConfig(newConfig);
                setHasChanges(true);
            };

            const updateFieldLabel = (fieldKey, newLabel) => {
                const newConfig = { ...config };
                newConfig.fieldLabels[fieldKey] = newLabel;
                setConfig(newConfig);
                setHasChanges(true);
            };

            const handleSave = () => {
                localStorage.setItem('systemConfig', JSON.stringify(config));
                setHasChanges(false);
                // Recarrega a página para aplicar mudanças
                window.location.reload();
            };

            const handleReset = () => {
                if (confirm('Tem certeza que deseja restaurar todas as configurações padrão? Esta ação não pode ser desfeita.')) {
                    localStorage.removeItem('systemConfig');
                    window.location.reload();
                }
            };

            return (
                <div className="settings-overlay" onClick={onClose}>
                    <div className="settings-panel" onClick={(e) => e.stopPropagation()}>
                        <div className="settings-header">
                            <h2>⚙️ Configurações do Sistema</h2>
                            <button className="settings-close-btn" onClick={onClose}>×</button>
                        </div>

                        <div className="settings-content">
                            {/* Seção: Categorias */}
                            <div className="settings-section">
                                <div className="settings-section-header">
                                    <span className="settings-section-icon">📁</span>
                                    <h3 className="settings-section-title">Categorias de Elementos</h3>
                                </div>
                                {config.categories.map((category, catIndex) => (
                                    <div key={catIndex} className="category-editor">
                                        <div className="category-editor-header">
                                            <input
                                                type="text"
                                                className="settings-input"
                                                value={category.icon}
                                                onChange={(e) => updateCategoryIcon(catIndex, e.target.value)}
                                                placeholder="Ícone"
                                                style={{ width: '60px', textAlign: 'center', fontSize: '20px' }}
                                            />
                                            <input
                                                type="text"
                                                className="settings-input"
                                                value={category.name}
                                                onChange={(e) => updateCategoryName(catIndex, e.target.value)}
                                                placeholder="Nome da categoria"
                                                style={{ flex: 1 }}
                                            />
                                        </div>
                                        <div className="settings-grid">
                                            {category.elements.map((element, elemIndex) => (
                                                <div key={elemIndex} className="settings-card">
                                                    <div className="settings-card-header">
                                                        <span className="settings-card-icon">{element.icon}</span>
                                                        <h4 className="settings-card-title">{element.type}</h4>
                                                    </div>
                                                    <div className="settings-input-group">
                                                        <label className="settings-label">Ícone</label>
                                                        <input
                                                            type="text"
                                                            className="settings-input"
                                                            value={element.icon}
                                                            onChange={(e) => updateElementIcon(catIndex, elemIndex, e.target.value)}
                                                            placeholder="Digite um emoji"
                                                        />
                                                    </div>
                                                    <div className="settings-input-group">
                                                        <label className="settings-label">Nome de Exibição</label>
                                                        <input
                                                            type="text"
                                                            className="settings-input"
                                                            value={element.name}
                                                            onChange={(e) => updateElementName(catIndex, elemIndex, e.target.value)}
                                                            placeholder="Nome do elemento"
                                                        />
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Seção: Labels de Campos */}
                            <div className="settings-section">
                                <div className="settings-section-header">
                                    <span className="settings-section-icon">🏷️</span>
                                    <h3 className="settings-section-title">Labels dos Campos</h3>
                                </div>
                                <div className="settings-grid">
                                    {Object.entries(config.fieldLabels).map(([key, label]) => (
                                        <div key={key} className="settings-card">
                                            <div className="settings-input-group">
                                                <label className="settings-label">Campo: {key}</label>
                                                <input
                                                    type="text"
                                                    className="settings-input"
                                                    value={label}
                                                    onChange={(e) => updateFieldLabel(key, e.target.value)}
                                                    placeholder="Label do campo"
                                                />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div className="settings-footer">
                            <button className="settings-btn settings-btn-secondary" onClick={handleReset}>
                                🔄 Restaurar Padrões
                            </button>
                            <div style={{ display: 'flex', gap: '12px' }}>
                                <button className="settings-btn settings-btn-secondary" onClick={onClose}>
                                    Cancelar
                                </button>
                                <button
                                    className="settings-btn settings-btn-primary"
                                    onClick={handleSave}
                                    disabled={!hasChanges}
                                >
                                    💾 Salvar Alterações
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            );
        }

        function App() {
            const [view, setView] = React.useState('dashboard');
            const [funnelId, setFunnelId] = React.useState(null);
            const [showSettings, setShowSettings] = React.useState(false);

            const selectFunnel = (id) => {
                setFunnelId(id);
                setView('editor');
            };

            const backToDashboard = () => {
                setView('dashboard');
                setFunnelId(null);
            };

            return (
                <>
                    {showSettings && <SettingsPanel onClose={() => setShowSettings(false)} />}
                    {view === 'dashboard' ? (
                        <FunnelDashboard onSelectFunnel={selectFunnel} onOpenSettings={() => setShowSettings(true)} />
                    ) : (
                        <FunnelBuilder funnelId={funnelId} onBack={backToDashboard} />
                    )}
                </>
            );
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
