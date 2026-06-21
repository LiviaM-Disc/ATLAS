from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import UsuarioForm
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


class AtlasFlowTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome="Livia",
            email="livia@example.com",
            senha=make_password("senha123"),
        )
        self.negocio = Negocio.objects.create(
            nome_negocio="Atelier ATLAS",
            segmento="Servicos",
            meta_mensal=Decimal("5000.00"),
            capital_inicial=Decimal("1000.00"),
            usuario=self.usuario,
        )
        self.categoria = Categoria.objects.create(nome_categoria="Geral", tipo="Geral")

    def autenticar(self):
        session = self.client.session
        session["usuario_id"] = self.usuario.id
        session["usuario_nome"] = self.usuario.nome
        session.save()

    def test_login_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("login"),
            {"email": "livia@example.com", "senha": "senha123"},
        )
        self.assertRedirects(response, reverse("index"))

    def test_usuario_form_hashes_password(self):
        form = UsuarioForm(
            data={
                "nome": "Novo usuario",
                "email": "novo@example.com",
                "senha": "senha-segura",
                "tipo_usuario": "MEI",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        usuario = form.save()
        self.assertTrue(check_password("senha-segura", usuario.senha))

    def test_login_rotates_session_key(self):
        session = self.client.session
        session["antes_do_login"] = True
        session.save()
        session_key_anterior = session.session_key

        self.client.post(
            reverse("login"),
            {"email": "livia@example.com", "senha": "senha123"},
        )

        self.assertNotEqual(self.client.session.session_key, session_key_anterior)

    def test_logout_requires_post(self):
        self.autenticar()

        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(self.client.session.get("usuario_id"), self.usuario.id)

        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("usuario_id", self.client.session)

    def test_django_superuser_can_login_by_username(self):
        auth_user = User.objects.create_superuser(username="admin", password="123456")
        response = self.client.post(
            reverse("login"),
            {"email": "admin", "senha": "123456"},
        )
        self.assertRedirects(response, reverse("index"))
        self.assertEqual(self.client.session.get("_auth_user_id"), str(auth_user.pk))
        self.assertTrue(Usuario.objects.filter(nome="admin", tipo_usuario="Administrador").exists())

    def test_django_superuser_can_login_by_email_and_access_admin(self):
        auth_user = User.objects.create_superuser(
            username="admin",
            email="admin@atlas.local",
            password="123456",
        )
        response = self.client.post(
            reverse("login"),
            {"email": "admin@atlas.local", "senha": "123456"},
        )
        self.assertRedirects(response, reverse("index"))
        self.assertEqual(self.client.session.get("_auth_user_id"), str(auth_user.pk))
        self.assertTrue(
            Usuario.objects.filter(
                nome="admin",
                email="admin@atlas.local",
                tipo_usuario="Administrador",
            ).exists()
        )

        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)

    def test_authenticated_pages_render(self):
        self.autenticar()
        for name in [
            "index",
            "listar_negocios",
            "lista_receitas",
            "despesas",
            "produtos",
            "servicos",
            "categorias",
            "precificacoes",
            "metas",
            "alertas",
            "relatorios",
            "fechamentos",
            "indicadores",
            "notificacoes",
            "usuarios",
        ]:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_financial_create_flows(self):
        self.autenticar()

        self.client.post(
            reverse("lista_receitas"),
            {
                "descricao": "Venda",
                "valor": "1500.00",
                "data": "2026-06-01",
                "forma_pagamento": "Pix",
                "categoria": self.categoria.id,
                "negocio": self.negocio.id,
            },
        )
        self.client.post(
            reverse("despesas"),
            {
                "descricao_despesa": "Fornecedor",
                "valor_despesa": "400.00",
                "data_despesa": "2026-06-02",
                "status": "Paga",
                "categoria": self.categoria.id,
                "negocio": self.negocio.id,
                "data_vencimento": "2026-06-03",
            },
        )
        self.client.post(
            reverse("produtos"),
            {
                "nome_produto": "Produto teste",
                "custo_producao": "30.00",
                "preco_venda": "75.00",
                "estoque": "10",
                "categoria": self.categoria.id,
                "negocio": self.negocio.id,
            },
        )
        self.client.post(
            reverse("servicos"),
            {
                "nome_servico": "Servico teste",
                "custo_operacional": "50.00",
                "valor_servico": "120.00",
                "categoria": self.categoria.id,
                "negocio": self.negocio.id,
            },
        )

        produto = Produto.objects.get(nome="Produto teste")
        servico = Servico.objects.get(nome_servico="Servico teste")

        self.client.post(
            reverse("precificacoes"),
            {
                "produto": produto.id,
                "servico": "",
                "custo_total": "100.00",
                "margem_lucro": "30.00",
                "impostos": "10.00",
            },
        )
        self.client.post(
            reverse("metas"),
            {
                "descricao_meta": "Aumentar faturamento",
                "valor_meta": "3000.00",
                "prazo": "2026-12-31",
                "negocio": self.negocio.id,
            },
        )
        
        self.client.post(
            reverse("relatorios"),
            {
                "tipo_relatorio": "Financeiro",
                "periodo": "2026-06-01",
                "negocio": self.negocio.id,
            },
        )

        self.assertEqual(Receita.objects.count(), 1)
        self.assertEqual(Despesa.objects.count(), 1)
        self.assertEqual(Produto.objects.count(), 1)
        self.assertEqual(Servico.objects.count(), 1)
        self.assertEqual(Precificacao.objects.count(), 1)
        self.assertEqual(MetaFinanceira.objects.count(), 1)
        self.assertEqual(Relatorio.objects.count(), 1)
        self.assertEqual(servico.nome_servico, "Servico teste")

    def test_anonymous_user_is_redirected(self):
        response = self.client.get(reverse("index"))
        self.assertRedirects(response, reverse("login"))

    def test_user_cannot_pay_another_users_expense(self):
        outro_usuario = Usuario.objects.create(
            nome="Outra pessoa",
            email="outra@example.com",
            senha=make_password("senha123"),
        )
        outro_negocio = Negocio.objects.create(
            nome_negocio="Outro negocio",
            segmento="Servicos",
            meta_mensal=Decimal("1000.00"),
            capital_inicial=Decimal("100.00"),
            usuario=outro_usuario,
        )
        despesa = Despesa.objects.create(
            valor_despesa=Decimal("80.00"),
            data_despesa=date(2026, 6, 1),
            descricao_despesa="Despesa privada",
            status="Pendente",
            categoria=self.categoria,
            negocio=outro_negocio,
        )
        self.autenticar()

        response = self.client.post(
            reverse("marcar_despesa_paga", args=[despesa.id])
        )

        self.assertEqual(response.status_code, 404)
        despesa.refresh_from_db()
        self.assertEqual(despesa.status, "Pendente")


class AutomationServiceTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome="Livia",
            email="livia@example.com",
            senha=make_password("senha123"),
        )
        self.negocio = Negocio.objects.create(
            nome_negocio="Atelier ATLAS",
            segmento="Servicos",
            meta_mensal=Decimal("5000.00"),
            capital_inicial=Decimal("1000.00"),
            usuario=self.usuario,
        )
        self.categoria = Categoria.objects.create(
            nome_categoria="Geral",
            tipo="Geral",
        )

    def test_due_date_notification_is_created_only_once(self):
        hoje = date(2026, 6, 21)
        despesa = Despesa.objects.create(
            valor_despesa=Decimal("80.00"),
            data_despesa=hoje,
            data_vencimento=hoje + timedelta(days=1),
            descricao_despesa="Fornecedor",
            status="Pendente",
            categoria=self.categoria,
            negocio=self.negocio,
        )

        self.assertEqual(
            gerar_notificacoes_de_vencimento(self.usuario, hoje),
            1,
        )
        self.assertEqual(
            gerar_notificacoes_de_vencimento(self.usuario, hoje),
            0,
        )
        self.assertEqual(
            Notificacao.objects.filter(despesa=despesa).count(),
            1,
        )

    def test_financial_alert_is_resolved_and_reopened(self):
        hoje = date(2026, 6, 21)
        Receita.objects.create(
            valor=Decimal("100.00"),
            data=hoje,
            descricao="Venda",
            forma_pagamento="Pix",
            categoria=self.categoria,
            negocio=self.negocio,
        )
        Despesa.objects.create(
            valor_despesa=Decimal("150.00"),
            data_despesa=hoje,
            descricao_despesa="Fornecedor",
            status="Paga",
            categoria=self.categoria,
            negocio=self.negocio,
        )

        self.assertEqual(gerar_alertas_financeiros(self.usuario, hoje), 1)
        alerta = Alerta.objects.get(negocio=self.negocio)
        self.assertEqual(alerta.status_alerta, "Não lido")

        Receita.objects.create(
            valor=Decimal("100.00"),
            data=hoje,
            descricao="Venda extra",
            forma_pagamento="Pix",
            categoria=self.categoria,
            negocio=self.negocio,
        )
        self.assertEqual(gerar_alertas_financeiros(self.usuario, hoje), 0)
        alerta.refresh_from_db()
        self.assertEqual(alerta.status_alerta, "Resolvido")

        Despesa.objects.create(
            valor_despesa=Decimal("100.00"),
            data_despesa=hoje,
            descricao_despesa="Despesa extra",
            status="Paga",
            categoria=self.categoria,
            negocio=self.negocio,
        )
        self.assertEqual(gerar_alertas_financeiros(self.usuario, hoje), 1)
        alerta.refresh_from_db()
        self.assertEqual(alerta.status_alerta, "Não lido")
