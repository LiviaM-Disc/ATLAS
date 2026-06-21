from django.urls import path

from . import views


urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("cadastro/", views.cadastro_view, name="cadastro"),
    path(
        "cadastrar-negocio/",
        views.cadastrar_negocio_view,
        name="cadastrar_negocio",
    ),

    path("", views.index_view, name="index"),

    path("negocios/", views.listar_negocios, name="listar_negocios"),
    path("receitas/", views.lista_receitas, name="lista_receitas"),

    path("despesas/", views.despesas_view, name="despesas"),
    path(
        "despesas/<int:despesa_id>/marcar-paga/",
        views.marcar_despesa_paga,
        name="marcar_despesa_paga",
    ),

    path("produtos/", views.produtos_view, name="produtos"),
    path("servicos/", views.servicos_view, name="servicos"),
    path("categorias/", views.categoria_view, name="categorias"),
    path("precificacoes/", views.precificacoes_view, name="precificacoes"),
    path("metas/", views.metas_view, name="metas"),
    path("alertas/", views.alertas_view, name="alertas"),
    path("relatorios/", views.relatorios_view, name="relatorios"),

    path("indicadores/", views.indicadores_view, name="indicadores"),
    path(
        "indicadores-financeiros/",
        views.indicadores_view,
        name="indicadores_financeiros",
    ),

    path("fechamentos/", views.fechamentos_view, name="fechamentos"),
    path(
        "fechamentos-mensais/",
        views.fechamentos_view,
        name="fechamentos_mensais",
    ),

    path(
        "notificacoes/",
        views.notificacoes_view,
        name="notificacoes",
    ),

    path("usuarios/", views.usuarios_view, name="usuarios"),
]