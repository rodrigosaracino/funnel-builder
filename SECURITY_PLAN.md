# 🔒 PLANO DE SEGURANÇA - FUNNEL BUILDER

## 📋 Sumário Executivo

Este documento apresenta um plano completo de segurança para o sistema Funnel Builder, identificando vulnerabilidades atuais e propondo soluções práticas para proteger contra ataques comuns.

**Prioridade**: 🔴 CRÍTICA - Sistema atualmente vulnerável a múltiplos vetores de ataque

---

## 🎯 Objetivo

Transformar o Funnel Builder em uma aplicação segura e resiliente contra:
- ✅ Ataques de força bruta
- ✅ Injeção de SQL
- ✅ Cross-Site Scripting (XSS)
- ✅ Cross-Site Request Forgery (CSRF)
- ✅ Ataques DDoS
- ✅ Vazamento de dados sensíveis
- ✅ Sequestro de sessão
- ✅ Enumeração de usuários

---

## 🔍 ANÁLISE DE VULNERABILIDADES ATUAIS

### 🚨 CRÍTICAS (Corrigir Imediatamente)

#### 1. **Sessões em Memória**
**Arquivo**: `auth.py:20`
```python
self.sessions = {}  # ❌ Perdidas em restart/crash
```
**Risco**:
- Sessões perdidas em qualquer restart do servidor
- Não funciona em ambientes multi-instância (load balancer)
- Impossível fazer logout distribuído

**Impacto**: 🔴 CRÍTICO

---

#### 2. **CORS Totalmente Aberto**
**Arquivo**: `funnel_builder.py:4377`
```python
self.send_header('Access-Control-Allow-Origin', '*')  # ❌ Qualquer origem
```
**Risco**:
- Qualquer site pode fazer requisições à API
- Facilita ataques CSRF
- Exposição de dados sensíveis

**Impacto**: 🔴 CRÍTICO

---

#### 3. **Sem Rate Limiting**
**Risco**:
- Ataques de força bruta em `/api/login` ilimitados
- Possível DDoS no servidor
- Enumeração de usuários via tentativa e erro

**Impacto**: 🔴 CRÍTICO

---

#### 4. **Senha Fraca (Mínimo 6 caracteres)**
**Arquivo**: `auth.py:56`
```python
if len(password) < 6:  # ❌ Muito fraco
```
**Risco**:
- Senhas fracas facilmente quebradas (ex: "123456")
- Violação de melhores práticas (OWASP recomenda min. 8)

**Impacto**: 🔴 CRÍTICO

---

#### 5. **Sem Limite de Payload**
**Arquivo**: `funnel_builder.py:4368`
```python
content_length = int(self.headers.get('Content-Length', 0))
if content_length > 0:
    body = self.rfile.read(content_length)  # ❌ Sem limite!
```
**Risco**:
- Aceita payloads de qualquer tamanho
- Possível DoS através de requisições gigantes
- Esgotamento de memória

**Impacto**: 🔴 CRÍTICO

---

### ⚠️ ALTAS (Corrigir em Breve)

#### 6. **HTTP sem HTTPS**
**Risco**:
- Credenciais trafegam em texto plano
- Tokens podem ser interceptados (man-in-the-middle)
- Violação de LGPD/GDPR

**Impacto**: 🟠 ALTO

---

#### 7. **Sem Headers de Segurança**
**Headers ausentes**:
- `Content-Security-Policy` (proteção XSS)
- `X-Frame-Options` (proteção clickjacking)
- `X-Content-Type-Options` (proteção MIME sniffing)
- `Strict-Transport-Security` (force HTTPS)
- `Referrer-Policy` (vazamento de informações)

**Impacto**: 🟠 ALTO

---

#### 8. **Sem Sistema de Logs de Segurança**
**Risco**:
- Impossível detectar tentativas de invasão
- Sem auditoria de acessos
- Dificulta resposta a incidentes

**Impacto**: 🟠 ALTO

---

