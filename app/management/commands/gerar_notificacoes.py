from django.core.management.base import BaseCommand

from app.services import (
    gerar_alertas_financeiros,
    gerar_notificacoes_de_vencimento,
)


class Command(BaseCommand):
    help = "Gera notificações e alertas financeiros automáticos."

    def handle(self, *args, **options):
        notificacoes = gerar_notificacoes_de_vencimento()
        alertas = gerar_alertas_financeiros()

        self.stdout.write(
            self.style.SUCCESS(
                f"{notificacoes} notificação(ões) criada(s) e "
                f"{alertas} alerta(s) financeiro(s) criado(s)."
            )
        )