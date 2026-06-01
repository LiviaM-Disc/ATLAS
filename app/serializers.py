from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import *


class UsuarioSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = '__all__'

    def create(self, validated_data):
        validated_data['senha'] = make_password(validated_data['senha'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'senha' in validated_data:
            validated_data['senha'] = make_password(validated_data['senha'])
        return super().update(instance, validated_data)


class NegocioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Negocio
        fields = '__all__'


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'


class ReceitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receita
        fields = '__all__'


class DespesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Despesa
        fields = '__all__'


class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = '__all__'


class ServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servico
        fields = '__all__'


class PrecificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Precificacao
        fields = '__all__'


class RelatorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relatorio
        fields = '__all__'


class MetaFinanceiraSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaFinanceira
        fields = '__all__'


class AlertaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alerta
        fields = '__all__'


class FechamentoMensalSerializer(serializers.ModelSerializer):
    class Meta:
        model = FechamentoMensal
        fields = '__all__'


class NotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacao
        fields = '__all__'


class IndicadorFinanceiroSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndicadorFinanceiro
        fields = '__all__'


class DashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dashboard
        fields = '__all__'