#### 9. **Tokens Sem Expiração Automática**
**Arquivo**: `auth.py:21`
```python
self.session_duration = 24 * 60 * 60  # 24 horas
```
**Risco**:
- Sessão válida por 24h mesmo sem atividade
- Tokens não expiram automaticamente
- Método `cleanup_expired_sessions` nunca é chamado

**Impacto**: 🟠 ALTO

---

#### 10. **Webhooks Sem Autenticação**
**Arquivo**: `webhooks.py:48-82`
**Risco**:
- Webhook URL pode vazar dados sensíveis
- Nenhuma verificação se o endpoint é confiável
- Dados de usuários enviados sem criptografia adicional

**Impacto**: 🟠 ALTO

---

### 🟡 MÉDIAS (Corrigir Gradualmente)

#### 11. **Validação de Email Inexistente**
**Risco**:
- Aceita qualquer string como email
- Possível injeção através de campos de email

**Impacto**: 🟡 MÉDIO

---

#### 12. **Mensagens de Erro Muito Detalhadas**
**Arquivo**: `auth.py:125-128`
```python
if not user_data:
    return {'message': 'Email ou senha incorretos'}  # ✅ BOM
```
**Status**: ✅ Correto, mas precisa garantir em todos os endpoints

**Impacto**: 🟡 MÉDIO

---

#### 13. **Sem Proteção CSRF**
**Risco**:
- Atacante pode forjar requisições em nome do usuário
- Principalmente perigoso em operações DELETE/PUT

**Impacto**: 🟡 MÉDIO

---

#### 14. **Banco SQLite em Produção**
**Arquivo**: `database.py:16-23`
**Risco**:
- SQLite não é ideal para múltiplos acessos simultâneos
- Não suporta múltiplas instâncias da aplicação
- Lock de arquivo pode causar problemas

**Impacto**: 🟡 MÉDIO (para escala)

---

### ✅ PONTOS POSITIVOS (Já Implementados)

1. **Parametrização SQL** ✅ - Proteção contra SQL Injection
2. **Bcrypt para Senhas** ✅ - Hash seguro com salt
3. **Tokens Aleatórios** ✅ - Usa `secrets.token_urlsafe()`
4. **Validação de Propriedade** ✅ - Verifica `user_id` antes de operações
5. **React Frontend** ✅ - Escaping automático de XSS

---

## 🛡️ PLANO DE AÇÃO

### FASE 1: Correções Críticas (1-2 semanas)

#### 1.1 Implementar Redis para Sessões
**Prioridade**: 🔴 CRÍTICA

**Implementação**:
```python
# requirements.txt
redis==5.0.1

# auth.py - Substituir dict por Redis
import redis

class Auth:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=0,
            decode_responses=True
        )
        self.session_duration = 24 * 60 * 60

    def create_session(self, user_id: int) -> str:
        token = self.generate_token()
        session_key = f"session:{token}"

        self.redis_client.setex(
            session_key,
            self.session_duration,
            json.dumps({'user_id': user_id})
        )

        return token

    def get_user_from_token(self, token: str) -> Optional[User]:
        session_key = f"session:{token}"
        session_data = self.redis_client.get(session_key)

        if not session_data:
            return None

        data = json.loads(session_data)
        return User.get_by_id(data['user_id'])
```

**Docker Compose**:
```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes

  funnel-builder:
    depends_on:
      - redis
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379

volumes:
  redis-data:
```

---

#### 1.2 Implementar Rate Limiting
**Prioridade**: 🔴 CRÍTICA

