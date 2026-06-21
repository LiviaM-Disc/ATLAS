from django.contrib import admin

from .forms import UsuarioForm
from .models import (
    Usuario, Negocio, Categoria, Receita, Despesa, Produto, Servico,
    Precificacao, Relatorio, MetaFinanceira, Alerta, FechamentoMensal,
    Notificacao, IndicadorFinanceiro, Dashboard
)


class NegocioInline(admin.TabularInline):
    model = Negocio
    extra = 0
    fields = (
        'nome_negocio',
        'segmento',
        'meta_mensal',
        'capital_inicial',
    )
    show_change_link = True


class ReceitaInline(admin.TabularInline):
    model = Receita
    extra = 0
    fields = ('descricao', 'valor', 'data', 'forma_pagamento', 'categoria')
    show_change_link = True
    classes = ('collapse',)


class DespesaInline(admin.TabularInline):
    model = Despesa
    extra = 0
    fields = (
        'descricao_despesa',
        'valor_despesa',
        'data_despesa',
        'data_vencimento',
        'status',
        'categoria',
    )
    show_change_link = True
    classes = ('collapse',)


class ProdutoInline(admin.TabularInline):
    model = Produto
    extra = 0
    fields = ('nome', 'custo', 'preco_venda', 'estoque', 'categoria')
    show_change_link = True
    classes = ('collapse',)


class ServicoInline(admin.TabularInline):
    model = Servico
    extra = 0
    fields = (
        'nome_servico',
        'custo_operacional',
        'valor_servico',
        'categoria',
    )
    show_change_link = True
    classes = ('collapse',)


class MetaFinanceiraInline(admin.TabularInline):
    model = MetaFinanceira
    extra = 0
    fields = ('descricao_meta', 'valor_meta', 'prazo')
    show_change_link = True
    classes = ('collapse',)


class PrecificacaoProdutoInline(admin.TabularInline):
    model = Precificacao
    fk_name = 'produto'
    extra = 0
    exclude = ('servico',)
    show_change_link = True


class PrecificacaoServicoInline(admin.TabularInline):
    model = Precificacao
    fk_name = 'servico'
    extra = 0
    exclude = ('produto',)
    show_change_link = True


class NotificacaoInline(admin.TabularInline):
    model = Notificacao
    extra = 0
    fields = (
        'mensagem_notificacao',
        'tipo',
        'status_notificacao',
        'data_criacao',
    )
    readonly_fields = fields
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    form = UsuarioForm
    inlines = (NegocioInline,)
    list_display = ('nome', 'email', 'tipo_usuario', 'data_cadastro')
    list_filter = ('tipo_usuario', 'data_cadastro')
    search_fields = ('nome', 'email')
    ordering = ('-data_cadastro',)


@admin.register(Negocio)
class NegocioAdmin(admin.ModelAdmin):
    inlines = (
        ReceitaInline,
        DespesaInline,
        ProdutoInline,
        ServicoInline,
        MetaFinanceiraInline,
    )
    list_display = ('nome_negocio', 'segmento', 'usuario', 'meta_mensal', 'capital_inicial')
    list_filter = ('segmento', 'usuario')
    search_fields = ('nome_negocio', 'segmento')

    def get_readonly_fields(self, request, obj=None):
        return ('usuario',) if obj else ()


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
    inlines = (NotificacaoInline,)
    list_display = (
        "descricao_despesa",
        "valor_despesa",
        "data_despesa",
        "data_vencimento",
        "status",
        "categoria",
        "negocio",
    )
    list_filter = (
        "data_vencimento",
        "status",
        "categoria",
        "negocio",
    )
    search_fields = (
        "descricao_despesa",
        "negocio__nome_negocio",
    )
    ordering = ("data_vencimento",)

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    inlines = (PrecificacaoProdutoInline,)
    list_display = ('nome', 'custo', 'preco_venda', 'estoque', 'categoria', 'negocio')
    list_filter = ('categoria', 'negocio')
    search_fields = ('nome', 'negocio__nome_negocio')


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    inlines = (PrecificacaoServicoInline,)
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
    list_display = (
        "mensagem_notificacao",
        "tipo",
        "status_notificacao",
        "usuario",
        "despesa",
        "data_criacao",
    )
    list_filter = (
        "tipo",
        "status_notificacao",
        "usuario",
    )
    search_fields = (
        "mensagem_notificacao",
        "usuario__nome",
        "despesa__descricao_despesa",
    )
    readonly_fields = (
        "mensagem_notificacao",
        "tipo",
        "usuario",
        "despesa",
        "data_criacao",
    )

    def has_add_permission(self, request):
        return False


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
