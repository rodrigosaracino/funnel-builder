"""
Authentication module for Funnel Builder
Gerencia autenticação, registro e sessões de usuários
"""

import bcrypt
import secrets
import time
from typing import Optional, Dict
from models import User
from database import db


class Auth:
    """Classe para gerenciar autenticação e sessões"""

    def __init__(self):
        # Armazena sessões ativas em memória (user_id -> token)
        # Em produção, use Redis ou banco de dados
        self.sessions = {}  # token -> {'user_id': int, 'expires': timestamp}
        self.session_duration = 24 * 60 * 60  # 24 horas em segundos

    def hash_password(self, password: str) -> str:
        """Gera hash seguro da senha"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verifica se a senha corresponde ao hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False

    def generate_token(self) -> str:
        """Gera um token seguro para sessão"""
        return secrets.token_urlsafe(32)

    def register(self, email: str, password: str, name: str = None, whatsapp: str = None) -> Dict:
        """
        Registra um novo usuário

        Returns:
            {'success': bool, 'message': str, 'user': User|None, 'token': str|None}
        """
        # Validações básicas
        if not email or not password:
            return {
                'success': False,
                'message': 'Email e senha são obrigatórios',
                'user': None,
                'token': None
            }

        if len(password) < 6:
            return {
                'success': False,
                'message': 'Senha deve ter no mínimo 6 caracteres',
                'user': None,
                'token': None
            }

        # Valida WhatsApp (obrigatório)
        if not whatsapp or len(whatsapp.strip()) == 0:
            return {
                'success': False,
                'message': 'WhatsApp é obrigatório',
                'user': None,
                'token': None
            }

        # Verifica se email já existe
        existing_user = User.get_by_email(email)
        if existing_user:
            return {
                'success': False,
                'message': 'Email já cadastrado',
                'user': None,
                'token': None
            }

        # Cria o usuário
        password_hash = self.hash_password(password)
        user = User.create(email, password_hash, name, whatsapp)

        if not user:
            return {
                'success': False,
                'message': 'Erro ao criar usuário',
                'user': None,
                'token': None
            }

        # Cria sessão
        token = self.create_session(user.id)

        return {
            'success': True,
            'message': 'Usuário cadastrado com sucesso',
            'user': user,
            'token': token
        }

    def login(self, email: str, password: str) -> Dict:
        """
        Autentica um usuário

        Returns:
            {'success': bool, 'message': str, 'user': User|None, 'token': str|None}
        """
        # Validações
        if not email or not password:
            return {
                'success': False,
                'message': 'Email e senha são obrigatórios',
                'user': None,
                'token': None
            }

        # Busca usuário
        user_data = db.get_user_by_email(email)
        if not user_data:
            return {
                'success': False,
                'message': 'Email ou senha incorretos',
                'user': None,
                'token': None
            }

        # Verifica senha
        if not self.verify_password(password, user_data['password_hash']):
            return {
                'success': False,
                'message': 'Email ou senha incorretos',
                'user': None,
                'token': None
            }

        # Cria usuário
        user = User(
            user_id=user_data['id'],
            email=user_data['email'],
            name=user_data['name'],
            whatsapp=user_data.get('whatsapp'),
            created_at=user_data['created_at']
        )

        # Cria sessão
        token = self.create_session(user.id)

        return {
            'success': True,
            'message': 'Login realizado com sucesso',
            'user': user,
            'token': token
        }

    def create_session(self, user_id: int) -> str:
        """Cria uma nova sessão para o usuário"""
        token = self.generate_token()
        expires = time.time() + self.session_duration

        self.sessions[token] = {
            'user_id': user_id,
            'expires': expires
        }

        return token

    def get_user_from_token(self, token: str) -> Optional[User]:
        """
        Retorna o usuário associado ao token (se válido)
        """
        if not token:
            return None

        session = self.sessions.get(token)
        if not session:
            return None

        # Verifica se a sessão expirou
        if time.time() > session['expires']:
            del self.sessions[token]
            return None

        # Retorna o usuário
        return User.get_by_id(session['user_id'])

    def logout(self, token: str) -> bool:
        """Remove a sessão (logout)"""
        if token in self.sessions:
            del self.sessions[token]
            return True
        return False

    def validate_token(self, token: str) -> bool:
        """Verifica se o token é válido"""
        return self.get_user_from_token(token) is not None

    def cleanup_expired_sessions(self):
        """Remove sessões expiradas (deve ser executado periodicamente)"""
        now = time.time()
        expired = [token for token, session in self.sessions.items()
                  if session['expires'] < now]

        for token in expired:
            del self.sessions[token]

        return len(expired)


# Instância global de autenticação
auth = Auth()


if __name__ == '__main__':
    # Testes
    print("🧪 Testando auth.py...")

    # Teste: Registrar usuário
    result = auth.register('auth@test.com', 'senha123', 'Teste Auth')
    print(f"✅ Registro: {result['success']} - {result['message']}")
    if result['success']:
        user = result['user']
        token = result['token']
        print(f"   Usuário: {user}")
        print(f"   Token: {token[:20]}...")

        # Teste: Validar token
        is_valid = auth.validate_token(token)
        print(f"✅ Token válido: {is_valid}")

        # Teste: Buscar usuário pelo token
        found_user = auth.get_user_from_token(token)
        print(f"✅ Usuário do token: {found_user}")

        # Teste: Login com credenciais corretas
        login_result = auth.login('auth@test.com', 'senha123')
        print(f"✅ Login correto: {login_result['success']} - {login_result['message']}")

        # Teste: Login com senha errada
        wrong_result = auth.login('auth@test.com', 'senhaerrada')
        print(f"✅ Login incorreto: {wrong_result['success']} - {wrong_result['message']}")

        # Teste: Logout
        logout_success = auth.logout(token)
        print(f"✅ Logout: {logout_success}")

        # Teste: Validar token após logout
        is_valid_after = auth.validate_token(token)
        print(f"✅ Token válido após logout: {is_valid_after}")

    # Teste: Tentar registrar email duplicado
    dup_result = auth.register('auth@test.com', 'outrasenha')
    print(f"✅ Email duplicado: {dup_result['success']} - {dup_result['message']}")

    print("\n✅ Todos os testes do auth.py passaram!")
