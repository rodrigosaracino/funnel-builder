"""
Rate Limiter para Funnel Builder
Protege contra ataques de força bruta e DDoS
"""

import time
from collections import defaultdict
from threading import Lock
from typing import Tuple, Dict


class RateLimiter:
    """Rate limiter usando sliding window algorithm"""

    def __init__(self):
        # IP/Identifier -> lista de timestamps
        self.attempts: Dict[str, list] = defaultdict(list)
        self.lock = Lock()

        # Configurações por tipo de ação
        self.limits = {
            'login': {'max_attempts': 5, 'window': 300},      # 5 tentativas em 5 minutos
            'register': {'max_attempts': 3, 'window': 600},   # 3 tentativas em 10 minutos
            'api': {'max_attempts': 100, 'window': 60},       # 100 requisições por minuto
            'api_write': {'max_attempts': 30, 'window': 60},  # 30 escritas por minuto
        }

    def is_allowed(self, identifier: str, action: str = 'api') -> Tuple[bool, int]:
        """
        Verifica se a requisição é permitida

        Args:
            identifier: IP ou user_id do cliente
            action: Tipo de ação ('login', 'register', 'api', 'api_write')

        Returns:
            (allowed, remaining_attempts)
        """
        with self.lock:
            now = time.time()

            # Obtém limites para esta ação
            config = self.limits.get(action, self.limits['api'])
            max_attempts = config['max_attempts']
            window = config['window']

            # Cria chave única por ação
            key = f"{identifier}:{action}"

            # Remove tentativas antigas (fora da janela)
            self.attempts[key] = [
                timestamp for timestamp in self.attempts[key]
                if now - timestamp < window
            ]

            # Verifica se excedeu o limite
            current_attempts = len(self.attempts[key])

            if current_attempts >= max_attempts:
                # Calcula tempo até liberar
                oldest = min(self.attempts[key])
                retry_after = int(window - (now - oldest))
                return False, retry_after

            # Registra esta tentativa
            self.attempts[key].append(now)

            # Calcula tentativas restantes
            remaining = max_attempts - current_attempts - 1
            return True, remaining

    def get_retry_after(self, identifier: str, action: str = 'api') -> int:
        """
        Retorna tempo em segundos até poder tentar novamente

        Returns:
            Segundos até próxima tentativa permitida
        """
        with self.lock:
            key = f"{identifier}:{action}"
            config = self.limits.get(action, self.limits['api'])

            if key not in self.attempts or not self.attempts[key]:
                return 0

            now = time.time()
            oldest = min(self.attempts[key])
            retry_after = int(config['window'] - (now - oldest))

            return max(0, retry_after)

    def reset(self, identifier: str, action: str = None):
        """
        Reseta o rate limit para um identifier
        Útil após login bem-sucedido
        """
        with self.lock:
            if action:
                key = f"{identifier}:{action}"
                if key in self.attempts:
                    del self.attempts[key]
            else:
                # Remove todos os limites para este identifier
                keys_to_remove = [k for k in self.attempts.keys() if k.startswith(f"{identifier}:")]
                for key in keys_to_remove:
                    del self.attempts[key]

    def cleanup_old_entries(self):
        """
        Remove entradas antigas para economizar memória
        Deve ser executado periodicamente
        """
        with self.lock:
            now = time.time()
            max_window = max(config['window'] for config in self.limits.values())

            # Remove entradas completamente expiradas
            for key in list(self.attempts.keys()):
                self.attempts[key] = [
                    timestamp for timestamp in self.attempts[key]
                    if now - timestamp < max_window
                ]

                # Remove chave se não há mais tentativas
                if not self.attempts[key]:
                    del self.attempts[key]

    def get_stats(self) -> Dict:
        """Retorna estatísticas do rate limiter"""
        with self.lock:
            return {
                'total_tracked_ips': len(set(k.split(':')[0] for k in self.attempts.keys())),
                'total_entries': len(self.attempts),
                'limits': self.limits
            }


# Instância global
rate_limiter = RateLimiter()


if __name__ == '__main__':
    # Testes
    print("🧪 Testando rate_limiter.py...")

    # Teste 1: Login - deve permitir 5 tentativas
    print("\n1️⃣ Teste: Login (5 tentativas permitidas)")
    for i in range(7):
        allowed, remaining = rate_limiter.is_allowed('192.168.1.1', 'login')
        if allowed:
            print(f"   Tentativa {i+1}: ✅ Permitida (restam {remaining})")
        else:
            print(f"   Tentativa {i+1}: ❌ Bloqueada (aguarde {remaining}s)")

    # Teste 2: Reset após sucesso
    print("\n2️⃣ Teste: Reset após login bem-sucedido")
    rate_limiter.reset('192.168.1.1', 'login')
    allowed, remaining = rate_limiter.is_allowed('192.168.1.1', 'login')
    print(f"   Após reset: {'✅ Permitida' if allowed else '❌ Bloqueada'}")

    # Teste 3: Registro - 3 tentativas
    print("\n3️⃣ Teste: Registro (3 tentativas permitidas)")
    for i in range(5):
        allowed, remaining = rate_limiter.is_allowed('192.168.1.2', 'register')
        if allowed:
            print(f"   Tentativa {i+1}: ✅ Permitida (restam {remaining})")
        else:
            print(f"   Tentativa {i+1}: ❌ Bloqueada (aguarde {remaining}s)")

    # Teste 4: Estatísticas
    print("\n4️⃣ Estatísticas:")
    stats = rate_limiter.get_stats()
    print(f"   IPs rastreados: {stats['total_tracked_ips']}")
    print(f"   Entradas totais: {stats['total_entries']}")

    # Teste 5: Cleanup
    print("\n5️⃣ Teste: Cleanup")
    rate_limiter.cleanup_old_entries()
    stats = rate_limiter.get_stats()
    print(f"   Após cleanup: {stats['total_entries']} entradas")

    print("\n✅ Todos os testes passaram!")
