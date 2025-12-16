"""
Security Logger para Funnel Builder
Registra eventos de segurança em formato estruturado (JSON)
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional


class SecurityLogger:
    """Logger especializado para eventos de segurança"""

    def __init__(self, log_file: str = None):
        # Define caminho do log
        if log_file is None:
            if os.path.exists('/app/data'):
                log_file = '/app/data/security.log'
            else:
                log_file = 'security.log'

        self.log_file = log_file

        # Configura logger
        self.logger = logging.getLogger('security')
        self.logger.setLevel(logging.INFO)

        # Remove handlers existentes
        self.logger.handlers = []

        # Handler para arquivo
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        # Formato simples (apenas a mensagem JSON)
        formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

        # Também loga no console em desenvolvimento
        if not os.path.exists('/app/data'):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def _log_event(self, event_type: str, level: str, data: Dict[str, Any]):
        """
        Log estruturado em JSON

        Args:
            event_type: Tipo do evento (ex: 'login_attempt')
            level: Nível (INFO, WARNING, ERROR, CRITICAL)
            data: Dados do evento
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event_type': event_type,
            'level': level,
            **data
        }

        # Serializa para JSON
        json_line = json.dumps(log_entry, ensure_ascii=False)

        # Escolhe método de log baseado no level
        if level == 'INFO':
            self.logger.info(json_line)
        elif level == 'WARNING':
            self.logger.warning(json_line)
        elif level == 'ERROR':
            self.logger.error(json_line)
        elif level == 'CRITICAL':
            self.logger.critical(json_line)

    # ==================== AUTENTICAÇÃO ====================

    def log_login_attempt(self, email: str, ip: str, user_agent: Optional[str] = None):
        """Log de tentativa de login (antes de validar)"""
        self._log_event('login_attempt', 'INFO', {
            'email': email,
            'ip': ip,
            'user_agent': user_agent
        })

    def log_login_success(self, user_id: int, email: str, ip: str):
        """Log de login bem-sucedido"""
        self._log_event('login_success', 'INFO', {
            'user_id': user_id,
            'email': email,
            'ip': ip
        })

    def log_login_failure(self, email: str, ip: str, reason: str):
        """Log de falha de login"""
        self._log_event('login_failure', 'WARNING', {
            'email': email,
            'ip': ip,
            'reason': reason
        })

    def log_registration(self, user_id: int, email: str, ip: str):
        """Log de novo registro"""
        self._log_event('user_registration', 'INFO', {
            'user_id': user_id,
            'email': email,
            'ip': ip
        })

    def log_registration_failure(self, email: str, ip: str, reason: str):
        """Log de falha no registro"""
        self._log_event('registration_failure', 'WARNING', {
            'email': email,
            'ip': ip,
            'reason': reason
        })

    def log_logout(self, user_id: int, ip: str):
        """Log de logout"""
        self._log_event('logout', 'INFO', {
            'user_id': user_id,
            'ip': ip
        })

    # ==================== RATE LIMITING ====================

    def log_rate_limit_exceeded(self, ip: str, action: str, retry_after: int):
        """Log de rate limit excedido"""
        self._log_event('rate_limit_exceeded', 'WARNING', {
            'ip': ip,
            'action': action,
            'retry_after_seconds': retry_after
        })

    # ==================== ATIVIDADES SUSPEITAS ====================

    def log_suspicious_activity(self, ip: str, description: str, details: Optional[Dict] = None):
        """Log de atividade suspeita"""
        self._log_event('suspicious_activity', 'WARNING', {
            'ip': ip,
            'description': description,
            'details': details or {}
        })

    def log_brute_force_attempt(self, ip: str, email: str, attempts: int):
        """Log de possível ataque de força bruta"""
        self._log_event('brute_force_attempt', 'CRITICAL', {
            'ip': ip,
            'email': email,
            'failed_attempts': attempts
        })

    def log_invalid_token(self, token_preview: str, ip: str):
        """Log de tentativa de usar token inválido"""
        self._log_event('invalid_token', 'WARNING', {
            'token_preview': token_preview[:10] + '...',
            'ip': ip
        })

    # ==================== ERROS DE API ====================

    def log_api_error(self, endpoint: str, method: str, ip: str, error: str, status_code: int):
        """Log de erro de API"""
        self._log_event('api_error', 'ERROR', {
            'endpoint': endpoint,
            'method': method,
            'ip': ip,
            'error': error,
            'status_code': status_code
        })

    def log_validation_error(self, endpoint: str, ip: str, field: str, error: str):
        """Log de erro de validação"""
        self._log_event('validation_error', 'INFO', {
            'endpoint': endpoint,
            'ip': ip,
            'field': field,
            'error': error
        })

    def log_payload_too_large(self, ip: str, size_bytes: int, max_size: int):
        """Log de payload muito grande"""
        self._log_event('payload_too_large', 'WARNING', {
            'ip': ip,
            'size_bytes': size_bytes,
            'max_size_bytes': max_size
        })

    # ==================== OPERAÇÕES CRUD ====================

    def log_funnel_created(self, user_id: int, funnel_id: int, ip: str):
        """Log de criação de funil"""
        self._log_event('funnel_created', 'INFO', {
            'user_id': user_id,
            'funnel_id': funnel_id,
            'ip': ip
        })

    def log_funnel_updated(self, user_id: int, funnel_id: int, ip: str):
        """Log de atualização de funil"""
        self._log_event('funnel_updated', 'INFO', {
            'user_id': user_id,
            'funnel_id': funnel_id,
            'ip': ip
        })

    def log_funnel_deleted(self, user_id: int, funnel_id: int, ip: str):
        """Log de exclusão de funil"""
        self._log_event('funnel_deleted', 'INFO', {
            'user_id': user_id,
            'funnel_id': funnel_id,
            'ip': ip
        })

    def log_unauthorized_access(self, user_id: int, resource: str, ip: str):
        """Log de tentativa de acesso não autorizado"""
        self._log_event('unauthorized_access', 'WARNING', {
            'user_id': user_id,
            'resource': resource,
            'ip': ip
        })

    # ==================== SISTEMA ====================

    def log_server_start(self, port: int):
        """Log de início do servidor"""
        self._log_event('server_start', 'INFO', {
            'port': port
        })

    def log_server_stop(self):
        """Log de parada do servidor"""
        self._log_event('server_stop', 'INFO', {})

    # ==================== ANÁLISE DE LOGS ====================

    def get_recent_events(self, event_type: Optional[str] = None, limit: int = 100) -> list:
        """
        Retorna eventos recentes do log

        Args:
            event_type: Filtrar por tipo de evento (opcional)
            limit: Número máximo de eventos

        Returns:
            Lista de eventos (dicionários)
        """
        try:
            events = []

            with open(self.log_file, 'r', encoding='utf-8') as f:
                # Lê arquivo de trás para frente (mais eficiente)
                lines = f.readlines()
                lines.reverse()

                for line in lines:
                    if len(events) >= limit:
                        break

                    try:
                        event = json.loads(line.strip())

                        # Filtra por tipo se especificado
                        if event_type is None or event.get('event_type') == event_type:
                            events.append(event)
                    except json.JSONDecodeError:
                        continue

            return events

        except FileNotFoundError:
            return []

    def get_failed_logins_by_ip(self, ip: str, minutes: int = 60) -> int:
        """
        Conta falhas de login de um IP em um período

        Args:
            ip: Endereço IP
            minutes: Janela de tempo em minutos

        Returns:
            Número de falhas
        """
        try:
            from datetime import timedelta

            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
            count = 0

            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())

                        if event.get('event_type') != 'login_failure':
                            continue

                        if event.get('ip') != ip:
                            continue

                        # Parse timestamp
                        event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))

                        if event_time > cutoff_time:
                            count += 1

                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue

            return count

        except FileNotFoundError:
            return 0


