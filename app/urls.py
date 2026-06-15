from django.urls import path
from . import views

urlpatterns = [

    # ==========================
    # AUTENTICAÇÃO
    # ==========================
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('cadastrar-negocio/', views.cadastrar_negocio_view, name='cadastrar_negocio'),

    # ==========================
    # DASHBOARD
    # ==========================
    path('', views.index_view, name='index'),

    # ==========================
    # NEGÓCIOS
    # ==========================
    path('negocios/', views.listar_negocios, name='listar_negocios'),

    # ==========================
    # RECEITAS
    # ==========================
    path('receitas/', views.lista_receitas, name='lista_receitas'),

    # ==========================
    # DESPESAS
    # ==========================
    path('despesas/', views.despesas_view, name='despesas'),

    # ==========================
    # PRODUTOS
    # ==========================
    path('produtos/', views.produtos_view, name='produtos'),

    # ==========================
    # SERVIÇOS
    # ==========================
    path('servicos/', views.servicos_view, name='servicos'),

    # ==========================
    # CATEGORIAS
    # ==========================
    path('categorias/', views.categoria_view, name='categorias'),

    # ==========================
    # PRECIFICAÇÃO
    # ==========================
    path('precificacoes/', views.precificacoes_view, name='precificacoes'),

    # ==========================
    # METAS
    # ==========================
    path('metas/', views.metas_view, name='metas'),

    # ==========================
    # ALERTAS
    # ==========================
    path('alertas/', views.alertas_view, name='alertas'),

    # ==========================
    # RELATÓRIOS
    # ==========================
    path('relatorios/', views.relatorios_view, name='relatorios'),

    # ==========================
    # INDICADORES
    # ==========================
    path('indicadores/', views.indicadores_view, name='indicadores'),

    # ==========================
    # FECHAMENTO MENSAL
    # ==========================
    path('fechamentos/', views.fechamentos_view, name='fechamentos'),

    # ==========================
    # NOTIFICAÇÕES
    # ==========================
    path('notificacoes/', views.notificacoes_view, name='notificacoes'),

    # ==========================
    # USUÁRIOS
    # ==========================
    path('usuarios/', views.usuarios_view, name='usuarios'),

]