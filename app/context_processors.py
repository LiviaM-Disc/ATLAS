from .models import Alerta, Notificacao


def contador_notificacoes(request):
    usuario_id = request.session.get("usuario_id")

    if not usuario_id:
        return {
            "notificacoes_nao_lidas": 0,
            "alertas_nao_lidos": 0,
        }

    return {
        "notificacoes_nao_lidas": Notificacao.objects.filter(
            usuario_id=usuario_id,
            status_notificacao="Não lida",
        ).count(),

        "alertas_nao_lidos": Alerta.objects.filter(
            negocio__usuario_id=usuario_id,
            status_alerta="Não lido",
        ).count(),
    }