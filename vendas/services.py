from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from produtos.models import Produto
from .models import Venda, ProdutoVenda


@transaction.atomic
def registrar_venda(itens_data):
    ids = sorted(item['produto'].id for item in itens_data)

    produtos = {
        produto.id: produto
        for produto in Produto.objects.select_for_update()
        .filter(id__in=ids)
        .order_by('id')
    }

    erros = []

    # Verifica o estoque de todos os produtos antes de registrar a venda.
    for item in itens_data:
        produto = produtos[item['produto'].id]

        if item['quantidade'] > produto.quantidade_estoque:
            erros.append(
                f"Estoque insuficiente para o produto '{produto.nome}' "
                f"(id {produto.id}): solicitado {item['quantidade']}, "
                f"disponível {produto.quantidade_estoque}."
            )

    if erros:
        raise serializers.ValidationError({'itens': erros})

    venda = Venda.objects.create()
    valor_total = Decimal('0.00')

    for item in itens_data:
        produto = produtos[item['produto'].id]
        quantidade = item['quantidade']
        subtotal = produto.preco * quantidade

        ProdutoVenda.objects.create(
            venda=venda,
            produto=produto,
            quantidade=quantidade,
            preco_unidade=produto.preco,
            subtotal=subtotal,
        )

        produto.quantidade_estoque -= quantidade
        produto.save(update_fields=['quantidade_estoque'])

        valor_total += subtotal

    venda.valor_total = valor_total
    venda.save(update_fields=['valor_total'])

    return venda