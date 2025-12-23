"""
Marketing Models - Gerenciamento de Páginas e UTMs
Classes para representar páginas, UTMs e testes A/B
"""

from typing import List, Dict, Optional
from datetime import datetime
import json


class Page:
    """Classe que representa uma página de marketing"""

    def __init__(self, page_id: int, user_id: int, name: str, url: str,
                 category: str = 'landing', description: str = None,
                 tags: List[str] = None, status: str = 'active',
                 thumbnail_url: str = None, created_at: str = None,
                 updated_at: str = None):
        self.id = page_id
        self.user_id = user_id
        self.name = name
        self.url = url
        self.category = category  # landing, vsl, checkout, thankyou, webinar, etc.
        self.description = description
        self.tags = tags or []
        self.status = status  # active, testing, paused, archived
        self.thumbnail_url = thumbnail_url
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def from_dict(data: Dict) -> 'Page':
        """Cria instância de Page a partir de dicionário"""
        return Page(
            page_id=data['id'],
            user_id=data['user_id'],
            name=data['name'],
            url=data['url'],
            category=data.get('category', 'landing'),
            description=data.get('description'),
            tags=json.loads(data.get('tags', '[]')) if isinstance(data.get('tags'), str) else data.get('tags', []),
            status=data.get('status', 'active'),
            thumbnail_url=data.get('thumbnail_url'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> Dict:
        """Converte página para dicionário"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'url': self.url,
            'category': self.category,
            'description': self.description,
            'tags': self.tags,
            'status': self.status,
            'thumbnail_url': self.thumbnail_url,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def __repr__(self):
        return f"<Page(id={self.id}, name='{self.name}', category='{self.category}')>"


class PageTest:
    """Classe que representa um teste A/B ou alteração em uma página"""

    def __init__(self, test_id: int, page_id: int, user_id: int,
                 date: str, title: str, description: str,
                 test_type: str = 'ab_test', results: str = None,
                 metrics: Dict = None, created_at: str = None):
        self.id = test_id
        self.page_id = page_id
        self.user_id = user_id
        self.date = date  # Data da alteração/teste
        self.title = title  # Ex: "Mudança do headline principal"
        self.description = description  # Detalhes do que foi alterado
        self.test_type = test_type  # ab_test, design_change, copy_change, etc.
        self.results = results  # Resultados observados
        self.metrics = metrics or {}  # {'conversion_before': 2.5, 'conversion_after': 3.8}
        self.created_at = created_at

    @staticmethod
    def from_dict(data: Dict) -> 'PageTest':
        """Cria instância de PageTest a partir de dicionário"""
        return PageTest(
            test_id=data['id'],
            page_id=data['page_id'],
            user_id=data['user_id'],
            date=data['date'],
            title=data['title'],
            description=data['description'],
            test_type=data.get('test_type', 'ab_test'),
            results=data.get('results'),
            metrics=json.loads(data.get('metrics', '{}')) if isinstance(data.get('metrics'), str) else data.get('metrics', {}),
            created_at=data.get('created_at')
        )

    def to_dict(self) -> Dict:
        """Converte teste para dicionário"""
        return {
            'id': self.id,
            'page_id': self.page_id,
            'user_id': self.user_id,
            'date': self.date,
            'title': self.title,
            'description': self.description,
            'test_type': self.test_type,
            'results': self.results,
            'metrics': self.metrics,
            'created_at': self.created_at
        }

    def __repr__(self):
        return f"<PageTest(id={self.id}, page_id={self.page_id}, title='{self.title}')>"


class UTM:
    """Classe que representa um conjunto de parâmetros UTM"""

    def __init__(self, utm_id: int, user_id: int, name: str,
                 utm_source: str, utm_medium: str, utm_campaign: str,
                 utm_content: str = None, utm_term: str = None,
                 tags: List[str] = None, notes: str = None,
                 created_at: str = None, updated_at: str = None):
        self.id = utm_id
        self.user_id = user_id
        self.name = name  # Nome descritivo: "Black Friday - Facebook Ads"
        self.utm_source = utm_source  # Ex: facebook, google, instagram
        self.utm_medium = utm_medium  # Ex: cpc, email, social
        self.utm_campaign = utm_campaign  # Ex: black_friday_2024
        self.utm_content = utm_content  # Ex: video_ad_1, banner_top
        self.utm_term = utm_term  # Ex: marketing_digital, funil_vendas
        self.tags = tags or []  # Para organização
        self.notes = notes  # Observações sobre a campanha
        self.created_at = created_at
        self.updated_at = updated_at

    def generate_url(self, base_url: str) -> str:
        """Gera URL completa com parâmetros UTM"""
        params = []
        params.append(f"utm_source={self.utm_source}")
        params.append(f"utm_medium={self.utm_medium}")
        params.append(f"utm_campaign={self.utm_campaign}")

        if self.utm_content:
            params.append(f"utm_content={self.utm_content}")
        if self.utm_term:
            params.append(f"utm_term={self.utm_term}")

        separator = '&' if '?' in base_url else '?'
        return f"{base_url}{separator}{'&'.join(params)}"

    @staticmethod
    def from_dict(data: Dict) -> 'UTM':
        """Cria instância de UTM a partir de dicionário"""
        return UTM(
            utm_id=data['id'],
            user_id=data['user_id'],
            name=data['name'],
            utm_source=data['utm_source'],
            utm_medium=data['utm_medium'],
            utm_campaign=data['utm_campaign'],
            utm_content=data.get('utm_content'),
            utm_term=data.get('utm_term'),
            tags=json.loads(data.get('tags', '[]')) if isinstance(data.get('tags'), str) else data.get('tags', []),
            notes=data.get('notes'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> Dict:
        """Converte UTM para dicionário"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'utm_source': self.utm_source,
            'utm_medium': self.utm_medium,
            'utm_campaign': self.utm_campaign,
            'utm_content': self.utm_content,
            'utm_term': self.utm_term,
            'tags': self.tags,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def __repr__(self):
        return f"<UTM(id={self.id}, name='{self.name}', campaign='{self.utm_campaign}')>"


class PageMetrics:
    """Classe que representa métricas de uma página"""

    def __init__(self, metric_id: int, page_id: int, user_id: int,
                 date: str, impressions: int = 0, clicks: int = 0,
                 conversions: int = 0, avg_time_on_page: float = 0,
                 bounce_rate: float = 0, utm_id: int = None,
                 notes: str = None, created_at: str = None):
        self.id = metric_id
        self.page_id = page_id
        self.user_id = user_id
        self.date = date  # Data da métrica (formato: YYYY-MM-DD)
        self.impressions = impressions
        self.clicks = clicks
        self.conversions = conversions
        self.avg_time_on_page = avg_time_on_page  # Em segundos
        self.bounce_rate = bounce_rate  # Porcentagem
        self.utm_id = utm_id  # Relaciona métrica com uma UTM específica
        self.notes = notes
        self.created_at = created_at

    @property
    def ctr(self) -> float:
        """Calcula CTR (Click-Through Rate)"""
        if self.impressions == 0:
            return 0
        return (self.clicks / self.impressions) * 100

    @property
    def conversion_rate(self) -> float:
        """Calcula taxa de conversão"""
        if self.clicks == 0:
            return 0
        return (self.conversions / self.clicks) * 100

    @staticmethod
    def from_dict(data: Dict) -> 'PageMetrics':
        """Cria instância de PageMetrics a partir de dicionário"""
        return PageMetrics(
            metric_id=data['id'],
            page_id=data['page_id'],
            user_id=data['user_id'],
            date=data['date'],
            impressions=data.get('impressions', 0),
            clicks=data.get('clicks', 0),
            conversions=data.get('conversions', 0),
            avg_time_on_page=data.get('avg_time_on_page', 0),
            bounce_rate=data.get('bounce_rate', 0),
            utm_id=data.get('utm_id'),
            notes=data.get('notes'),
            created_at=data.get('created_at')
        )

    def to_dict(self) -> Dict:
        """Converte métrica para dicionário"""
        return {
            'id': self.id,
            'page_id': self.page_id,
            'user_id': self.user_id,
            'date': self.date,
            'impressions': self.impressions,
            'clicks': self.clicks,
            'conversions': self.conversions,
            'avg_time_on_page': self.avg_time_on_page,
            'bounce_rate': self.bounce_rate,
            'ctr': self.ctr,
            'conversion_rate': self.conversion_rate,
            'utm_id': self.utm_id,
            'notes': self.notes,
            'created_at': self.created_at
        }

    def __repr__(self):
        return f"<PageMetrics(id={self.id}, page_id={self.page_id}, date='{self.date}')>"


if __name__ == '__main__':
    # Testes básicos
    print("🧪 Testando marketing_models.py...")

    # Teste: Criar página
    page = Page(
        page_id=1,
        user_id=1,
        name='Landing Page - Curso Digital',
        url='https://exemplo.com/curso-digital',
        category='landing',
        description='Landing page principal do curso',
        tags=['produto-digital', 'cursos'],
        status='active'
    )
    print(f"✅ Página criada: {page}")
    print(f"   Dados: {page.to_dict()}")

    # Teste: Criar UTM
    utm = UTM(
        utm_id=1,
        user_id=1,
        name='Black Friday - Facebook',
        utm_source='facebook',
        utm_medium='cpc',
        utm_campaign='black_friday_2024',
        utm_content='video_ad_1',
        tags=['black-friday', 'video']
    )
    print(f"\n✅ UTM criada: {utm}")
    print(f"   URL gerada: {utm.generate_url('https://exemplo.com/curso')}")

    # Teste: Criar teste de página
    test = PageTest(
        test_id=1,
        page_id=1,
        user_id=1,
        date='2024-11-15',
        title='Mudança de headline',
        description='Alterado headline de "Aprenda Marketing" para "Domine Marketing Digital em 30 dias"',
        test_type='ab_test',
        results='Aumento de 25% na conversão',
        metrics={'conversion_before': 2.5, 'conversion_after': 3.1}
    )
    print(f"\n✅ Teste criado: {test}")
    print(f"   Dados: {test.to_dict()}")

    # Teste: Criar métricas
    metrics = PageMetrics(
        metric_id=1,
        page_id=1,
        user_id=1,
        date='2024-11-20',
        impressions=10000,
        clicks=500,
        conversions=25
    )
    print(f"\n✅ Métricas criadas: {metrics}")
    print(f"   CTR: {metrics.ctr:.2f}%")
    print(f"   Taxa de conversão: {metrics.conversion_rate:.2f}%")

    print("\n✅ Todos os testes de marketing_models.py passaram!")
