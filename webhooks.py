"""
Webhooks module for Funnel Builder
Gerencia envio de webhooks para eventos do sistema
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Optional
from threading import Thread


class WebhookManager:
    """Gerencia o envio de webhooks para eventos do sistema"""

    def __init__(self):
        # URL do webhook - pode ser configurado via variável de ambiente
        # Exemplo: https://hooks.zapier.com/hooks/catch/123456/abcdef/
        self.webhook_url = None
        self.enabled = False

    def configure(self, webhook_url: str):
        """Configura a URL do webhook"""
        if webhook_url and webhook_url.startswith(('http://', 'https://')):
            self.webhook_url = webhook_url
            self.enabled = True
            print(f"✅ Webhook configurado: {webhook_url}")
        else:
            self.enabled = False
            print("⚠️ Webhook URL inválida ou não configurada")

    def send_webhook(self, event: str, data: Dict):
        """
        Envia webhook de forma assíncrona (não bloqueia o request)

        Args:
            event: Nome do evento (ex: 'user.registered')
            data: Dados do evento
        """
        if not self.enabled or not self.webhook_url:
            return

        # Executa em thread separada para não bloquear
        thread = Thread(target=self._send_webhook_sync, args=(event, data))
        thread.daemon = True  # Thread finaliza quando app terminar
        thread.start()

    def _send_webhook_sync(self, event: str, data: Dict):
        """Envia webhook de forma síncrona (executa em thread separada)"""
        try:
            payload = {
                'event': event,
                'data': data,
                'timestamp': data.get('timestamp')
            }

            # Prepara request
            json_data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                self.webhook_url,
                data=json_data,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'FunnelBuilder-Webhook/1.0'
                },
                method='POST'
            )

            # Envia webhook com timeout de 10 segundos
            with urllib.request.urlopen(req, timeout=10) as response:
                status_code = response.getcode()
                if status_code in (200, 201, 204):
                    print(f"✅ Webhook enviado com sucesso: {event}")
                else:
                    print(f"⚠️ Webhook retornou status {status_code}: {event}")

        except urllib.error.HTTPError as e:
            print(f"❌ Erro HTTP ao enviar webhook {event}: {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            print(f"❌ Erro de conexão ao enviar webhook {event}: {e.reason}")
        except Exception as e:
            print(f"❌ Erro inesperado ao enviar webhook {event}: {e}")

    def on_user_registered(self, user_data: Dict):
        """
        Webhook disparado quando um novo usuário se registra

        Args:
            user_data: Dados do usuário registrado (sem senha!)
        """
        from datetime import datetime

        event_data = {
            'user_id': user_data.get('id'),
            'email': user_data.get('email'),
            'name': user_data.get('name'),
            'created_at': user_data.get('created_at'),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

        self.send_webhook('user.registered', event_data)

    def on_funnel_created(self, funnel_data: Dict, user_data: Dict):
        """
        Webhook disparado quando um novo funil é criado

        Args:
            funnel_data: Dados do funil criado
            user_data: Dados do usuário que criou
        """
        from datetime import datetime

        event_data = {
            'funnel_id': funnel_data.get('id'),
            'funnel_name': funnel_data.get('name'),
            'funnel_icon': funnel_data.get('icon'),
            'user_id': user_data.get('id'),
            'user_email': user_data.get('email'),
            'user_name': user_data.get('name'),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

        self.send_webhook('funnel.created', event_data)


# Instância global
webhook_manager = WebhookManager()


if __name__ == '__main__':
    # Teste do webhook
    print("🧪 Testando webhooks...")

    # Configurar webhook de teste (use webhook.site para testar)
    # Visite https://webhook.site para obter uma URL de teste
    test_url = input("Digite a URL do webhook para teste (ou Enter para pular): ").strip()

    if test_url:
        webhook_manager.configure(test_url)

        # Simula registro de usuário
        print("\n📨 Enviando webhook de teste: user.registered")
        webhook_manager.on_user_registered({
            'id': 999,
            'email': 'teste@webhook.com',
            'name': 'Usuário Teste',
            'created_at': '2025-10-30T19:00:00'
        })

        print("\n⏳ Aguardando envio... (webhook é assíncrono)")
        import time
        time.sleep(3)

        print("\n✅ Teste concluído!")
        print("\n💡 Verifique no webhook.site se a requisição chegou!")
    else:
        print("⏭️ Teste pulado - nenhuma URL fornecida")
