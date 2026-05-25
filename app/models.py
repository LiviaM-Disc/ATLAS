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

class Despesa (models.Model):
    valor_despesa=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Valor")
    data_depesa=models.DateField(verbose_name="Data")
    descricao_despesa=models.CharField(max_length=150,verbose_name="Descrição da Despesa")
    status=models.CharField(max_length=100,verbose_name= "Status")

    categoria=models.ForeignKey(Categoria,on_delete=models.CASCADE, verbose_name="Categoria")
    negocio=models.ForeignKey(Negocio, on_delete=models.CASCADE,verbose_name="Negócio")

    def __str__(self):
        return f"{self.valor_despesa},{self.data_depesa},{self.descricao_despesa},{self.status}"
    class Meta:
        verbose_name="Despesa"
        verbose_name_plural="Despesas"


class Produto (models.Model):
    nome=models.CharField(max_length=100,verbose_name="Valor")
    custo=models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Custo")
    preco_venda=models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço da Venda")
    estoque=models.CharField(max_length=100,verbose_name= "Estoque")

    categoria=models.ForeignKey(Categoria,on_delete=models.CASCADE, verbose_name="Categoria")
    negocio=models.ForeignKey(Negocio, on_delete=models.CASCADE,verbose_name="Negócio")

    def __str__(self):
        return f"{self.nome},{self.custo},{self.preco_venda},{self.estoque}"
    class Meta:
        verbose_name="Estoque"
        verbose_name_plural="Estoques"

class Servico (models.Model):
    nome_servico=models.CharField(max_length=100,verbose_name="Nome")
    custo_operacional=models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Custo")
    valor_servico=models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor do Serviço")
   

    categoria=models.ForeignKey(Categoria,on_delete=models.CASCADE, verbose_name="Categoria")
    negocio=models.ForeignKey(Negocio, on_delete=models.CASCADE,verbose_name="Negócio")

    def __str__(self):
        return f"{self.nome_servico},{self.custo_operacional},{self.valor_servico}"
    class Meta:
        verbose_name="Serviço"
        verbose_name_plural="Serviços"

class Precificacao (models.Model):
    custo_total=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Valor")
    margem_lucros=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Margem de lucro")
    impostos=models.DecimalField(max_digits=10, decimal_places=2,verbose_name="Impostos")
    preco_final=models.DecimalField(max_digits=100,decimal_places=2,verbose_name= "Preço Final")

    produto=models.ForeignKey(Produto,on_delete=models.CASCADE, verbose_name="Produto")
    servico=models.ForeignKey(Servico, on_delete=models.CASCADE,verbose_name="Servico")

    def __str__(self):
        return f"{self.custo_total},{self.margem_lucros},{self.impostos},{self.preco_final}"
    class Meta:
        verbose_name="Precificação"
        verbose_name_plural="Precificações"

class Relatorio (models.Model):
    tipo_relatorio=models.CharField(max_length=25,verbose_name="Tipo de Relatório")
    periodo=models.DateField(verbose_name="Periodo")
    data_geracao=models.DateField(max_length=150,verbose_name="Data de Geração")

    negocio=models.ForeignKey(Negocio, on_delete=models.CASCADE,verbose_name="Negócio")

    def __str__(self):
        return f"{self.tipo_relatorio},{self.periodo},{self.data_geracao}"
    class Meta:
        verbose_name="Relatório"
        verbose_name_plural="Relatórios"

class MetaFinanceira  (models.Model):
    valor_meta=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Valor")
    prazo=models.DateField(verbose_name="Data")
    descricao_meta=models.CharField(max_length=150,verbose_name="Descrição da Meta")
   
    negocio=models.ForeignKey(Negocio, on_delete=models.CASCADE,verbose_name="Negócio")

    def __str__(self):
        return f"{self.valor_meta},{self.prazo},{self.descricao_meta}"
    class Meta:
        verbose_name="Meta"
        verbose_name_plural="Metas"

class Alerta (models.Model):
    mensagem=models.CharField(max_length=100,verbose_name="Mensagem")
    data_alerta=models.DateField(verbose_name="Data")
    prioridade=models.CharField(max_length=150,verbose_name="Prioridade")
    
    negocio=models.ForeignKey(Negocio, on_delete=models.CASCADE,verbose_name="Negócio")

    def __str__(self):
        return f"{self.mensagem},{self.data_alerta},{self.prioridade}"
    class Meta:
        verbose_name="Alerta"
        verbose_name_plural="Alertas"

class FechamentoMensal (models.Model):
    receita_total=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Valor total da Receita")
    despesa_total=models.DecimalField(max_digits=10,decimal_places=2, verbose_name="Despesa total")
    lucro_liquido=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Lucro Liquido")
    saldo_final=models.DecimalField(max_digits=10,decimal_places=2,verbose_name= "Saldo Final")
    periodo=models.DateField(verbose_name="Periodo")

    negocio=models.ForeignKey(Negocio, on_delete=models.CASCADE,verbose_name="Negócio")

    def __str__(self):
        return f"{self.receita_total},{self.despesa_total},{self.lucro_liquido},{self.saldo_final},{self.periodo}"
    class Meta:
        verbose_name="Fechamento Mensal"
        verbose_name_plural="Fechamentos Mensais"

class Notificacao (models.Model):
    mensagem_notificacao=models.CharField(max_length=100,verbose_name="Notificação")
    tipo=models.CharField(max_length=100,verbose_name="Tipo")
    status_notificacao=models.CharField(max_length=150,verbose_name="Status")

    usuario=models.ForeignKey(Usuario,on_delete=models.CASCADE, verbose_name="Usuário")
    

    def __str__(self):
        return f"{self.mensagem_notificacao},{self.tipo},{self.status_notificacao}"
    class Meta:
        verbose_name="Notificação"
        verbose_name_plural="Notificações"

class IndicadorFinanceiro (models.Model):
    margem_lucro=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Margem de Lucro")
    ponto_equilibrio=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Data")
    
    negocio=models.ForeignKey(Negocio, on_delete=models.CASCADE,verbose_name="Negócio")

    def __str__(self):
        return f"{self.margem_lucro},{self.ponto_equilibrio}"
    class Meta:
        verbose_name="Indicador Financeiro"
        verbose_name_plural="Indicadores Financeiros"

class Dashboard (models.Model):
    faturamento_mensal=models.DecimalField(max_digits=10,decimal_places=2, verbose_name="Faturamento Mensal")
    despesas_totais=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Total de Despesas")
    lucro_total=models.DecimalField(max_digits=10, decimal_places=2,verbose_name="Lucro Total")
    saldo_atual=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="Saldo Atual")

    negocio=models.ForeignKey(Negocio, on_delete=models.CASCADE,verbose_name="Negócio")

    def __str__(self):
        return f"{self.faturamento_mensal},{self.despesas_totais},{self.lucro_total},{self.saldo_atual}"

    class Meta:
        verbose_name="Dashboard"
        verbose_name_plural="Dashboards"

