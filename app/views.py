from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import render
from django.views import View
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import *
from .serializers import *


class IndexView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer


class NegocioViewSet(viewsets.ModelViewSet):
    queryset = Negocio.objects.all()
    serializer_class = NegocioSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class ReceitaViewSet(viewsets.ModelViewSet):
    queryset = Receita.objects.all()
    serializer_class = ReceitaSerializer


class DespesaViewSet(viewsets.ModelViewSet):
    queryset = Despesa.objects.all()
    serializer_class = DespesaSerializer


class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer


class ServicoViewSet(viewsets.ModelViewSet):
    queryset = Servico.objects.all()
    serializer_class = ServicoSerializer


class PrecificacaoViewSet(viewsets.ModelViewSet):
    queryset = Precificacao.objects.all()
    serializer_class = PrecificacaoSerializer


class RelatorioViewSet(viewsets.ModelViewSet):
    queryset = Relatorio.objects.all()
    serializer_class = RelatorioSerializer


class MetaFinanceiraViewSet(viewsets.ModelViewSet):
    queryset = MetaFinanceira.objects.all()
    serializer_class = MetaFinanceiraSerializer


class AlertaViewSet(viewsets.ModelViewSet):
    queryset = Alerta.objects.all()
    serializer_class = AlertaSerializer


class FechamentoMensalViewSet(viewsets.ModelViewSet):
    queryset = FechamentoMensal.objects.all()
    serializer_class = FechamentoMensalSerializer


class NotificacaoViewSet(viewsets.ModelViewSet):
    queryset = Notificacao.objects.all()
    serializer_class = NotificacaoSerializer


class IndicadorFinanceiroViewSet(viewsets.ModelViewSet):
    queryset = IndicadorFinanceiro.objects.all()
    serializer_class = IndicadorFinanceiroSerializer


class DashboardViewSet(viewsets.ModelViewSet):
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer


def total(queryset, campo):
    return queryset.aggregate(total=Sum(campo))['total'] or Decimal('0.00')


@api_view(['GET'])
def resumo_financeiro(request, negocio_id):
    receitas = total(Receita.objects.filter(negocio_id=negocio_id), 'valor')
    despesas = total(Despesa.objects.filter(negocio_id=negocio_id), 'valor_despesa')
    lucro = receitas - despesas

    margem_lucro = Decimal('0.00')
    if receitas > 0:
        margem_lucro = (lucro / receitas) * 100

    return Response({
        'receitas': receitas,
        'despesas': despesas,
        'lucro': lucro,
        'margem_lucro': round(margem_lucro, 2),
    })


@api_view(['POST'])
def simular_precificacao(request):
    custo_total = Decimal(str(request.data.get('custo_total', 0)))
    margem_lucro = Decimal(str(request.data.get('margem_lucro', 0)))
    impostos = Decimal(str(request.data.get('impostos', 0)))

    divisor = Decimal('1.00') - ((margem_lucro + impostos) / 100)

    if divisor <= 0:
        return Response({'erro': 'Margem + impostos não podem ser 100% ou mais.'}, status=400)

    preco_final = custo_total / divisor

    return Response({
        'custo_total': custo_total,
        'margem_lucro': margem_lucro,
        'impostos': impostos,
        'preco_final': round(preco_final, 2),
    })