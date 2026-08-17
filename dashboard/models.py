from django.db import models


class Dashboard(models.Model):
    """
    Modelo para armazenar os Dashboards disponíveis no sistema.
    Os dashboards serão importados do SGS (Sistema de Gestão de Relatórios).
    """

    class Meta:
        db_table = "Dashboard"
        managed = False
        ordering = ["Nome"]
        verbose_name = "Dashboard"
        verbose_name_plural = "Dashboards"

    Nome = models.CharField(max_length=50, verbose_name="Nome")
    Descricao = models.CharField(max_length=255, verbose_name="Descrição")
    Ativo = models.BooleanField(
        null=True, blank=True, default=True, verbose_name="Ativo"
    )

    def __str__(self):
        return self.Nome


class Dashboard_Config(models.Model):
    """
    Modelo para configurar a ordem e duração de exibição dos Dashboards.
    Define a sequência de exibição em formato de slides com transição automática.
    """

    class Meta:
        db_table = "Dashboard_Config"
        managed = False
        ordering = ["Ordem"]
        verbose_name = "Dashboard Configuração"
        verbose_name_plural = "Dashboard Configurações"

    Dashboard = models.ForeignKey(
        Dashboard, on_delete=models.CASCADE, verbose_name="Dashboard"
    )
    Ordem = models.IntegerField(verbose_name="Ordem de Exibição")
    Duracao = models.IntegerField(verbose_name="Duração (segundos)")
    Mensagem = models.CharField(
        max_length=255, verbose_name="Mensagem", null=True, blank=True
    )

    def __str__(self):
        return f"{self.Ordem} - {self.Dashboard.Nome} ({self.Duracao}s)"


class RPA(models.Model):
    """
    Modelo para armazenar informações sobre RPAs.
    Tabela existente no banco de dados (não gera migração).
    """

    class Meta:
        db_table = "RPA"
        managed = False
        verbose_name = "RPA"
        verbose_name_plural = "RPAs"

    Nome = models.CharField(max_length=255, verbose_name="Nome")
    Descricao = models.CharField(
        max_length=255, verbose_name="Descrição", null=True, blank=True
    )

    def __str__(self):
        return self.Nome


class RPA_Atualizacao(models.Model):
    """
    Modelo para armazenar informações sobre atualizações de RPAs.
    """

    class Meta:
        db_table = "RPA_Atualizacao"
        managed = False
        ordering = ["Data"]
        verbose_name = "RPA Atualização"
        verbose_name_plural = "RPA Atualizações"

    Data = models.CharField(max_length=100, verbose_name="Data")
    Hora = models.CharField(max_length=100, verbose_name="Hora")
    Periodo = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Período"
    )
    Inseridos = models.CharField(max_length=100, verbose_name="Inseridos")
    Atualizados = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Atualizados"
    )
    RPA = models.ForeignKey(RPA, on_delete=models.CASCADE, verbose_name="RPA")

    def __str__(self):
        return f"{self.Periodo} - {self.Data} {self.Hora}"


class Log(models.Model):
    """
    Log de auditoria compartilhado do legado `sga` (tabela `Log`, mesma estrutura
    usada em todo o ecossistema oficial: id/NomeUsuario/Acao/Descricao/Data/Hora/
    Detalhes). Adicionado na auditoria de 17/08/2026 — as gravações da tela
    "Gerenciar" (Meta/Mensagens/Configuração) não tinham Log Duplo (regra 11 do
    CLAUDE.md). Ver `dashboard/services.py::registrar_log`.
    """

    class Meta:
        db_table = "Log"
        managed = False
        ordering = ["-Data", "-Hora"]
        verbose_name = "Log"
        verbose_name_plural = "Logs"

    NomeUsuario = models.CharField(max_length=200, verbose_name="Usuário")
    Acao = models.IntegerField(verbose_name="Ação")
    Descricao = models.CharField(max_length=200, verbose_name="Descrição")
    Data = models.DateField(verbose_name="Data")
    Hora = models.TimeField(verbose_name="Hora")
    Detalhes = models.TextField(null=True, blank=True, verbose_name="Detalhes")

    def __str__(self):
        return f"{self.NomeUsuario} - {self.Descricao}"


class VendaConfiguracao(models.Model):
    """
    Modelo para armazenar configurações de vendas.
    Tabela existente no banco de dados (não gera migração).
    """

    class Meta:
        db_table = "VendaConfiguracao"
        managed = False
        verbose_name = "Venda Configuração"
        verbose_name_plural = "Vendas Configurações"

    Descricao = models.CharField(max_length=255, verbose_name="Descrição")
    Valor = models.CharField(max_length=255, verbose_name="Valor")

    def __str__(self):
        return f"{self.Descricao} - {self.Valor}"


class Dashboard_Log(models.Model):
    """
    Novo Modelo para registrar logs de exibição de dashboards (auditoria).
    Registra quando cada dashboard foi exibido e por quanto tempo.
    """

    class Meta:
        db_table = "Dashboard_Log"
        managed = False
        ordering = ["-DataHora_Inicio"]
        verbose_name = "Dashboard Log"
        verbose_name_plural = "Dashboard Logs"

    Dashboard = models.ForeignKey(
        Dashboard, on_delete=models.CASCADE, verbose_name="Dashboard"
    )
    DataHora_Inicio = models.DateTimeField(
        auto_now_add=True, verbose_name="Data/Hora Início"
    )
    DataHora_Fim = models.DateTimeField(
        null=True, blank=True, verbose_name="Data/Hora Fim"
    )
    Duracao_Exibida = models.IntegerField(
        null=True, blank=True, verbose_name="Duração Exibida (segundos)"
    )
    Tipo_Transicao = models.CharField(
        max_length=20,
        choices=[
            ("automatica", "Automática"),
            ("manual", "Manual"),
            ("pausa", "Pausado"),
        ],
        default="automatica",
        verbose_name="Tipo de Transição",
    )

    def __str__(self):
        return f"{self.Dashboard.Nome} - {self.DataHora_Inicio.strftime('%d/%m/%Y %H:%M:%S')}"