**Implementação**:
```python
# rate_limiter.py
import time
from collections import defaultdict
from threading import Lock

class RateLimiter:
    """Rate limiter usando sliding window"""

    def __init__(self):
        # IP -> [(timestamp, count)]
        self.attempts = defaultdict(list)
        self.lock = Lock()

        # Configurações
        self.max_attempts = {
            'login': 5,      # 5 tentativas
            'register': 3,   # 3 tentativas
            'api': 100       # 100 requisições
        }

        self.windows = {
            'login': 300,    # 5 minutos
            'register': 600, # 10 minutos
            'api': 60        # 1 minuto
        }

    def is_allowed(self, identifier: str, action: str = 'api') -> tuple[bool, int]:
        """
        Verifica se a requisição é permitida

        Returns:
            (allowed, remaining_attempts)
        """
        with self.lock:
            now = time.time()
            window = self.windows.get(action, 60)
            max_attempts = self.max_attempts.get(action, 100)

            # Remove tentativas antigas
            self.attempts[identifier] = [
                t for t in self.attempts[identifier]
                if now - t < window
            ]

            # Verifica limite
            current_attempts = len(self.attempts[identifier])

            if current_attempts >= max_attempts:
                return False, 0

            # Registra tentativa
            self.attempts[identifier].append(now)

            remaining = max_attempts - current_attempts - 1
            return True, remaining

    def cleanup_old_entries(self):
        """Remove entradas antigas (executar periodicamente)"""
        with self.lock:
            now = time.time()
            max_window = max(self.windows.values())

            for identifier in list(self.attempts.keys()):
                self.attempts[identifier] = [
                    t for t in self.attempts[identifier]
                    if now - t < max_window
                ]

                if not self.attempts[identifier]:
                    del self.attempts[identifier]

# rate_limiter global
rate_limiter = RateLimiter()
```

**Uso no Handler**:
```python
# funnel_builder.py
from rate_limiter import rate_limiter

class FunnelBuilderHandler(BaseHTTPRequestHandler):

    def _get_client_ip(self):
        """Obtém IP do cliente"""
        # Considera proxy reverso
        forwarded = self.headers.get('X-Forwarded-For')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return self.client_address[0]

    def do_POST(self):
        client_ip = self._get_client_ip()

        # Rate limit para login
        if self.path == '/api/login':
            allowed, remaining = rate_limiter.is_allowed(client_ip, 'login')

            if not allowed:
                self._send_json({
                    'error': 'Muitas tentativas. Tente novamente em 5 minutos.'
                }, 429)
                return

            # Adiciona header com tentativas restantes
            self.send_header('X-RateLimit-Remaining', str(remaining))

            # ... resto do código de login
```

---

#### 1.3 Restringir CORS
**Prioridade**: 🔴 CRÍTICA

**Implementação**:
```python
# funnel_builder.py
ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'https://funnel-builder.seudominio.com',
    'https://app.seudominio.com'
]

class FunnelBuilderHandler(BaseHTTPRequestHandler):

    def _send_cors_headers(self):
        """Envia headers CORS restritos"""
        origin = self.headers.get('Origin', '')

        # Valida origem
        if origin in ALLOWED_ORIGINS:
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Access-Control-Allow-Credentials', 'true')
        else:
            # Não permite origens não autorizadas
            self.send_header('Access-Control-Allow-Origin', ALLOWED_ORIGINS[0])

        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')  # Cache preflight 24h

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
```

---

#### 1.4 Aumentar Requisitos de Senha
**Prioridade**: 🔴 CRÍTICA

**Implementação**:
```python
# auth.py
import re

class Auth:

    def validate_password(self, password: str) -> tuple[bool, str]:
        """
        Valida força da senha

        Returns:
            (is_valid, error_message)
        """
        if len(password) < 8:
            return False, 'Senha deve ter no mínimo 8 caracteres'

        if len(password) > 128:
            return False, 'Senha muito longa (máximo 128 caracteres)'

        # Pelo menos uma letra maiúscula
        if not re.search(r'[A-Z]', password):
            return False, 'Senha deve conter pelo menos uma letra maiúscula'

        # Pelo menos uma letra minúscula
        if not re.search(r'[a-z]', password):
            return False, 'Senha deve conter pelo menos uma letra minúscula'

        # Pelo menos um número
        if not re.search(r'\d', password):
            return False, 'Senha deve conter pelo menos um número'

        # Pelo menos um caractere especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, 'Senha deve conter pelo menos um caractere especial'

        # Verifica senhas comuns (lista top 1000)
        common_passwords = ['123456', 'password', '12345678', 'qwerty', ...]
        if password.lower() in common_passwords:
            return False, 'Senha muito comum. Escolha uma senha mais segura'

        return True, ''

    def register(self, email: str, password: str, name: str = None, whatsapp: str = None):
        # Valida senha
        is_valid, error_msg = self.validate_password(password)
        if not is_valid:
            return {
                'success': False,
                'message': error_msg,
                'user': None,
                'token': None
            }

        # ... resto do código
```

