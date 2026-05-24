from django.db import models

class Usuario (models.Model):
    nome = models.CharField(max_length=150,verbose_name="Nome do Usuario")
    email=models.EmailField(max_length=30,verbose_name="Email")
    senha=models.CharField(max_length=120,verbose_name="Senha")
    data_cadastro=models.DateField(verbose_name=" Data de Cadastro")
    tipo_usuario=models.CharField(max_length=20,verbose_name=" Tipo de Usuario")
    def __str__(self):
        return f"{self.nome},{self.email},{self.data_cadastro},{self.tipo_usuario}"
    class Meta:
        verbose_name= "Usuário"
        verbose_name_plural= "Usuários"

class Negocio (models.Model):
    nome_negocio = models.CharField(max_length=150,verbose_name="Nome do Negócio")
    segmento=models.CharField(max_length=30,verbose_name="Segmento")
    meta_mensal=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Meta Mensal")
    capital_inicial=models.DecimalField(max_digits=10, decimal_places=2,verbose_name="Capital Inicial")
   
    usuario=models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name="Nome do Usuário")

    def __str__(self):
        return f"{self.nome_negocio},{self.segmento},{self.meta_mensal},{self.capital_inicial}"
    class Meta:
        verbose_name= "Negócio"
        verbose_name_plural= "Negócios"

class Categoria (models.Model):
    nome_categoria=models.CharField(max_length=30, verbose_name="Nome da Categoria")
    tipo=models.CharField(max_length=100,verbose_name="Tipo de Categoria")

    def __str__(self):
        return f"{self.nome_categoria},{self.tipo}"
    class Meta:
        verbose_name="Categoria"
        verbose_name_plural="Categorias"

class Receita (models.Model):
    valor=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Valor")
    data=models.DateField(verbose_name="Data")
    descricao=models.CharField(max_length=150,verbose_name="Descrição da Receita")
    forma_pagamento=models.CharField(max_length=100,verbose_name= "Forma de Pagamento")

    categoria=models.ForeignKey(Categoria,on_delete=models.CASCADE, verbose_name="Categoria")
    negocio=models.ForeignKey(Negocio, on_delete=models.CASCADE,verbose_name="Negócio")

    def __str__(self):
        return f"{self.valor},{self.data},{self.descricao},{self.forma_pagamento}"
    class Meta:
        verbose_name="Receita"
        verbose_name_plural="Receitas"