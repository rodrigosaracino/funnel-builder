"""
Database module for Funnel Builder
Gerencia conexão SQLite e operações CRUD
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional


class Database:
    """Classe para gerenciar operações do banco de dados"""

    def __init__(self, db_path='funnel_builder.db'):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Retorna uma nova conexão com o banco"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
        return conn

    def init_db(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabela de funis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS funnels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                icon TEXT DEFAULT '🚀',
                elements TEXT,
                connections TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # Índices para performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_funnels_user_id ON funnels(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')

        conn.commit()
        conn.close()
        print("✅ Banco de dados inicializado com sucesso!")

    # ==================== OPERAÇÕES DE USUÁRIO ====================

    def create_user(self, email: str, password_hash: str, name: str = None) -> Optional[int]:
        """Cria um novo usuário"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)',
                (email, password_hash, name)
            )
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            # Email já existe
            return None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Busca usuário por email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row['id'],
                'email': row['email'],
                'password_hash': row['password_hash'],
                'name': row['name'],
                'created_at': row['created_at']
            }
        return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Busca usuário por ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, name, created_at FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row['id'],
                'email': row['email'],
                'name': row['name'],
                'created_at': row['created_at']
            }
        return None

    # ==================== OPERAÇÕES DE FUNIL ====================

    def create_funnel(self, user_id: int, name: str, icon: str = '🚀',
                     elements: List = None, connections: List = None) -> int:
        """Cria um novo funil"""
        conn = self.get_connection()
        cursor = conn.cursor()

        elements_json = json.dumps(elements or [])
        connections_json = json.dumps(connections or [])

        cursor.execute('''
            INSERT INTO funnels (user_id, name, icon, elements, connections)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, name, icon, elements_json, connections_json))

        funnel_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return funnel_id

    def get_funnels_by_user(self, user_id: int) -> List[Dict]:
        """Retorna todos os funis de um usuário"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, icon, elements, connections, created_at, updated_at
            FROM funnels
            WHERE user_id = ?
            ORDER BY updated_at DESC
        ''', (user_id,))

        rows = cursor.fetchall()
        conn.close()

        funnels = []
        for row in rows:
            funnels.append({
                'id': row['id'],
                'name': row['name'],
                'icon': row['icon'],
                'elements': json.loads(row['elements']) if row['elements'] else [],
                'connections': json.loads(row['connections']) if row['connections'] else [],
                'createdAt': row['created_at'],
                'updatedAt': row['updated_at']
            })

        return funnels

    def get_funnel_by_id(self, funnel_id: int, user_id: int) -> Optional[Dict]:
        """Retorna um funil específico (valida se pertence ao usuário)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, user_id, name, icon, elements, connections, created_at, updated_at
            FROM funnels
            WHERE id = ? AND user_id = ?
        ''', (funnel_id, user_id))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row['id'],
                'user_id': row['user_id'],
                'name': row['name'],
                'icon': row['icon'],
                'elements': json.loads(row['elements']) if row['elements'] else [],
                'connections': json.loads(row['connections']) if row['connections'] else [],
                'createdAt': row['created_at'],
                'updatedAt': row['updated_at']
            }
        return None

    def update_funnel(self, funnel_id: int, user_id: int, name: str = None,
                     icon: str = None, elements: List = None,
                     connections: List = None) -> bool:
        """Atualiza um funil existente"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Monta query dinâmica baseado nos campos fornecidos
            updates = []
            params = []

            if name is not None:
                updates.append('name = ?')
                params.append(name)

            if icon is not None:
                updates.append('icon = ?')
                params.append(icon)

            if elements is not None:
                updates.append('elements = ?')
                params.append(json.dumps(elements))

            if connections is not None:
                updates.append('connections = ?')
                params.append(json.dumps(connections))

            if not updates:
                return False

            # Sempre atualiza o timestamp
            updates.append('updated_at = CURRENT_TIMESTAMP')

            query = f"UPDATE funnels SET {', '.join(updates)} WHERE id = ? AND user_id = ?"
            params.extend([funnel_id, user_id])

            cursor.execute(query, params)
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()

            return rows_affected > 0
        except Exception as e:
            print(f"❌ Erro ao atualizar funil: {e}")
            return False

    def delete_funnel(self, funnel_id: int, user_id: int) -> bool:
        """Deleta um funil"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM funnels WHERE id = ? AND user_id = ?', (funnel_id, user_id))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0

    # ==================== UTILITÁRIOS ====================

    def get_stats(self) -> Dict:
        """Retorna estatísticas do banco"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) as count FROM users')
        users_count = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM funnels')
        funnels_count = cursor.fetchone()['count']

        conn.close()

        return {
            'total_users': users_count,
            'total_funnels': funnels_count
        }


# Instância global do banco
db = Database()


if __name__ == '__main__':
    # Testes básicos
    print("🧪 Testando database.py...")

    test_db = Database('test_funnel.db')

    # Teste: criar usuário
    user_id = test_db.create_user('teste@email.com', 'hash123', 'Usuário Teste')
    print(f"✅ Usuário criado com ID: {user_id}")

    # Teste: buscar usuário
    user = test_db.get_user_by_email('teste@email.com')
    print(f"✅ Usuário encontrado: {user['email']}")

    # Teste: criar funil
    funnel_id = test_db.create_funnel(
        user_id=user_id,
        name='Funil Teste',
        icon='🎯',
        elements=[{'id': 1, 'type': 'trafego', 'name': 'Tráfego Pago'}],
        connections=[]
    )
    print(f"✅ Funil criado com ID: {funnel_id}")

    # Teste: listar funis
    funnels = test_db.get_funnels_by_user(user_id)
    print(f"✅ Total de funis do usuário: {len(funnels)}")

    # Teste: estatísticas
    stats = test_db.get_stats()
    print(f"✅ Estatísticas: {stats}")

    print("\n✅ Todos os testes passaram!")