---

#### 1.5 Limitar Tamanho de Payload
**Prioridade**: 🔴 CRÍTICA

**Implementação**:
```python
# funnel_builder.py
MAX_PAYLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

class FunnelBuilderHandler(BaseHTTPRequestHandler):

    def _read_json_body(self):
        """Lê e parse o corpo JSON da requisição com limite"""
        content_length = int(self.headers.get('Content-Length', 0))

        # Verifica tamanho
        if content_length > MAX_PAYLOAD_SIZE:
            raise ValueError(f'Payload muito grande (máximo: {MAX_PAYLOAD_SIZE} bytes)')

        if content_length > 0:
            body = self.rfile.read(content_length)
            return json.loads(body.decode('utf-8'))

        return {}

    def do_POST(self):
        try:
            data = self._read_json_body()
            # ... processar requisição
        except ValueError as e:
            self._send_json({'error': str(e)}, 413)  # Payload Too Large
            return
        except json.JSONDecodeError:
            self._send_json({'error': 'JSON inválido'}, 400)
            return
```

---

### FASE 2: Melhorias de Segurança (2-3 semanas)

#### 2.1 Implementar HTTPS
**Prioridade**: 🟠 ALTA

**Opção 1: Usando Nginx como Reverse Proxy**

```yaml
# docker-compose.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - funnel-builder

  funnel-builder:
    # Remove exposição de porta externa
    # ports:
    #   - "8000:8000"
    expose:
      - "8000"
```

```nginx
# nginx.conf
http {
    # Redireciona HTTP para HTTPS
    server {
        listen 80;
        server_name funnel-builder.seudominio.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS
    server {
        listen 443 ssl http2;
        server_name funnel-builder.seudominio.com;

        # Certificados SSL (Let's Encrypt)
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # Configurações SSL modernas
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # HSTS
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Outros headers de segurança
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # CSP
        add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:;" always;

        location / {
            proxy_pass http://funnel-builder:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

**Opção 2: Usando Certbot (Let's Encrypt)**

```bash
# Script para obter certificado SSL gratuito
docker run -it --rm \
  -v ./ssl:/etc/letsencrypt \
  certbot/certbot certonly \
  --standalone \
  -d funnel-builder.seudominio.com \
  --agree-tos \
  --email seu-email@exemplo.com
```

---

#### 2.2 Adicionar Headers de Segurança
**Prioridade**: 🟠 ALTA

**Implementação**:
```python
# funnel_builder.py
class FunnelBuilderHandler(BaseHTTPRequestHandler):

    def _send_security_headers(self):
        """Adiciona headers de segurança"""

        # Previne clickjacking
        self.send_header('X-Frame-Options', 'SAMEORIGIN')

        # Previne MIME sniffing
        self.send_header('X-Content-Type-Options', 'nosniff')

        # XSS Protection (legacy, mas ainda útil)
        self.send_header('X-XSS-Protection', '1; mode=block')

        # HSTS - Force HTTPS (apenas se usando HTTPS!)
        if self.is_https():
            self.send_header(
                'Strict-Transport-Security',
                'max-age=31536000; includeSubDomains; preload'
            )

        # Content Security Policy
        csp = "; ".join([
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ])
        self.send_header('Content-Security-Policy', csp)

        # Referrer Policy
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')

        # Permissions Policy
        permissions = ", ".join([
            "geolocation=()",
            "microphone=()",
            "camera=()"
        ])
        self.send_header('Permissions-Policy', permissions)

    def is_https(self):
        """Verifica se está usando HTTPS"""
        # Verifica header de proxy reverso
        proto = self.headers.get('X-Forwarded-Proto', '')
        return proto == 'https'

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self._send_cors_headers()
        self._send_security_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
