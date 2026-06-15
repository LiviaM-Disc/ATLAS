from django.contrib import admin
from .models import (
    Usuario, Negocio, Categoria, Receita, Despesa, Produto, Servico,
    Precificacao, Relatorio, MetaFinanceira, Alerta, FechamentoMensal,
    Notificacao, IndicadorFinanceiro, Dashboard
)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'tipo_usuario', 'data_cadastro')
    list_filter = ('tipo_usuario', 'data_cadastro')
    search_fields = ('nome', 'email')
    ordering = ('-data_cadastro',)


@admin.register(Negocio)
class NegocioAdmin(admin.ModelAdmin):
    list_display = ('nome_negocio', 'segmento', 'usuario', 'meta_mensal', 'capital_inicial')
    list_filter = ('segmento', 'usuario')
    search_fields = ('nome_negocio', 'segmento')
    readonly_fields = ('usuario',)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome_categoria', 'tipo')
    list_filter = ('tipo',)
    search_fields = ('nome_categoria',)


@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'valor', 'data', 'forma_pagamento', 'categoria', 'negocio')
    list_filter = ('data', 'forma_pagamento', 'categoria', 'negocio')
    search_fields = ('descricao', 'negocio__nome_negocio')
    ordering = ('-data',)
    date_hierarchy = 'data'


@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ('descricao_despesa', 'valor_despesa', 'data_despesa', 'status', 'categoria', 'negocio')
    list_filter = ('data_despesa', 'status', 'categoria', 'negocio')
    search_fields = ('descricao_despesa', 'negocio__nome_negocio')
    ordering = ('-data_despesa',)
    date_hierarchy = 'data_despesa'


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'custo', 'preco_venda', 'estoque', 'categoria', 'negocio')
    list_filter = ('categoria', 'negocio')
    search_fields = ('nome', 'negocio__nome_negocio')


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome_servico', 'custo_operacional', 'valor_servico', 'categoria', 'negocio')
    list_filter = ('categoria', 'negocio')
    search_fields = ('nome_servico', 'negocio__nome_negocio')


@admin.register(Precificacao)
class PrecificacaoAdmin(admin.ModelAdmin):
    list_display = ('custo_total', 'margem_lucro', 'impostos', 'preco_final', 'produto', 'servico')
    list_filter = ('margem_lucro', 'produto__negocio', 'servico__negocio')
    search_fields = ('produto__nome', 'servico__nome_servico')


@admin.register(MetaFinanceira)
class MetaFinanceiraAdmin(admin.ModelAdmin):
    list_display = ('descricao_meta', 'valor_meta', 'prazo', 'negocio')
    list_filter = ('prazo', 'negocio')
    search_fields = ('descricao_meta', 'negocio__nome_negocio')
    ordering = ('-prazo',)
    date_hierarchy = 'prazo'


@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ('mensagem', 'data_alerta', 'prioridade', 'negocio')
    list_filter = ('data_alerta', 'prioridade', 'negocio')
    search_fields = ('mensagem', 'negocio__nome_negocio')
    ordering = ('-data_alerta',)
    date_hierarchy = 'data_alerta'


@admin.register(FechamentoMensal)
class FechamentoMensalAdmin(admin.ModelAdmin):
    list_display = ('periodo', 'receita_total', 'despesa_total', 'lucro_liquido', 'saldo_final', 'negocio')
    list_filter = ('periodo', 'negocio')
    search_fields = ('negocio__nome_negocio',)
    ordering = ('-periodo',)
    date_hierarchy = 'periodo'


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('mensagem_notificacao', 'tipo', 'status_notificacao', 'usuario')
    list_filter = ('tipo', 'status_notificacao', 'usuario')
    search_fields = ('mensagem_notificacao', 'usuario__nome')


@admin.register(IndicadorFinanceiro)
class IndicadorFinanceiroAdmin(admin.ModelAdmin):
    list_display = ('negocio', 'margem_lucro', 'ponto_equilibrio')
    list_filter = ('negocio',)
    search_fields = ('negocio__nome_negocio',)


@admin.register(Relatorio)
class RelatorioAdmin(admin.ModelAdmin):
    list_display = ('tipo_relatorio', 'periodo', 'data_geracao', 'negocio')
    list_filter = ('tipo_relatorio', 'periodo', 'data_geracao', 'negocio')
    search_fields = ('tipo_relatorio', 'negocio__nome_negocio')
    ordering = ('-data_geracao',)
    date_hierarchy = 'data_geracao'


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ('negocio', 'faturamento_mensal', 'despesas_totais', 'lucro_total', 'saldo_atual')
    list_filter = ('negocio',)
    search_fields = ('negocio__nome_negocio',)