# Instância global
security_logger = SecurityLogger()


if __name__ == '__main__':
    # Testes
    print("🧪 Testando security_logger.py...")

    # Teste 1: Login bem-sucedido
    print("\n1️⃣ Teste: Login bem-sucedido")
    security_logger.log_login_success(
        user_id=1,
        email='teste@exemplo.com',
        ip='192.168.1.1'
    )
    print("   ✅ Log gravado")

    # Teste 2: Login falho
    print("\n2️⃣ Teste: Login falho")
    security_logger.log_login_failure(
        email='hacker@exemplo.com',
        ip='192.168.1.100',
        reason='Senha incorreta'
    )
    print("   ✅ Log gravado")

    # Teste 3: Rate limit excedido
    print("\n3️⃣ Teste: Rate limit excedido")
    security_logger.log_rate_limit_exceeded(
        ip='192.168.1.100',
        action='login',
        retry_after=300
    )
    print("   ✅ Log gravado")

    # Teste 4: Atividade suspeita
    print("\n4️⃣ Teste: Atividade suspeita")
    security_logger.log_suspicious_activity(
        ip='192.168.1.100',
        description='Múltiplas tentativas de SQL injection',
        details={'endpoint': '/api/login', 'attempts': 5}
    )
    print("   ✅ Log gravado")

    # Teste 5: Listar eventos recentes
    print("\n5️⃣ Teste: Listar eventos recentes")
    recent = security_logger.get_recent_events(limit=5)
    print(f"   ✅ Encontrados {len(recent)} eventos recentes")
    for event in recent:
        print(f"      - {event['event_type']} ({event['level']})")

    # Teste 6: Contar falhas de login
    print("\n6️⃣ Teste: Contar falhas de login por IP")
    count = security_logger.get_failed_logins_by_ip('192.168.1.100', minutes=60)
    print(f"   ✅ IP 192.168.1.100 teve {count} falhas nos últimos 60 minutos")

    print(f"\n✅ Todos os testes passaram!")
    print(f"\n📁 Arquivo de log: {security_logger.log_file}")