```

---

#### 2.3 Sistema de Logs de Segurança
**Prioridade**: 🟠 ALTA

**Implementação**:
```python
# security_logger.py
import logging
import json
from datetime import datetime
from typing import Dict, Any

class SecurityLogger:
    """Logger especializado para eventos de segurança"""

    def __init__(self, log_file='security.log'):
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)

        # Handler para arquivo
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # Formato JSON estruturado
        formatter = logging.Formatter(
            '%(message)s'
        )
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """Log estruturado em JSON"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event_type': event_type,
            **data
        }
        self.logger.info(json.dumps(log_entry))

    def log_login_attempt(self, email: str, ip: str, success: bool, user_agent: str = None):
        """Log de tentativa de login"""
        self._log_event('login_attempt', {
            'email': email,
            'ip': ip,
            'success': success,
            'user_agent': user_agent
        })

    def log_login_success(self, user_id: int, email: str, ip: str):
        """Log de login bem-sucedido"""
        self._log_event('login_success', {
            'user_id': user_id,
            'email': email,
            'ip': ip
        })

    def log_login_failure(self, email: str, ip: str, reason: str):
        """Log de falha de login"""
        self._log_event('login_failure', {
            'email': email,
            'ip': ip,
            'reason': reason
        })

    def log_rate_limit_exceeded(self, ip: str, action: str):
        """Log de rate limit excedido"""
        self._log_event('rate_limit_exceeded', {
            'ip': ip,
            'action': action
        })

    def log_suspicious_activity(self, ip: str, description: str, details: Dict = None):
        """Log de atividade suspeita"""
        self._log_event('suspicious_activity', {
            'ip': ip,
            'description': description,
            'details': details or {}
        })

    def log_registration(self, user_id: int, email: str, ip: str):
        """Log de novo registro"""
        self._log_event('user_registration', {
            'user_id': user_id,
            'email': email,
            'ip': ip
        })

    def log_password_change(self, user_id: int, ip: str):
        """Log de mudança de senha"""
        self._log_event('password_change', {
            'user_id': user_id,
            'ip': ip
        })

    def log_api_error(self, endpoint: str, ip: str, error: str):
        """Log de erro de API"""
        self._log_event('api_error', {
            'endpoint': endpoint,
            'ip': ip,
            'error': error
        })

# Instância global
security_logger = SecurityLogger('/app/data/security.log')
```

**Uso**:
```python
# funnel_builder.py
from security_logger import security_logger

class FunnelBuilderHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path == '/api/login':
            client_ip = self._get_client_ip()
            user_agent = self.headers.get('User-Agent', '')
            data = self._read_json_body()
            email = data.get('email')

            # Log tentativa
            security_logger.log_login_attempt(
                email=email,
                ip=client_ip,
                success=False,
                user_agent=user_agent
            )

            result = auth.login(email, data.get('password'))

            if result['success']:
                security_logger.log_login_success(
                    user_id=result['user'].id,
                    email=email,
                    ip=client_ip
                )
            else:
                security_logger.log_login_failure(
                    email=email,
                    ip=client_ip,
                    reason=result['message']
                )
```

---

#### 2.4 Validação de Email
**Prioridade**: 🟠 ALTA

**Implementação**:
```python
# validators.py
import re
from typing import Tuple

def validate_email(email: str) -> Tuple[bool, str]:
    """
    Valida formato de email

    Returns:
        (is_valid, error_message)
    """
    if not email:
        return False, 'Email é obrigatório'

    # Tamanho máximo
    if len(email) > 254:
        return False, 'Email muito longo'

    # Regex RFC 5322 simplificado
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(email_regex, email):
        return False, 'Email inválido'

    # Lista negra de domínios temporários (opcional)
    temp_domains = ['tempmail.com', '10minutemail.com', 'guerrillamail.com']
    domain = email.split('@')[1].lower()

    if domain in temp_domains:
        return False, 'Email temporário não permitido'

    return True, ''

def validate_whatsapp(whatsapp: str) -> Tuple[bool, str]:
    """
    Valida número de WhatsApp

    Returns:
        (is_valid, error_message)
    """
    if not whatsapp:
        return False, 'WhatsApp é obrigatório'

    # Remove caracteres não numéricos
    digits = re.sub(r'\D', '', whatsapp)

    # Valida tamanho (mínimo 10, máximo 15)
    if len(digits) < 10:
        return False, 'WhatsApp muito curto'

    if len(digits) > 15:
        return False, 'WhatsApp muito longo'

    return True, ''

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitiza input de texto
    """
    if not text:
        return ''

    # Remove caracteres de controle
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')

    # Limita tamanho
    text = text[:max_length]

    # Trim
    text = text.strip()

    return text
