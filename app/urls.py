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
    cadastro_usuario,
    login_usuario,
    dashboard_usuario,
    gerar_fechamento_mensal,
    gerar_indicadores_financeiros,
    gerar_alertas_financeiros,
    negocios_do_usuario,
    receitas_do_usuario,
    despesas_do_usuario,
    produtos_do_usuario,
    servicos_do_usuario,
    alertas_do_usuario,
    fechamentos_do_usuario,
    resumo_mensal_negocio,
    fluxo_caixa_negocio,
    criar_receita,
    criar_despesa,
    criar_produto,
    criar_servico,
    criar_negocio_usuario,
    criar_categoria,
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
    path('auth/cadastro/', cadastro_usuario),
    path('auth/login/', login_usuario),
    path('financeiro/usuarios/<int:usuario_id>/dashboard/', dashboard_usuario),
    path('financeiro/fechamento-mensal/gerar/', gerar_fechamento_mensal),
    path('financeiro/negocios/<int:negocio_id>/indicadores/gerar/', gerar_indicadores_financeiros),
    path('financeiro/negocios/<int:negocio_id>/alertas/gerar/', gerar_alertas_financeiros),
    path('usuarios/<int:usuario_id>/negocios/', negocios_do_usuario),
    path('usuarios/<int:usuario_id>/receitas/', receitas_do_usuario),
    path('usuarios/<int:usuario_id>/despesas/', despesas_do_usuario),
    path('usuarios/<int:usuario_id>/produtos/', produtos_do_usuario),
    path('usuarios/<int:usuario_id>/servicos/', servicos_do_usuario),
    path('usuarios/<int:usuario_id>/alertas/', alertas_do_usuario),
    path('usuarios/<int:usuario_id>/fechamentos/', fechamentos_do_usuario),
    path('financeiro/negocios/<int:negocio_id>/resumo-mensal/<int:ano>/<int:mes>/', resumo_mensal_negocio),
    path('financeiro/negocios/<int:negocio_id>/fluxo-caixa/', fluxo_caixa_negocio),
    path('negocios/<int:negocio_id>/receitas/criar/', criar_receita),
    path('negocios/<int:negocio_id>/despesas/criar/', criar_despesa),
    path('negocios/<int:negocio_id>/produtos/criar/', criar_produto),
    path('negocios/<int:negocio_id>/servicos/criar/', criar_servico),
    path('usuarios/<int:usuario_id>/negocios/criar/', criar_negocio_usuario),
    path('categorias/criar/', criar_categoria),
]