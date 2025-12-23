"""
Marketing Routes - Handlers para endpoints de Páginas, UTMs e Métricas
Define as rotas de API para gerenciamento de marketing digital
"""

import json
from typing import Dict
from database import db
from marketing_models import Page, PageTest, UTM, PageMetrics
from validators import validate_url


def handle_pages_list(user_id: int, query_params: Dict = None) -> tuple:
    """GET /api/pages - Lista páginas do usuário"""
    try:
        category = query_params.get('category') if query_params else None
        status = query_params.get('status') if query_params else None

        pages_data = db.get_pages_by_user(user_id, category=category, status=status)
        pages = [Page.from_dict(p).to_dict() for p in pages_data]

        return 200, {
            'success': True,
            'pages': pages,
            'total': len(pages)
        }
    except Exception as e:
        return 500, {'success': False, 'error': f'Erro ao buscar páginas: {str(e)}'}


def handle_page_create(user_id: int, data: Dict) -> tuple:
    """POST /api/pages - Cria nova página"""
    try:
        # Validação
        if not data.get('name') or not data.get('url'):
            return 400, {'success': False, 'error': 'Nome e URL são obrigatórios'}

        url = data.get('url')
        is_valid, error_msg = validate_url(url, optional=False)
        if not is_valid:
            return 400, {'success': False, 'error': error_msg or 'URL inválida'}

        # Criar página
        page_id = db.create_page(
            user_id=user_id,
            name=data.get('name'),
            url=url,
            category=data.get('category', 'landing'),
            description=data.get('description'),
            tags=data.get('tags', []),
            status=data.get('status', 'active'),
            thumbnail_url=data.get('thumbnail_url')
        )

        page_data = db.get_page_by_id(page_id, user_id)
        page = Page.from_dict(page_data)

        return 201, {
            'success': True,
            'message': 'Página criada com sucesso',
            'page': page.to_dict()
        }
    except Exception as e:
        return 500, {'success': False, 'error': f'Erro ao criar página: {str(e)}'}


def handle_page_get(user_id: int, page_id: int) -> tuple:
    """GET /api/pages/:id - Busca página específica"""
    try:
        page_data = db.get_page_by_id(page_id, user_id)

        if not page_data:
            return 404, {'success': False, 'error': 'Página não encontrada'}

        page = Page.from_dict(page_data)

        # Buscar testes da página
        tests_data = db.get_page_tests(page_id, user_id)
        tests = [PageTest.from_dict(t).to_dict() for t in tests_data]

        # Buscar métricas da página (últimos 30 dias)
        metrics_data = db.get_page_metrics(page_id, user_id)
        metrics = [PageMetrics.from_dict(m).to_dict() for m in metrics_data[:30]]

        return 200, {
            'success': True,
            'page': page.to_dict(),
            'tests': tests,
            'metrics': metrics
        }
    except Exception as e:
        return 500, {'success': False, 'error': f'Erro ao buscar página: {str(e)}'}


def handle_page_update(user_id: int, page_id: int, data: Dict) -> tuple:
    """PUT /api/pages/:id - Atualiza página"""
    try:
        # Verificar se página existe
        page_data = db.get_page_by_id(page_id, user_id)
        if not page_data:
            return 404, {'success': False, 'error': 'Página não encontrada'}

        # Validar URL se fornecida
        if 'url' in data:
            is_valid, error_msg = validate_url(data['url'], optional=False)
            if not is_valid:
                return 400, {'success': False, 'error': error_msg or 'URL inválida'}

        # Atualizar
        success = db.update_page(page_id, user_id, **data)

        if not success:
            return 400, {'success': False, 'error': 'Nenhum dado para atualizar'}

        # Retornar página atualizada
        updated_data = db.get_page_by_id(page_id, user_id)
        page = Page.from_dict(updated_data)

        return 200, {
            'success': True,
            'message': 'Página atualizada com sucesso',
            'page': page.to_dict()
        }
    except Exception as e:
        return 500, {'success': False, 'error': f'Erro ao atualizar página: {str(e)}'}


def handle_page_delete(user_id: int, page_id: int) -> tuple:
    """DELETE /api/pages/:id - Deleta página"""
    try:
        success = db.delete_page(page_id, user_id)

        if not success:
            return 404, {'success': False, 'error': 'Página não encontrada'}

        return 200, {
            'success': True,
            'message': 'Página deletada com sucesso'
        }
    except Exception as e:
        return 500, {'success': False, 'error': f'Erro ao deletar página: {str(e)}'}


