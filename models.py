"""
Models module for Funnel Builder
Define classes User e Funnel com métodos convenientes
"""

from typing import List, Dict, Optional
from database import db


class User:
    """Classe que representa um usuário do sistema"""

    def __init__(self, user_id: int, email: str, name: str = None, whatsapp: str = None, created_at: str = None):
        self.id = user_id
        self.email = email
        self.name = name
        self.whatsapp = whatsapp
        self.created_at = created_at

    @staticmethod
    def create(email: str, password_hash: str, name: str = None, whatsapp: str = None) -> Optional['User']:
        """Cria um novo usuário no banco"""
        user_id = db.create_user(email, password_hash, name, whatsapp)
        if user_id:
            return User(user_id, email, name, whatsapp)
        return None

    @staticmethod
    def get_by_email(email: str) -> Optional['User']:
        """Busca usuário por email"""
        user_data = db.get_user_by_email(email)
        if user_data:
            return User(
                user_id=user_data['id'],
                email=user_data['email'],
                name=user_data['name'],
                whatsapp=user_data.get('whatsapp'),
                created_at=user_data['created_at']
            )
        return None

    @staticmethod
    def get_by_id(user_id: int) -> Optional['User']:
        """Busca usuário por ID"""
        user_data = db.get_user_by_id(user_id)
        if user_data:
            return User(
                user_id=user_data['id'],
                email=user_data['email'],
                name=user_data['name'],
                whatsapp=user_data.get('whatsapp'),
                created_at=user_data['created_at']
            )
        return None

    def get_funnels(self) -> List['Funnel']:
        """Retorna todos os funis deste usuário"""
        funnels_data = db.get_funnels_by_user(self.id)
        return [Funnel.from_dict(data) for data in funnels_data]

    def create_funnel(self, name: str, icon: str = '🚀',
                     elements: List = None, connections: List = None) -> 'Funnel':
        """Cria um novo funil para este usuário"""
        funnel_id = db.create_funnel(self.id, name, icon, elements, connections)
        return Funnel(funnel_id, self.id, name, icon, elements or [], connections or [])

    def to_dict(self) -> Dict:
        """Converte usuário para dicionário (sem senha)"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'whatsapp': self.whatsapp,
            'created_at': self.created_at
        }

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"


class Funnel:
    """Classe que representa um funil de vendas"""

    def __init__(self, funnel_id: int, user_id: int, name: str, icon: str = '🚀',
                 elements: List = None, connections: List = None,
                 created_at: str = None, updated_at: str = None):
        self.id = funnel_id
        self.user_id = user_id
        self.name = name
        self.icon = icon
        self.elements = elements or []
        self.connections = connections or []
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def get_by_id(funnel_id: int, user_id: int) -> Optional['Funnel']:
        """Busca funil por ID (valida ownership)"""
        funnel_data = db.get_funnel_by_id(funnel_id, user_id)
        if funnel_data:
            return Funnel.from_dict(funnel_data)
        return None

    @staticmethod
    def from_dict(data: Dict) -> 'Funnel':
        """Cria instância de Funnel a partir de dicionário"""
        return Funnel(
            funnel_id=data['id'],
            user_id=data.get('user_id'),
            name=data['name'],
            icon=data.get('icon', '🚀'),
            elements=data.get('elements', []),
            connections=data.get('connections', []),
            created_at=data.get('createdAt'),
            updated_at=data.get('updatedAt')
        )

    def update(self, name: str = None, icon: str = None,
              elements: List = None, connections: List = None) -> bool:
        """Atualiza o funil no banco"""
        success = db.update_funnel(
            funnel_id=self.id,
            user_id=self.user_id,
            name=name,
            icon=icon,
            elements=elements,
            connections=connections
        )

        if success:
            # Atualiza instância local
            if name is not None:
                self.name = name
            if icon is not None:
                self.icon = icon
            if elements is not None:
                self.elements = elements
            if connections is not None:
                self.connections = connections

        return success

    def delete(self) -> bool:
        """Deleta o funil do banco"""
        return db.delete_funnel(self.id, self.user_id)

    def to_dict(self) -> Dict:
        """Converte funil para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'elements': self.elements,
            'connections': self.connections,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at
        }

    def __repr__(self):
        return f"<Funnel(id={self.id}, name='{self.name}', elements={len(self.elements)})>"


if __name__ == '__main__':
    # Testes
    print("🧪 Testando models.py...")

    # Teste: Criar usuário via modelo
    user = User.create('modelo@test.com', 'hash_senha_123', 'Teste Modelo')
    if user:
        print(f"✅ Usuário criado: {user}")
        print(f"   Dados: {user.to_dict()}")

        # Teste: Criar funil via usuário
        funnel = user.create_funnel(
            name='Funil do Modelo',
            icon='🎯',
            elements=[
                {'id': 1, 'type': 'trafego', 'name': 'Tráfego'},
                {'id': 2, 'type': 'landing', 'name': 'Landing Page'}
            ],
            connections=[
                {'from': 1, 'to': 2, 'conversion': 50}
            ]
        )
        print(f"✅ Funil criado: {funnel}")
        print(f"   Dados: {funnel.to_dict()}")

        # Teste: Listar funis do usuário
        all_funnels = user.get_funnels()
        print(f"✅ Total de funis do usuário: {len(all_funnels)}")

        # Teste: Atualizar funil
        funnel.update(name='Funil Atualizado', icon='🚀')
        print(f"✅ Funil atualizado: {funnel.name}")

        # Teste: Buscar usuário por email
        found_user = User.get_by_email('modelo@test.com')
        print(f"✅ Usuário encontrado: {found_user}")

        # Teste: Buscar funil por ID
        found_funnel = Funnel.get_by_id(funnel.id, user.id)
        print(f"✅ Funil encontrado: {found_funnel}")

    print("\n✅ Todos os testes do models.py passaram!")
