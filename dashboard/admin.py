from django.contrib import admin

from .models import (
    Dashboard,
    Dashboard_Config,
    Dashboard_Log,
    Produtos,
    ControleAtualizacao,
    VendaProdutos,
    Vendas,
    VendasSituacao,
    Vendedores,
)


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    """
    Administração do modelo Dashboard.
    """

    list_display = ('Nome', 'Descricao', 'Ativo')
    list_filter = ('Ativo',)
    search_fields = ('Nome', 'Descricao')
    list_editable = ('Ativo',)
    ordering = ('Nome',)


@admin.register(Dashboard_Config)
class DashboardConfigAdmin(admin.ModelAdmin):
    """
    Administração do modelo Dashboard_Config.
    Configuração da ordem e duração de exibição dos dashboards.
    """

    list_display = ('Ordem', 'Dashboard', 'Duracao', 'dashboard_ativo')
    list_filter = ('Dashboard__Ativo',)
    search_fields = ('Dashboard__Nome',)
    ordering = ('Ordem',)

    def dashboard_ativo(self, obj):
        """Exibe se o dashboard associado está ativo."""
        return obj.Dashboard.Ativo

    dashboard_ativo.boolean = True
    dashboard_ativo.short_description = 'Dashboard Ativo'


@admin.register(Dashboard_Log)
class DashboardLogAdmin(admin.ModelAdmin):
    """
    Administração do modelo Dashboard_Log.
    Exibe logs de exibição dos dashboards para auditoria.
    """

    list_display = (
        'Dashboard',
        'DataHora_Inicio',
        'DataHora_Fim',
        'Duracao_Exibida',
        'Tipo_Transicao',
    )
    list_filter = ('Dashboard', 'Tipo_Transicao', 'DataHora_Inicio')
    search_fields = ('Dashboard__Nome',)
    ordering = ('-DataHora_Inicio',)
    readonly_fields = (
        'Dashboard',
        'DataHora_Inicio',
        'DataHora_Fim',
        'Duracao_Exibida',
        'Tipo_Transicao',
    )

    def has_add_permission(self, request):
        """Desabilita a criação manual de logs."""
        return False

    def has_change_permission(self, request, obj=None):
        """Permite apenas visualização dos logs."""
        return False


@admin.register(Vendas)
class VendasAdmin(admin.ModelAdmin):
    """
    Administração do modelo Vendas (somente leitura).
    Tabela existente no banco de dados.
    """

    list_display = (
        'codigo',
        'clientenome',
        'vendedornome',
        'data',
        'situacaonome',
        'valortotal',
    )
    list_filter = ('situacaonome', 'vendedornome', 'nomecanalvenda')
    search_fields = ('codigo', 'clientenome', 'vendedornome')
    ordering = ('-data',)
    readonly_fields = (
        'id_gestao',
        'codigo',
        'clientenome',
        'vendedornome',
        'data',
        'situacaonome',
        'nomecanalvenda',
        'condicaopagamento',
        'valorcusto',
        'valorprodutos',
        'valordesconto',
        'valortotal',
    )

    def has_add_permission(self, request):
        """Desabilita a criação manual."""
        return False

    def has_change_permission(self, request, obj=None):
        """Permite apenas visualização."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Desabilita exclusão."""
        return False


@admin.register(Vendedores)
class VendedoresAdmin(admin.ModelAdmin):
    """
    Administração do modelo Vendedores (somente leitura).
    Tabela existente no banco de dados.
    """

    list_display = ('nome',)
    search_fields = ('nome',)
    ordering = ('nome',)
    readonly_fields = ('nome',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Produtos)
class ProdutosAdmin(admin.ModelAdmin):
    """
    Administração do modelo Produtos (somente leitura).
    Tabela existente no banco de dados.
    """

    list_display = ('nome', 'codigointerno', 'valorvenda', 'valorcusto')
    search_fields = ('nome', 'codigointerno', 'codigobarra')
    ordering = ('nome',)
    readonly_fields = (
        'id_gestao',
        'id_loja',
        'nome',
        'descricao',
        'codigointerno',
        'codigobarra',
        'valorvenda',
        'valorcusto',
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(VendasSituacao)
class VendasSituacaoAdmin(admin.ModelAdmin):
    """
    Administração do modelo VendasSituacao (somente leitura).
    Tabela existente no banco de dados.
    """

    list_display = ('situacaonome',)
    search_fields = ('situacaonome',)
    readonly_fields = ('situacaonome',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(VendaProdutos)
class VendaProdutosAdmin(admin.ModelAdmin):
    """
    Administração do modelo VendaProdutos (somente leitura).
    Tabela existente no banco de dados.
    """

    list_display = ('venda_id', 'nome', 'quantidade', 'valorvenda', 'valortotal')
    search_fields = ('venda_id', 'nome')
    list_filter = ('venda_id',)
    ordering = ('-venda_id',)
    readonly_fields = (
        'venda_id',
        'nome',
        'detalhes',
        'quantidade',
        'valorcusto',
        'valorvenda',
        'valordesconto',
        'valortotal',
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ControleAtualizacao)
class ControleAtualizacaoAdmin(admin.ModelAdmin):
    """
    Administração do controle de atualização dos RPAs (somente leitura).
    """

    list_display = ('rpa_id', 'modo', 'periodo', 'fim', 'inseridos', 'atualizados')
    list_filter = ('rpa_id', 'modo')
    ordering = ('-fim',)

    def has_add_permission(self, request):
        """Desabilita a criação manual."""
        return False

    def has_change_permission(self, request, obj=None):
        """Permite apenas visualização."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Desabilita exclusão."""
        return False