```

**Uso**:
```python
# auth.py
from validators import validate_email, validate_whatsapp, sanitize_input

class Auth:

    def register(self, email: str, password: str, name: str = None, whatsapp: str = None):
        # Valida email
        is_valid, error_msg = validate_email(email)
        if not is_valid:
            return {
                'success': False,
                'message': error_msg,
                'user': None,
                'token': None
            }

        # Normaliza email
        email = email.lower().strip()

        # Valida WhatsApp
        is_valid, error_msg = validate_whatsapp(whatsapp)
        if not is_valid:
            return {
                'success': False,
                'message': error_msg,
                'user': None,
                'token': None
            }

        # Sanitiza name
        if name:
            name = sanitize_input(name, max_length=100)

        # ... resto do código
```

---

#### 2.5 Proteção CSRF
**Prioridade**: 🟡 MÉDIA

**Implementação**:
```python
# csrf.py
import secrets
import time
from typing import Optional

class CSRFProtection:
    """Proteção contra CSRF usando tokens"""

    def __init__(self):
        # token -> timestamp
        self.tokens = {}
        self.token_duration = 3600  # 1 hora

    def generate_token(self) -> str:
        """Gera token CSRF"""
        token = secrets.token_urlsafe(32)
        self.tokens[token] = time.time()
        return token

    def validate_token(self, token: str) -> bool:
        """Valida token CSRF"""
        if not token or token not in self.tokens:
            return False

        # Verifica expiração
        timestamp = self.tokens[token]
        if time.time() - timestamp > self.token_duration:
            del self.tokens[token]
            return False

        # Remove token (uso único)
        del self.tokens[token]
        return True

    def cleanup_expired_tokens(self):
        """Remove tokens expirados"""
        now = time.time()
        expired = [
            token for token, timestamp in self.tokens.items()
            if now - timestamp > self.token_duration
        ]

        for token in expired:
            del self.tokens[token]

csrf = CSRFProtection()
```

**Uso**:
```python
# funnel_builder.py - Para operações sensíveis (DELETE, PUT)
from csrf import csrf

class FunnelBuilderHandler(BaseHTTPRequestHandler):

    def do_DELETE(self):
        # Valida CSRF token
        csrf_token = self.headers.get('X-CSRF-Token', '')

        if not csrf.validate_token(csrf_token):
            self._send_json({'error': 'CSRF token inválido'}, 403)
            return

        # ... resto do código
```

---

### FASE 3: Hardening e Otimizações (3-4 semanas)

#### 3.1 Migrar para PostgreSQL
**Prioridade**: 🟡 MÉDIA (para produção)

**Docker Compose**:
```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: funnel_builder
      POSTGRES_USER: funnel_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  funnel-builder:
    depends_on:
      - postgres
    environment:
      - DB_TYPE=postgres
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=funnel_builder
      - DB_USER=funnel_user
      - DB_PASSWORD=${DB_PASSWORD}

volumes:
  postgres-data:
```

---

#### 3.2 Gerenciamento de Secrets
**Prioridade**: 🟡 MÉDIA

**Usando Docker Secrets**:
```yaml
# docker-compose.yml (swarm mode)
services:
  funnel-builder:
    secrets:
      - db_password
      - jwt_secret
    environment:
      - DB_PASSWORD_FILE=/run/secrets/db_password
      - JWT_SECRET_FILE=/run/secrets/jwt_secret

