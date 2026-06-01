from decimal import Decimal
from datetime import date
from calendar import monthrange

from django.db.models import Sum
from django.shortcuts import render
from django.views import View
from rest_framework import viewsets
from rest_framework.decorators import api_view
from django.contrib.auth.hashers import check_password, make_password
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

@api_view(['POST'])
def cadastro_usuario(request):
    nome = request.data.get('nome')
    email = request.data.get('email')
    senha = request.data.get('senha')
    tipo_usuario = request.data.get('tipo_usuario', 'MEI')

    if not nome or not email or not senha:
        return Response(
            {'erro': 'Nome, email e senha são obrigatórios.'},
            status=400
        )

    if Usuario.objects.filter(email=email).exists():
        return Response(
            {'erro': 'Já existe um usuário com este email.'},
            status=400
        )

    usuario = Usuario.objects.create(
        nome=nome,
        email=email,
        senha=make_password(senha),
        tipo_usuario=tipo_usuario,
        data_cadastro=request.data.get('data_cadastro')
    )

    return Response({
        'id': usuario.id,
        'nome': usuario.nome,
        'email': usuario.email,
        'tipo_usuario': usuario.tipo_usuario,
    }, status=201)


@api_view(['POST'])
def login_usuario(request):
    email = request.data.get('email')
    senha = request.data.get('senha')

    if not email or not senha:
        return Response(
            {'erro': 'Email e senha são obrigatórios.'},
            status=400
        )

    try:
        usuario = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        return Response(
            {'erro': 'Email ou senha inválidos.'},
            status=400
        )

    if not check_password(senha, usuario.senha):
        return Response(
            {'erro': 'Email ou senha inválidos.'},
            status=400
        )

    return Response({
        'id': usuario.id,
        'nome': usuario.nome,
        'email': usuario.email,
        'tipo_usuario': usuario.tipo_usuario,
    })

@api_view(['GET'])
def dashboard_usuario(request, usuario_id):
    negocios = Negocio.objects.filter(usuario_id=usuario_id)

    receitas = total(Receita.objects.filter(negocio__in=negocios), 'valor')
    despesas = total(Despesa.objects.filter(negocio__in=negocios), 'valor_despesa')
    lucro = receitas - despesas
    meta_mensal = total(negocios, 'meta_mensal')

    margem_lucro = Decimal('0.00')
    if receitas > 0:
        margem_lucro = (lucro / receitas) * 100

    return Response({
        'usuario_id': usuario_id,
        'quantidade_negocios': negocios.count(),
        'receitas': receitas,
        'despesas': despesas,
        'lucro': lucro,
        'meta_mensal': meta_mensal,
        'margem_lucro': round(margem_lucro, 2),
        'alertas': Alerta.objects.filter(negocio__in=negocios).count(),
    })


@api_view(['POST'])
def gerar_fechamento_mensal(request):
    negocio = get_object_or_404(Negocio, id=request.data.get('negocio_id'))
    ano = int(request.data.get('ano'))
    mes = int(request.data.get('mes'))

    inicio = date(ano, mes, 1)
    fim = date(ano, mes, monthrange(ano, mes)[1])

    receitas = total(
        Receita.objects.filter(negocio=negocio, data__range=(inicio, fim)),
        'valor'
    )
    despesas = total(
        Despesa.objects.filter(negocio=negocio, data_despesa__range=(inicio, fim)),
        'valor_despesa'
    )

    lucro = receitas - despesas
    saldo_final = negocio.capital_inicial + lucro

    fechamento, created = FechamentoMensal.objects.update_or_create(
        negocio=negocio,
        periodo=inicio,
        defaults={
            'receita_total': receitas,
            'despesa_total': despesas,
            'lucro_liquido': lucro,
            'saldo_final': saldo_final,
        }
    )

    return Response(
        FechamentoMensalSerializer(fechamento).data,
        status=201 if created else 200
    )

@api_view(['GET'])
def negocios_do_usuario(request, usuario_id):
    negocios = Negocio.objects.filter(usuario_id=usuario_id)
    serializer = NegocioSerializer(negocios, many=True)

    return Response(serializer.data)


@api_view(['GET'])
def receitas_do_usuario(request, usuario_id):
    receitas = Receita.objects.filter(negocio__usuario_id=usuario_id)
    serializer = ReceitaSerializer(receitas, many=True)

    return Response(serializer.data)


