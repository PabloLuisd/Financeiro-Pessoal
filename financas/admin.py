from django.contrib import admin
from .models import Categoria, Transacao, MetaFinanceira

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'usuario')
    list_filter = ('tipo',)
    search_fields = ('nome', 'usuario__username')

@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'tipo', 'valor', 'data', 'usuario', 'categoria')
    list_filter = ('tipo', 'data')
    search_fields = ('descricao', 'usuario__username')

@admin.register(MetaFinanceira)
class MetaFinanceiraAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'valor_atual', 'valor_objetivo', 'prazo')
    search_fields = ('titulo', 'usuario__username')
