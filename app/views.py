import json
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import (
    Alerta,
    Categoria,
    Despesa,
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


ZERO = Decimal("0.00")
CENTAVOS = Decimal("0.01")


def decimal_from_post(value, default=ZERO):
    if value in (None, ""):
        return default
    try:
        return Decimal(str(value).replace(",", ".")).quantize(CENTAVOS)
    except (InvalidOperation, ValueError):
        return default


def int_from_post(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def date_from_post(value):
    if not value:
        return timezone.localdate()
    try:
        return date.fromisoformat(value)
    except ValueError:
        return timezone.localdate()


def money_sum(queryset, field):
    return queryset.aggregate(total=Sum(field))["total"] or ZERO


def get_usuario_logado(request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return None
    return Usuario.objects.filter(pk=usuario_id).first()


def iniciar_sessao_atlas(request, usuario):
    request.session["usuario_id"] = usuario.id
    request.session["usuario_nome"] = usuario.nome


def autenticar_usuario_django(request, identificador, senha):
    auth_user = authenticate(request, username=identificador, password=senha)
    if auth_user:
        return auth_user

    user_model = get_user_model()
    for user in user_model._default_manager.filter(email__iexact=identificador):
        auth_user = authenticate(request, username=user.get_username(), password=senha)
        if auth_user:
            return auth_user

    return None


def sincronizar_usuario_atlas(auth_user, senha):
    email = auth_user.email or f"{auth_user.get_username()}@atlas.local"
    usuario, _ = Usuario.objects.update_or_create(
        email=email,
        defaults={
            "nome": auth_user.get_full_name() or auth_user.get_username(),
            "senha": make_password(senha),
            "tipo_usuario": "Administrador" if auth_user.is_staff or auth_user.is_superuser else "MEI",
        },
    )
    return usuario


def atlas_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        usuario = get_usuario_logado(request)
        if not usuario:
            request.session.flush()
            return redirect("login")
        request.atlas_usuario = usuario
        return view_func(request, *args, **kwargs)

    return wrapper


def negocios_do_usuario(usuario):
    return Negocio.objects.filter(usuario=usuario).order_by("nome_negocio")


def categorias_ordenadas():
    return Categoria.objects.all().order_by("tipo", "nome_categoria")


def calcular_preco_final(custo, margem, impostos):
    percentual_total = margem + impostos
    if custo <= ZERO or percentual_total >= Decimal("100"):
        return None
    divisor = Decimal("1") - (percentual_total / Decimal("100"))
    return (custo / divisor).quantize(CENTAVOS, rounding=ROUND_HALF_UP)


def aplicar_margem(objetos, custo_attr, preco_attr):
    for item in objetos:
        custo = getattr(item, custo_attr) or ZERO
        preco = getattr(item, preco_attr) or ZERO
        item.margem_calculada = ZERO
        if preco > ZERO:
            item.margem_calculada = ((preco - custo) / preco * Decimal("100")).quantize(
                CENTAVOS,
                rounding=ROUND_HALF_UP,
            )
    return objetos


def calcular_fechamentos(usuario):
    receitas = (
        Receita.objects.filter(negocio__usuario=usuario)
        .annotate(mes=TruncMonth("data"))
        .values("negocio_id", "negocio__nome_negocio", "mes")
        .annotate(total=Sum("valor"))
    )
    despesas = (
        Despesa.objects.filter(negocio__usuario=usuario)
        .annotate(mes=TruncMonth("data_despesa"))
        .values("negocio_id", "negocio__nome_negocio", "mes")
        .annotate(total=Sum("valor_despesa"))
    )

    por_mes = defaultdict(lambda: {"receita_total": ZERO, "despesa_total": ZERO})

    for item in receitas:
        chave = (item["negocio_id"], item["mes"])
        por_mes[chave]["negocio_nome"] = item["negocio__nome_negocio"]
        por_mes[chave]["periodo"] = item["mes"]
        por_mes[chave]["receita_total"] = item["total"] or ZERO

    for item in despesas:
        chave = (item["negocio_id"], item["mes"])
        por_mes[chave]["negocio_nome"] = item["negocio__nome_negocio"]
        por_mes[chave]["periodo"] = item["mes"]
        por_mes[chave]["despesa_total"] = item["total"] or ZERO

    fechamentos = []
    for dados in por_mes.values():
        receita_total = dados["receita_total"]
        despesa_total = dados["despesa_total"]
        lucro_liquido = receita_total - despesa_total
        dados["lucro_liquido"] = lucro_liquido
        dados["saldo_final"] = lucro_liquido
        fechamentos.append(dados)

    return sorted(fechamentos, key=lambda item: item["periodo"], reverse=True)


def calcular_indicadores(usuario):
    indicadores = []
    for negocio in negocios_do_usuario(usuario):
        receitas = Receita.objects.filter(negocio=negocio)
        despesas = Despesa.objects.filter(negocio=negocio)
        produtos = Produto.objects.filter(negocio=negocio)
        servicos = Servico.objects.filter(negocio=negocio)

        total_receitas = money_sum(receitas, "valor")
        total_despesas = money_sum(despesas, "valor_despesa")
        total_custos = money_sum(produtos, "custo") + money_sum(servicos, "custo_operacional")
        lucro = total_receitas - total_despesas
        margem = ZERO
        ticket_medio = ZERO

        if total_receitas > ZERO:
            margem = (lucro / total_receitas * Decimal("100")).quantize(CENTAVOS)

        quantidade_receitas = receitas.count()
        if quantidade_receitas:
            ticket_medio = (total_receitas / Decimal(quantidade_receitas)).quantize(CENTAVOS)

        indicadores.append(
            {
                "negocio": negocio,
                "receitas": total_receitas,
                "despesas": total_despesas,
                "custos": total_custos,
                "lucro": lucro,
                "margem_lucro": margem,
                "ponto_equilibrio": total_despesas + total_custos,
                "ticket_medio": ticket_medio,
            }
        )

    return indicadores


def login_view(request):
    if "usuario_id" in request.session:
        return redirect("index")

    if request.method == "POST":
        identificador = request.POST.get("email", "").strip()
        senha_post = request.POST.get("senha", "")

        auth_user = autenticar_usuario_django(request, identificador, senha_post)
        if auth_user:
            usuario = sincronizar_usuario_atlas(auth_user, senha_post)
            django_login(request, auth_user)
            iniciar_sessao_atlas(request, usuario)
            return redirect("index")

        usuario = Usuario.objects.filter(Q(email=identificador) | Q(nome=identificador)).first()
        if usuario and check_password(senha_post, usuario.senha):
            iniciar_sessao_atlas(request, usuario)
            return redirect("index")

        messages.error(request, "Usuario/e-mail ou senha invalidos.")

    return render(request, "login.html")


def cadastro_view(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip()
        senha = request.POST.get("senha", "")

        if not nome or not email or not senha:
            messages.error(request, "Preencha nome, e-mail e senha para criar a conta.")
        elif Usuario.objects.filter(email=email).exists():
            messages.error(request, "Este e-mail ja esta cadastrado.")
        else:
            novo_usuario = Usuario.objects.create(
                nome=nome,
                email=email,
                senha=make_password(senha),
            )
            iniciar_sessao_atlas(request, novo_usuario)
            messages.success(request, "Cadastro realizado. Agora configure seu negocio.")
            return redirect("cadastrar_negocio")

    return render(request, "cadastro.html")


@atlas_login_required
def cadastrar_negocio_view(request):
    usuario = request.atlas_usuario

    if request.method == "POST":
        nome = request.POST.get("nome_negocio", "").strip()
        segmento = request.POST.get("segmento", "").strip()
        meta_mensal = decimal_from_post(request.POST.get("meta_mensal"))
        capital_inicial = decimal_from_post(request.POST.get("capital_inicial"))

        if not nome:
            messages.error(request, "O nome do negocio e obrigatorio.")
        else:
            Negocio.objects.create(
                nome_negocio=nome,
                segmento=segmento or "Nao informado",
                meta_mensal=meta_mensal,
                capital_inicial=capital_inicial,
                usuario=usuario,
            )
            messages.success(request, "Negocio cadastrado com sucesso.")
            return redirect("index")

    return render(request, "negocio_form.html")


def logout_view(request):
    django_logout(request)
    return redirect("login")


@atlas_login_required
def index_view(request):
    usuario = request.atlas_usuario
    receitas = Receita.objects.filter(negocio__usuario=usuario).select_related("negocio")
    despesas = Despesa.objects.filter(negocio__usuario=usuario).select_related("negocio")
    negocios = negocios_do_usuario(usuario)

    total_receitas = money_sum(receitas, "valor")
    total_despesas = money_sum(despesas, "valor_despesa")
    capital_total = money_sum(negocios, "capital_inicial")
    saldo = capital_total + total_receitas - total_despesas

    context = {
        "nome": usuario.nome,
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "saldo": saldo,
        "qtd_negocios": negocios.count(),
        "negocios": negocios,
        "ultimas_receitas": receitas.order_by("-data", "-id")[:5],
        "ultimas_despesas": despesas.order_by("-data_despesa", "-id")[:5],
        "chart_labels": json.dumps(["Receitas", "Despesas", "Saldo"]),
        "chart_values": json.dumps([float(total_receitas), float(total_despesas), float(saldo)]),
    }
    return render(request, "index.html", context)


@atlas_login_required
def listar_negocios(request):
    return render(request, "negocios.html", {"negocios": negocios_do_usuario(request.atlas_usuario)})


@atlas_login_required
def lista_receitas(request):
    usuario = request.atlas_usuario

    if request.method == "POST":
        negocio = get_object_or_404(Negocio, pk=request.POST.get("negocio"), usuario=usuario)
        categoria = get_object_or_404(Categoria, pk=request.POST.get("categoria"))
        Receita.objects.create(
            descricao=request.POST.get("descricao", "").strip(),
            valor=decimal_from_post(request.POST.get("valor")),
            data=date_from_post(request.POST.get("data")),
            forma_pagamento=request.POST.get("forma_pagamento", "Outro"),
            categoria=categoria,
            negocio=negocio,
        )
        messages.success(request, "Receita cadastrada com sucesso.")
        return redirect("lista_receitas")

    receitas = Receita.objects.filter(negocio__usuario=usuario).select_related("categoria", "negocio")
    return render(
        request,
        "receitas.html",
        {
            "receitas": receitas.order_by("-data", "-id"),
            "categorias": categorias_ordenadas(),
            "negocios": negocios_do_usuario(usuario),
        },
    )


@atlas_login_required
def despesas_view(request):
    usuario = request.atlas_usuario

    if request.method == "POST":
        negocio = get_object_or_404(Negocio, pk=request.POST.get("negocio"), usuario=usuario)
        categoria = get_object_or_404(Categoria, pk=request.POST.get("categoria"))
        Despesa.objects.create(
            descricao_despesa=request.POST.get("descricao_despesa", "").strip(),
            valor_despesa=decimal_from_post(request.POST.get("valor_despesa")),
            data_despesa=date_from_post(request.POST.get("data_despesa")),
            status=request.POST.get("status", "Pendente"),
            categoria=categoria,
            negocio=negocio,
        )
        messages.success(request, "Despesa cadastrada com sucesso.")
        return redirect("despesas")

    despesas = Despesa.objects.filter(negocio__usuario=usuario).select_related("categoria", "negocio")
    return render(
        request,
        "despesas.html",
        {
            "despesas": despesas.order_by("-data_despesa", "-id"),
            "categorias": categorias_ordenadas(),
            "negocios": negocios_do_usuario(usuario),
        },
    )


@atlas_login_required
def produtos_view(request):
    usuario = request.atlas_usuario

    if request.method == "POST":
        negocio = get_object_or_404(Negocio, pk=request.POST.get("negocio"), usuario=usuario)
        categoria = get_object_or_404(Categoria, pk=request.POST.get("categoria"))
        Produto.objects.create(
            nome=request.POST.get("nome_produto", "").strip(),
            custo=decimal_from_post(request.POST.get("custo_producao")),
            preco_venda=decimal_from_post(request.POST.get("preco_venda")),
            estoque=int_from_post(request.POST.get("estoque")),
            categoria=categoria,
            negocio=negocio,
        )
        messages.success(request, "Produto cadastrado com sucesso.")
        return redirect("produtos")

    produtos = list(
        Produto.objects.filter(negocio__usuario=usuario)
        .select_related("categoria", "negocio")
        .order_by("nome")
    )
    return render(
        request,
        "produtos.html",
        {
            "produtos": aplicar_margem(produtos, "custo", "preco_venda"),
            "categorias": categorias_ordenadas(),
            "negocios": negocios_do_usuario(usuario),
        },
    )


@atlas_login_required
def servicos_view(request):
    usuario = request.atlas_usuario

    if request.method == "POST":
        negocio = get_object_or_404(Negocio, pk=request.POST.get("negocio"), usuario=usuario)
        categoria = get_object_or_404(Categoria, pk=request.POST.get("categoria"))
        Servico.objects.create(
            nome_servico=request.POST.get("nome_servico", "").strip(),
            custo_operacional=decimal_from_post(request.POST.get("custo_operacional")),
            valor_servico=decimal_from_post(request.POST.get("valor_servico")),
            categoria=categoria,
            negocio=negocio,
        )
        messages.success(request, "Servico cadastrado com sucesso.")
        return redirect("servicos")

    servicos = list(
        Servico.objects.filter(negocio__usuario=usuario)
        .select_related("categoria", "negocio")
        .order_by("nome_servico")
    )
    return render(
        request,
        "servicos.html",
        {
            "servicos": aplicar_margem(servicos, "custo_operacional", "valor_servico"),
            "categorias": categorias_ordenadas(),
            "negocios": negocios_do_usuario(usuario),
        },
    )


@atlas_login_required
def precificacoes_view(request):
    usuario = request.atlas_usuario

    if request.method == "POST":
        produto_id = request.POST.get("produto") or None
        servico_id = request.POST.get("servico") or None
        produto = None
        servico = None

        if produto_id:
            produto = get_object_or_404(Produto, pk=produto_id, negocio__usuario=usuario)
        if servico_id:
            servico = get_object_or_404(Servico, pk=servico_id, negocio__usuario=usuario)

        custo = decimal_from_post(request.POST.get("custo_total"))
        margem = decimal_from_post(request.POST.get("margem_lucro"))
        impostos = decimal_from_post(request.POST.get("impostos"))
        preco_final = calcular_preco_final(custo, margem, impostos)

        if not produto and not servico:
            messages.error(request, "Selecione um produto ou servico para salvar a precificacao.")
        elif preco_final is None:
            messages.error(request, "Informe custo maior que zero e percentuais abaixo de 100%.")
        else:
            Precificacao.objects.create(
                custo_total=custo,
                margem_lucro=margem,
                impostos=impostos,
                preco_final=preco_final,
                produto=produto,
                servico=servico,
            )
            messages.success(request, "Precificacao salva com sucesso.")
            return redirect("precificacoes")

    precificacoes = (
        Precificacao.objects.filter(
            Q(produto__negocio__usuario=usuario) | Q(servico__negocio__usuario=usuario)
        )
        .select_related("produto", "servico")
        .distinct()
        .order_by("-id")
    )
    return render(
        request,
        "precificacoes.html",
        {
            "precificacoes": precificacoes,
            "produtos": Produto.objects.filter(negocio__usuario=usuario).order_by("nome"),
            "servicos": Servico.objects.filter(negocio__usuario=usuario).order_by("nome_servico"),
        },
    )


@atlas_login_required
def metas_view(request):
    usuario = request.atlas_usuario

    if request.method == "POST":
        negocio = get_object_or_404(Negocio, pk=request.POST.get("negocio"), usuario=usuario)
        MetaFinanceira.objects.create(
            descricao_meta=request.POST.get("descricao_meta", "").strip(),
            valor_meta=decimal_from_post(request.POST.get("valor_meta")),
            prazo=date_from_post(request.POST.get("prazo")),
            negocio=negocio,
        )
        messages.success(request, "Meta cadastrada com sucesso.")
        return redirect("metas")

    negocios = negocios_do_usuario(usuario).annotate(total_receitas=Sum("receita__valor"))
    metas = MetaFinanceira.objects.filter(negocio__usuario=usuario).select_related("negocio")
    return render(request, "Metas.html", {"metas": metas.order_by("prazo"), "negocios": negocios})


@atlas_login_required
def alertas_view(request):
    usuario = request.atlas_usuario

    if request.method == "POST":
        negocio = get_object_or_404(Negocio, pk=request.POST.get("negocio"), usuario=usuario)
        Alerta.objects.create(
            mensagem=request.POST.get("mensagem", "").strip(),
            data_alerta=date_from_post(request.POST.get("data_alerta")),
            prioridade=request.POST.get("prioridade", "Baixa"),
            negocio=negocio,
        )
        messages.success(request, "Alerta cadastrado com sucesso.")
        return redirect("alertas")

    alertas = Alerta.objects.filter(negocio__usuario=usuario).select_related("negocio")
    return render(
        request,
        "alertas.html",
        {
            "alertas": alertas.order_by("-data_alerta", "-id"),
            "negocios": negocios_do_usuario(usuario),
        },
    )


@atlas_login_required
def fechamentos_view(request):
    return render(
        request,
        "fechamentosMensais.html",
        {"fechamentos": calcular_fechamentos(request.atlas_usuario)},
    )


@atlas_login_required
def indicadores_view(request):
    return render(
        request,
        "IndicadoresFinanceiros.html",
        {"indicadores": calcular_indicadores(request.atlas_usuario)},
    )


@atlas_login_required
def notificacoes_view(request):
    usuario = request.atlas_usuario

    if request.method == "POST":
        Notificacao.objects.create(
            mensagem_notificacao=request.POST.get("mensagem_notificacao", "").strip(),
            tipo=request.POST.get("tipo", "Informacao"),
            status_notificacao=request.POST.get("status_notificacao", "Nao lida"),
            usuario=usuario,
        )
        messages.success(request, "Notificacao cadastrada com sucesso.")
        return redirect("notificacoes")

    notificacoes = Notificacao.objects.filter(usuario=usuario).order_by("-id")
    return render(request, "notificacoes.html", {"notificacoes": notificacoes})


@atlas_login_required
def relatorios_view(request):
    usuario = request.atlas_usuario

    if request.method == "POST":
        negocio = get_object_or_404(Negocio, pk=request.POST.get("negocio"), usuario=usuario)
        Relatorio.objects.create(
            tipo_relatorio=request.POST.get("tipo_relatorio", "Financeiro"),
            periodo=date_from_post(request.POST.get("periodo")),
            data_geracao=timezone.localdate(),
            negocio=negocio,
        )
        messages.success(request, "Relatorio registrado com sucesso.")
        return redirect("relatorios")

    relatorios = Relatorio.objects.filter(negocio__usuario=usuario).select_related("negocio")
    return render(
        request,
        "relatorios.html",
        {
            "fechamentos": calcular_fechamentos(usuario),
            "indicadores": calcular_indicadores(usuario),
            "relatorios": relatorios.order_by("-data_geracao", "-id"),
            "negocios": negocios_do_usuario(usuario),
        },
    )


@atlas_login_required
def usuarios_view(request):
    usuario = request.atlas_usuario

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip()
        tipo_usuario = request.POST.get("tipo_usuario", "MEI")

        if Usuario.objects.exclude(pk=usuario.pk).filter(email=email).exists():
            messages.error(request, "Este e-mail ja esta sendo usado por outro usuario.")
        else:
            usuario.nome = nome
            usuario.email = email
            usuario.tipo_usuario = tipo_usuario
            usuario.save(update_fields=["nome", "email", "tipo_usuario"])
            request.session["usuario_nome"] = usuario.nome
            messages.success(request, "Perfil atualizado com sucesso.")
            return redirect("usuarios")

    return render(request, "usuarios.html", {"usuario": usuario})


@atlas_login_required
def categoria_view(request):
    if request.method == "POST":
        nome_categoria = request.POST.get("nome_categoria", "").strip()
        tipo = request.POST.get("tipo", "Geral")

        if not nome_categoria:
            messages.error(request, "Informe o nome da categoria.")
        else:
            Categoria.objects.get_or_create(nome_categoria=nome_categoria, tipo=tipo)
            messages.success(request, "Categoria salva com sucesso.")
            return redirect("categorias")

    return render(request, "categoria.html", {"categorias": categorias_ordenadas()})