@api_view(['GET'])
def despesas_do_usuario(request, usuario_id):
    despesas = Despesa.objects.filter(negocio__usuario_id=usuario_id)
    serializer = DespesaSerializer(despesas, many=True)

    return Response(serializer.data)


@api_view(['GET'])
def produtos_do_usuario(request, usuario_id):
    produtos = Produto.objects.filter(negocio__usuario_id=usuario_id)
    serializer = ProdutoSerializer(produtos, many=True)

    return Response(serializer.data)


@api_view(['GET'])
def servicos_do_usuario(request, usuario_id):
    servicos = Servico.objects.filter(negocio__usuario_id=usuario_id)
    serializer = ServicoSerializer(servicos, many=True)

    return Response(serializer.data)


@api_view(['GET'])
def alertas_do_usuario(request, usuario_id):
    alertas = Alerta.objects.filter(negocio__usuario_id=usuario_id)
    serializer = AlertaSerializer(alertas, many=True)

    return Response(serializer.data)


@api_view(['GET'])
def fechamentos_do_usuario(request, usuario_id):
    fechamentos = FechamentoMensal.objects.filter(negocio__usuario_id=usuario_id)
    serializer = FechamentoMensalSerializer(fechamentos, many=True)

    return Response(serializer.data)

@api_view(['GET'])
def resumo_mensal_negocio(request, negocio_id, ano, mes):
    negocio = get_object_or_404(Negocio, id=negocio_id)

    inicio = date(ano, mes, 1)
    fim = date(ano, mes, monthrange(ano, mes)[1])

    receitas = total(
        Receita.objects.filter(negocio=negocio, data__range=(inicio, fim)),
        'valor'
    )
    despesas = total(
        Despesa.objects.filter(negocio=negocio, data_despesa__range=(inicio, fim)),
        'valor_despesa'
    )

    lucro = receitas - despesas
    saldo_projetado = negocio.capital_inicial + lucro

    margem_lucro = Decimal('0.00')
    if receitas > 0:
        margem_lucro = (lucro / receitas) * 100

    return Response({
        'negocio_id': negocio.id,
        'negocio': negocio.nome_negocio,
        'ano': ano,
        'mes': mes,
        'receitas': receitas,
        'despesas': despesas,
        'lucro': lucro,
        'saldo_projetado': saldo_projetado,
        'meta_mensal': negocio.meta_mensal,
        'meta_atingida': receitas >= negocio.meta_mensal,
        'margem_lucro': round(margem_lucro, 2),
    })


@api_view(['GET'])
def fluxo_caixa_negocio(request, negocio_id):
    negocio = get_object_or_404(Negocio, id=negocio_id)

    receitas = Receita.objects.filter(negocio=negocio).order_by('data')
    despesas = Despesa.objects.filter(negocio=negocio).order_by('data_despesa')

    movimentos = []

    for receita in receitas:
        movimentos.append({
            'tipo': 'receita',
            'data': receita.data,
            'descricao': receita.descricao,
            'valor': receita.valor,
        })

    for despesa in despesas:
        movimentos.append({
            'tipo': 'despesa',
            'data': despesa.data_despesa,
            'descricao': despesa.descricao_despesa,
            'valor': despesa.valor_despesa * Decimal('-1'),
        })

    movimentos = sorted(movimentos, key=lambda item: item['data'])

    saldo = negocio.capital_inicial
    fluxo = []

    for movimento in movimentos:
        saldo += movimento['valor']
        fluxo.append({
            'tipo': movimento['tipo'],
            'data': movimento['data'],
            'descricao': movimento['descricao'],
            'valor': movimento['valor'],
            'saldo': saldo,
        })

    return Response({
        'negocio_id': negocio.id,
        'negocio': negocio.nome_negocio,
        'capital_inicial': negocio.capital_inicial,
        'saldo_atual': saldo,
        'movimentos': fluxo,
    })

