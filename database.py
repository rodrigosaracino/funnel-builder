"""
Database module for Funnel Builder
Gerencia conexão SQLite e operações CRUD
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class Database:
    """Classe para gerenciar operações do banco de dados"""

    def __init__(self, db_path=None):
        # Se rodando em Docker, usa /app/data/
        # Senão, usa o diretório atual
        if db_path is None:
            if os.path.exists('/app/data'):
                db_path = '/app/data/funnel_builder.db'
            else:
                db_path = 'funnel_builder.db'

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
                whatsapp TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Adiciona coluna whatsapp se não existir (migração)
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN whatsapp TEXT')
            print("✅ Coluna whatsapp adicionada à tabela users")
        except sqlite3.OperationalError:
            # Coluna já existe
            pass

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

        # Tabela de páginas de marketing
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                category TEXT DEFAULT 'landing',
                description TEXT,
                tags TEXT,
                status TEXT DEFAULT 'active',
                thumbnail_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # Tabela de testes/alterações em páginas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS page_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                test_type TEXT DEFAULT 'ab_test',
                results TEXT,
                metrics TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # Tabela de UTMs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS utms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                utm_source TEXT NOT NULL,
                utm_medium TEXT NOT NULL,
                utm_campaign TEXT NOT NULL,
                utm_content TEXT,
                utm_term TEXT,
                tags TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # Tabela de métricas de páginas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS page_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                impressions INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                conversions INTEGER DEFAULT 0,
                avg_time_on_page REAL DEFAULT 0,
                bounce_rate REAL DEFAULT 0,
                utm_id INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (utm_id) REFERENCES utms(id) ON DELETE SET NULL
            )
        ''')

        # Índices para performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_funnels_user_id ON funnels(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pages_user_id ON pages(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_page_tests_page_id ON page_tests(page_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_utms_user_id ON utms(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_page_metrics_page_id ON page_metrics(page_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_page_metrics_date ON page_metrics(date)')

        conn.commit()
        conn.close()
        print("✅ Banco de dados inicializado com sucesso!")

    # ==================== OPERAÇÕES DE USUÁRIO ====================

    def create_user(self, email: str, password_hash: str, name: str = None, whatsapp: str = None) -> Optional[int]:
        """Cria um novo usuário"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (email, password_hash, name, whatsapp) VALUES (?, ?, ?, ?)',
                (email, password_hash, name, whatsapp)
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
                'whatsapp': row['whatsapp'] if 'whatsapp' in row.keys() else None,
                'created_at': row['created_at']
            }
        return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Busca usuário por ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, name, whatsapp, created_at FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row['id'],
                'email': row['email'],
                'name': row['name'],
                'whatsapp': row['whatsapp'] if 'whatsapp' in row.keys() else None,
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

    # ==================== OPERAÇÕES DE PÁGINAS ====================

    def create_page(self, user_id: int, name: str, url: str, category: str = 'landing',
                   description: str = None, tags: List[str] = None, status: str = 'active',
                   thumbnail_url: str = None) -> int:
        """Cria uma nova página de marketing"""
        conn = self.get_connection()
        cursor = conn.cursor()

        tags_json = json.dumps(tags or [])

        cursor.execute('''
            INSERT INTO pages (user_id, name, url, category, description, tags, status, thumbnail_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, url, category, description, tags_json, status, thumbnail_url))

        page_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return page_id

    def get_pages_by_user(self, user_id: int, category: str = None, status: str = None) -> List[Dict]:
        """Retorna todas as páginas de um usuário"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM pages WHERE user_id = ?'
        params = [user_id]

        if category:
            query += ' AND category = ?'
            params.append(category)

        if status:
            query += ' AND status = ?'
            params.append(status)

        query += ' ORDER BY updated_at DESC'

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        pages = []
        for row in rows:
            pages.append({
                'id': row['id'],
                'user_id': row['user_id'],
                'name': row['name'],
                'url': row['url'],
                'category': row['category'],
                'description': row['description'],
                'tags': json.loads(row['tags']) if row['tags'] else [],
                'status': row['status'],
                'thumbnail_url': row['thumbnail_url'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })

        return pages

    def get_page_by_id(self, page_id: int, user_id: int) -> Optional[Dict]:
        """Retorna uma página específica"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM pages WHERE id = ? AND user_id = ?', (page_id, user_id))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row['id'],
                'user_id': row['user_id'],
                'name': row['name'],
                'url': row['url'],
                'category': row['category'],
                'description': row['description'],
                'tags': json.loads(row['tags']) if row['tags'] else [],
                'status': row['status'],
                'thumbnail_url': row['thumbnail_url'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
        return None

    def update_page(self, page_id: int, user_id: int, **kwargs) -> bool:
        """Atualiza uma página"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            updates = []
            params = []

            for key, value in kwargs.items():
                if key in ['name', 'url', 'category', 'description', 'status', 'thumbnail_url']:
                    updates.append(f'{key} = ?')
                    params.append(value)
                elif key == 'tags':
                    updates.append('tags = ?')
                    params.append(json.dumps(value))

            if not updates:
                return False

            updates.append('updated_at = CURRENT_TIMESTAMP')
            query = f"UPDATE pages SET {', '.join(updates)} WHERE id = ? AND user_id = ?"
            params.extend([page_id, user_id])

            cursor.execute(query, params)
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()

            return rows_affected > 0
        except Exception as e:
            print(f"❌ Erro ao atualizar página: {e}")
            return False

    def delete_page(self, page_id: int, user_id: int) -> bool:
        """Deleta uma página e seus dados relacionados"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM pages WHERE id = ? AND user_id = ?', (page_id, user_id))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0

    # ==================== OPERAÇÕES DE TESTES DE PÁGINA ====================

    def create_page_test(self, page_id: int, user_id: int, date: str, title: str,
                        description: str, test_type: str = 'ab_test', results: str = None,
                        metrics: Dict = None) -> int:
        """Cria um novo teste/alteração em uma página"""
        conn = self.get_connection()
        cursor = conn.cursor()

        metrics_json = json.dumps(metrics or {})

        cursor.execute('''
            INSERT INTO page_tests (page_id, user_id, date, title, description, test_type, results, metrics)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (page_id, user_id, date, title, description, test_type, results, metrics_json))

        test_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return test_id

    def get_page_tests(self, page_id: int, user_id: int) -> List[Dict]:
        """Retorna todos os testes de uma página"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM page_tests
            WHERE page_id = ? AND user_id = ?
            ORDER BY date DESC
        ''', (page_id, user_id))

        rows = cursor.fetchall()
        conn.close()

        tests = []
        for row in rows:
            tests.append({
                'id': row['id'],
                'page_id': row['page_id'],
                'user_id': row['user_id'],
                'date': row['date'],
                'title': row['title'],
                'description': row['description'],
                'test_type': row['test_type'],
                'results': row['results'],
                'metrics': json.loads(row['metrics']) if row['metrics'] else {},
                'created_at': row['created_at']
            })

        return tests

    def delete_page_test(self, test_id: int, user_id: int) -> bool:
        """Deleta um teste de página"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM page_tests WHERE id = ? AND user_id = ?', (test_id, user_id))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0

    # ==================== OPERAÇÕES DE UTMs ====================

    def create_utm(self, user_id: int, name: str, utm_source: str, utm_medium: str,
                  utm_campaign: str, utm_content: str = None, utm_term: str = None,
                  tags: List[str] = None, notes: str = None) -> int:
        """Cria um novo conjunto de parâmetros UTM"""
        conn = self.get_connection()
        cursor = conn.cursor()

        tags_json = json.dumps(tags or [])

        cursor.execute('''
            INSERT INTO utms (user_id, name, utm_source, utm_medium, utm_campaign,
                            utm_content, utm_term, tags, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, utm_source, utm_medium, utm_campaign, utm_content, utm_term, tags_json, notes))

        utm_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return utm_id

    def get_utms_by_user(self, user_id: int) -> List[Dict]:
        """Retorna todas as UTMs de um usuário"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM utms
            WHERE user_id = ?
            ORDER BY updated_at DESC
        ''', (user_id,))

        rows = cursor.fetchall()
        conn.close()

        utms = []
        for row in rows:
            utms.append({
                'id': row['id'],
                'user_id': row['user_id'],
                'name': row['name'],
                'utm_source': row['utm_source'],
                'utm_medium': row['utm_medium'],
                'utm_campaign': row['utm_campaign'],
                'utm_content': row['utm_content'],
                'utm_term': row['utm_term'],
                'tags': json.loads(row['tags']) if row['tags'] else [],
                'notes': row['notes'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            })

        return utms

    def get_utm_by_id(self, utm_id: int, user_id: int) -> Optional[Dict]:
        """Retorna uma UTM específica"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM utms WHERE id = ? AND user_id = ?', (utm_id, user_id))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row['id'],
                'user_id': row['user_id'],
                'name': row['name'],
                'utm_source': row['utm_source'],
                'utm_medium': row['utm_medium'],
                'utm_campaign': row['utm_campaign'],
                'utm_content': row['utm_content'],
                'utm_term': row['utm_term'],
                'tags': json.loads(row['tags']) if row['tags'] else [],
                'notes': row['notes'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
        return None

    def update_utm(self, utm_id: int, user_id: int, **kwargs) -> bool:
        """Atualiza uma UTM"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            updates = []
            params = []

            for key, value in kwargs.items():
                if key in ['name', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'notes']:
                    updates.append(f'{key} = ?')
                    params.append(value)
                elif key == 'tags':
                    updates.append('tags = ?')
                    params.append(json.dumps(value))

            if not updates:
                return False

            updates.append('updated_at = CURRENT_TIMESTAMP')
            query = f"UPDATE utms SET {', '.join(updates)} WHERE id = ? AND user_id = ?"
            params.extend([utm_id, user_id])

            cursor.execute(query, params)
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()

            return rows_affected > 0
        except Exception as e:
            print(f"❌ Erro ao atualizar UTM: {e}")
            return False

    def delete_utm(self, utm_id: int, user_id: int) -> bool:
        """Deleta uma UTM"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM utms WHERE id = ? AND user_id = ?', (utm_id, user_id))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0

    # ==================== OPERAÇÕES DE MÉTRICAS DE PÁGINA ====================

    def create_page_metrics(self, page_id: int, user_id: int, date: str,
                           impressions: int = 0, clicks: int = 0, conversions: int = 0,
                           avg_time_on_page: float = 0, bounce_rate: float = 0,
                           utm_id: int = None, notes: str = None) -> int:
        """Cria registro de métricas para uma página"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO page_metrics (page_id, user_id, date, impressions, clicks, conversions,
                                     avg_time_on_page, bounce_rate, utm_id, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (page_id, user_id, date, impressions, clicks, conversions, avg_time_on_page, bounce_rate, utm_id, notes))

        metric_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return metric_id

    def get_page_metrics(self, page_id: int, user_id: int, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Retorna métricas de uma página"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM page_metrics WHERE page_id = ? AND user_id = ?'
        params = [page_id, user_id]

        if start_date:
            query += ' AND date >= ?'
            params.append(start_date)

        if end_date:
            query += ' AND date <= ?'
            params.append(end_date)

        query += ' ORDER BY date DESC'

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        metrics = []
        for row in rows:
            metrics.append({
                'id': row['id'],
                'page_id': row['page_id'],
                'user_id': row['user_id'],
                'date': row['date'],
                'impressions': row['impressions'],
                'clicks': row['clicks'],
                'conversions': row['conversions'],
                'avg_time_on_page': row['avg_time_on_page'],
                'bounce_rate': row['bounce_rate'],
                'utm_id': row['utm_id'],
                'notes': row['notes'],
                'created_at': row['created_at']
            })

        return metrics

    def delete_page_metrics(self, metric_id: int, user_id: int) -> bool:
        """Deleta registro de métricas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM page_metrics WHERE id = ? AND user_id = ?', (metric_id, user_id))
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

        cursor.execute('SELECT COUNT(*) as count FROM pages')
        pages_count = cursor.fetchone()['count']

        cursor.execute('SELECT COUNT(*) as count FROM utms')
        utms_count = cursor.fetchone()['count']

        conn.close()

        return {
            'total_users': users_count,
            'total_funnels': funnels_count,
            'total_pages': pages_count,
            'total_utms': utms_count
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
