from django.contrib import admin

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

admin.site.register(Usuario)
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