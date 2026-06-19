from decimal import Decimal

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

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
            reverse("alertas"),
            {
                "mensagem": "Revisar fluxo de caixa",
                "data_alerta": "2026-06-15",
                "prioridade": "Alta",
                "negocio": self.negocio.id,
            },
        )
        self.client.post(
            reverse("notificacoes"),
            {
                "mensagem_notificacao": "Bem-vinda ao ATLAS",
                "tipo": "Informacao",
                "status_notificacao": "Nao lida",
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
        self.assertEqual(Alerta.objects.count(), 1)
        self.assertEqual(Notificacao.objects.count(), 1)
        self.assertEqual(Relatorio.objects.count(), 1)
        self.assertEqual(servico.nome_servico, "Servico teste")

    def test_anonymous_user_is_redirected(self):
        response = self.client.get(reverse("index"))
        self.assertRedirects(response, reverse("login"))