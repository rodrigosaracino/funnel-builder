#!/usr/bin/env python3
"""
Funnel Builder - Sistema completo de construção de funis com drag & drop
Autor: Sistema de Funnel Builder
Versão: 1.0
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser
import threading
import json
import urllib.parse
from auth import auth
from models import User, Funnel
from webhooks import webhook_manager
from rate_limiter import rate_limiter
from security_logger import security_logger
from marketing_routes import (
    handle_pages_list, handle_page_create, handle_page_get, handle_page_update, handle_page_delete,
    handle_page_test_create, handle_page_test_delete,
    handle_utms_list, handle_utm_create, handle_utm_get, handle_utm_update, handle_utm_delete,
    handle_utm_generate_url,
    handle_metrics_create, handle_metrics_list, handle_metrics_delete
)
import os

# ==================== CONFIGURAÇÕES DE SEGURANÇA ====================

# Limite máximo de payload (10MB)
MAX_PAYLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

# CORS: Domínios permitidos (ajustar para produção)
ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    # Adicionar domínios de produção aqui:
    # 'https://funnel-builder.seudominio.com',
    # 'https://app.seudominio.com'
]

# ====================================================================

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

        .color-google { background: linear-gradient(135deg, #4285f4 0%, #34a853 100%); }
        .color-facebook { background: linear-gradient(135deg, #1877f2 0%, #0a66c2 100%); }
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

        // ==================== API HELPERS ====================
        const API_BASE = '';  // Mesmo domínio

        // Helper para fazer chamadas autenticadas à API
        const apiCall = async (endpoint, options = {}) => {
            const token = localStorage.getItem('authToken');

            const config = {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            };

            // Adiciona token se existir
            if (token) {
                config.headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await fetch(`${API_BASE}${endpoint}`, config);

            // Se retornar 401 e tinha token, desloga
            if (response.status === 401) {
                // Se retornou 401 e não tem token, é normal (não está logado)
                if (!token) {
                    return response.json();
                }

                // Se tinha token, significa que expirou - desloga e recarrega
                console.log('Token expirado, redirecionando para login...');
                localStorage.removeItem('authToken');
                localStorage.removeItem('currentUser');
                window.location.reload();
                return null;
            }

            return response.json();
        };

        // API: Buscar todos os funis
        const apiFetchFunnels = async () => {
            return await apiCall('/api/funnels');
        };

        // API: Criar funil
        const apiCreateFunnel = async (funnelData) => {
            return await apiCall('/api/funnels', {
                method: 'POST',
                body: JSON.stringify(funnelData)
            });
        };

        // API: Atualizar funil
        const apiUpdateFunnel = async (funnelId, funnelData) => {
            return await apiCall(`/api/funnels/${funnelId}`, {
                method: 'PUT',
                body: JSON.stringify(funnelData)
            });
        };

        // API: Deletar funil
        const apiDeleteFunnel = async (funnelId) => {
            return await apiCall(`/api/funnels/${funnelId}`, {
                method: 'DELETE'
            });
        };

        // API: Duplicar funil
        const apiDuplicateFunnel = async (funnelId) => {
            // Busca o funil original
            const originalFunnel = await apiCall(`/api/funnels/${funnelId}`);

            if (!originalFunnel || !originalFunnel.funnel) {
                throw new Error('Funil não encontrado');
            }

            const funnel = originalFunnel.funnel;

            // Cria cópia com novo nome
            const copyName = `${funnel.name} (Cópia)`;

            // Cria o novo funil
            return await apiCall('/api/funnels', {
                method: 'POST',
                body: JSON.stringify({
                    name: copyName,
                    icon: funnel.icon,
                    elements: funnel.elements,
                    connections: funnel.connections
                })
            });
        };

        // ==================== FIM API HELPERS ====================

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
                    { type: 'google', name: 'Google Ads', icon: '🔍', color: 'color-google' },
                    { type: 'facebook', name: 'Facebook Ads', icon: '📘', color: 'color-facebook' },
                    { type: 'trafego', name: 'Outros Tráfegos', icon: '🎯', color: 'color-trafego' },
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
            // Tráfego - Cores específicas por plataforma
            'google': 'linear-gradient(135deg, #4285f4 0%, #34a853 100%)',
            'facebook': 'linear-gradient(135deg, #1877f2 0%, #0a66c2 100%)',
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
            const [name, setName] = useState('');
            const [whatsapp, setWhatsapp] = useState('');
            const [isRegister, setIsRegister] = useState(false);
            const [loading, setLoading] = useState(false);
            const [error, setError] = useState('');

            const handleSubmit = async (e) => {
                e.preventDefault();
                setLoading(true);
                setError('');

                try {
                    const endpoint = isRegister ? '/api/register' : '/api/login';
                    const body = isRegister
                        ? { email, password, name, whatsapp }
                        : { email, password };

                    const response = await fetch(endpoint, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(body)
                    });

                    const data = await response.json();

                    if (data.success) {
                        // Salva token e dados do usuário
                        localStorage.setItem('authToken', data.token);
                        localStorage.setItem('currentUser', JSON.stringify(data.user));
                        onLogin();
                    } else {
                        setError(data.message || 'Erro ao fazer login');
                    }
                } catch (err) {
                    setError('Erro ao conectar com o servidor');
                    console.error('Erro:', err);
                } finally {
                    setLoading(false);
                }
            };

            return (
                <div className="login-container">
                    <div className="login-card">
                        <div className="login-header">
                            <div className="login-logo">🚀</div>
                            <h1 className="login-title">Funnel Builder</h1>
                            <p className="login-subtitle">Construa funis de vendas de alta conversão</p>
                        </div>

                        {error && (
                            <div style={{
                                padding: '12px',
                                marginBottom: '20px',
                                background: '#fee',
                                border: '1px solid #fcc',
                                borderRadius: '8px',
                                color: '#c33',
                                fontSize: '14px'
                            }}>
                                ⚠️ {error}
                            </div>
                        )}

                        <form className="login-form" onSubmit={handleSubmit}>
                            {isRegister && (
                                <>
                                    <div className="login-input-group">
                                        <label className="login-label" htmlFor="name">Nome</label>
                                        <input
                                            id="name"
                                            type="text"
                                            className="login-input"
                                            placeholder="Seu nome completo"
                                            value={name}
                                            onChange={(e) => setName(e.target.value)}
                                        />
                                    </div>
                                    <div className="login-input-group">
                                        <label className="login-label" htmlFor="whatsapp">WhatsApp</label>
                                        <input
                                            id="whatsapp"
                                            type="tel"
                                            className="login-input"
                                            placeholder="(11) 99999-9999"
                                            value={whatsapp}
                                            onChange={(e) => setWhatsapp(e.target.value)}
                                            required
                                        />
                                        <small style={{ color: '#666', fontSize: '12px', marginTop: '4px' }}>
                                            Formato: (DD) 9XXXX-XXXX
                                        </small>
                                    </div>
                                </>
                            )}
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
                                    minLength={6}
                                />
                                {isRegister && (
                                    <small style={{ color: '#666', fontSize: '12px', marginTop: '4px' }}>
                                        Mínimo de 6 caracteres
                                    </small>
                                )}
                            </div>
                            <button
                                type="submit"
                                className="login-button"
                                disabled={loading}
                                style={{ opacity: loading ? 0.6 : 1 }}
                            >
                                {loading ? '⏳ Aguarde...' : (isRegister ? '📝 Criar Conta' : '🚀 Acessar Sistema')}
                            </button>
                        </form>

                        <div style={{
                            textAlign: 'center',
                            marginTop: '20px',
                            paddingTop: '20px',
                            borderTop: '1px solid #e2e8f0'
                        }}>
                            <button
                                onClick={() => {
                                    setIsRegister(!isRegister);
                                    setError('');
                                }}
                                style={{
                                    background: 'none',
                                    border: 'none',
                                    color: '#667eea',
                                    cursor: 'pointer',
                                    fontSize: '14px',
                                    textDecoration: 'underline'
                                }}
                            >
                                {isRegister ? '← Já tenho conta' : '✨ Criar nova conta'}
                            </button>
                        </div>

                        <div className="login-footer">
                            Versão 2.0 - Sistema de Funis com Banco de Dados
                        </div>
                    </div>
                </div>
            );
        }

        function FunnelBuilder({ funnelId, onBack }) {
            const [elements, setElements] = useState([]);
            const [connections, setConnections] = useState([]);
            const [currentFunnel, setCurrentFunnel] = useState(null);
            const [saving, setSaving] = useState(false);
            const saveTimeoutRef = useRef(null);
            const initialLoadRef = useRef(false);

            // Estados para páginas e UTMs
            const [pages, setPages] = useState([]);
            const [utms, setUtms] = useState([]);
            const [showUtmGenerator, setShowUtmGenerator] = useState(false);

            // Carrega páginas e UTMs
            React.useEffect(() => {
                loadPages();
                loadUtms();
            }, []);

            const loadPages = async () => {
                try {
                    const data = await apiCall('/api/pages');
                    if (data && data.pages) {
                        setPages(data.pages);
                    }
                } catch (error) {
                    console.error('Erro ao carregar páginas:', error);
                }
            };

            const loadUtms = async () => {
                try {
                    const data = await apiCall('/api/utms');
                    if (data && data.utms) {
                        setUtms(data.utms);
                    }
                } catch (error) {
                    console.error('Erro ao carregar UTMs:', error);
                }
            };

            // Carrega o funil específico da API
            React.useEffect(() => {
                if (funnelId) {
                    loadFunnel();
                }
            }, [funnelId]);

            const loadFunnel = async () => {
                try {
                    const data = await apiCall(`/api/funnels/${funnelId}`);
                    if (data && data.funnel) {
                        setCurrentFunnel(data.funnel);
                        setElements(data.funnel.elements || []);
                        setConnections(data.funnel.connections || []);
                        // Marca como carregado para não salvar no primeiro render
                        setTimeout(() => {
                            initialLoadRef.current = true;
                        }, 100);
                    }
                } catch (error) {
                    console.error('Erro ao carregar funil:', error);
                }
            };

            // Auto-salva com debounce quando elementos ou conexões mudam
            React.useEffect(() => {
                // Não salva no carregamento inicial
                if (!initialLoadRef.current || !funnelId) {
                    return;
                }

                // Limpa timeout anterior
                if (saveTimeoutRef.current) {
                    clearTimeout(saveTimeoutRef.current);
                }

                // Agenda novo salvamento após 2 segundos de inatividade
                saveTimeoutRef.current = setTimeout(() => {
                    console.log('💾 Salvando funil automaticamente...');
                    saveFunnel();
                }, 2000);

                // Cleanup
                return () => {
                    if (saveTimeoutRef.current) {
                        clearTimeout(saveTimeoutRef.current);
                    }
                };
            }, [elements, connections, funnelId]);

            const [saveSuccess, setSaveSuccess] = useState(false);
            const [showBottleneckAnalysis, setShowBottleneckAnalysis] = useState(false);

            const saveFunnel = async () => {
                if (saving) return;
                setSaving(true);
                setSaveSuccess(false);

                try {
                    await apiUpdateFunnel(funnelId, {
                        elements,
                        connections
                    });
                    console.log('✅ Funil salvo automaticamente');
                    setSaveSuccess(true);
                    setTimeout(() => setSaveSuccess(false), 2000);
                } catch (error) {
                    console.error('❌ Erro ao salvar funil:', error);
                } finally {
                    setSaving(false);
                }
            };
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
                    const isTrafficSource = ['trafego', 'google', 'facebook', 'retargeting'].includes(element.type);
                    if (isTrafficSource && element.clicks > 0) {
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

            // Análise de Gargalos - identifica onde o funil perde mais pessoas
            const analyzeBottlenecks = () => {
                const metrics = calculateMetrics();
                const bottlenecks = [];

                // Para cada conexão, calcula a taxa de dropout
                connections.forEach(conn => {
                    const fromElement = elements.find(el => el.id === conn.from);
                    const toElement = elements.find(el => el.id === conn.to);

                    if (fromElement && toElement && metrics[fromElement.id] && metrics[toElement.id]) {
                        const fromVisitors = metrics[fromElement.id].calculatedMetrics?.visitors || 0;
                        const toVisitors = metrics[toElement.id].calculatedMetrics?.visitors || 0;

                        if (fromVisitors > 0) {
                            const dropoutRate = ((fromVisitors - toVisitors) / fromVisitors) * 100;
                            const dropoutCount = fromVisitors - toVisitors;

                            if (dropoutRate > 0) {
                                bottlenecks.push({
                                    fromId: fromElement.id,
                                    toId: toElement.id,
                                    fromName: fromElement.name,
                                    toName: toElement.name,
                                    fromVisitors: fromVisitors,
                                    toVisitors: toVisitors,
                                    dropoutCount: dropoutCount,
                                    dropoutRate: dropoutRate,
                                    conversionRate: 100 - dropoutRate
                                });
                            }
                        }
                    }
                });

                // Ordena por taxa de dropout (maior primeiro)
                bottlenecks.sort((a, b) => b.dropoutRate - a.dropoutRate);

                return bottlenecks;
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
                // Google Ads sempre usa modo 'metrics' (CPM)
                const defaultTrafficMode = elementType.type === 'google' ? 'metrics' : 'absolute';

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
                    cpc: 0, // Custo Por Clique (usado pelo Google Ads)
                    trafficMode: defaultTrafficMode, // 'absolute' ou 'metrics'
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
                        if (['investment', 'impressions', 'clicks', 'pageViewRate', 'conversionRate', 'price', 'ctr', 'cpm', 'cpc', 'orderBumpPrice', 'orderBumpConversion', 'addToCartRate', 'retargetingInvestment'].includes(property)) {
                            // Se o valor estiver vazio, permite vazio (não força 0)
                            if (value === '' || value === null || value === undefined) {
                                return { ...el, [property]: 0 };
                            }
                            const numValue = parseFloat(value);
                            const updated = { ...el, [property]: numValue };

                            // Cálculos automáticos para modo de tráfego (trafego, google, facebook e retargeting)
                            const isTrafficElement = ['trafego', 'google', 'facebook', 'retargeting'].includes(el.type);
                            if (isTrafficElement) {
                                // Para retargeting, usa investment ou retargetingInvestment
                                const inv = el.type === 'retargeting' ? (updated.investment || updated.retargetingInvestment) : updated.investment;

                                // Google usa CPC (Custo Por Clique)
                                if (el.type === 'google') {
                                    // Calcula cliques baseado em CPC e investimento
                                    if (updated.cpc > 0 && inv > 0) {
                                        updated.clicks = Math.round(inv / updated.cpc);
                                    }
                                    // Calcula CPC baseado em investimento e cliques
                                    if (updated.clicks > 0 && inv > 0 && updated.cpc === 0) {
                                        updated.cpc = parseFloat((inv / updated.clicks).toFixed(2));
                                    }
                                } else if (el.trafficMode === 'metrics') {
                                    // Facebook/Outros usam CPM + CTR
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
                        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                            {onBack && (
                                <button onClick={onBack} style={{ padding: '10px 20px', backgroundColor: 'rgba(255,255,255,0.2)', color: 'white', border: '1px solid rgba(255,255,255,0.3)', borderRadius: '8px', cursor: 'pointer', fontWeight: '600' }}>
                                    ← Voltar
                                </button>
                            )}
                            <button
                                onClick={() => setShowBottleneckAnalysis(!showBottleneckAnalysis)}
                                style={{
                                    padding: '10px 20px',
                                    backgroundColor: showBottleneckAnalysis ? '#ef4444' : '#10b981',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '8px',
                                    cursor: 'pointer',
                                    fontWeight: '600',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px'
                                }}
                            >
                                {showBottleneckAnalysis ? '✕ Fechar Análise' : '🔍 Análise de Gargalos'}
                            </button>
                            <button
                                onClick={() => saveFunnel()}
                                disabled={saving}
                                style={{
                                    padding: '10px 20px',
                                    backgroundColor: saveSuccess ? 'rgba(46, 213, 115, 0.5)' : (saving ? 'rgba(100,100,100,0.3)' : 'rgba(46, 213, 115, 0.3)'),
                                    color: 'white',
                                    border: saveSuccess ? '1px solid rgba(46, 213, 115, 0.8)' : (saving ? '1px solid rgba(100,100,100,0.5)' : '1px solid rgba(46, 213, 115, 0.5)'),
                                    borderRadius: '8px',
                                    cursor: saving ? 'not-allowed' : 'pointer',
                                    fontWeight: '600',
                                    transition: 'all 0.3s ease'
                                }}
                            >
                                {saveSuccess ? '✅ Salvo!' : (saving ? '💾 Salvando...' : '💾 Salvar')}
                            </button>
                        </div>
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
                        {/* Painel de Análise de Gargalos */}
                        {showBottleneckAnalysis && (
                            <div style={{
                                position: 'fixed',
                                top: '80px',
                                right: '20px',
                                width: '400px',
                                maxHeight: '80vh',
                                overflowY: 'auto',
                                background: 'white',
                                borderRadius: '12px',
                                boxShadow: '0 10px 40px rgba(0,0,0,0.3)',
                                zIndex: 1000,
                                padding: '20px'
                            }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                                    <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#1f2937' }}>🔍 Análise de Gargalos</h3>
                                    <button
                                        onClick={() => setShowBottleneckAnalysis(false)}
                                        style={{
                                            background: 'none',
                                            border: 'none',
                                            fontSize: '24px',
                                            cursor: 'pointer',
                                            color: '#9ca3af'
                                        }}
                                    >
                                        ×
                                    </button>
                                </div>

                                {(() => {
                                    const bottlenecks = analyzeBottlenecks();

                                    if (bottlenecks.length === 0) {
                                        return (
                                            <div style={{ textAlign: 'center', padding: '40px 20px', color: '#9ca3af' }}>
                                                <div style={{ fontSize: '48px', marginBottom: '16px' }}>📊</div>
                                                <p>Adicione conexões entre elementos para ver a análise de gargalos</p>
                                            </div>
                                        );
                                    }

                                    const worstBottleneck = bottlenecks[0];

                                    return (
                                        <div>
                                            {/* Maior Gargalo */}
                                            <div style={{
                                                background: 'linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)',
                                                border: '2px solid #ef4444',
                                                borderRadius: '12px',
                                                padding: '16px',
                                                marginBottom: '20px'
                                            }}>
                                                <div style={{ fontSize: '14px', fontWeight: '600', color: '#dc2626', marginBottom: '8px' }}>
                                                    🚨 MAIOR GARGALO
                                                </div>
                                                <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#1f2937', marginBottom: '8px' }}>
                                                    {worstBottleneck.fromName} → {worstBottleneck.toName}
                                                </div>
                                                <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#dc2626', marginBottom: '8px' }}>
                                                    {worstBottleneck.dropoutRate.toFixed(1)}%
                                                </div>
                                                <div style={{ fontSize: '13px', color: '#7f1d1d' }}>
                                                    {worstBottleneck.dropoutCount.toLocaleString('pt-BR')} pessoas abandonam aqui
                                                </div>
                                            </div>

                                            {/* Lista de Gargalos */}
                                            <div style={{ fontSize: '14px', fontWeight: '600', color: '#4b5563', marginBottom: '12px' }}>
                                                Todas as etapas:
                                            </div>

                                            {bottlenecks.map((bottleneck, index) => (
                                                <div
                                                    key={index}
                                                    style={{
                                                        background: index === 0 ? '#fef2f2' : '#f9fafb',
                                                        border: `2px solid ${index === 0 ? '#fca5a5' : '#e5e7eb'}`,
                                                        borderRadius: '8px',
                                                        padding: '12px',
                                                        marginBottom: '12px'
                                                    }}
                                                >
                                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                                                        <div style={{ fontSize: '13px', fontWeight: '600', color: '#1f2937' }}>
                                                            {bottleneck.fromName} → {bottleneck.toName}
                                                        </div>
                                                        <div style={{
                                                            fontSize: '16px',
                                                            fontWeight: 'bold',
                                                            color: bottleneck.dropoutRate > 70 ? '#dc2626' : bottleneck.dropoutRate > 50 ? '#f59e0b' : '#10b981'
                                                        }}>
                                                            {bottleneck.dropoutRate.toFixed(1)}%
                                                        </div>
                                                    </div>

                                                    <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '8px' }}>
                                                        {bottleneck.fromVisitors.toLocaleString('pt-BR')} pessoas → {bottleneck.toVisitors.toLocaleString('pt-BR')} pessoas
                                                    </div>

                                                    {/* Barra de progresso */}
                                                    <div style={{
                                                        width: '100%',
                                                        height: '8px',
                                                        background: '#e5e7eb',
                                                        borderRadius: '4px',
                                                        overflow: 'hidden'
                                                    }}>
                                                        <div style={{
                                                            width: `${bottleneck.conversionRate}%`,
                                                            height: '100%',
                                                            background: bottleneck.dropoutRate > 70 ? '#dc2626' : bottleneck.dropoutRate > 50 ? '#f59e0b' : '#10b981',
                                                            transition: 'width 0.3s'
                                                        }} />
                                                    </div>

                                                    <div style={{ fontSize: '11px', color: '#9ca3af', marginTop: '4px' }}>
                                                        Taxa de conversão: {bottleneck.conversionRate.toFixed(1)}%
                                                    </div>
                                                </div>
                                            ))}

                                            {/* Sugestões */}
                                            <div style={{
                                                background: '#dbeafe',
                                                border: '2px solid #3b82f6',
                                                borderRadius: '8px',
                                                padding: '12px',
                                                marginTop: '20px'
                                            }}>
                                                <div style={{ fontSize: '13px', fontWeight: '600', color: '#1e40af', marginBottom: '8px' }}>
                                                    💡 Dica de Otimização
                                                </div>
                                                <div style={{ fontSize: '12px', color: '#1e3a8a' }}>
                                                    Foque em melhorar o maior gargalo primeiro. Uma melhoria de 10% nesta etapa pode aumentar significativamente o resultado final do funil.
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })()}
                            </div>
                        )}

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
                                                {['trafego', 'google', 'facebook'].includes(element.type) ? (
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

                                    {/* Seletor de Página */}
                                    {['landing', 'vsl', 'checkout', 'vendas', 'squeeze', 'captura', 'upsell', 'downsell', 'webinar'].includes(selectedElementData.type) && (
                                        <div className="form-group">
                                            <label className="form-label">📄 Vincular Página Cadastrada</label>
                                            <select
                                                className="form-input"
                                                value={selectedElementData.pageId || ''}
                                                onChange={(e) => {
                                                    const pageId = e.target.value;

                                                    if (pageId) {
                                                        const page = pages.find(p => p.id === parseInt(pageId));
                                                        if (page) {
                                                            // Atualiza tudo de uma vez usando setElements
                                                            setElements(elements.map(el => {
                                                                if (el.id === selectedElement) {
                                                                    return {
                                                                        ...el,
                                                                        pageId: parseInt(pageId),
                                                                        pageName: page.name,
                                                                        url: page.url,
                                                                        description: page.description || el.description
                                                                    };
                                                                }
                                                                return el;
                                                            }));
                                                        }
                                                    } else {
                                                        // Remove vinculação
                                                        setElements(elements.map(el => {
                                                            if (el.id === selectedElement) {
                                                                return {
                                                                    ...el,
                                                                    pageId: null,
                                                                    pageName: null
                                                                };
                                                            }
                                                            return el;
                                                        }));
                                                    }
                                                }}
                                                style={{ fontSize: '14px' }}
                                            >
                                                <option value="">Nenhuma página vinculada</option>
                                                {pages.map(page => (
                                                    <option key={page.id} value={page.id}>
                                                        {page.name} ({page.category})
                                                    </option>
                                                ))}
                                            </select>
                                            {selectedElementData.pageId && (
                                                <small className="form-help" style={{ display: 'block', marginTop: '8px', color: '#10b981' }}>
                                                    ✓ Página vinculada: {selectedElementData.pageName}
                                                </small>
                                            )}
                                            {selectedElementData.url && (
                                                <small className="form-help" style={{ display: 'block', marginTop: '4px', color: '#6b7280', fontSize: '12px', wordBreak: 'break-all' }}>
                                                    🔗 {selectedElementData.url}
                                                </small>
                                            )}
                                            {pages.length === 0 && (
                                                <small className="form-help" style={{ display: 'block', marginTop: '8px', color: '#f59e0b' }}>
                                                    💡 Cadastre páginas em Marketing &gt; Páginas
                                                </small>
                                            )}
                                        </div>
                                    )}

                                    {/* Gerador de UTM */}
                                    {['landing', 'vsl', 'checkout', 'vendas', 'squeeze', 'captura', 'upsell', 'downsell', 'webinar'].includes(selectedElementData.type) && selectedElementData.url && (
                                        <div className="form-group">
                                            <label className="form-label">🔗 UTMs para Rastreamento</label>

                                            {/* Lista de UTMs existentes - Mostrar primeiro */}
                                            {utms.length > 0 && !showUtmGenerator && (
                                                <div style={{ marginBottom: '12px' }}>
                                                    <label style={{ fontSize: '13px', color: '#718096', display: 'block', marginBottom: '8px' }}>
                                                        Selecione uma UTM e copie a URL completa:
                                                    </label>
                                                    <div style={{
                                                        border: '1px solid #e2e8f0',
                                                        borderRadius: '8px',
                                                        padding: '12px',
                                                        background: '#f9fafb',
                                                        maxHeight: '200px',
                                                        overflowY: 'auto'
                                                    }}>
                                                        {utms.map(utm => {
                                                            const utmUrl = `${selectedElementData.url}${selectedElementData.url.includes('?') ? '&' : '?'}utm_source=${utm.utm_source}&utm_medium=${utm.utm_medium}&utm_campaign=${utm.utm_campaign}${utm.utm_content ? '&utm_content=' + utm.utm_content : ''}${utm.utm_term ? '&utm_term=' + utm.utm_term : ''}`;

                                                            return (
                                                                <div
                                                                    key={utm.id}
                                                                    style={{
                                                                        padding: '10px',
                                                                        background: 'white',
                                                                        border: '1px solid #e2e8f0',
                                                                        borderRadius: '6px',
                                                                        marginBottom: '8px',
                                                                        cursor: 'pointer',
                                                                        transition: 'all 0.2s'
                                                                    }}
                                                                    onMouseOver={(e) => {
                                                                        e.currentTarget.style.borderColor = '#667eea';
                                                                        e.currentTarget.style.background = '#f0f4ff';
                                                                    }}
                                                                    onMouseOut={(e) => {
                                                                        e.currentTarget.style.borderColor = '#e2e8f0';
                                                                        e.currentTarget.style.background = 'white';
                                                                    }}
                                                                    onClick={() => {
                                                                        navigator.clipboard.writeText(utmUrl);
                                                                        alert('✓ URL copiada com sucesso!');
                                                                    }}
                                                                >
                                                                    <div style={{ fontSize: '13px', fontWeight: '600', color: '#1f2937', marginBottom: '4px' }}>
                                                                        {utm.name}
                                                                    </div>
                                                                    <div style={{ fontSize: '11px', color: '#6b7280', marginBottom: '6px' }}>
                                                                        {utm.utm_source} • {utm.utm_medium} • {utm.utm_campaign}
                                                                    </div>
                                                                    <div style={{
                                                                        fontSize: '10px',
                                                                        color: '#9ca3af',
                                                                        fontFamily: 'monospace',
                                                                        background: '#f3f4f6',
                                                                        padding: '4px 6px',
                                                                        borderRadius: '4px',
                                                                        overflow: 'hidden',
                                                                        textOverflow: 'ellipsis',
                                                                        whiteSpace: 'nowrap'
                                                                    }}>
                                                                        {utmUrl}
                                                                    </div>
                                                                    <div style={{ fontSize: '11px', color: '#667eea', marginTop: '6px', textAlign: 'center', fontWeight: '600' }}>
                                                                        📋 Clique para copiar
                                                                    </div>
                                                                </div>
                                                            );
                                                        })}
                                                    </div>
                                                </div>
                                            )}

                                            {/* Botão para criar nova UTM */}
                                            {!showUtmGenerator ? (
                                                <button
                                                    className="form-button"
                                                    style={{
                                                        padding: '10px 16px',
                                                        background: utms.length > 0 ? '#e2e8f0' : '#667eea',
                                                        color: utms.length > 0 ? '#4a5568' : 'white',
                                                        border: 'none',
                                                        borderRadius: '6px',
                                                        cursor: 'pointer',
                                                        fontWeight: '600',
                                                        fontSize: '14px',
                                                        width: '100%'
                                                    }}
                                                    onClick={() => setShowUtmGenerator(true)}
                                                >
                                                    ➕ {utms.length > 0 ? 'Criar nova UTM' : 'Criar primeira UTM'}
                                                </button>
                                            ) : (
                                                <div style={{
                                                    border: '1px solid #667eea',
                                                    borderRadius: '8px',
                                                    padding: '12px',
                                                    background: '#f0f4ff',
                                                    marginTop: '8px'
                                                }}>
                                                    <UtmGeneratorInline
                                                        elementUrl={selectedElementData.url || ''}
                                                        onUtmCreated={(utmData) => {
                                                            // Salva a UTM e atualiza a lista
                                                            apiCall('/api/utms', {
                                                                method: 'POST',
                                                                body: JSON.stringify(utmData)
                                                            }).then(() => {
                                                                loadUtms();
                                                                setShowUtmGenerator(false);
                                                                alert('✓ UTM criada com sucesso!');
                                                            }).catch(err => {
                                                                console.error('Erro ao criar UTM:', err);
                                                                alert('✗ Erro ao criar UTM');
                                                            });
                                                        }}
                                                        onCancel={() => setShowUtmGenerator(false)}
                                                    />
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    {/* Aviso se não tem URL configurada */}
                                    {['landing', 'vsl', 'checkout', 'vendas', 'squeeze', 'captura', 'upsell', 'downsell', 'webinar'].includes(selectedElementData.type) && !selectedElementData.url && (
                                        <div className="form-group">
                                            <div style={{
                                                padding: '12px',
                                                background: '#fef3c7',
                                                border: '1px solid #fbbf24',
                                                borderRadius: '8px',
                                                fontSize: '13px',
                                                color: '#92400e'
                                            }}>
                                                ⚠️ Configure a URL do elemento primeiro para poder gerar UTMs
                                            </div>
                                        </div>
                                    )}

                                    {/* Campos específicos para TRÁFEGO */}
                                    {['trafego', 'google', 'facebook'].includes(selectedElementData.type) && !connections.some(conn => conn.to === selectedElementData.id) && (
                                        <>
                                            {/* Google Ads não tem toggle - sempre usa CPM */}
                                            {selectedElementData.type !== 'google' && (
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
                                            )}

                                            {/* Google Ads sempre mostra info de que usa CPC */}
                                            {selectedElementData.type === 'google' && (
                                                <div style={{
                                                    background: 'linear-gradient(135deg, #4285f4 0%, #34a853 100%)',
                                                    color: 'white',
                                                    padding: '12px',
                                                    borderRadius: '8px',
                                                    marginBottom: '20px',
                                                    fontSize: '13px',
                                                    fontWeight: '600'
                                                }}>
                                                    🔍 Google Ads utiliza modelo CPC (Custo Por Clique)
                                                </div>
                                            )}

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

                                            {/* Google sempre usa CPM, outros podem escolher */}
                                            {(selectedElementData.trafficMode === 'absolute' && selectedElementData.type !== 'google') ? (
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
                                            ) : selectedElementData.type === 'google' ? (
                                                <>
                                                    {/* Google Ads usa CPC (Custo Por Clique) */}
                                                    <div className="form-group">
                                                        <label className="form-label">💵 CPC - Custo por Clique (R$)</label>
                                                        <input
                                                            type="number"
                                                            className="form-input"
                                                            value={selectedElementData.cpc === 0 ? '' : selectedElementData.cpc}
                                                            onChange={(e) => updateElementProperty('cpc', e.target.value)}
                                                            placeholder="Ex: 2.50"
                                                            step="0.01"
                                                        />
                                                        <small className="form-help">Quanto você paga por cada clique? (Cliques calculados: {selectedElementData.clicks.toLocaleString('pt-BR')})</small>
                                                    </div>
                                                </>
                                            ) : (
                                                <>
                                                    {/* Facebook e Outros usam CPM + CTR */}
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

        function FunnelDashboard({ onSelectFunnel, onCreateBlank, onOpenSettings, onGoToMarketing, onLogout }) {
            const [funnels, setFunnels] = React.useState([]);
            const [showNewModal, setShowNewModal] = React.useState(false);
            const [newName, setNewName] = React.useState('');
            const [loading, setLoading] = React.useState(true);

            // Carrega funis da API ao montar o componente
            React.useEffect(() => {
                loadFunnels();
            }, []);

            const loadFunnels = async () => {
                setLoading(true);
                try {
                    const data = await apiFetchFunnels();
                    if (data && data.funnels) {
                        setFunnels(data.funnels);
                    }
                } catch (error) {
                    console.error('Erro ao carregar funis:', error);
                } finally {
                    setLoading(false);
                }
            };

            const createFromTemplate = async (template) => {
                try {
                    const result = await apiCreateFunnel({
                        name: template.name,
                        icon: template.icon,
                        elements: template.elements,
                        connections: template.connections
                    });

                    if (result && result.funnel) {
                        setFunnels([...funnels, result.funnel]);
                        onSelectFunnel(result.funnel.id);
                    }
                } catch (error) {
                    console.error('Erro ao criar funil:', error);
                    alert('Erro ao criar funil do template');
                }
            };

            const createBlank = async () => {
                if (!newName.trim()) {
                    alert('Digite um nome para o funil');
                    return;
                }

                try {
                    const result = await apiCreateFunnel({
                        name: newName,
                        icon: '🎯',
                        elements: [],
                        connections: []
                    });

                    if (result && result.funnel) {
                        setFunnels([...funnels, result.funnel]);
                        setShowNewModal(false);
                        setNewName('');
                        onSelectFunnel(result.funnel.id);
                    }
                } catch (error) {
                    console.error('Erro ao criar funil:', error);
                    alert('Erro ao criar funil');
                }
            };

            const deleteFunnel = async (id, e) => {
                e.stopPropagation();
                if (confirm('Deletar este funil?')) {
                    try {
                        const result = await apiDeleteFunnel(id);
                        if (result && result.success) {
                            setFunnels(funnels.filter(f => f.id !== id));
                        }
                    } catch (error) {
                        console.error('Erro ao deletar funil:', error);
                        alert('Erro ao deletar funil');
                    }
                }
            };

            const duplicateFunnel = async (id, e) => {
                e.stopPropagation();
                try {
                    const result = await apiDuplicateFunnel(id);
                    if (result && result.funnel) {
                        setFunnels([...funnels, result.funnel]);
                        alert('✓ Funil duplicado com sucesso!');
                    }
                } catch (error) {
                    console.error('Erro ao duplicar funil:', error);
                    alert('✗ Erro ao duplicar funil');
                }
            };

            return (
                <div style={{ minHeight: '100vh', maxHeight: '100vh', overflow: 'auto', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '40px 20px', position: 'relative' }}>
                    <div style={{
                        position: 'fixed',
                        top: '20px',
                        right: '20px',
                        zIndex: '1000',
                        display: 'flex',
                        gap: '12px'
                    }}>
                        <button
                            onClick={onGoToMarketing}
                            style={{
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
                            📊 Marketing
                        </button>
                        <button
                            onClick={onOpenSettings}
                            style={{
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
                        <button
                            onClick={onLogout}
                            style={{
                                padding: '12px 20px',
                                background: 'rgba(239, 68, 68, 0.3)',
                                border: '2px solid rgba(239, 68, 68, 0.5)',
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
                            onMouseOver={(e) => { e.currentTarget.style.background = 'rgba(239, 68, 68, 0.5)'; e.currentTarget.style.transform = 'scale(1.05)'; }}
                            onMouseOut={(e) => { e.currentTarget.style.background = 'rgba(239, 68, 68, 0.3)'; e.currentTarget.style.transform = 'scale(1)'; }}
                        >
                            🚪 Sair
                        </button>
                    </div>
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
                                        <div key={f.id} onClick={() => onSelectFunnel(f.id)} style={{ backgroundColor: 'white', border: '2px solid #e5e7eb', borderRadius: '12px', padding: '20px', cursor: 'pointer', position: 'relative', transition: 'all 0.2s' }}
                                            onMouseOver={(e) => { e.currentTarget.style.borderColor = '#667eea'; e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.15)'; }}
                                            onMouseOut={(e) => { e.currentTarget.style.borderColor = '#e5e7eb'; e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none'; }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                                                <span style={{ fontSize: '32px' }}>{f.icon}</span>
                                                <h3 style={{ fontSize: '18px', fontWeight: 'bold', flex: 1 }}>{f.name}</h3>
                                                <button
                                                    onClick={(e) => duplicateFunnel(f.id, e)}
                                                    style={{
                                                        padding: '8px 12px',
                                                        backgroundColor: '#3b82f6',
                                                        color: 'white',
                                                        border: 'none',
                                                        borderRadius: '6px',
                                                        cursor: 'pointer',
                                                        fontSize: '14px',
                                                        fontWeight: '600',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        gap: '4px',
                                                        transition: 'all 0.2s'
                                                    }}
                                                    onMouseOver={(e) => { e.currentTarget.style.backgroundColor = '#2563eb'; e.currentTarget.style.transform = 'scale(1.05)'; }}
                                                    onMouseOut={(e) => { e.currentTarget.style.backgroundColor = '#3b82f6'; e.currentTarget.style.transform = 'scale(1)'; }}
                                                    title="Duplicar funil"
                                                >
                                                    📋 Duplicar
                                                </button>
                                                <button
                                                    onClick={(e) => deleteFunnel(f.id, e)}
                                                    style={{
                                                        padding: '8px',
                                                        backgroundColor: '#ef4444',
                                                        color: 'white',
                                                        border: 'none',
                                                        borderRadius: '6px',
                                                        cursor: 'pointer',
                                                        transition: 'all 0.2s'
                                                    }}
                                                    onMouseOver={(e) => { e.currentTarget.style.backgroundColor = '#dc2626'; e.currentTarget.style.transform = 'scale(1.05)'; }}
                                                    onMouseOut={(e) => { e.currentTarget.style.backgroundColor = '#ef4444'; e.currentTarget.style.transform = 'scale(1)'; }}
                                                    title="Deletar funil"
                                                >
                                                    🗑️
                                                </button>
                                            </div>
                                            <p style={{ fontSize: '12px', color: '#9ca3af' }}>{f.elements?.length || 0} elementos • {f.connections?.length || 0} conexões</p>
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

        // ==================== UTM GENERATOR INLINE ====================

        function UtmGeneratorInline({ elementUrl, onUtmCreated, onCancel }) {
            const [formData, setFormData] = useState({
                name: '',
                utm_source: '',
                utm_medium: '',
                utm_campaign: '',
                utm_content: '',
                utm_term: '',
                notes: ''
            });

            const handleSubmit = (e) => {
                e.preventDefault();
                if (!formData.name || !formData.utm_source || !formData.utm_medium || !formData.utm_campaign) {
                    alert('Nome, Source, Medium e Campaign são obrigatórios');
                    return;
                }
                onUtmCreated(formData);
            };

            const previewUrl = elementUrl ?
                `${elementUrl}${elementUrl.includes('?') ? '&' : '?'}utm_source=${formData.utm_source || 'source'}&utm_medium=${formData.utm_medium || 'medium'}&utm_campaign=${formData.utm_campaign || 'campaign'}${formData.utm_content ? '&utm_content=' + formData.utm_content : ''}${formData.utm_term ? '&utm_term=' + formData.utm_term : ''}`
                : 'Configure a URL do elemento primeiro';

            return (
                <form onSubmit={handleSubmit} style={{ fontSize: '13px' }}>
                    <div style={{ marginBottom: '12px' }}>
                        <input
                            type="text"
                            placeholder="Nome da campanha *"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            style={{
                                width: '100%',
                                padding: '8px',
                                border: '1px solid #e2e8f0',
                                borderRadius: '6px',
                                fontSize: '13px'
                            }}
                        />
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
                        <input
                            type="text"
                            placeholder="Source * (ex: facebook)"
                            value={formData.utm_source}
                            onChange={(e) => setFormData({ ...formData, utm_source: e.target.value })}
                            style={{
                                padding: '8px',
                                border: '1px solid #e2e8f0',
                                borderRadius: '6px',
                                fontSize: '13px'
                            }}
                        />
                        <input
                            type="text"
                            placeholder="Medium * (ex: cpc)"
                            value={formData.utm_medium}
                            onChange={(e) => setFormData({ ...formData, utm_medium: e.target.value })}
                            style={{
                                padding: '8px',
                                border: '1px solid #e2e8f0',
                                borderRadius: '6px',
                                fontSize: '13px'
                            }}
                        />
                    </div>
                    <div style={{ marginBottom: '12px' }}>
                        <input
                            type="text"
                            placeholder="Campaign * (ex: black_friday)"
                            value={formData.utm_campaign}
                            onChange={(e) => setFormData({ ...formData, utm_campaign: e.target.value })}
                            style={{
                                width: '100%',
                                padding: '8px',
                                border: '1px solid #e2e8f0',
                                borderRadius: '6px',
                                fontSize: '13px'
                            }}
                        />
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
                        <input
                            type="text"
                            placeholder="Content (opcional)"
                            value={formData.utm_content}
                            onChange={(e) => setFormData({ ...formData, utm_content: e.target.value })}
                            style={{
                                padding: '8px',
                                border: '1px solid #e2e8f0',
                                borderRadius: '6px',
                                fontSize: '13px'
                            }}
                        />
                        <input
                            type="text"
                            placeholder="Term (opcional)"
                            value={formData.utm_term}
                            onChange={(e) => setFormData({ ...formData, utm_term: e.target.value })}
                            style={{
                                padding: '8px',
                                border: '1px solid #e2e8f0',
                                borderRadius: '6px',
                                fontSize: '13px'
                            }}
                        />
                    </div>

                    {elementUrl && (
                        <div style={{
                            background: '#edf2f7',
                            padding: '10px',
                            borderRadius: '6px',
                            marginBottom: '12px',
                            fontSize: '11px',
                            fontFamily: 'monospace',
                            wordBreak: 'break-all',
                            color: '#4a5568'
                        }}>
                            {previewUrl}
                        </div>
                    )}

                    <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                            type="button"
                            onClick={onCancel}
                            style={{
                                flex: 1,
                                padding: '8px',
                                background: '#e2e8f0',
                                border: 'none',
                                borderRadius: '6px',
                                cursor: 'pointer',
                                fontSize: '13px',
                                fontWeight: '600'
                            }}
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            style={{
                                flex: 1,
                                padding: '8px',
                                background: '#667eea',
                                color: 'white',
                                border: 'none',
                                borderRadius: '6px',
                                cursor: 'pointer',
                                fontSize: '13px',
                                fontWeight: '600'
                            }}
                        >
                            Criar UTM
                        </button>
                    </div>
                </form>
            );
        }

        // ==================== MARKETING MANAGER ====================

        function MarketingManager({ onBack }) {
            const [activeTab, setActiveTab] = useState('pages');
            const [pages, setPages] = useState([]);
            const [utms, setUtms] = useState([]);
            const [showPageModal, setShowPageModal] = useState(false);
            const [showUtmModal, setShowUtmModal] = useState(false);
            const [editingPage, setEditingPage] = useState(null);
            const [editingUtm, setEditingUtm] = useState(null);

            // Carrega dados ao montar
            useEffect(() => {
                loadPages();
                loadUtms();
            }, []);

            const loadPages = async () => {
                try {
                    const data = await apiCall('/api/pages');
                    if (data && data.pages) {
                        setPages(data.pages);
                    }
                } catch (error) {
                    console.error('Erro ao carregar páginas:', error);
                }
            };

            const loadUtms = async () => {
                try {
                    const data = await apiCall('/api/utms');
                    if (data && data.utms) {
                        setUtms(data.utms);
                    }
                } catch (error) {
                    console.error('Erro ao carregar UTMs:', error);
                }
            };

            const savePage = async (pageData) => {
                try {
                    if (editingPage) {
                        await apiCall(`/api/pages/${editingPage.id}`, {
                            method: 'PUT',
                            body: JSON.stringify(pageData)
                        });
                    } else {
                        await apiCall('/api/pages', {
                            method: 'POST',
                            body: JSON.stringify(pageData)
                        });
                    }
                    loadPages();
                    setShowPageModal(false);
                    setEditingPage(null);
                } catch (error) {
                    console.error('Erro ao salvar página:', error);
                    alert('Erro ao salvar página');
                }
            };

            const deletePage = async (id) => {
                if (confirm('Deletar esta página?')) {
                    try {
                        await apiCall(`/api/pages/${id}`, { method: 'DELETE' });
                        loadPages();
                    } catch (error) {
                        console.error('Erro ao deletar página:', error);
                    }
                }
            };

            const saveUtm = async (utmData) => {
                try {
                    if (editingUtm) {
                        await apiCall(`/api/utms/${editingUtm.id}`, {
                            method: 'PUT',
                            body: JSON.stringify(utmData)
                        });
                    } else {
                        await apiCall('/api/utms', {
                            method: 'POST',
                            body: JSON.stringify(utmData)
                        });
                    }
                    loadUtms();
                    setShowUtmModal(false);
                    setEditingUtm(null);
                } catch (error) {
                    console.error('Erro ao salvar UTM:', error);
                    alert('Erro ao salvar UTM');
                }
            };

            const deleteUtm = async (id) => {
                if (confirm('Deletar esta UTM?')) {
                    try {
                        await apiCall(`/api/utms/${id}`, { method: 'DELETE' });
                        loadUtms();
                    } catch (error) {
                        console.error('Erro ao deletar UTM:', error);
                    }
                }
            };

            return (
                <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '40px 20px' }}>
                    <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
                        {/* Header */}
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
                            <div>
                                <h1 style={{ color: 'white', fontSize: '42px', fontWeight: 'bold', marginBottom: '5px' }}>📊 Marketing Digital</h1>
                                <p style={{ color: 'rgba(255,255,255,0.9)', fontSize: '16px' }}>Gerencie suas páginas e UTMs</p>
                            </div>
                            <button onClick={onBack} style={{
                                padding: '12px 24px',
                                background: 'rgba(255,255,255,0.2)',
                                border: '2px solid rgba(255,255,255,0.3)',
                                borderRadius: '12px',
                                color: 'white',
                                fontSize: '16px',
                                fontWeight: '600',
                                cursor: 'pointer',
                                transition: 'all 0.2s'
                            }}>
                                ← Voltar
                            </button>
                        </div>

                        {/* Tabs */}
                        <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
                            <button onClick={() => setActiveTab('pages')} style={{
                                padding: '12px 24px',
                                background: activeTab === 'pages' ? 'white' : 'rgba(255,255,255,0.2)',
                                border: '2px solid rgba(255,255,255,0.3)',
                                borderRadius: '12px',
                                color: activeTab === 'pages' ? '#667eea' : 'white',
                                fontSize: '16px',
                                fontWeight: '600',
                                cursor: 'pointer',
                                transition: 'all 0.2s'
                            }}>
                                📄 Páginas ({pages.length})
                            </button>
                            <button onClick={() => setActiveTab('utms')} style={{
                                padding: '12px 24px',
                                background: activeTab === 'utms' ? 'white' : 'rgba(255,255,255,0.2)',
                                border: '2px solid rgba(255,255,255,0.3)',
                                borderRadius: '12px',
                                color: activeTab === 'utms' ? '#667eea' : 'white',
                                fontSize: '16px',
                                fontWeight: '600',
                                cursor: 'pointer',
                                transition: 'all 0.2s'
                            }}>
                                🔗 UTMs ({utms.length})
                            </button>
                        </div>

                        {/* Content */}
                        <div style={{ background: 'white', borderRadius: '16px', padding: '30px', minHeight: '500px' }}>
                            {activeTab === 'pages' ? (
                                <PagesManager pages={pages} onAdd={() => { setEditingPage(null); setShowPageModal(true); }} onEdit={(page) => { setEditingPage(page); setShowPageModal(true); }} onDelete={deletePage} />
                            ) : (
                                <UtmsManager utms={utms} onAdd={() => { setEditingUtm(null); setShowUtmModal(true); }} onEdit={(utm) => { setEditingUtm(utm); setShowUtmModal(true); }} onDelete={deleteUtm} />
                            )}
                        </div>
                    </div>

                    {/* Modals */}
                    {showPageModal && <PageModal page={editingPage} onSave={savePage} onClose={() => { setShowPageModal(false); setEditingPage(null); }} />}
                    {showUtmModal && <UtmModal utm={editingUtm} onSave={saveUtm} onClose={() => { setShowUtmModal(false); setEditingUtm(null); }} />}
                </div>
            );
        }

        function PagesManager({ pages, onAdd, onEdit, onDelete }) {
            const categories = {
                'landing': 'Landing Page',
                'vsl': 'VSL',
                'checkout': 'Checkout',
                'thankyou': 'Obrigado',
                'webinar': 'Webinar',
                'other': 'Outro'
            };

            return (
                <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                        <h2 style={{ fontSize: '24px', fontWeight: 'bold' }}>Minhas Páginas</h2>
                        <button onClick={onAdd} style={{
                            padding: '10px 20px',
                            background: '#667eea',
                            border: 'none',
                            borderRadius: '8px',
                            color: 'white',
                            fontSize: '14px',
                            fontWeight: '600',
                            cursor: 'pointer'
                        }}>
                            + Nova Página
                        </button>
                    </div>

                    {pages.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '60px 20px', color: '#999' }}>
                            <div style={{ fontSize: '64px', marginBottom: '16px' }}>📄</div>
                            <p style={{ fontSize: '18px' }}>Nenhuma página cadastrada</p>
                            <p style={{ fontSize: '14px', marginTop: '8px' }}>Clique em "Nova Página" para começar</p>
                        </div>
                    ) : (
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
                            {pages.map(page => (
                                <div key={page.id} style={{
                                    border: '1px solid #e5e7eb',
                                    borderRadius: '12px',
                                    padding: '20px',
                                    transition: 'all 0.2s',
                                    cursor: 'pointer'
                                }} onMouseOver={(e) => e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)'}
                                   onMouseOut={(e) => e.currentTarget.style.boxShadow = 'none'}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                                        <span style={{
                                            padding: '4px 12px',
                                            background: '#f3f4f6',
                                            borderRadius: '6px',
                                            fontSize: '12px',
                                            fontWeight: '600'
                                        }}>
                                            {categories[page.category] || page.category}
                                        </span>
                                        <div style={{ display: 'flex', gap: '8px' }}>
                                            <button onClick={(e) => { e.stopPropagation(); onEdit(page); }} style={{
                                                padding: '4px 8px',
                                                background: '#3b82f6',
                                                border: 'none',
                                                borderRadius: '4px',
                                                color: 'white',
                                                fontSize: '12px',
                                                cursor: 'pointer'
                                            }}>
                                                ✏️
                                            </button>
                                            <button onClick={(e) => { e.stopPropagation(); onDelete(page.id); }} style={{
                                                padding: '4px 8px',
                                                background: '#ef4444',
                                                border: 'none',
                                                borderRadius: '4px',
                                                color: 'white',
                                                fontSize: '12px',
                                                cursor: 'pointer'
                                            }}>
                                                🗑️
                                            </button>
                                        </div>
                                    </div>
                                    <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '8px', color: '#1f2937' }}>{page.name}</h3>
                                    <a href={page.url} target="_blank" style={{ fontSize: '13px', color: '#6b7280', textDecoration: 'none', display: 'block', marginBottom: '12px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                        {page.url}
                                    </a>
                                    {page.description && <p style={{ fontSize: '13px', color: '#6b7280', marginBottom: '12px' }}>{page.description}</p>}
                                    {page.tags && page.tags.length > 0 && (
                                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                                            {page.tags.map((tag, i) => (
                                                <span key={i} style={{
                                                    padding: '2px 8px',
                                                    background: '#e0e7ff',
                                                    borderRadius: '4px',
                                                    fontSize: '11px',
                                                    color: '#667eea'
                                                }}>
                                                    {tag}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            );
        }

        function UtmsManager({ utms, onAdd, onEdit, onDelete }) {
            const copyToClipboard = (text) => {
                navigator.clipboard.writeText(text);
                alert('UTM copiada!');
            };

            return (
                <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                        <h2 style={{ fontSize: '24px', fontWeight: 'bold' }}>Minhas UTMs</h2>
                        <button onClick={onAdd} style={{
                            padding: '10px 20px',
                            background: '#667eea',
                            border: 'none',
                            borderRadius: '8px',
                            color: 'white',
                            fontSize: '14px',
                            fontWeight: '600',
                            cursor: 'pointer'
                        }}>
                            + Nova UTM
                        </button>
                    </div>

                    {utms.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '60px 20px', color: '#999' }}>
                            <div style={{ fontSize: '64px', marginBottom: '16px' }}>🔗</div>
                            <p style={{ fontSize: '18px' }}>Nenhuma UTM cadastrada</p>
                            <p style={{ fontSize: '14px', marginTop: '8px' }}>Clique em "Nova UTM" para começar</p>
                        </div>
                    ) : (
                        <div style={{ display: 'grid', gap: '16px' }}>
                            {utms.map(utm => {
                                const exampleUrl = `https://exemplo.com?utm_source=${utm.utm_source}&utm_medium=${utm.utm_medium}&utm_campaign=${utm.utm_campaign}${utm.utm_content ? '&utm_content=' + utm.utm_content : ''}${utm.utm_term ? '&utm_term=' + utm.utm_term : ''}`;

                                return (
                                    <div key={utm.id} style={{
                                        border: '1px solid #e5e7eb',
                                        borderRadius: '12px',
                                        padding: '20px',
                                        transition: 'all 0.2s'
                                    }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                                            <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#1f2937' }}>{utm.name}</h3>
                                            <div style={{ display: 'flex', gap: '8px' }}>
                                                <button onClick={() => copyToClipboard(exampleUrl)} style={{
                                                    padding: '6px 12px',
                                                    background: '#10b981',
                                                    border: 'none',
                                                    borderRadius: '6px',
                                                    color: 'white',
                                                    fontSize: '12px',
                                                    cursor: 'pointer'
                                                }}>
                                                    📋 Copiar URL
                                                </button>
                                                <button onClick={() => onEdit(utm)} style={{
                                                    padding: '6px 12px',
                                                    background: '#3b82f6',
                                                    border: 'none',
                                                    borderRadius: '6px',
                                                    color: 'white',
                                                    fontSize: '12px',
                                                    cursor: 'pointer'
                                                }}>
                                                    ✏️ Editar
                                                </button>
                                                <button onClick={() => onDelete(utm.id)} style={{
                                                    padding: '6px 12px',
                                                    background: '#ef4444',
                                                    border: 'none',
                                                    borderRadius: '6px',
                                                    color: 'white',
                                                    fontSize: '12px',
                                                    cursor: 'pointer'
                                                }}>
                                                    🗑️
                                                </button>
                                            </div>
                                        </div>

                                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '16px' }}>
                                            <div>
                                                <div style={{ fontSize: '11px', color: '#9ca3af', marginBottom: '4px' }}>Source</div>
                                                <div style={{ fontSize: '14px', fontWeight: '600', color: '#4b5563' }}>{utm.utm_source}</div>
                                            </div>
                                            <div>
                                                <div style={{ fontSize: '11px', color: '#9ca3af', marginBottom: '4px' }}>Medium</div>
                                                <div style={{ fontSize: '14px', fontWeight: '600', color: '#4b5563' }}>{utm.utm_medium}</div>
                                            </div>
                                            <div>
                                                <div style={{ fontSize: '11px', color: '#9ca3af', marginBottom: '4px' }}>Campaign</div>
                                                <div style={{ fontSize: '14px', fontWeight: '600', color: '#4b5563' }}>{utm.utm_campaign}</div>
                                            </div>
                                            {utm.utm_content && (
                                                <div>
                                                    <div style={{ fontSize: '11px', color: '#9ca3af', marginBottom: '4px' }}>Content</div>
                                                    <div style={{ fontSize: '14px', fontWeight: '600', color: '#4b5563' }}>{utm.utm_content}</div>
                                                </div>
                                            )}
                                            {utm.utm_term && (
                                                <div>
                                                    <div style={{ fontSize: '11px', color: '#9ca3af', marginBottom: '4px' }}>Term</div>
                                                    <div style={{ fontSize: '14px', fontWeight: '600', color: '#4b5563' }}>{utm.utm_term}</div>
                                                </div>
                                            )}
                                        </div>

                                        <div style={{ background: '#f9fafb', padding: '12px', borderRadius: '8px', fontSize: '12px', color: '#6b7280', fontFamily: 'monospace', overflowX: 'auto' }}>
                                            {exampleUrl}
                                        </div>

                                        {utm.notes && (
                                            <div style={{ marginTop: '12px', fontSize: '13px', color: '#6b7280', fontStyle: 'italic' }}>
                                                💡 {utm.notes}
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            );
        }

        function PageModal({ page, onSave, onClose }) {
            const [formData, setFormData] = useState(page || {
                name: '',
                url: '',
                category: 'landing',
                description: '',
                tags: [],
                status: 'active'
            });
            const [tagInput, setTagInput] = useState('');

            const handleSubmit = (e) => {
                e.preventDefault();
                if (!formData.name || !formData.url) {
                    alert('Nome e URL são obrigatórios');
                    return;
                }
                onSave(formData);
            };

            const addTag = () => {
                if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
                    setFormData({ ...formData, tags: [...formData.tags, tagInput.trim()] });
                    setTagInput('');
                }
            };

            const removeTag = (tag) => {
                setFormData({ ...formData, tags: formData.tags.filter(t => t !== tag) });
            };

            return (
                <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 }}>
                    <div style={{ background: 'white', borderRadius: '16px', padding: '30px', width: '90%', maxWidth: '600px', maxHeight: '90vh', overflowY: 'auto' }}>
                        <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '24px' }}>{page ? 'Editar Página' : 'Nova Página'}</h2>

                        <form onSubmit={handleSubmit}>
                            <div style={{ marginBottom: '20px' }}>
                                <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>Nome *</label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    style={{ width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: '8px', fontSize: '14px' }}
                                    placeholder="Ex: Landing Page - Curso Marketing Digital"
                                />
                            </div>

                            <div style={{ marginBottom: '20px' }}>
                                <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>URL *</label>
                                <input
                                    type="url"
                                    value={formData.url}
                                    onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                                    style={{ width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: '8px', fontSize: '14px' }}
                                    placeholder="https://exemplo.com/minha-pagina"
                                />
                            </div>

                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
                                <div>
                                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>Categoria</label>
                                    <select
                                        value={formData.category}
                                        onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                                        style={{ width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: '8px', fontSize: '14px' }}
                                    >
                                        <option value="landing">Landing Page</option>
                                        <option value="vsl">VSL</option>
                                        <option value="checkout">Checkout</option>
                                        <option value="thankyou">Obrigado</option>
                                        <option value="webinar">Webinar</option>
                                        <option value="other">Outro</option>
                                    </select>
                                </div>
                                <div>
                                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>Status</label>
                                    <select
                                        value={formData.status}
                                        onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                                        style={{ width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: '8px', fontSize: '14px' }}
                                    >
                                        <option value="active">Ativa</option>
                                        <option value="testing">Em Teste</option>
                                        <option value="paused">Pausada</option>
                                        <option value="archived">Arquivada</option>
                                    </select>
                                </div>
                            </div>

                            <div style={{ marginBottom: '20px' }}>
                                <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>Descrição</label>
                                <textarea
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    style={{ width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: '8px', fontSize: '14px', minHeight: '80px' }}
                                    placeholder="Descreva o objetivo e contexto desta página..."
                                />
                            </div>

                            <div style={{ marginBottom: '20px' }}>
                                <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>Tags</label>
                                <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
                                    <input
                                        type="text"
                                        value={tagInput}
                                        onChange={(e) => setTagInput(e.target.value)}
                                        onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                                        style={{ flex: 1, padding: '10px', border: '1px solid #d1d5db', borderRadius: '8px', fontSize: '14px' }}
                                        placeholder="Digite uma tag e pressione Enter"
                                    />
                                    <button type="button" onClick={addTag} style={{
                                        padding: '10px 16px',
                                        background: '#667eea',
                                        border: 'none',
                                        borderRadius: '8px',
                                        color: 'white',
                                        fontSize: '14px',
                                        cursor: 'pointer'
                                    }}>
                                        + Adicionar
                                    </button>
                                </div>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                                    {formData.tags.map((tag, i) => (
                                        <span key={i} style={{
                                            padding: '4px 10px',
                                            background: '#e0e7ff',
                                            borderRadius: '6px',
                                            fontSize: '12px',
                                            color: '#667eea',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '6px'
                                        }}>
                                            {tag}
                                            <span onClick={() => removeTag(tag)} style={{ cursor: 'pointer', fontWeight: 'bold' }}>×</span>
                                        </span>
                                    ))}
                                </div>
                            </div>

                            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                                <button type="button" onClick={onClose} style={{
                                    padding: '10px 20px',
                                    background: '#f3f4f6',
                                    border: 'none',
                                    borderRadius: '8px',
                                    fontSize: '14px',
                                    fontWeight: '600',
                                    cursor: 'pointer'
                                }}>
                                    Cancelar
                                </button>
                                <button type="submit" style={{
                                    padding: '10px 20px',
                                    background: '#667eea',
                                    border: 'none',
                                    borderRadius: '8px',
                                    color: 'white',
                                    fontSize: '14px',
                                    fontWeight: '600',
                                    cursor: 'pointer'
                                }}>
                                    {page ? 'Salvar Alterações' : 'Criar Página'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            );
        }

        function UtmModal({ utm, onSave, onClose }) {
            const [formData, setFormData] = useState(utm || {
                name: '',
                utm_source: '',
                utm_medium: '',
                utm_campaign: '',
                utm_content: '',
                utm_term: '',
                notes: ''
            });

            const handleSubmit = (e) => {
                e.preventDefault();
                if (!formData.name || !formData.utm_source || !formData.utm_medium || !formData.utm_campaign) {
                    alert('Nome, Source, Medium e Campaign são obrigatórios');
                    return;
                }
                onSave(formData);
            };

            const exampleUrl = `https://exemplo.com?utm_source=${formData.utm_source || 'source'}&utm_medium=${formData.utm_medium || 'medium'}&utm_campaign=${formData.utm_campaign || 'campaign'}${formData.utm_content ? '&utm_content=' + formData.utm_content : ''}${formData.utm_term ? '&utm_term=' + formData.utm_term : ''}`;

            return (
                <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 }}>
                    <div style={{ background: 'white', borderRadius: '16px', padding: '30px', width: '90%', maxWidth: '700px', maxHeight: '90vh', overflowY: 'auto' }}>
                        <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '24px' }}>{utm ? 'Editar UTM' : 'Nova UTM'}</h2>

                        <form onSubmit={handleSubmit}>
                            <div style={{ marginBottom: '20px' }}>
                                <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>Nome da Campanha *</label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    style={{ width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: '8px', fontSize: '14px' }}
                                    placeholder="Ex: Black Friday 2024 - Facebook Ads"
                                />
                            </div>

                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
                                <div>
                                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>Source * (origem)</label>
                                    <input
                                        type="text"
                                        value={formData.utm_source}
                                        onChange={(e) => setFormData({ ...formData, utm_source: e.target.value })}
                                        style={{ width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: '8px', fontSize: '14px' }}
                                        placeholder="Ex: facebook, google, instagram"
                                    />
                                </div>
                                <div>
                                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>Medium * (meio)</label>
                                    <input
                                        type="text"
                                        value={formData.utm_medium}
                                        onChange={(e) => setFormData({ ...formData, utm_medium: e.target.value })}
                                        style={{ width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: '8px', fontSize: '14px' }}
                                        placeholder="Ex: cpc, email, social"
                                    />
                                </div>
                            </div>

                            <div style={{ marginBottom: '20px' }}>
                                <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>Campaign * (campanha)</label>
                                <input
                                    type="text"
                                    value={formData.utm_campaign}
                                    onChange={(e) => setFormData({ ...formData, utm_campaign: e.target.value })}
                                    style={{ width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: '8px', fontSize: '14px' }}
                                    placeholder="Ex: black_friday_2024"
                                />
                            </div>

                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
                                <div>
                                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>Content (conteúdo)</label>
                                    <input
                                        type="text"
                                        value={formData.utm_content}
                                        onChange={(e) => setFormData({ ...formData, utm_content: e.target.value })}
                                        style={{ width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: '8px', fontSize: '14px' }}
                                        placeholder="Ex: banner_topo, video_1"
                                    />
                                </div>
                                <div>
                                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>Term (termo)</label>
                                    <input
                                        type="text"
                                        value={formData.utm_term}
                                        onChange={(e) => setFormData({ ...formData, utm_term: e.target.value })}
                                        style={{ width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: '8px', fontSize: '14px' }}
                                        placeholder="Ex: marketing_digital"
                                    />
                                </div>
                            </div>

                            <div style={{ marginBottom: '20px' }}>
                                <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>Observações</label>
                                <textarea
                                    value={formData.notes}
                                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                                    style={{ width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: '8px', fontSize: '14px', minHeight: '60px' }}
                                    placeholder="Anotações sobre esta campanha..."
                                />
                            </div>

                            <div style={{ marginBottom: '20px', background: '#f9fafb', padding: '16px', borderRadius: '8px' }}>
                                <div style={{ fontSize: '12px', fontWeight: '600', color: '#6b7280', marginBottom: '8px' }}>Preview da URL:</div>
                                <div style={{ fontSize: '12px', color: '#4b5563', fontFamily: 'monospace', wordBreak: 'break-all' }}>
                                    {exampleUrl}
                                </div>
                            </div>

                            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                                <button type="button" onClick={onClose} style={{
                                    padding: '10px 20px',
                                    background: '#f3f4f6',
                                    border: 'none',
                                    borderRadius: '8px',
                                    fontSize: '14px',
                                    fontWeight: '600',
                                    cursor: 'pointer'
                                }}>
                                    Cancelar
                                </button>
                                <button type="submit" style={{
                                    padding: '10px 20px',
                                    background: '#667eea',
                                    border: 'none',
                                    borderRadius: '8px',
                                    color: 'white',
                                    fontSize: '14px',
                                    fontWeight: '600',
                                    cursor: 'pointer'
                                }}>
                                    {utm ? 'Salvar Alterações' : 'Criar UTM'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            );
        }

        // ==================== APP ====================

        function App() {
            const [isAuthenticated, setIsAuthenticated] = React.useState(false);
            const [view, setView] = React.useState('dashboard');
            const [funnelId, setFunnelId] = React.useState(null);
            const [showSettings, setShowSettings] = React.useState(false);

            // Verifica autenticação ao montar
            React.useEffect(() => {
                const token = localStorage.getItem('authToken');
                setIsAuthenticated(!!token);
            }, []);

            const handleLogin = () => {
                setIsAuthenticated(true);
            };

            const selectFunnel = (id) => {
                setFunnelId(id);
                setView('editor');
            };

            const backToDashboard = () => {
                setView('dashboard');
                setFunnelId(null);
            };

            const goToMarketing = () => {
                setView('marketing');
            };

            const handleLogout = async () => {
                const token = localStorage.getItem('authToken');

                // Chama API de logout
                if (token) {
                    try {
                        await apiCall('/api/logout', {
                            method: 'DELETE'
                        });
                    } catch (error) {
                        console.error('Erro ao fazer logout:', error);
                    }
                }

                // Remove dados locais
                localStorage.removeItem('authToken');
                localStorage.removeItem('currentUser');

                // Atualiza estado
                setIsAuthenticated(false);
                setView('dashboard');
                setFunnelId(null);
            };

            // Se não está autenticado, mostra tela de login
            if (!isAuthenticated) {
                return <LoginScreen onLogin={handleLogin} />;
            }

            return (
                <>
                    {showSettings && <SettingsPanel onClose={() => setShowSettings(false)} />}
                    {view === 'dashboard' ? (
                        <FunnelDashboard
                            onSelectFunnel={selectFunnel}
                            onOpenSettings={() => setShowSettings(true)}
                            onGoToMarketing={goToMarketing}
                            onLogout={handleLogout}
                        />
                    ) : view === 'marketing' ? (
                        <MarketingManager onBack={backToDashboard} />
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

# Configuração do webhook
# Pode ser configurado via variável de ambiente WEBHOOK_URL
# Exemplo: export WEBHOOK_URL="https://hooks.zapier.com/hooks/catch/123456/abcdef/"
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
if WEBHOOK_URL:
    webhook_manager.configure(WEBHOOK_URL)
    print(f"🔗 Webhook configurado para: {WEBHOOK_URL}")
else:
    print("ℹ️ Webhook não configurado (defina WEBHOOK_URL para ativar)")


class FunnelBuilderHandler(BaseHTTPRequestHandler):
    """Handler HTTP para servir a aplicação Funnel Builder e REST API"""

    def _get_client_ip(self):
        """Obtém IP real do cliente (considera proxies)"""
        # Verifica header de proxy reverso
        forwarded = self.headers.get('X-Forwarded-For')
        if forwarded:
            # Pega o primeiro IP da lista
            return forwarded.split(',')[0].strip()

        # Verifica outros headers de proxy
        real_ip = self.headers.get('X-Real-IP')
        if real_ip:
            return real_ip.strip()

        # Fallback para IP direto
        return self.client_address[0]

    def _send_security_headers(self):
        """Adiciona headers de segurança"""
        # Previne clickjacking
        self.send_header('X-Frame-Options', 'SAMEORIGIN')

        # Previne MIME sniffing
        self.send_header('X-Content-Type-Options', 'nosniff')

        # XSS Protection (legacy, mas ainda útil)
        self.send_header('X-XSS-Protection', '1; mode=block')

        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "frame-ancestors 'none'"
        ]
        self.send_header('Content-Security-Policy', '; '.join(csp_directives))

        # Referrer Policy
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')

    def _send_cors_headers(self):
        """Envia headers CORS restritos"""
        origin = self.headers.get('Origin', '')

        # Valida origem
        if origin in ALLOWED_ORIGINS:
            self.send_header('Access-Control-Allow-Origin', origin)
        else:
            # Fallback para localhost em desenvolvimento
            self.send_header('Access-Control-Allow-Origin', ALLOWED_ORIGINS[0])

        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')  # Cache preflight por 24h

    def _send_json(self, data, status=200):
        """Envia resposta JSON com headers de segurança"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self._send_cors_headers()
        self._send_security_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _get_token(self):
        """Extrai token do header Authorization"""
        auth_header = self.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        return None

    def _read_json_body(self):
        """Lê e parse o corpo JSON da requisição com validações"""
        content_length = int(self.headers.get('Content-Length', 0))

        # Verifica tamanho do payload
        if content_length > MAX_PAYLOAD_SIZE:
            client_ip = self._get_client_ip()
            security_logger.log_payload_too_large(
                ip=client_ip,
                size_bytes=content_length,
                max_size=MAX_PAYLOAD_SIZE
            )
            raise ValueError(f'Payload muito grande. Máximo: {MAX_PAYLOAD_SIZE // (1024*1024)}MB')

        if content_length > 0:
            body = self.rfile.read(content_length)
            try:
                return json.loads(body.decode('utf-8'))
            except json.JSONDecodeError as e:
                raise ValueError(f'JSON inválido: {str(e)}')

        return {}

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self._send_cors_headers()
        self._send_security_headers()
        self.end_headers()

    def log_message(self, format, *args):
        """Sobrescreve log padrão para formato mais limpo"""
        # Log apenas em desenvolvimento ou para erros
        if args[1] not in ['200', '201', '204']:
            print(f"[Funnel Builder] {format % args}")

    def do_GET(self):
        """Responde a requisições GET"""
        # API: Listar funis do usuário
        if self.path == '/api/funnels':
            token = self._get_token()
            user = auth.get_user_from_token(token)

            if not user:
                self._send_json({'error': 'Não autenticado'}, 401)
                return

            funnels = user.get_funnels()
            self._send_json({
                'funnels': [f.to_dict() for f in funnels]
            })
            return

        # API: Buscar funil específico
        if self.path.startswith('/api/funnels/'):
            token = self._get_token()
            user = auth.get_user_from_token(token)

            if not user:
                self._send_json({'error': 'Não autenticado'}, 401)
                return

            funnel_id = int(self.path.split('/')[-1])
            funnel = Funnel.get_by_id(funnel_id, user.id)

            if not funnel:
                self._send_json({'error': 'Funil não encontrado'}, 404)
                return

            self._send_json({'funnel': funnel.to_dict()})
            return

        # ==================== ROTAS DE MARKETING ====================

        # API: Listar páginas
        if self.path.startswith('/api/pages'):
            token = self._get_token()
            user = auth.get_user_from_token(token)

            if not user:
                self._send_json({'error': 'Não autenticado'}, 401)
                return

            # Se tem ID específico: GET /api/pages/:id
            if '/' in self.path[11:]:  # Remove '/api/pages' e verifica se tem mais /
                parts = self.path.split('/')

                # GET /api/pages/:id/metrics
                if len(parts) >= 5 and parts[4] == 'metrics':
                    page_id = int(parts[3])
                    # Parse query params
                    query_params = {}
                    if '?' in self.path:
                        query_string = self.path.split('?')[1]
                        query_params = urllib.parse.parse_qs(query_string)
                        query_params = {k: v[0] for k, v in query_params.items()}

                    status, response = handle_metrics_list(user.id, page_id, query_params)
                    self._send_json(response, status)
                    return

                # GET /api/pages/:id
                page_id = int(parts[3])
                status, response = handle_page_get(user.id, page_id)
                self._send_json(response, status)
                return

            # GET /api/pages (lista)
            query_params = {}
            if '?' in self.path:
                query_string = self.path.split('?')[1]
                query_params = urllib.parse.parse_qs(query_string)
                query_params = {k: v[0] for k, v in query_params.items()}

            status, response = handle_pages_list(user.id, query_params)
            self._send_json(response, status)
            return

        # API: Listar UTMs
        if self.path.startswith('/api/utms'):
            token = self._get_token()
            user = auth.get_user_from_token(token)

            if not user:
                self._send_json({'error': 'Não autenticado'}, 401)
                return

            # Se tem ID específico: GET /api/utms/:id
            if '/' in self.path[10:]:  # Remove '/api/utms' e verifica se tem mais /
                utm_id = int(self.path.split('/')[-1])
                status, response = handle_utm_get(user.id, utm_id)
                self._send_json(response, status)
                return

            # GET /api/utms (lista)
            status, response = handle_utms_list(user.id)
            self._send_json(response, status)
            return

        # Página HTML principal
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML_CONTENT.encode('utf-8'))

    def do_POST(self):
        """Responde a requisições POST"""
        client_ip = self._get_client_ip()
        user_agent = self.headers.get('User-Agent', '')

        try:
            # API: Registrar novo usuário
            if self.path == '/api/register':
                # Rate limiting: 3 tentativas de registro por 10 minutos
                allowed, retry_after = rate_limiter.is_allowed(client_ip, 'register')
                if not allowed:
                    security_logger.log_rate_limit_exceeded(client_ip, 'register', retry_after)
                    self._send_json({
                        'error': f'Muitas tentativas de registro. Tente novamente em {retry_after} segundos.'
                    }, 429)
                    return

                data = self._read_json_body()
                email = data.get('email', '')

                result = auth.register(
                    email=email,
                    password=data.get('password'),
                    name=data.get('name'),
                    whatsapp=data.get('whatsapp')
                )

                if result['success']:
                    # Log sucesso
                    security_logger.log_registration(
                        user_id=result['user'].id,
                        email=email,
                        ip=client_ip
                    )

                    # Reseta rate limit após sucesso
                    rate_limiter.reset(client_ip, 'register')

                    # Envia webhook de novo usuário registrado
                    webhook_manager.on_user_registered(result['user'].to_dict())

                    self._send_json({
                        'success': True,
                        'message': result['message'],
                        'token': result['token'],
                        'user': result['user'].to_dict()
                    })
                else:
                    # Log falha
                    security_logger.log_registration_failure(
                        email=email,
                        ip=client_ip,
                        reason=result['message']
                    )

                    self._send_json({
                        'success': False,
                        'message': result['message']
                    }, 400)
                return

            # API: Login
            if self.path == '/api/login':
                # Rate limiting: 5 tentativas de login por 5 minutos
                allowed, retry_after = rate_limiter.is_allowed(client_ip, 'login')
                if not allowed:
                    security_logger.log_rate_limit_exceeded(client_ip, 'login', retry_after)
                    self._send_json({
                        'error': f'Muitas tentativas de login. Tente novamente em {retry_after} segundos.'
                    }, 429)
                    return

                data = self._read_json_body()
                email = data.get('email', '')

                # Log tentativa
                security_logger.log_login_attempt(email, client_ip, user_agent)

                result = auth.login(
                    email=email,
                    password=data.get('password')
                )

                if result['success']:
                    # Log sucesso
                    security_logger.log_login_success(
                        user_id=result['user'].id,
                        email=email,
                        ip=client_ip
                    )

                    # Reseta rate limit após sucesso
                    rate_limiter.reset(client_ip, 'login')

                    self._send_json({
                        'success': True,
                        'message': result['message'],
                        'token': result['token'],
                        'user': result['user'].to_dict()
                    })
                else:
                    # Log falha
                    security_logger.log_login_failure(
                        email=email,
                        ip=client_ip,
                        reason=result['message']
                    )

                    # Detecta possível brute force
                    failed_count = security_logger.get_failed_logins_by_ip(client_ip, minutes=10)
                    if failed_count >= 10:
                        security_logger.log_brute_force_attempt(client_ip, email, failed_count)

                    self._send_json({
                        'success': False,
                        'message': result['message']
                    }, 401)
                return

            # API: Criar novo funil
            if self.path == '/api/funnels':
                # Rate limiting para operações de escrita
                allowed, retry_after = rate_limiter.is_allowed(client_ip, 'api_write')
                if not allowed:
                    security_logger.log_rate_limit_exceeded(client_ip, 'api_write', retry_after)
                    self._send_json({
                        'error': f'Muitas requisições. Tente novamente em {retry_after} segundos.'
                    }, 429)
                    return

                token = self._get_token()
                user = auth.get_user_from_token(token)

                if not user:
                    security_logger.log_invalid_token(token or 'none', client_ip)
                    self._send_json({'error': 'Não autenticado'}, 401)
                    return

                data = self._read_json_body()
                funnel = user.create_funnel(
                    name=data.get('name', 'Novo Funil'),
                    icon=data.get('icon', '🚀'),
                    elements=data.get('elements', []),
                    connections=data.get('connections', [])
                )

                # Log operação
                security_logger.log_funnel_created(
                    user_id=user.id,
                    funnel_id=funnel.id,
                    ip=client_ip
                )

                self._send_json({
                    'success': True,
                    'funnel': funnel.to_dict()
                }, 201)
                return

            # ==================== ROTAS POST DE MARKETING ====================

            # API: Criar nova página
            if self.path == '/api/pages':
                allowed, retry_after = rate_limiter.is_allowed(client_ip, 'api_write')
                if not allowed:
                    self._send_json({
                        'error': f'Muitas requisições. Tente novamente em {retry_after} segundos.'
                    }, 429)
                    return

                token = self._get_token()
                user = auth.get_user_from_token(token)

                if not user:
                    self._send_json({'error': 'Não autenticado'}, 401)
                    return

                data = self._read_json_body()
                status, response = handle_page_create(user.id, data)
                self._send_json(response, status)
                return

            # API: Adicionar teste a uma página
            if self.path.startswith('/api/pages/') and '/tests' in self.path:
                allowed, retry_after = rate_limiter.is_allowed(client_ip, 'api_write')
                if not allowed:
                    self._send_json({
                        'error': f'Muitas requisições. Tente novamente em {retry_after} segundos.'
                    }, 429)
                    return

                token = self._get_token()
                user = auth.get_user_from_token(token)

                if not user:
                    self._send_json({'error': 'Não autenticado'}, 401)
                    return

                parts = self.path.split('/')
                page_id = int(parts[3])
                data = self._read_json_body()
                status, response = handle_page_test_create(user.id, page_id, data)
                self._send_json(response, status)
                return

            # API: Adicionar métricas a uma página
            if self.path.startswith('/api/pages/') and '/metrics' in self.path:
                allowed, retry_after = rate_limiter.is_allowed(client_ip, 'api_write')
                if not allowed:
                    self._send_json({
                        'error': f'Muitas requisições. Tente novamente em {retry_after} segundos.'
                    }, 429)
                    return

                token = self._get_token()
                user = auth.get_user_from_token(token)

                if not user:
                    self._send_json({'error': 'Não autenticado'}, 401)
                    return

                parts = self.path.split('/')
                page_id = int(parts[3])
                data = self._read_json_body()
                status, response = handle_metrics_create(user.id, page_id, data)
                self._send_json(response, status)
                return

            # API: Criar nova UTM
            if self.path == '/api/utms':
                allowed, retry_after = rate_limiter.is_allowed(client_ip, 'api_write')
                if not allowed:
                    self._send_json({
                        'error': f'Muitas requisições. Tente novamente em {retry_after} segundos.'
                    }, 429)
                    return

                token = self._get_token()
                user = auth.get_user_from_token(token)

                if not user:
                    self._send_json({'error': 'Não autenticado'}, 401)
                    return

                data = self._read_json_body()
                status, response = handle_utm_create(user.id, data)
                self._send_json(response, status)
                return

            # API: Gerar URL com UTM
            if self.path.startswith('/api/utms/') and '/generate' in self.path:
                token = self._get_token()
                user = auth.get_user_from_token(token)

                if not user:
                    self._send_json({'error': 'Não autenticado'}, 401)
                    return

                parts = self.path.split('/')
                utm_id = int(parts[3])
                data = self._read_json_body()
                status, response = handle_utm_generate_url(user.id, utm_id, data)
                self._send_json(response, status)
                return

            self._send_json({'error': 'Endpoint não encontrado'}, 404)

        except ValueError as e:
            # Erro de validação (payload, JSON, etc)
            security_logger.log_api_error(
                endpoint=self.path,
                method='POST',
                ip=client_ip,
                error=str(e),
                status_code=400
            )
            self._send_json({'error': str(e)}, 400)

        except Exception as e:
            # Erro inesperado
            security_logger.log_api_error(
                endpoint=self.path,
                method='POST',
                ip=client_ip,
                error=str(e),
                status_code=500
            )
            self._send_json({'error': 'Erro interno do servidor'}, 500)

    def do_PUT(self):
        """Responde a requisições PUT"""
        # API: Atualizar funil
        if self.path.startswith('/api/funnels/'):
            token = self._get_token()
            user = auth.get_user_from_token(token)

            if not user:
                self._send_json({'error': 'Não autenticado'}, 401)
                return

            funnel_id = int(self.path.split('/')[-1])
            funnel = Funnel.get_by_id(funnel_id, user.id)

            if not funnel:
                self._send_json({'error': 'Funil não encontrado'}, 404)
                return

            data = self._read_json_body()
            success = funnel.update(
                name=data.get('name'),
                icon=data.get('icon'),
                elements=data.get('elements'),
                connections=data.get('connections')
            )

            if success:
                self._send_json({
                    'success': True,
                    'funnel': funnel.to_dict()
                })
            else:
                self._send_json({'error': 'Erro ao atualizar funil'}, 500)
            return

        # ==================== ROTAS PUT DE MARKETING ====================

        # API: Atualizar página
        if self.path.startswith('/api/pages/'):
            token = self._get_token()
            user = auth.get_user_from_token(token)

            if not user:
                self._send_json({'error': 'Não autenticado'}, 401)
                return

            page_id = int(self.path.split('/')[3])
            data = self._read_json_body()
            status, response = handle_page_update(user.id, page_id, data)
            self._send_json(response, status)
            return

        # API: Atualizar UTM
        if self.path.startswith('/api/utms/'):
            token = self._get_token()
            user = auth.get_user_from_token(token)

            if not user:
                self._send_json({'error': 'Não autenticado'}, 401)
                return

            utm_id = int(self.path.split('/')[3])
            data = self._read_json_body()
            status, response = handle_utm_update(user.id, utm_id, data)
            self._send_json(response, status)
            return

        self._send_json({'error': 'Endpoint não encontrado'}, 404)

    def do_DELETE(self):
        """Responde a requisições DELETE"""
        client_ip = self._get_client_ip()

        try:
            # API: Deletar funil
            if self.path.startswith('/api/funnels/'):
                # Rate limiting
                allowed, retry_after = rate_limiter.is_allowed(client_ip, 'api_write')
                if not allowed:
                    security_logger.log_rate_limit_exceeded(client_ip, 'api_write', retry_after)
                    self._send_json({
                        'error': f'Muitas requisições. Tente novamente em {retry_after} segundos.'
                    }, 429)
                    return

                token = self._get_token()
                user = auth.get_user_from_token(token)

                if not user:
                    security_logger.log_invalid_token(token or 'none', client_ip)
                    self._send_json({'error': 'Não autenticado'}, 401)
                    return

                funnel_id = int(self.path.split('/')[-1])
                funnel = Funnel.get_by_id(funnel_id, user.id)

                if not funnel:
                    security_logger.log_unauthorized_access(
                        user_id=user.id,
                        resource=f'funnel:{funnel_id}',
                        ip=client_ip
                    )
                    self._send_json({'error': 'Funil não encontrado'}, 404)
                    return

                success = funnel.delete()

                if success:
                    # Log operação
                    security_logger.log_funnel_deleted(
                        user_id=user.id,
                        funnel_id=funnel_id,
                        ip=client_ip
                    )
                    self._send_json({'success': True, 'message': 'Funil deletado'})
                else:
                    self._send_json({'error': 'Erro ao deletar funil'}, 500)
                return

            # ==================== ROTAS DELETE DE MARKETING ====================

            # API: Deletar página
            if self.path.startswith('/api/pages/') and not '/tests' in self.path:
                allowed, retry_after = rate_limiter.is_allowed(client_ip, 'api_write')
                if not allowed:
                    self._send_json({
                        'error': f'Muitas requisições. Tente novamente em {retry_after} segundos.'
                    }, 429)
                    return

                token = self._get_token()
                user = auth.get_user_from_token(token)

                if not user:
                    self._send_json({'error': 'Não autenticado'}, 401)
                    return

                page_id = int(self.path.split('/')[3])
                status, response = handle_page_delete(user.id, page_id)
                self._send_json(response, status)
                return

            # API: Deletar teste de página
            if self.path.startswith('/api/pages/tests/'):
                allowed, retry_after = rate_limiter.is_allowed(client_ip, 'api_write')
                if not allowed:
                    self._send_json({
                        'error': f'Muitas requisições. Tente novamente em {retry_after} segundos.'
                    }, 429)
                    return

                token = self._get_token()
                user = auth.get_user_from_token(token)

                if not user:
                    self._send_json({'error': 'Não autenticado'}, 401)
                    return

                test_id = int(self.path.split('/')[-1])
                status, response = handle_page_test_delete(user.id, test_id)
                self._send_json(response, status)
                return

            # API: Deletar métricas
            if self.path.startswith('/api/metrics/'):
                allowed, retry_after = rate_limiter.is_allowed(client_ip, 'api_write')
                if not allowed:
                    self._send_json({
                        'error': f'Muitas requisições. Tente novamente em {retry_after} segundos.'
                    }, 429)
                    return

                token = self._get_token()
                user = auth.get_user_from_token(token)

                if not user:
                    self._send_json({'error': 'Não autenticado'}, 401)
                    return

                metric_id = int(self.path.split('/')[-1])
                status, response = handle_metrics_delete(user.id, metric_id)
                self._send_json(response, status)
                return

            # API: Deletar UTM
            if self.path.startswith('/api/utms/'):
                allowed, retry_after = rate_limiter.is_allowed(client_ip, 'api_write')
                if not allowed:
                    self._send_json({
                        'error': f'Muitas requisições. Tente novamente em {retry_after} segundos.'
                    }, 429)
                    return

                token = self._get_token()
                user = auth.get_user_from_token(token)

                if not user:
                    self._send_json({'error': 'Não autenticado'}, 401)
                    return

                utm_id = int(self.path.split('/')[3])
                status, response = handle_utm_delete(user.id, utm_id)
                self._send_json(response, status)
                return

            # API: Logout
            if self.path == '/api/logout':
                token = self._get_token()
                user = auth.get_user_from_token(token)

                if token and user:
                    auth.logout(token)
                    security_logger.log_logout(user.id, client_ip)

                self._send_json({'success': True, 'message': 'Logout realizado'})
                return

            self._send_json({'error': 'Endpoint não encontrado'}, 404)

        except Exception as e:
            security_logger.log_api_error(
                endpoint=self.path,
                method='DELETE',
                ip=client_ip,
                error=str(e),
                status_code=500
            )
            self._send_json({'error': 'Erro interno do servidor'}, 500)