class Vendas(models.Model):
    """
    Modelo para acessar vendas do sistema.
    Tabela existente no banco de dados (não gera migração).
    """

    class Meta:
        db_table = "Vendas"
        managed = False
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"

    id = models.BigAutoField(primary_key=True)
    id_gestao = models.BigIntegerField(db_column="ID_Gestao")
    codigo = models.CharField(db_column="Codigo", max_length=100)
    clientenome = models.CharField(db_column="ClienteNome", max_length=100)
    vendedornome = models.CharField(db_column="VendedorNome", max_length=100)
    data = models.DateField(db_column="Data")
    prazoentrega = models.DateField(db_column="PrazoEntrega", null=True, blank=True)
    situacaonome = models.CharField(db_column="SituacaoNome", max_length=100)
    nomecanalvenda = models.CharField(db_column="NomeCanalVenda", max_length=100)
    condicaopagamento = models.CharField(db_column="CondicaoPagamento", max_length=100)
    valorcusto = models.DecimalField(
        db_column="ValorCusto", max_digits=15, decimal_places=2
    )
    valorprodutos = models.DecimalField(
        db_column="ValorProdutos", max_digits=15, decimal_places=2
    )
    valordesconto = models.DecimalField(
        db_column="ValorDesconto", max_digits=15, decimal_places=2
    )
    valortotal = models.DecimalField(
        db_column="ValorTotal", max_digits=15, decimal_places=2
    )
    origem = models.CharField(db_column="Origem", max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.codigo} - {self.clientenome}"


class Vendedores(models.Model):
    """
    Modelo para acessar vendedores do sistema.
    Tabela existente no banco de dados (não gera migração).
    """

    class Meta:
        db_table = "Vendedores"
        managed = False
        verbose_name = "Vendedor"
        verbose_name_plural = "Vendedores"

    nome = models.CharField(db_column="Nome", max_length=100, primary_key=True)
    curto = models.CharField(db_column="Curto", max_length=50, blank=True, null=True)
    percentual = models.IntegerField(db_column="Percentual", blank=True, null=True)

    def __str__(self):
        return self.nome


class Produtos(models.Model):
    """
    Modelo para acessar produtos do sistema.
    Tabela existente no banco de dados (não gera migração).
    """

    class Meta:
        db_table = "Produtos"
        managed = False
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    id_gestao = models.CharField(
        db_column="ID_Gestao", max_length=100, blank=True, null=True
    )
    id_loja = models.CharField(
        db_column="ID_Loja", max_length=10, blank=True, null=True
    )
    nome = models.CharField(db_column="Nome", max_length=200, blank=True, null=True)
    descricao = models.CharField(
        db_column="Descricao", max_length=200, blank=True, null=True
    )
    codigointerno = models.CharField(
        db_column="CodigoInterno", max_length=100, blank=True, null=True
    )
    codigobarra = models.CharField(
        db_column="CodigoBarra", max_length=100, blank=True, null=True
    )
    valorvenda = models.DecimalField(
        db_column="ValorVenda", max_digits=15, decimal_places=2, blank=True, null=True
    )
    valorcusto = models.DecimalField(
        db_column="ValorCusto", max_digits=15, decimal_places=2, blank=True, null=True
    )

    def __str__(self):
        return self.nome if self.nome else "Produto sem nome"


class VendasSituacao(models.Model):
    """
    Modelo para acessar situações de vendas do sistema.
    Tabela existente no banco de dados (não gera migração).
    """

    class Meta:
        db_table = "VendasSituacao"
        managed = False
        verbose_name = "Venda Situação"
        verbose_name_plural = "Vendas Situações"

    situacaonome = models.CharField(
        db_column="SituacaoNome", max_length=100, blank=True, null=True
    )

    def __str__(self):
        return self.situacaonome if self.situacaonome else "Situação"


class VendaProdutos(models.Model):
    """
    Modelo para acessar produtos vendidos.
    Tabela existente no banco de dados (não gera migração).
    """

    class Meta:
        db_table = "VendaProdutos"
        managed = False
        verbose_name = "Venda Produto"
        verbose_name_plural = "Venda Produtos"

    id = models.BigAutoField(primary_key=True)
    venda_id = models.BigIntegerField(db_column="Venda_ID")
    nome = models.TextField(db_column="Nome")
    detalhes = models.TextField(db_column="Detalhes", blank=True, null=True)
    quantidade = models.IntegerField(db_column="Quantidade")
    valorcusto = models.DecimalField(
        db_column="ValorCusto", max_digits=15, decimal_places=2
    )
    valorvenda = models.DecimalField(
        db_column="ValorVenda", max_digits=15, decimal_places=2
    )
    valordesconto = models.DecimalField(
        db_column="ValorDesconto", max_digits=15, decimal_places=2
    )
    valortotal = models.DecimalField(
        db_column="ValorTotal", max_digits=15, decimal_places=2
    )
    codigoexpedicao = models.CharField(
        db_column="CodigoExpedicao", max_length=100, null=True, blank=True
    )

    def __str__(self):
        return f"{self.nome} (Venda {self.venda_id})"