@api_view(['POST'])
def gerar_indicadores_financeiros(request, negocio_id):
    negocio = get_object_or_404(Negocio, id=negocio_id)

    receitas = total(Receita.objects.filter(negocio=negocio), 'valor')
    despesas = total(Despesa.objects.filter(negocio=negocio), 'valor_despesa')
    lucro = receitas - despesas

    margem_lucro = Decimal('0.00')
    if receitas > 0:
        margem_lucro = (lucro / receitas) * 100

    indicador, created = IndicadorFinanceiro.objects.update_or_create(
        negocio=negocio,
        defaults={
            'margem_lucro': margem_lucro,
            'ponto_equilibrio': despesas,
        }
    )

    return Response(
        IndicadorFinanceiroSerializer(indicador).data,
        status=201 if created else 200
    )


@api_view(['POST'])
def gerar_alertas_financeiros(request, negocio_id):
    negocio = get_object_or_404(Negocio, id=negocio_id)

    receitas = total(Receita.objects.filter(negocio=negocio), 'valor')
    despesas = total(Despesa.objects.filter(negocio=negocio), 'valor_despesa')
    hoje = date.today()

    alertas = []

    def criar_alerta(mensagem, prioridade):
        alerta, _ = Alerta.objects.get_or_create(
            negocio=negocio,
            mensagem=mensagem,
            data_alerta=hoje,
            defaults={'prioridade': prioridade}
        )
        alertas.append(alerta)

    if receitas == 0 and despesas > 0:
        criar_alerta('Existem despesas sem receitas registradas.', 'Alta')

    if despesas > receitas:
        criar_alerta('Despesas maiores que receitas.', 'Alta')

    if receitas > 0 and despesas >= receitas * Decimal('0.80'):
        criar_alerta('Despesas acima de 80% das receitas.', 'Média')

    if receitas < negocio.meta_mensal:
        criar_alerta('Receitas abaixo da meta mensal.', 'Média')

    serializer = AlertaSerializer(alertas, many=True)

    return Response({
        'quantidade_alertas': len(alertas),
        'alertas': serializer.data,
    })

@api_view(['POST'])
def criar_receita(request, negocio_id):
        negocio = get_object_or_404(Negocio, id=negocio_id)

        serializer = ReceitaSerializer(data={
            'valor': request.data.get('valor'),
            'data': request.data.get('data'),
            'descricao': request.data.get('descricao'),
            'forma_pagamento': request.data.get('forma_pagamento'),
            'categoria': request.data.get('categoria'),
            'negocio': negocio.id,
        })

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


@api_view(['POST'])
def criar_despesa(request, negocio_id):
        negocio = get_object_or_404(Negocio, id=negocio_id)

        serializer = DespesaSerializer(data={
            'valor_despesa': request.data.get('valor_despesa'),
            'data_despesa': request.data.get('data_despesa'),
            'descricao_despesa': request.data.get('descricao_despesa'),
            'status': request.data.get('status'),
            'categoria': request.data.get('categoria'),
            'negocio': negocio.id,
        })

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)

@api_view(['POST'])
def criar_produto(request, negocio_id):
        negocio = get_object_or_404(Negocio, id=negocio_id)

        serializer = ProdutoSerializer(data={
            'nome': request.data.get('nome'),
            'custo': request.data.get('custo'),
            'preco_venda': request.data.get('preco_venda'),
            'estoque': request.data.get('estoque'),
            'categoria': request.data.get('categoria'),
            'negocio': negocio.id,
        })

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


@api_view(['POST'])
def criar_servico(request, negocio_id):
        negocio = get_object_or_404(Negocio, id=negocio_id)

        serializer = ServicoSerializer(data={
            'nome_servico': request.data.get('nome_servico'),
            'custo_operacional': request.data.get('custo_operacional'),
            'valor_servico': request.data.get('valor_servico'),
            'categoria': request.data.get('categoria'),
            'negocio': negocio.id,
        })

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)

@api_view(['POST'])
def criar_negocio_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)

    serializer = NegocioSerializer(data={
        'nome_negocio': request.data.get('nome_negocio'),
        'segmento': request.data.get('segmento'),
        'meta_mensal': request.data.get('meta_mensal'),
        'capital_inicial': request.data.get('capital_inicial'),
        'usuario': usuario.id,
    })

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


@api_view(['POST'])
def criar_categoria(request):
    serializer = CategoriaSerializer(data={
        'nome_categoria': request.data.get('nome_categoria'),
        'tipo': request.data.get('tipo'),
    })

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)