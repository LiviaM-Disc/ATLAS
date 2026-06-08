from django.urls import path
from . import views

urlpatterns = [
    # Rotas de visualização (Páginas HTML)
    # Como você mudou os nomes no views.py, vamos apontar para os novos nomes
    
    path('dashboard/', views.index_view, name='dashboard_index'),
    
    # Se você quiser criar rotas para as outras páginas que você tem na pasta templates:
    # Exemplo:
    # path('receitas/', views.lista_receitas, name='receitas'),
    # path('produtos/', views.lista_produtos, name='produtos'),
]