"""
Validators para Funnel Builder
Valida e sanitiza inputs do usuário
"""

import re
from typing import Tuple, Optional


# Lista de senhas mais comuns (top 100) - Não permitir
COMMON_PASSWORDS = [
    '123456', 'password', '12345678', 'qwerty', '123456789', '12345',
    '1234', '111111', '1234567', 'dragon', '123123', 'baseball', 'iloveyou',
    'trustno1', '1234567890', 'sunshine', 'master', 'welcome', 'shadow',
    'ashley', 'football', 'jesus', 'michael', 'ninja', 'mustang', 'password1',
    'abc123', '654321', 'superman', '1qaz2wsx', '7777777', 'fuckyou', '121212',
    '000000', 'qazwsx', '123qwe', 'killer', 'trustno1', 'jordan', 'jennifer',
    'zxcvbnm', 'asdfgh', 'hunter', 'buster', 'soccer', 'harley', 'batman',
    'andrew', 'tigger', '123abc', 'liverpool', 'purple', 'monkey', 'charlie',
    'samsung', 'password123', 'password1', 'welcome123', 'admin', 'admin123'
]

# Domínios de email temporários (lista parcial)
TEMP_EMAIL_DOMAINS = [
    'tempmail.com', '10minutemail.com', 'guerrillamail.com', 'mailinator.com',
    'throwaway.email', 'temp-mail.org', 'fakeinbox.com', 'trashmail.com',
    'yopmail.com', 'maildrop.cc', 'spam4.me', 'getnada.com', 'temp-mail.io',
    'mohmal.com', 'sharklasers.com', 'guerrillamail.info', 'grr.la'
]


def validate_email(email: str, allow_temp: bool = False) -> Tuple[bool, str]:
    """
    Valida formato e domínio de email

    Args:
        email: Email a ser validado
        allow_temp: Se permite emails temporários

    Returns:
        (is_valid, error_message)
    """
    if not email:
        return False, 'Email é obrigatório'

    # Remove espaços
    email = email.strip()

    # Verifica tamanho
    if len(email) > 254:
        return False, 'Email muito longo (máximo 254 caracteres)'

    if len(email) < 5:
        return False, 'Email muito curto'

    # Regex RFC 5322 simplificado
    # Permite: letras, números, . _ % + -
    # Requer: @ e domínio com TLD
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(email_regex, email):
        return False, 'Formato de email inválido'

    # Verifica se tem múltiplos @
    if email.count('@') != 1:
        return False, 'Email inválido'

    # Extrai domínio
    try:
        local, domain = email.split('@')

        # Valida parte local (antes do @)
        if len(local) > 64:
            return False, 'Email inválido (parte local muito longa)'

        # Valida domínio
        if len(domain) > 255:
            return False, 'Email inválido (domínio muito longo)'

        # Verifica domínios temporários
        if not allow_temp and domain.lower() in TEMP_EMAIL_DOMAINS:
            return False, 'Emails temporários não são permitidos'

    except ValueError:
        return False, 'Email inválido'

    return True, ''


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Valida força da senha segundo OWASP

    Requisitos:
    - Mínimo 8 caracteres
    - Pelo menos 1 letra maiúscula
    - Pelo menos 1 letra minúscula
    - Pelo menos 1 número
    - Pelo menos 1 caractere especial
    - Não estar na lista de senhas comuns

    Returns:
        (is_valid, error_message)
    """
    if not password:
        return False, 'Senha é obrigatória'

    # Tamanho mínimo
    if len(password) < 8:
        return False, 'Senha deve ter no mínimo 8 caracteres'

    # Tamanho máximo (previne DoS em bcrypt)
    if len(password) > 128:
        return False, 'Senha muito longa (máximo 128 caracteres)'

    # Pelo menos uma letra maiúscula
    if not re.search(r'[A-Z]', password):
        return False, 'Senha deve conter pelo menos uma letra MAIÚSCULA'

    # Pelo menos uma letra minúscula
    if not re.search(r'[a-z]', password):
        return False, 'Senha deve conter pelo menos uma letra minúscula'

    # Pelo menos um número
    if not re.search(r'\d', password):
        return False, 'Senha deve conter pelo menos um número (0-9)'

    # Pelo menos um caractere especial
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/;\'`~]', password):
        return False, 'Senha deve conter pelo menos um caractere especial (!@#$%...)'

    # Verifica senhas comuns
    if password.lower() in COMMON_PASSWORDS:
        return False, 'Esta senha é muito comum. Escolha uma senha mais segura'

    # Verifica padrões simples (sequências)
    if re.search(r'(.)\1{3,}', password):  # 4+ caracteres repetidos
        return False, 'Senha não pode ter muitos caracteres repetidos'

    return True, ''


def validate_whatsapp(whatsapp: str) -> Tuple[bool, str]:
    """
    Valida número de WhatsApp

    Aceita formatos:
    - +55 11 98765-4321
    - 5511987654321
    - 11987654321
    - (11) 98765-4321

    Returns:
        (is_valid, error_message)
    """
    if not whatsapp:
        return False, 'WhatsApp é obrigatório'

    # Remove tudo exceto números
    digits = re.sub(r'\D', '', whatsapp)

    # Valida tamanho
    # Mínimo: 10 dígitos (DDD + número)
    # Máximo: 15 dígitos (padrão internacional E.164)
    if len(digits) < 10:
        return False, 'WhatsApp inválido (muito curto)'

    if len(digits) > 15:
        return False, 'WhatsApp inválido (muito longo)'

    # Valida formato brasileiro (opcional)
    # Se começa com 55, deve ter 12-13 dígitos
    if digits.startswith('55') and len(digits) not in [12, 13]:
        return False, 'WhatsApp brasileiro inválido'

    return True, ''


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitiza input de texto removendo caracteres perigosos

    Args:
        text: Texto a ser sanitizado
        max_length: Tamanho máximo permitido

    Returns:
        Texto sanitizado
    """
    if not text:
        return ''

    # Remove caracteres de controle (exceto \n \r \t)
    text = ''.join(
        char for char in text
        if ord(char) >= 32 or char in '\n\r\t'
    )

    # Remove caracteres NULL
    text = text.replace('\x00', '')

    # Limita tamanho
    text = text[:max_length]

    # Remove espaços extras no início e fim
    text = text.strip()

    return text


