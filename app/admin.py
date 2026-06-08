from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Usuario

from .models import (
    Alerta,
    Categoria,
    Dashboard,
    Despesa,
    FechamentoMensal,
    IndicadorFinanceiro,
    MetaFinanceira,
    Negocio,
    Notificacao,
    Precificacao,
    Produto,
    Receita,
    Relatorio,
    Servico,
    Usuario,
)
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'tipo_usuario', 'data_cadastro')
    search_fields = ('nome', 'email')

    def save_model(self, request, obj, form, change):
        # Esta função verifica se a senha já está criptografada
        # Se não começar com os prefixos do Django (ex: pbkdf2), ele encripta
        if not obj.senha.startswith('pbkdf2_sha256$') and not obj.senha.startswith('bcrypt'):
            obj.senha = make_password(obj.senha)
        
        super().save_model(request, obj, form, change)

admin.site.register(Negocio)
admin.site.register(Categoria)
admin.site.register(Receita)
admin.site.register(Despesa)
admin.site.register(Produto)
admin.site.register(Servico)
admin.site.register(Precificacao)
admin.site.register(Relatorio)
admin.site.register(MetaFinanceira)
admin.site.register(Alerta)
admin.site.register(FechamentoMensal)
admin.site.register(Notificacao)
admin.site.register(IndicadorFinanceiro)
admin.site.register(Dashboard)