secrets:
  db_password:
    external: true
  jwt_secret:
    external: true
```

**Ou usando .env (desenvolvimento)**:
```bash
# .env (NÃO COMMITAR!)
DB_PASSWORD=senha_super_secreta_123
JWT_SECRET=chave_jwt_muito_aleatoria_456
REDIS_PASSWORD=senha_redis_789
WEBHOOK_SECRET=secret_para_validar_webhooks
```

```python
# config.py
import os
from typing import Optional

def get_secret(name: str, default: Optional[str] = None) -> str:
    """
    Obtém secret de arquivo Docker ou variável de ambiente
    """
    # Tenta ler de arquivo Docker Secret
    secret_file = os.getenv(f'{name}_FILE')
    if secret_file and os.path.exists(secret_file):
        with open(secret_file, 'r') as f:
            return f.read().strip()

    # Fallback para variável de ambiente
    return os.getenv(name, default)

# Configurações
DB_PASSWORD = get_secret('DB_PASSWORD', 'changeme')
JWT_SECRET = get_secret('JWT_SECRET')
REDIS_PASSWORD = get_secret('REDIS_PASSWORD')

# Valida secrets obrigatórios
if not JWT_SECRET:
    raise ValueError('JWT_SECRET não configurado!')
```

---

#### 3.3 Monitoramento e Alertas
**Prioridade**: 🟡 MÉDIA

**Usando Prometheus + Grafana**:
```python
# metrics.py
from prometheus_client import Counter, Histogram, generate_latest

# Métricas
login_attempts = Counter('login_attempts_total', 'Total login attempts', ['status'])
api_requests = Counter('api_requests_total', 'Total API requests', ['endpoint', 'method'])
request_duration = Histogram('request_duration_seconds', 'Request duration')

def collect_metrics():
    """Endpoint /metrics para Prometheus"""
    return generate_latest()
```

---

#### 3.4 Backup Automatizado
**Prioridade**: 🟡 MÉDIA

**Script de Backup**:
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/app/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup banco de dados
docker exec funnel-builder-postgres pg_dump -U funnel_user funnel_builder > "$BACKUP_DIR/db_$DATE.sql"

# Backup arquivos
tar -czf "$BACKUP_DIR/data_$DATE.tar.gz" /app/data

# Remove backups antigos (mantém últimos 7 dias)
find "$BACKUP_DIR" -name "*.sql" -mtime +7 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

echo "Backup concluído: $DATE"
```

**Cron Job**:
```bash
# Adicionar ao crontab
0 2 * * * /app/scripts/backup.sh >> /var/log/backup.log 2>&1
```

---

## 📊 CHECKLIST DE SEGURANÇA

### Autenticação e Sessão
- [ ] ✅ Sessões em Redis (não em memória)
- [ ] ✅ Tokens com expiração automática
- [ ] ✅ Cleanup de sessões expiradas
- [ ] ✅ Senha mínima de 8 caracteres
- [ ] ✅ Validação de complexidade de senha
- [ ] ✅ Bcrypt com salt (já implementado)
- [ ] ✅ Rate limiting em login/registro
- [ ] ✅ Logs de tentativas de login

### Proteção de Rede
- [ ] ✅ HTTPS obrigatório
- [ ] ✅ CORS restrito a domínios específicos
- [ ] ✅ Rate limiting global
- [ ] ✅ Limite de tamanho de payload
- [ ] ✅ Timeout de requisições
- [ ] ✅ Headers de segurança (CSP, HSTS, etc)

### Validação e Sanitização
- [ ] ✅ Validação de email
- [ ] ✅ Validação de WhatsApp
- [ ] ✅ Sanitização de inputs
- [ ] ✅ Parametrização SQL (já implementado)
- [ ] ✅ Escape de outputs HTML (React já faz)