def open_browser(port):
    """Abre o navegador após um pequeno delay"""
    import time
    time.sleep(1)
    webbrowser.open(f'http://localhost:{port}')


def cleanup_task():
    """Task periódica para limpar rate limiter e sessões expiradas"""
    import time
    while True:
        time.sleep(300)  # A cada 5 minutos
        try:
            rate_limiter.cleanup_old_entries()
            auth.cleanup_expired_sessions()
        except Exception as e:
            print(f"⚠️ Erro no cleanup: {e}")


def run_server(port=8000):
    """Inicia o servidor HTTP"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, FunnelBuilderHandler)

    # Log de início do servidor
    security_logger.log_server_start(port)

    print("=" * 70)
    print("🚀 FUNNEL BUILDER - Sistema de Construção de Funis")
    print("=" * 70)
    print(f"\n✅ Servidor iniciado com sucesso!")
    print(f"🌐 Acesse: http://localhost:{port}")
    print(f"\n🔒 Proteções de Segurança Ativas:")
    print("   ✓ Rate Limiting (brute force protection)")
    print("   ✓ CORS Restrito")
    print("   ✓ Senhas Fortes Obrigatórias")
    print("   ✓ Headers de Segurança (CSP, X-Frame-Options)")
    print("   ✓ Validação de Inputs")
    print("   ✓ Logs de Auditoria")
    print(f"\n📖 Como usar:")
    print("   1. Arraste elementos da barra lateral para o canvas")
    print("   2. Clique no botão 🔗 para conectar elementos")
    print("   3. Clique em um elemento para editar suas propriedades")
    print("   4. Use o botão 🗑️ para deletar elementos")
    print(f"\n⚠️  Pressione Ctrl+C para parar o servidor\n")
    print("=" * 70)

    # Inicia thread de cleanup
    cleanup_thread = threading.Thread(target=cleanup_task)
    cleanup_thread.daemon = True
    cleanup_thread.start()

    # Abre o navegador em uma thread separada
    browser_thread = threading.Thread(target=open_browser, args=(port,))
    browser_thread.daemon = True
    browser_thread.start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor encerrado pelo usuário")
        security_logger.log_server_stop()
        httpd.server_close()


if __name__ == '__main__':
    run_server()
