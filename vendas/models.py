from django.db import models
from django.core.validators import MinValueValidator

from produtos.models import Produto


class Venda(models.Model):
    data_venda = models.DateTimeField(auto_now_add=True)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Venda {self.pk}"


class ProdutoVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name='vendas')
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    # Guardamos o preço no momento da venda, para o histórico não mudar
    # caso o preço do produto seja atualizado depois.
    preco_unidade = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade}x {self.produto} (venda {self.venda_id})"
