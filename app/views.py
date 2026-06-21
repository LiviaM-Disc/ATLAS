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
from django.views.decorators.http import require_GET, require_POST

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
from .services import (
    gerar_alertas_financeiros,
    gerar_notificacoes_de_vencimento,
)


ZERO = Decimal("0.00")
CENTAVOS = Decimal("0.01")
STATUS_DESPESA = {"Pendente", "Paga", "Cancelada"}
TIPOS_USUARIO = {"MEI", "PJ", "Pessoa Física"}


def decimal_from_post(value, default=ZERO):
    if value in (None, ""):
        return default

    try:
        return Decimal(str(value).replace(",", ".")).quantize(CENTAVOS)
    except (InvalidOperation, TypeError, ValueError):
        return default


def int_from_post(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def date_from_post(value, default=None):
    if not value:
        return default

    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return default


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
    auth_user = authenticate(
        request,
        username=identificador,
        password=senha,
    )

    if auth_user:
        return auth_user

    user_model = get_user_model()

    for user in user_model._default_manager.filter(
        email__iexact=identificador
    ):
        auth_user = authenticate(
            request,
            username=user.get_username(),
            password=senha,
        )

        if auth_user:
            return auth_user

    return None


def sincronizar_usuario_atlas(auth_user, senha):
    email = (
        auth_user.email.lower()
        if auth_user.email
        else f"{auth_user.get_username()}@atlas.local"
    )

    usuario, _ = Usuario.objects.update_or_create(
        email=email,
        defaults={
            "nome": (
                auth_user.get_full_name()
                or auth_user.get_username()
            ),
            "senha": make_password(senha),
            "tipo_usuario": (
                "Administrador"
                if auth_user.is_staff or auth_user.is_superuser
                else "MEI"
            ),
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

        gerar_notificacoes_de_vencimento(usuario=usuario)
        gerar_alertas_financeiros(usuario=usuario)

        return view_func(request, *args, **kwargs)

    return wrapper


def negocios_do_usuario(usuario):
    return Negocio.objects.filter(
        usuario=usuario
    ).order_by("nome_negocio")


def categorias_ordenadas():
    return Categoria.objects.all().order_by(
        "tipo",
        "nome_categoria",
    )


def calcular_preco_final(custo, margem, impostos):
    percentual_total = margem + impostos

    if custo <= ZERO or percentual_total >= Decimal("100"):
        return None

    divisor = Decimal("1") - (
        percentual_total / Decimal("100")
    )

    return (custo / divisor).quantize(
        CENTAVOS,
        rounding=ROUND_HALF_UP,
    )


def aplicar_margem(objetos, custo_attr, preco_attr):
    for item in objetos:
        custo = getattr(item, custo_attr) or ZERO
        preco = getattr(item, preco_attr) or ZERO

        item.margem_calculada = ZERO

        if preco > ZERO:
            item.margem_calculada = (
                (preco - custo)
                / preco
                * Decimal("100")
            ).quantize(
                CENTAVOS,
                rounding=ROUND_HALF_UP,
            )

    return objetos


def calcular_fechamentos(usuario):
    receitas = (
        Receita.objects
        .filter(negocio__usuario=usuario)
        .annotate(mes=TruncMonth("data"))
        .values(
            "negocio_id",
            "negocio__nome_negocio",
            "mes",
        )
        .annotate(total=Sum("valor"))
    )

    despesas = (
        Despesa.objects
        .filter(negocio__usuario=usuario)
        .exclude(status__iexact="Cancelada")
        .annotate(mes=TruncMonth("data_despesa"))
        .values(
            "negocio_id",
            "negocio__nome_negocio",
            "mes",
        )
        .annotate(total=Sum("valor_despesa"))
    )

    por_mes = defaultdict(
        lambda: {
            "receita_total": ZERO,
            "despesa_total": ZERO,
        }
    )

    for item in receitas:
        chave = (item["negocio_id"], item["mes"])

        por_mes[chave]["negocio_nome"] = (
            item["negocio__nome_negocio"]
        )
        por_mes[chave]["periodo"] = item["mes"]
        por_mes[chave]["receita_total"] = (
            item["total"] or ZERO
        )

    for item in despesas:
        chave = (item["negocio_id"], item["mes"])

        por_mes[chave]["negocio_nome"] = (
            item["negocio__nome_negocio"]
        )
        por_mes[chave]["periodo"] = item["mes"]
        por_mes[chave]["despesa_total"] = (
            item["total"] or ZERO
        )

    fechamentos = []

    for dados in por_mes.values():
        receita_total = dados["receita_total"]
        despesa_total = dados["despesa_total"]
        lucro_liquido = receita_total - despesa_total

        dados["lucro_liquido"] = lucro_liquido
        dados["saldo_final"] = lucro_liquido

        fechamentos.append(dados)

    return sorted(
        fechamentos,
        key=lambda item: item["periodo"],
        reverse=True,
    )


def calcular_indicadores(usuario):
    indicadores = []

    for negocio in negocios_do_usuario(usuario):
        receitas = Receita.objects.filter(negocio=negocio)

        despesas = (
            Despesa.objects
            .filter(negocio=negocio)
            .exclude(status__iexact="Cancelada")
        )

        produtos = Produto.objects.filter(negocio=negocio)
        servicos = Servico.objects.filter(negocio=negocio)

        total_receitas = money_sum(receitas, "valor")
        total_despesas = money_sum(
            despesas,
            "valor_despesa",
        )
        total_custos = (
            money_sum(produtos, "custo")
            + money_sum(servicos, "custo_operacional")
        )

        lucro = total_receitas - total_despesas
        margem = ZERO
        ticket_medio = ZERO

        if total_receitas > ZERO:
            margem = (
                lucro
                / total_receitas
                * Decimal("100")
            ).quantize(CENTAVOS)

        quantidade_receitas = receitas.count()

        if quantidade_receitas:
            ticket_medio = (
                total_receitas
                / Decimal(quantidade_receitas)
            ).quantize(CENTAVOS)

        indicadores.append(
            {
                "negocio": negocio,
                "receitas": total_receitas,
                "despesas": total_despesas,
                "custos": total_custos,
                "lucro": lucro,
                "margem_lucro": margem,
                "ponto_equilibrio": (
                    total_despesas + total_custos
                ),
                "ticket_medio": ticket_medio,
            }
        )

    return indicadores


def login_view(request):
    if "usuario_id" in request.session:
        return redirect("index")

    if request.method == "POST":
        identificador = request.POST.get(
            "email",
            "",
        ).strip()

        senha_post = request.POST.get("senha", "")

        auth_user = autenticar_usuario_django(
            request,
            identificador,
            senha_post,
        )

        if auth_user:
            usuario = sincronizar_usuario_atlas(
                auth_user,
                senha_post,
            )

            django_login(request, auth_user)
            iniciar_sessao_atlas(request, usuario)

            return redirect("index")

        usuario = Usuario.objects.filter(
            Q(email__iexact=identificador)
            | Q(nome=identificador)
        ).first()

        if usuario and check_password(
            senha_post,
            usuario.senha,
        ):
            iniciar_sessao_atlas(request, usuario)
            return redirect("index")

        messages.error(
            request,
            "Usuário/e-mail ou senha inválidos.",
        )

    return render(request, "login.html")


def cadastro_view(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get(
            "email",
            "",
        ).strip().lower()
        senha = request.POST.get("senha", "")

        if not nome or not email or not senha:
            messages.error(
                request,
                "Preencha nome, e-mail e senha.",
            )

        elif len(senha) < 6:
            messages.error(
                request,
                "A senha precisa ter pelo menos 6 caracteres.",
            )

        elif Usuario.objects.filter(
            email__iexact=email
        ).exists():
            messages.error(
                request,
                "Este e-mail já está cadastrado.",
            )

        else:
            novo_usuario = Usuario.objects.create(
                nome=nome,
                email=email,
                senha=make_password(senha),
            )

            iniciar_sessao_atlas(
                request,
                novo_usuario,
            )

            messages.success(
                request,
                "Cadastro realizado. Configure seu negócio.",
            )

            return redirect("cadastrar_negocio")

    return render(request, "cadastro.html")


@atlas_login_required
def cadastrar_negocio_view(request):
    usuario = request.atlas_usuario

    if request.method == "POST":
        nome = request.POST.get(
            "nome_negocio",
            "",
        ).strip()

        segmento = request.POST.get(
            "segmento",
            "",
        ).strip()

        meta_mensal = decimal_from_post(
            request.POST.get("meta_mensal")
        )

        capital_inicial = decimal_from_post(
            request.POST.get("capital_inicial")
        )

        if not nome:
            messages.error(
                request,
                "O nome do negócio é obrigatório.",
            )

        elif meta_mensal < ZERO or capital_inicial < ZERO:
            messages.error(
                request,
                "Os valores não podem ser negativos.",
            )

        else:
            Negocio.objects.create(
                nome_negocio=nome,
                segmento=segmento or "Não informado",
                meta_mensal=meta_mensal,
                capital_inicial=capital_inicial,
                usuario=usuario,
            )

            messages.success(
                request,
                "Negócio cadastrado com sucesso.",
            )

            return redirect("index")

    return render(request, "negocio_form.html")


def logout_view(request):
    django_logout(request)
    return redirect("login")


@atlas_login_required
def index_view(request):
    usuario = request.atlas_usuario

    receitas = (
        Receita.objects
        .filter(negocio__usuario=usuario)
        .select_related("negocio")
    )

    despesas = (
        Despesa.objects
        .filter(negocio__usuario=usuario)
        .exclude(status__iexact="Cancelada")
        .select_related("negocio")
    )

    negocios = negocios_do_usuario(usuario)

    total_receitas = money_sum(receitas, "valor")
    total_despesas = money_sum(
        despesas,
        "valor_despesa",
    )
    capital_total = money_sum(
        negocios,
        "capital_inicial",
    )

    saldo = (
        capital_total
        + total_receitas
        - total_despesas
    )

    context = {
        "nome": usuario.nome,
        "total_receitas": total_receitas,
        "total_despesas": total_despesas,
        "saldo": saldo,
        "qtd_negocios": negocios.count(),
        "negocios": negocios,
        "ultimas_receitas": receitas.order_by(
            "-data",
            "-id",
        )[:5],
        "ultimas_despesas": despesas.order_by(
            "-data_despesa",
            "-id",
        )[:5],
        "chart_labels": json.dumps(
            ["Receitas", "Despesas", "Saldo"]
        ),
        "chart_values": json.dumps(
            [
                float(total_receitas),
                float(total_despesas),
                float(saldo),
            ]
        ),
    }

    return render(request, "index.html", context)


@atlas_login_required
def listar_negocios(request):
    return render(
        request,
        "negocios.html",
        {
            "negocios": negocios_do_usuario(
                request.atlas_usuario
            )
        },
    )


@atlas_login_required
def lista_receitas(request):
    usuario = request.atlas_usuario

    if request.method == "POST":
        negocio = get_object_or_404(
            Negocio,
            pk=request.POST.get("negocio"),
            usuario=usuario,
        )

        categoria = get_object_or_404(
            Categoria,
            pk=request.POST.get("categoria"),
        )

        descricao = request.POST.get(
            "descricao",
            "",
        ).strip()

        valor = decimal_from_post(
            request.POST.get("valor")
        )

        data_receita = date_from_post(
            request.POST.get("data")
        )

        if not descricao:
            messages.error(
                request,
                "Informe a descrição da receita.",
            )

        elif valor <= ZERO:
            messages.error(
                request,
                "Informe um valor maior que zero.",
            )

        elif not data_receita:
            messages.error(
                request,
                "Informe uma data válida.",
            )

        else:
            Receita.objects.create(
                descricao=descricao,
                valor=valor,
                data=data_receita,
                forma_pagamento=request.POST.get(
                    "forma_pagamento",
                    "Outro",
                ),
                categoria=categoria,
                negocio=negocio,
            )

            messages.success(
                request,
                "Receita cadastrada com sucesso.",
            )

            return redirect("lista_receitas")

    receitas = (
        Receita.objects
        .filter(negocio__usuario=usuario)
        .select_related("categoria", "negocio")
        .order_by("-data", "-id")
    )

    return render(
        request,
        "receitas.html",
        {
            "receitas": receitas,
            "categorias": categorias_ordenadas(),
            "negocios": negocios_do_usuario(usuario),
        },
    )


@atlas_login_required
def despesas_view(request):
    usuario = request.atlas_usuario

    if request.method == "POST":
        negocio = get_object_or_404(
            Negocio,
            pk=request.POST.get("negocio"),
            usuario=usuario,
        )

        categoria = get_object_or_404(
            Categoria,
            pk=request.POST.get("categoria"),
        )

        descricao = request.POST.get(
            "descricao_despesa",
            "",
        ).strip()

        valor = decimal_from_post(
            request.POST.get("valor_despesa")
        )

        data_despesa = date_from_post(
            request.POST.get("data_despesa")
        )

        data_vencimento = date_from_post(
            request.POST.get("data_vencimento")
        )

        status = request.POST.get(
            "status",
            "Pendente",
        )

        if not descricao:
            messages.error(
                request,
                "Informe a descrição da despesa.",
            )

        elif valor <= ZERO:
            messages.error(
                request,
                "Informe um valor maior que zero.",
            )

        elif not data_despesa:
            messages.error(
                request,
                "Informe a data da despesa.",
            )

        elif not data_vencimento:
            messages.error(
                request,
                "Informe a data de vencimento.",
            )

        elif status not in STATUS_DESPESA:
            messages.error(
                request,
                "O status informado é inválido.",
            )

        else:
            Despesa.objects.create(
                descricao_despesa=descricao,
                valor_despesa=valor,
                data_despesa=data_despesa,
                data_vencimento=data_vencimento,
                status=status,
                categoria=categoria,
                negocio=negocio,
            )

            messages.success(
                request,
                "Despesa cadastrada com sucesso.",
            )

            return redirect("despesas")

    despesas = (
        Despesa.objects
        .filter(negocio__usuario=usuario)
        .select_related("categoria", "negocio")
        .order_by("-data_despesa", "-id")
    )

    return render(
        request,
        "despesas.html",
        {
            "despesas": despesas,
            "categorias": categorias_ordenadas(),
            "negocios": negocios_do_usuario(usuario),
        },
    )


@atlas_login_required
def produtos_view(request):
    usuario = request.atlas_usuario

    if request.method == "POST":
        negocio = get_object_or_404(
            Negocio,
            pk=request.POST.get("negocio"),
            usuario=usuario,
        )

        categoria = get_object_or_404(
            Categoria,
            pk=request.POST.get("categoria"),
        )

        nome = request.POST.get(
            "nome_produto",
            "",
        ).strip()

        custo = decimal_from_post(
            request.POST.get("custo_producao")
        )

        preco = decimal_from_post(
            request.POST.get("preco_venda")
        )

        estoque = int_from_post(
            request.POST.get("estoque")
        )

        if not nome:
            messages.error(
                request,
                "Informe o nome do produto.",
            )

        elif custo < ZERO or preco <= ZERO or estoque < 0:
            messages.error(
                request,
                "Verifique custo, preço e estoque.",
            )

        else:
            Produto.objects.create(
                nome=nome,
                custo=custo,
                preco_venda=preco,
                estoque=estoque,
                categoria=categoria,
                negocio=negocio,
            )

            messages.success(
                request,
                "Produto cadastrado com sucesso.",
            )

            return redirect("produtos")

    produtos = list(
        Produto.objects
        .filter(negocio__usuario=usuario)
        .select_related("categoria", "negocio")
        .order_by("nome")
    )

    return render(
        request,
        "produtos.html",
        {
            "produtos": aplicar_margem(
                produtos,
                "custo",
                "preco_venda",
            ),
            "categorias": categorias_ordenadas(),
            "negocios": negocios_do_usuario(usuario),
        },
    )


@atlas_login_required
def servicos_view(request):
    usuario = request.atlas_usuario

    if request.method == "POST":
        negocio = get_object_or_404(
            Negocio,
            pk=request.POST.get("negocio"),
            usuario=usuario,
        )

        categoria = get_object_or_404(
            Categoria,
            pk=request.POST.get("categoria"),
        )

        nome = request.POST.get(
            "nome_servico",
            "",
        ).strip()

        custo = decimal_from_post(
            request.POST.get("custo_operacional")
        )

        valor = decimal_from_post(
            request.POST.get("valor_servico")
        )

        if not nome:
            messages.error(
                request,
                "Informe o nome do serviço.",
            )

        elif custo < ZERO or valor <= ZERO:
            messages.error(
                request,
                "Verifique o custo e o valor do serviço.",
            )

        else:
            Servico.objects.create(
                nome_servico=nome,
                custo_operacional=custo,
                valor_servico=valor,
                categoria=categoria,
                negocio=negocio,
            )

            messages.success(
                request,
                "Serviço cadastrado com sucesso.",
            )

            return redirect("servicos")

    servicos = list(
        Servico.objects
        .filter(negocio__usuario=usuario)
        .select_related("categoria", "negocio")
        .order_by("nome_servico")
    )

    return render(
        request,
        "servicos.html",
        {
            "servicos": aplicar_margem(
                servicos,
                "custo_operacional",
                "valor_servico",
            ),
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
            produto = get_object_or_404(
                Produto,
                pk=produto_id,
                negocio__usuario=usuario,
            )

        if servico_id:
            servico = get_object_or_404(
                Servico,
                pk=servico_id,
                negocio__usuario=usuario,
            )

        custo = decimal_from_post(
            request.POST.get("custo_total")
        )

        margem = decimal_from_post(
            request.POST.get("margem_lucro")
        )

        impostos = decimal_from_post(
            request.POST.get("impostos")
        )

        preco_final = calcular_preco_final(
            custo,
            margem,
            impostos,
        )

        if not produto and not servico:
            messages.error(
                request,
                "Selecione um produto ou serviço.",
            )

        elif produto and servico:
            messages.error(
                request,
                "Selecione apenas um produto ou serviço.",
            )

        elif margem < ZERO or impostos < ZERO:
            messages.error(
                request,
                "Os percentuais não podem ser negativos.",
            )

        elif preco_final is None:
            messages.error(
                request,
                "Informe custo maior que zero e "
                "percentuais abaixo de 100%.",
            )

        else:
            Precificacao.objects.create(
                custo_total=custo,
                margem_lucro=margem,
                impostos=impostos,
                preco_final=preco_final,
                produto=produto,
                servico=servico,
            )

            messages.success(
                request,
                "Precificação salva com sucesso.",
            )

            return redirect("precificacoes")

    precificacoes = (
        Precificacao.objects
        .filter(
            Q(produto__negocio__usuario=usuario)
            | Q(servico__negocio__usuario=usuario)
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
            "produtos": Produto.objects.filter(
                negocio__usuario=usuario
            ).order_by("nome"),
            "servicos": Servico.objects.filter(
                negocio__usuario=usuario
            ).order_by("nome_servico"),
        },
    )


@atlas_login_required
def metas_view(request):
    usuario = request.atlas_usuario

    if request.method == "POST":
        negocio = get_object_or_404(
            Negocio,
            pk=request.POST.get("negocio"),
            usuario=usuario,
        )

        descricao = request.POST.get(
            "descricao_meta",
            "",
        ).strip()

        valor = decimal_from_post(
            request.POST.get("valor_meta")
        )

        prazo = date_from_post(
            request.POST.get("prazo")
        )

        if not descricao:
            messages.error(
                request,
                "Informe a descrição da meta.",
            )

        elif valor <= ZERO:
            messages.error(
                request,
                "Informe um valor maior que zero.",
            )

        elif not prazo:
            messages.error(
                request,
                "Informe um prazo válido.",
            )

        else:
            MetaFinanceira.objects.create(
                descricao_meta=descricao,
                valor_meta=valor,
                prazo=prazo,
                negocio=negocio,
            )

            messages.success(
                request,
                "Meta cadastrada com sucesso.",
            )

            return redirect("metas")

    negocios = negocios_do_usuario(usuario).annotate(
        total_receitas=Sum("receita__valor")
    )

    metas = (
        MetaFinanceira.objects
        .filter(negocio__usuario=usuario)
        .select_related("negocio")
        .order_by("prazo")
    )

    return render(
        request,
        "Metas.html",
        {
            "metas": metas,
            "negocios": negocios,
        },
    )


@atlas_login_required
@require_GET
def alertas_view(request):
    usuario = request.atlas_usuario

    Alerta.objects.filter(
        negocio__usuario=usuario,
        status_alerta="Não lido",
    ).update(status_alerta="Lido")

    alertas = (
        Alerta.objects
        .filter(negocio__usuario=usuario)
        .select_related("negocio")
        .order_by("-data_criacao", "-id")
    )

    return render(
        request,
        "alertas.html",
        {
            "alertas": alertas,
            "alertas_nao_lidos": 0,
        },
    )


@atlas_login_required
def fechamentos_view(request):
    return render(
        request,
        "fechamentosMensais.html",
        {
            "fechamentos": calcular_fechamentos(
                request.atlas_usuario
            )
        },
    )


@atlas_login_required
def indicadores_view(request):
    return render(
        request,
        "IndicadoresFinanceiros.html",
        {
            "indicadores": calcular_indicadores(
                request.atlas_usuario
            )
        },
    )


@atlas_login_required
@require_GET
def notificacoes_view(request):
    usuario = request.atlas_usuario

    Notificacao.objects.filter(
        usuario=usuario,
    ).exclude(
        status_notificacao__iexact="Lida",
    ).update(
        status_notificacao="Lida",
    )

    notificacoes = (
        Notificacao.objects
        .filter(usuario=usuario)
        .select_related("despesa")
        .order_by("-data_criacao", "-id")
    )

    return render(
        request,
        "notificacoes.html",
        {
            "notificacoes": notificacoes,
            "notificacoes_nao_lidas": 0,
        },
    )


@atlas_login_required
def relatorios_view(request):
    usuario = request.atlas_usuario

    if request.method == "POST":
        negocio = get_object_or_404(
            Negocio,
            pk=request.POST.get("negocio"),
            usuario=usuario,
        )

        periodo = date_from_post(
            request.POST.get("periodo")
        )

        if not periodo:
            messages.error(
                request,
                "Informe um período válido.",
            )

        else:
            Relatorio.objects.create(
                tipo_relatorio=request.POST.get(
                    "tipo_relatorio",
                    "Financeiro",
                ),
                periodo=periodo,
                data_geracao=timezone.localdate(),
                negocio=negocio,
            )

            messages.success(
                request,
                "Relatório registrado com sucesso.",
            )

            return redirect("relatorios")

    relatorios = (
        Relatorio.objects
        .filter(negocio__usuario=usuario)
        .select_related("negocio")
        .order_by("-data_geracao", "-id")
    )

    return render(
        request,
        "relatorios.html",
        {
            "fechamentos": calcular_fechamentos(usuario),
            "indicadores": calcular_indicadores(usuario),
            "relatorios": relatorios,
            "negocios": negocios_do_usuario(usuario),
        },
    )


@atlas_login_required
def usuarios_view(request):
    usuario = request.atlas_usuario

    if request.method == "POST":
        nome = request.POST.get(
            "nome",
            "",
        ).strip()

        email = request.POST.get(
            "email",
            "",
        ).strip().lower()

        tipo_usuario = request.POST.get(
            "tipo_usuario",
            "MEI",
        )

        if usuario.tipo_usuario == "Administrador":
            tipo_usuario = "Administrador"
        elif tipo_usuario not in TIPOS_USUARIO:
            tipo_usuario = "MEI"

        if not nome or not email:
            messages.error(
                request,
                "Informe nome e e-mail.",
            )

        elif Usuario.objects.exclude(
            pk=usuario.pk
        ).filter(
            email__iexact=email
        ).exists():
            messages.error(
                request,
                "Este e-mail já está sendo usado.",
            )

        else:
            usuario.nome = nome
            usuario.email = email
            usuario.tipo_usuario = tipo_usuario

            usuario.save(
                update_fields=[
                    "nome",
                    "email",
                    "tipo_usuario",
                ]
            )

            request.session["usuario_nome"] = usuario.nome

            messages.success(
                request,
                "Perfil atualizado com sucesso.",
            )

            return redirect("usuarios")

    return render(
        request,
        "usuarios.html",
        {"usuario": usuario},
    )


@atlas_login_required
def categoria_view(request):
    if request.method == "POST":
        nome_categoria = request.POST.get(
            "nome_categoria",
            "",
        ).strip()

        tipo = request.POST.get(
            "tipo",
            "Geral",
        ).strip()

        if not nome_categoria:
            messages.error(
                request,
                "Informe o nome da categoria.",
            )

        else:
            Categoria.objects.get_or_create(
                nome_categoria=nome_categoria,
                tipo=tipo or "Geral",
            )

            messages.success(
                request,
                "Categoria salva com sucesso.",
            )

            return redirect("categorias")

    return render(
        request,
        "categoria.html",
        {
            "categorias": categorias_ordenadas()
        },
    )


@atlas_login_required
@require_POST
def marcar_despesa_paga(request, despesa_id):
    despesa = get_object_or_404(
        Despesa,
        pk=despesa_id,
        negocio__usuario=request.atlas_usuario,
    )

    if despesa.status == "Cancelada":
        messages.error(
            request,
            "Uma despesa cancelada não pode ser paga.",
        )

        return redirect("despesas")

    if despesa.status == "Paga":
        messages.info(
            request,
            "Essa despesa já estava paga.",
        )

        return redirect("despesas")

    despesa.status = "Paga"
    despesa.save(update_fields=["status"])

    Notificacao.objects.filter(
        despesa=despesa,
    ).exclude(
        status_notificacao__iexact="Lida",
    ).update(
        status_notificacao="Lida",
    )

    gerar_alertas_financeiros(
        usuario=request.atlas_usuario
    )

    messages.success(
        request,
        "Despesa marcada como paga.",
    )

    return redirect("despesas")