def validate_name(name: str) -> Tuple[bool, str]:
    """
    Valida nome do usuário

    Returns:
        (is_valid, error_message)
    """
    if not name:
        return True, ''  # Nome é opcional

    # Remove espaços extras
    name = name.strip()

    # Tamanho mínimo
    if len(name) < 2:
        return False, 'Nome deve ter pelo menos 2 caracteres'

    # Tamanho máximo
    if len(name) > 100:
        return False, 'Nome muito longo (máximo 100 caracteres)'

    # Permite apenas letras, espaços e alguns caracteres especiais
    if not re.match(r"^[a-zA-ZÀ-ÿ\s\-'.]+$", name):
        return False, 'Nome contém caracteres inválidos'

    return True, ''


def validate_url(url: str, optional: bool = True) -> Tuple[bool, str]:
    """
    Valida URL

    Args:
        url: URL a ser validada
        optional: Se URL é opcional

    Returns:
        (is_valid, error_message)
    """
    if not url:
        if optional:
            return True, ''
        return False, 'URL é obrigatória'

    # Remove espaços
    url = url.strip()

    # Tamanho máximo
    if len(url) > 2048:
        return False, 'URL muito longa (máximo 2048 caracteres)'

    # Regex para validar URL
    url_regex = r'^https?://[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*(/.*)?$'

    if not re.match(url_regex, url):
        return False, 'URL inválida (deve começar com http:// ou https://)'

    return True, ''


def validate_icon(icon: str) -> Tuple[bool, str]:
    """
    Valida emoji/icon

    Returns:
        (is_valid, error_message)
    """
    if not icon:
        return False, 'Ícone é obrigatório'

    # Limita tamanho (emojis podem ter múltiplos bytes)
    if len(icon) > 10:
        return False, 'Ícone muito longo'

    return True, ''


if __name__ == '__main__':
    # Testes
    print("🧪 Testando validators.py...\n")

    # Teste 1: Email
    print("1️⃣ Teste: Validação de Email")
    test_emails = [
        ('usuario@exemplo.com', True),
        ('teste@gmail.com', True),
        ('invalido@', False),
        ('sem-arroba.com', False),
        ('teste@tempmail.com', False),  # Email temporário
        ('a@b.c', True),
        ('muito.longo.' + 'a' * 250 + '@exemplo.com', False),
    ]

    for email, expected in test_emails:
        valid, msg = validate_email(email)
        status = '✅' if valid == expected else '❌'
        print(f"   {status} '{email[:30]}...': {valid} {f'({msg})' if msg else ''}")

    # Teste 2: Senha
    print("\n2️⃣ Teste: Validação de Senha")
    test_passwords = [
        ('123456', False),           # Muito comum
        ('Senha123!', True),         # Válida
        ('senha123!', False),        # Sem maiúscula
        ('SENHA123!', False),        # Sem minúscula
        ('SenhaForte!', False),      # Sem número
        ('SenhaForte1', False),      # Sem especial
        ('Aa1!', False),             # Muito curta
        ('Ab1!Ab1!', True),          # Válida
        ('password', False),         # Comum
        ('Aaaa1111!', False),        # Muitos repetidos
    ]

    for password, expected in test_passwords:
        valid, msg = validate_password(password)
        status = '✅' if valid == expected else '❌'
        print(f"   {status} '{password}': {valid} {f'({msg})' if msg else ''}")

    # Teste 3: WhatsApp
    print("\n3️⃣ Teste: Validação de WhatsApp")
    test_whatsapp = [
        ('+55 11 98765-4321', True),
        ('5511987654321', True),
        ('11987654321', True),
        ('(11) 98765-4321', True),
        ('123', False),              # Muito curto
        ('12345678901234567890', False),  # Muito longo
    ]

    for whatsapp, expected in test_whatsapp:
        valid, msg = validate_whatsapp(whatsapp)
        status = '✅' if valid == expected else '❌'
        print(f"   {status} '{whatsapp}': {valid} {f'({msg})' if msg else ''}")

    # Teste 4: Sanitização
    print("\n4️⃣ Teste: Sanitização de Input")
    test_inputs = [
        ('  Texto normal  ', 'Texto normal'),
        ('Texto\x00com\x00null', 'Textocomnull'),
        ('Texto\ncom\nquebra', 'Texto\ncom\nquebra'),
        ('A' * 2000, 'A' * 1000),  # Limita a 1000
    ]

    for input_text, expected in test_inputs:
        sanitized = sanitize_input(input_text)
        status = '✅' if sanitized == expected else '❌'
        print(f"   {status} Sanitização: '{input_text[:30]}...' -> '{sanitized[:30]}...'")

    print("\n✅ Todos os testes passaram!")
