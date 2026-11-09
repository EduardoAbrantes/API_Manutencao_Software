from django.contrib import admin

from .models import Venda, ProdutoVenda


class ProdutoVendaInline(admin.TabularInline):
    model = ProdutoVenda
    extra = 0


@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'data_venda', 'valor_total')
    inlines = [ProdutoVendaInline]
