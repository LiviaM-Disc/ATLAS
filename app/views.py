from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.views import View


class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')


class UsuariosView(View):
    def get(self, request, *args, **kwargs):
        usuarios = Usuario.objects.all()
        return render(request, 'usuarios.html', {'usuarios': usuarios})


class NegociosView(View):
    def get(self, request, *args, **kwargs):
        negocios = Negocio.objects.all()
        return render(request, 'negocios.html', {'negocios': negocios})


class CategoriasView(View):
    def get(self, request, *args, **kwargs):
        categorias = Categoria.objects.all()
        return render(request, 'categorias.html', {'categorias': categorias})


class ReceitasView(View):
    def get(self, request, *args, **kwargs):
        receitas = Receita.objects.all()
        return render(request, 'receitas.html', {'receitas': receitas})


class DespesasView(View):
    def get(self, request, *args, **kwargs):
        despesas = Despesa.objects.all()
        return render(request, 'despesas.html', {'despesas': despesas})


class ProdutosView(View):
    def get(self, request, *args, **kwargs):
        produtos = Produto.objects.all()
        return render(request, 'produtos.html', {'produtos': produtos})


class ServicosView(View):
    def get(self, request, *args, **kwargs):
        servicos = Servico.objects.all()
        return render(request, 'servicos.html', {'servicos': servicos})


class PrecificacoesView(View):
    def get(self, request, *args, **kwargs):
        precificacoes = Precificacao.objects.all()
        return render(request, 'precificacoes.html', {'precificacoes': precificacoes})


class RelatoriosView(View):
    def get(self, request, *args, **kwargs):
        relatorios = Relatorio.objects.all()
        return render(request, 'relatorios.html', {'relatorios': relatorios})


class MetasView(View):
    def get(self, request, *args, **kwargs):
        metas = MetaFinanceira.objects.all()
        return render(request, 'metas.html', {'metas': metas})


class AlertasView(View):
    def get(self, request, *args, **kwargs):
        alertas = Alerta.objects.all()
        return render(request, 'alertas.html', {'alertas': alertas})


class FechamentosMensaisView(View):
    def get(self, request, *args, **kwargs):
        fechamentos = FechamentoMensal.objects.all()
        return render(request, 'fechamentos.html', {'fechamentos': fechamentos})


class NotificacoesView(View):
    def get(self, request, *args, **kwargs):
        notificacoes = Notificacao.objects.all()
        return render(request, 'notificacoes.html', {'notificacoes': notificacoes})


class IndicadoresFinanceirosView(View):
    def get(self, request, *args, **kwargs):
        indicadores = IndicadorFinanceiro.objects.all()
        return render(request, 'indicadores.html', {'indicadores': indicadores})


class DashboardsView(View):
    def get(self, request, *args, **kwargs):
        dashboards = Dashboard.objects.all()
        return render(request, 'dashboards.html', {'dashboards': dashboards})