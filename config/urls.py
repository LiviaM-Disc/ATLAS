from django.contrib import admin
from django.urls import path
# Importe as funções da sua pasta 'app'
from app.views import index_view, login_view, logout_view, cadastro_view 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_view, name='index'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('cadastro/', cadastro_view, name='cadastro'), # Agora o Python conhece a cadastro_view
]