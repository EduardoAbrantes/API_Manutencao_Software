from django.db import models
from django.core.validators import MinValueValidator

class Produto(models.Model):
    nome = models.CharField(max_length=150)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    quantidade_estoque = models.PositiveIntegerField()

    def __str__(self):
        return self.nome