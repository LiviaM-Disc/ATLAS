from django.contrib import admin
from django.urls import path, include # Importe o 'include' aqui

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Isso faz o Django ler todas as rotas que você criou dentro de app/urls.py
    path('', include('app.urls')), 
]