from django.db import transaction
from django.utils import timezone

from decimal import Decimal

from django.db.models import Sum

from .models import (
    Alerta,
    Despesa,
    Negocio,
    Notificacao,
    Receita,
)


TIPO_ANTECIPADO = "Vencimento amanhã"
TIPO_VENCIMENTO = "Vencimento hoje"


def criar_notificacao(despesa, tipo, mensagem, campo_controle):
    with transaction.atomic():
        filtros = {
            "pk": despesa.pk,
            "status__iexact": "Pendente",
            campo_controle: False,
        }

        atualizada = Despesa.objects.filter(**filtros).update(
            **{campo_controle: True}
        )

        if not atualizada:
            return False

        Notificacao.objects.get_or_create(
            despesa=despesa,
            tipo=tipo,
            defaults={
                "usuario": despesa.negocio.usuario,
                "mensagem_notificacao": mensagem,
                "status_notificacao": "Não lida",
            },
        )

        return True


def gerar_notificacoes_de_vencimento(usuario=None, hoje=None):
    hoje = hoje or timezone.localdate()
    total_criadas = 0

    despesas = (
        Despesa.objects
        .filter(
            status__iexact="Pendente",
            data_vencimento__isnull=False,
        )
        .select_related("negocio__usuario")
    )

    if usuario is not None:
        despesas = despesas.filter(negocio__usuario=usuario)

    for despesa in despesas:
        dias_restantes = (despesa.data_vencimento - hoje).days
        descricao = despesa.descricao_despesa[:80]

        if dias_restantes == 1:
            criada = criar_notificacao(
                despesa=despesa,
                tipo=TIPO_ANTECIPADO,
                mensagem=f'A conta "{descricao}" vence amanhã.',
                campo_controle="aviso_antecipado_enviado",
            )
            total_criadas += int(criada)

        elif dias_restantes == 0:
            criada = criar_notificacao(
                despesa=despesa,
                tipo=TIPO_VENCIMENTO,
                mensagem=f'A conta "{descricao}" vence hoje.',
                campo_controle="aviso_vencimento_enviado",
            )
            total_criadas += int(criada)

    return total_criadas

TIPO_ALERTA_DESPESAS = "Despesas acima das receitas"


def gerar_alertas_financeiros(usuario=None, hoje=None):
    hoje = hoje or timezone.localdate()
    periodo = hoje.replace(day=1)
    total_criados = 0

    negocios = Negocio.objects.all()

    if usuario is not None:
        negocios = negocios.filter(usuario=usuario)

    for negocio in negocios:
        total_receitas = (
            Receita.objects
            .filter(
                negocio=negocio,
                data__year=hoje.year,
                data__month=hoje.month,
            )
            .aggregate(total=Sum("valor"))["total"]
            or Decimal("0.00")
        )

        total_despesas = (
            Despesa.objects
            .filter(
                negocio=negocio,
                data_despesa__year=hoje.year,
                data_despesa__month=hoje.month,
            )
            .exclude(status__iexact="Cancelada")
            .aggregate(total=Sum("valor_despesa"))["total"]
            or Decimal("0.00")
        )

        alerta = Alerta.objects.filter(
            negocio=negocio,
            tipo=TIPO_ALERTA_DESPESAS,
            periodo_referencia=periodo,
        ).first()

        if total_despesas <= total_receitas:
            if alerta and alerta.status_alerta != "Resolvido":
                alerta.status_alerta = "Resolvido"
                alerta.save(update_fields=["status_alerta"])

            continue

        mensagem = (
            f'As despesas do negócio "{negocio.nome_negocio}" '
            f'estão maiores que as receitas em '
            f'{hoje.month:02d}/{hoje.year}. '
            f'Receitas: R$ {total_receitas:.2f}. '
            f'Despesas: R$ {total_despesas:.2f}.'
        )

        if alerta is None:
            Alerta.objects.create(
                negocio=negocio,
                tipo=TIPO_ALERTA_DESPESAS,
                periodo_referencia=periodo,
                mensagem=mensagem,
                data_alerta=hoje,
                prioridade="Alta",
                status_alerta="Não lido",
                automatico=True,
            )
            total_criados += 1
            continue

        campos_alterados = []

        if alerta.mensagem != mensagem:
            alerta.mensagem = mensagem
            campos_alterados.append("mensagem")

        if alerta.status_alerta == "Resolvido":
            alerta.status_alerta = "Não lido"
            campos_alterados.append("status_alerta")
            total_criados += 1

        if campos_alterados:
            alerta.save(update_fields=campos_alterados)

    return total_criados