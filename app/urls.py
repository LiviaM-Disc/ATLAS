from django.urls import path
from . import views

urlpatterns = [
    # Autenticação e Sessão
    path('login/', views.login_view, name='login'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('cadastrar-negocio/', views.cadastrar_negocio_view, name='cadastrar_negocio'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard Principal
    path('', views.index_view, name='index'),

    # Módulos Específicos
    path('negocios/', views.listar_negocios, name='listar_negocios'),
    path('receitas/', views.lista_receitas, name='lista_receitas'),
    path('despesas/', views.despesas_view, name='despesas'),
    path('produtos/', views.produtos_view, name='produtos'),
    path('categorias/', views.categoria_view, name='categorias'),
    path('servicos/', views.servicos_view, name='servicos'),
    path('precificacoes/', views.precificacoes_view, name='precificacoes'),
    path('metas/', views.metas_view, name='metas'),
    
    # Páginas Extras da Barra Lateral
    path('alertas/', views.alertas_view, name='alertas'),
    path('fechamentos/', views.fechamentos_view, name='fechamentos'),
    path('indicadores/', views.indicadores_view, name='indicadores'),
    path('notificacoes/', views.notificacoes_view, name='notificacoes'),
    path('relatorios/', views.relatorios_view, name='relatorios'),
    path('usuarios/', views.usuarios_view, name='usuarios'),
    path('fechamentos/', views.fechamentos_view, name='fechamentos_mensais'),
    path('indicadores/', views.indicadores_view, name='indicadores_financeiros'),
    path('usuarios/', views.usuarios_view, name='usuarios'),
]