from django.contrib import admin
from django.urls import include, path

from app.views import IndexView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('api/', include('app.urls')),
]