### Monitoramento e Logs
- [ ] ✅ Sistema de logs de segurança
- [ ] ✅ Log de tentativas de login
- [ ] ✅ Log de ações sensíveis
- [ ] ✅ Métricas de segurança (Prometheus)
- [ ] ✅ Alertas automáticos

### Infraestrutura
- [ ] ✅ Secrets gerenciados corretamente
- [ ] ✅ Backups automatizados
- [ ] ✅ PostgreSQL em produção
- [ ] ✅ Redis para sessões
- [ ] ✅ Nginx como reverse proxy

### Proteções Específicas
- [ ] ✅ Proteção CSRF
- [ ] ✅ Proteção XSS (React + CSP)
- [ ] ✅ Proteção SQL Injection (parametrização)
- [ ] ✅ Proteção clickjacking (X-Frame-Options)
- [ ] ✅ Proteção MIME sniffing

---

## 🚀 ROADMAP DE IMPLEMENTAÇÃO

### Semana 1-2: Crítico
- ✅ Redis para sessões
- ✅ Rate limiting
- ✅ CORS restrito
- ✅ Requisitos de senha fortes
- ✅ Limite de payload

### Semana 3-4: Alto
- ✅ HTTPS com Let's Encrypt
- ✅ Headers de segurança
- ✅ Sistema de logs
- ✅ Validação de inputs

### Semana 5-6: Médio
- ✅ Proteção CSRF
- ✅ Migração PostgreSQL
- ✅ Gerenciamento de secrets

### Semana 7-8: Otimização
- ✅ Monitoramento (Prometheus)
- ✅ Backups automatizados
- ✅ Testes de penetração
- ✅ Auditoria de segurança

---

## 📝 TESTES DE SEGURANÇA

### Após Implementação, Testar:

1. **Autenticação**
   ```bash
   # Teste brute force (deve bloquear após 5 tentativas)
   for i in {1..10}; do
     curl -X POST http://localhost:8000/api/login \
       -H "Content-Type: application/json" \
       -d '{"email":"teste@example.com","password":"wrong"}'
   done
   ```

2. **CORS**
   ```bash
   # Deve rejeitar origem não autorizada
   curl -H "Origin: http://evil.com" \
        -X GET http://localhost:8000/api/funnels
   ```

3. **Payload Size**
   ```bash
   # Deve rejeitar payload > 10MB
   dd if=/dev/zero bs=1M count=15 | \
     curl -X POST http://localhost:8000/api/funnels \
       -H "Content-Type: application/json" \
       --data-binary @-
   ```

4. **SQL Injection**
   ```bash
   # Deve ser bloqueado por parametrização
   curl -X POST http://localhost:8000/api/login \
     -d '{"email":"admin@test.com\" OR \"1\"=\"1","password":"test"}'
   ```

---

## 🆘 RESPOSTA A INCIDENTES

### Em Caso de Breach:

1. **Isolar o sistema**
   ```bash
   docker-compose down
   ```

2. **Analisar logs**
   ```bash
   tail -f /app/data/security.log
   grep "suspicious" /app/data/security.log
   ```

3. **Invalidar todas as sessões**
   ```bash
   docker exec funnel-redis redis-cli FLUSHDB
   ```

4. **Forçar troca de senhas**
   - Enviar email para todos os usuários
   - Implementar flag `force_password_change` no banco

5. **Investigar e corrigir vulnerabilidade**

6. **Notificar usuários afetados** (LGPD)

---

## 📚 REFERÊNCIAS

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [Mozilla Web Security Guidelines](https://infosec.mozilla.org/guidelines/web_security)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)

---

## ✅ CONCLUSÃO

Implementando este plano de segurança, o Funnel Builder estará protegido contra os principais vetores de ataque e em conformidade com as melhores práticas da indústria.

**Próximos passos:**
1. Revisar e aprovar o plano
2. Definir prioridades e timeline
3. Implementar Fase 1 (crítico)
4. Testar e validar
5. Continuar com Fases 2 e 3

---

**Última atualização**: 2025-12-16
**Versão**: 1.0
**Status**: 🔴 AGUARDANDO IMPLEMENTAÇÃO
