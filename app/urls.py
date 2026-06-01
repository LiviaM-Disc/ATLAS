from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AlertaViewSet,
    CategoriaViewSet,
    DashboardViewSet,
    DespesaViewSet,
    FechamentoMensalViewSet,
    IndicadorFinanceiroViewSet,
    MetaFinanceiraViewSet,
    NegocioViewSet,
    NotificacaoViewSet,
    PrecificacaoViewSet,
    ProdutoViewSet,
    ReceitaViewSet,
    RelatorioViewSet,
    ServicoViewSet,
    UsuarioViewSet,
    resumo_financeiro,
    simular_precificacao,
)

router = DefaultRouter()

router.register('usuarios', UsuarioViewSet)
router.register('negocios', NegocioViewSet)
router.register('categorias', CategoriaViewSet)
router.register('receitas', ReceitaViewSet)
router.register('despesas', DespesaViewSet)
router.register('produtos', ProdutoViewSet)
router.register('servicos', ServicoViewSet)
router.register('precificacoes', PrecificacaoViewSet)
router.register('relatorios', RelatorioViewSet)
router.register('metas', MetaFinanceiraViewSet)
router.register('alertas', AlertaViewSet)
router.register('fechamentos', FechamentoMensalViewSet)
router.register('notificacoes', NotificacaoViewSet)
router.register('indicadores', IndicadorFinanceiroViewSet)
router.register('dashboards', DashboardViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('financeiro/negocios/<int:negocio_id>/resumo/', resumo_financeiro),
    path('financeiro/precificacao/simular/', simular_precificacao),
]