from django import forms
from django.contrib.auth.hashers import make_password

from .models import (
    Alerta,
    Categoria,
    Despesa,
    FechamentoMensal,
    IndicadorFinanceiro,
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


def date_widget():
    return forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")


class AtlasModelForm(forms.ModelForm):
    def __init__(self, *args, usuario=None, **kwargs):
        self.usuario_logado = usuario
        super().__init__(*args, **kwargs)
        self.aplicar_estilo()
        self.limitar_relacionamentos(usuario)

    def aplicar_estilo(self):
        for field in self.fields.values():
            css_class = "form-control"
            if isinstance(field.widget, forms.CheckboxInput):
                css_class = "form-check-input"
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("rows", 3)
            field.widget.attrs["class"] = field.widget.attrs.get("class", css_class)

    def limitar_relacionamentos(self, usuario):
        if not usuario:
            return

        if "usuario" in self.fields:
            self.fields["usuario"].queryset = Usuario.objects.filter(pk=usuario.pk)
            self.fields["usuario"].initial = usuario
            self.fields["usuario"].widget = forms.HiddenInput()

        if "negocio" in self.fields:
            self.fields["negocio"].queryset = Negocio.objects.filter(usuario=usuario)

        if "produto" in self.fields:
            self.fields["produto"].queryset = Produto.objects.filter(negocio__usuario=usuario)

        if "servico" in self.fields:
            self.fields["servico"].queryset = Servico.objects.filter(negocio__usuario=usuario)


class UsuarioForm(AtlasModelForm):
    senha = forms.CharField(
        label="Senha",
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Deixe em branco para manter a senha atual.",
    )

    class Meta:
        model = Usuario
        fields = ["nome", "email", "senha", "tipo_usuario"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["senha"].required = True
            self.fields["senha"].help_text = ""

    def save(self, commit=True):
        usuario = super().save(commit=False)
        senha = self.cleaned_data.get("senha")
        if senha:
            usuario.senha = make_password(senha)
        elif self.instance.pk:
            usuario.senha = Usuario.objects.get(pk=self.instance.pk).senha
        if commit:
            usuario.save()
        return usuario


class CadastroForm(forms.ModelForm):
    senha = forms.CharField(label="Senha", widget=forms.PasswordInput(render_value=False))

    class Meta:
        model = Usuario
        fields = ["nome", "email", "senha"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.senha = make_password(self.cleaned_data["senha"])
        if commit:
            usuario.save()
        return usuario


class NegocioForm(AtlasModelForm):
    class Meta:
        model = Negocio
        fields = ["nome_negocio", "segmento", "meta_mensal", "capital_inicial", "usuario"]


class CategoriaForm(AtlasModelForm):
    class Meta:
        model = Categoria
        fields = ["nome_categoria", "tipo"]


class ReceitaForm(AtlasModelForm):
    class Meta:
        model = Receita
        fields = ["valor", "data", "descricao", "forma_pagamento", "categoria", "negocio"]
        widgets = {"data": date_widget()}


class DespesaForm(AtlasModelForm):
    class Meta:
        model = Despesa
        fields = ["valor_despesa", "data_despesa", "descricao_despesa", "status", "categoria", "negocio"]
        widgets = {"data_despesa": date_widget()}


class ProdutoForm(AtlasModelForm):
    class Meta:
        model = Produto
        fields = ["nome", "custo", "preco_venda", "estoque", "categoria", "negocio"]


class ServicoForm(AtlasModelForm):
    class Meta:
        model = Servico
        fields = ["nome_servico", "custo_operacional", "valor_servico", "categoria", "negocio"]


class PrecificacaoForm(AtlasModelForm):
    class Meta:
        model = Precificacao
        fields = ["custo_total", "margem_lucro", "impostos", "preco_final", "produto", "servico"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["produto"].required = False
        self.fields["servico"].required = False


class RelatorioForm(AtlasModelForm):
    class Meta:
        model = Relatorio
        fields = ["tipo_relatorio", "periodo", "data_geracao", "negocio"]
        widgets = {"periodo": date_widget(), "data_geracao": date_widget()}


class MetaFinanceiraForm(AtlasModelForm):
    class Meta:
        model = MetaFinanceira
        fields = ["descricao_meta", "valor_meta", "prazo", "negocio"]
        widgets = {"prazo": date_widget()}


class AlertaForm(AtlasModelForm):
    class Meta:
        model = Alerta
        fields = ["mensagem", "prioridade", "data_alerta", "negocio"]
        widgets = {"data_alerta": date_widget()}


class FechamentoMensalForm(AtlasModelForm):
    class Meta:
        model = FechamentoMensal
        fields = ["receita_total", "despesa_total", "lucro_liquido", "saldo_final", "periodo", "negocio"]
        widgets = {"periodo": date_widget()}


class NotificacaoForm(AtlasModelForm):
    class Meta:
        model = Notificacao
        fields = ["mensagem_notificacao", "tipo", "status_notificacao", "usuario"]


class IndicadorFinanceiroForm(AtlasModelForm):
    class Meta:
        model = IndicadorFinanceiro
        fields = ["margem_lucro", "ponto_equilibrio", "negocio"]