def handle_page_test_create(user_id: int, page_id: int, data: Dict) -> tuple:
    """POST /api/pages/:id/tests - Adiciona teste/alteração à página"""
    try:
        # Verificar se página existe
        page_data = db.get_page_by_id(page_id, user_id)
        if not page_data:
            return 404, {'success': False, 'error': 'Página não encontrada'}

        # Validação
        if not data.get('title') or not data.get('description') or not data.get('date'):
            return 400, {'success': False, 'error': 'Título, descrição e data são obrigatórios'}

        # Criar teste
        test_id = db.create_page_test(
            page_id=page_id,
            user_id=user_id,
            date=data.get('date'),
            title=data.get('title'),
            description=data.get('description'),
            test_type=data.get('test_type', 'ab_test'),
            results=data.get('results'),
            metrics=data.get('metrics', {})
        )

        # Buscar teste criado
        tests_data = db.get_page_tests(page_id, user_id)
        test = next((t for t in tests_data if t['id'] == test_id), None)

        return 201, {
            'success': True,
            'message': 'Teste adicionado com sucesso',
            'test': PageTest.from_dict(test).to_dict() if test else None
        }
    except Exception as e:
        return 500, {'success': False, 'error': f'Erro ao adicionar teste: {str(e)}'}


def handle_page_test_delete(user_id: int, test_id: int) -> tuple:
    """DELETE /api/pages/tests/:id - Deleta teste de página"""
    try:
        success = db.delete_page_test(test_id, user_id)

        if not success:
            return 404, {'success': False, 'error': 'Teste não encontrado'}

        return 200, {
            'success': True,
            'message': 'Teste deletado com sucesso'
        }
    except Exception as e:
        return 500, {'success': False, 'error': f'Erro ao deletar teste: {str(e)}'}


# ==================== ROTAS DE UTMs ====================

def handle_utms_list(user_id: int) -> tuple:
    """GET /api/utms - Lista UTMs do usuário"""
    try:
        utms_data = db.get_utms_by_user(user_id)
        utms = [UTM.from_dict(u).to_dict() for u in utms_data]

        return 200, {
            'success': True,
            'utms': utms,
            'total': len(utms)
        }
    except Exception as e:
        return 500, {'success': False, 'error': f'Erro ao buscar UTMs: {str(e)}'}


def handle_utm_create(user_id: int, data: Dict) -> tuple:
    """POST /api/utms - Cria nova UTM"""
    try:
        # Validação
        required = ['name', 'utm_source', 'utm_medium', 'utm_campaign']
        missing = [f for f in required if not data.get(f)]

        if missing:
            return 400, {
                'success': False,
                'error': f'Campos obrigatórios faltando: {", ".join(missing)}'
            }

        # Criar UTM
        utm_id = db.create_utm(
            user_id=user_id,
            name=data.get('name'),
            utm_source=data.get('utm_source'),
            utm_medium=data.get('utm_medium'),
            utm_campaign=data.get('utm_campaign'),
            utm_content=data.get('utm_content'),
            utm_term=data.get('utm_term'),
            tags=data.get('tags', []),
            notes=data.get('notes')
        )

        utm_data = db.get_utm_by_id(utm_id, user_id)
        utm = UTM.from_dict(utm_data)

        # Gerar preview de URL
        preview_url = utm.generate_url('https://exemplo.com')

        return 201, {
            'success': True,
            'message': 'UTM criada com sucesso',
            'utm': utm.to_dict(),
            'preview_url': preview_url
        }
    except Exception as e:
        return 500, {'success': False, 'error': f'Erro ao criar UTM: {str(e)}'}


def handle_utm_get(user_id: int, utm_id: int) -> tuple:
    """GET /api/utms/:id - Busca UTM específica"""
    try:
        utm_data = db.get_utm_by_id(utm_id, user_id)

        if not utm_data:
            return 404, {'success': False, 'error': 'UTM não encontrada'}

        utm = UTM.from_dict(utm_data)

        return 200, {
            'success': True,
            'utm': utm.to_dict()
        }
    except Exception as e:
        return 500, {'success': False, 'error': f'Erro ao buscar UTM: {str(e)}'}


def handle_utm_update(user_id: int, utm_id: int, data: Dict) -> tuple:
    """PUT /api/utms/:id - Atualiza UTM"""
    try:
        # Verificar se UTM existe
        utm_data = db.get_utm_by_id(utm_id, user_id)
        if not utm_data:
            return 404, {'success': False, 'error': 'UTM não encontrada'}

        # Atualizar
        success = db.update_utm(utm_id, user_id, **data)

        if not success:
            return 400, {'success': False, 'error': 'Nenhum dado para atualizar'}

        # Retornar UTM atualizada
        updated_data = db.get_utm_by_id(utm_id, user_id)
        utm = UTM.from_dict(updated_data)

        return 200, {
            'success': True,
            'message': 'UTM atualizada com sucesso',
            'utm': utm.to_dict()
        }
    except Exception as e:
        return 500, {'success': False, 'error': f'Erro ao atualizar UTM: {str(e)}'}


def handle_utm_delete(user_id: int, utm_id: int) -> tuple:
    """DELETE /api/utms/:id - Deleta UTM"""
    try:
        success = db.delete_utm(utm_id, user_id)

        if not success:
            return 404, {'success': False, 'error': 'UTM não encontrada'}

        return 200, {
            'success': True,
            'message': 'UTM deletada com sucesso'
        }
    except Exception as e:
        return 500, {'success': False, 'error': f'Erro ao deletar UTM: {str(e)}'}


def handle_utm_generate_url(user_id: int, utm_id: int, data: Dict) -> tuple:
    """POST /api/utms/:id/generate - Gera URL com parâmetros UTM"""
    try:
        # Buscar UTM
        utm_data = db.get_utm_by_id(utm_id, user_id)
        if not utm_data:
            return 404, {'success': False, 'error': 'UTM não encontrada'}

        # Validar URL base
        base_url = data.get('base_url')
        if not base_url:
            return 400, {'success': False, 'error': 'URL base é obrigatória'}

        is_valid, error_msg = validate_url(base_url, optional=False)
        if not is_valid:
            return 400, {'success': False, 'error': error_msg or 'URL base inválida'}

        # Gerar URL
        utm = UTM.from_dict(utm_data)
        generated_url = utm.generate_url(base_url)

        return 200, {
            'success': True,
            'generated_url': generated_url,
            'utm_params': {
                'utm_source': utm.utm_source,
                'utm_medium': utm.utm_medium,
                'utm_campaign': utm.utm_campaign,
                'utm_content': utm.utm_content,
                'utm_term': utm.utm_term
            }
        }
    except Exception as e:
        return 500, {'success': False, 'error': f'Erro ao gerar URL: {str(e)}'}


# ==================== ROTAS DE MÉTRICAS ====================

def handle_metrics_create(user_id: int, page_id: int, data: Dict) -> tuple:
    """POST /api/pages/:id/metrics - Adiciona métricas à página"""
    try:
        # Verificar se página existe
        page_data = db.get_page_by_id(page_id, user_id)
        if not page_data:
            return 404, {'success': False, 'error': 'Página não encontrada'}

        # Validação
        if not data.get('date'):
            return 400, {'success': False, 'error': 'Data é obrigatória'}

        # Criar métricas
        metric_id = db.create_page_metrics(
            page_id=page_id,
            user_id=user_id,
            date=data.get('date'),
            impressions=data.get('impressions', 0),
            clicks=data.get('clicks', 0),
            conversions=data.get('conversions', 0),
            avg_time_on_page=data.get('avg_time_on_page', 0),
            bounce_rate=data.get('bounce_rate', 0),
            utm_id=data.get('utm_id'),
            notes=data.get('notes')
        )

        # Buscar métrica criada
        metrics_data = db.get_page_metrics(page_id, user_id)
        metric = next((m for m in metrics_data if m['id'] == metric_id), None)

        return 201, {
            'success': True,
            'message': 'Métricas adicionadas com sucesso',
            'metric': PageMetrics.from_dict(metric).to_dict() if metric else None
        }
    except Exception as e:
        return 500, {'success': False, 'error': f'Erro ao adicionar métricas: {str(e)}'}


def handle_metrics_list(user_id: int, page_id: int, query_params: Dict = None) -> tuple:
    """GET /api/pages/:id/metrics - Lista métricas da página"""
    try:
        # Verificar se página existe
        page_data = db.get_page_by_id(page_id, user_id)
        if not page_data:
            return 404, {'success': False, 'error': 'Página não encontrada'}

        start_date = query_params.get('start_date') if query_params else None
        end_date = query_params.get('end_date') if query_params else None

        metrics_data = db.get_page_metrics(page_id, user_id, start_date, end_date)
        metrics = [PageMetrics.from_dict(m).to_dict() for m in metrics_data]

        # Calcular estatísticas agregadas
        total_impressions = sum(m['impressions'] for m in metrics)
        total_clicks = sum(m['clicks'] for m in metrics)
        total_conversions = sum(m['conversions'] for m in metrics)

        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0

        return 200, {
            'success': True,
            'metrics': metrics,
            'total': len(metrics),
            'summary': {
                'total_impressions': total_impressions,
                'total_clicks': total_clicks,
                'total_conversions': total_conversions,
                'avg_ctr': round(avg_ctr, 2),
                'avg_conversion_rate': round(avg_conversion_rate, 2)
            }
        }
    except Exception as e:
        return 500, {'success': False, 'error': f'Erro ao buscar métricas: {str(e)}'}


def handle_metrics_delete(user_id: int, metric_id: int) -> tuple:
    """DELETE /api/metrics/:id - Deleta métrica"""
    try:
        success = db.delete_page_metrics(metric_id, user_id)

        if not success:
            return 404, {'success': False, 'error': 'Métrica não encontrada'}

        return 200, {
            'success': True,
            'message': 'Métrica deletada com sucesso'
        }
    except Exception as e:
        return 500, {'success': False, 'error': f'Erro ao deletar métrica: {str(e)}'}
