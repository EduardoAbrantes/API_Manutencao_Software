from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from produtos.models import Produto
from .models import Venda, ProdutoVenda


class ProdutoVendaSerializer(serializers.ModelSerializer):
    produto = serializers.PrimaryKeyRelatedField(queryset=Produto.objects.all())
    quantidade = serializers.IntegerField(min_value=1)
    produto_nome = serializers.CharField(source='produto.nome', read_only=True)

    class Meta:
        model = ProdutoVenda
        fields = ['produto', 'produto_nome', 'quantidade', 'preco_unidade', 'subtotal']
        read_only_fields = ['preco_unidade', 'subtotal']


class VendaSerializer(serializers.ModelSerializer):
    itens = ProdutoVendaSerializer(many=True)

    class Meta:
        model = Venda
        fields = ['id', 'data_venda', 'valor_total', 'itens']
        read_only_fields = ['data_venda', 'valor_total']

    def validate_itens(self, itens):
        if not itens:
            raise serializers.ValidationError("A venda deve conter ao menos um produto.")

        ids = [item['produto'].id for item in itens]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                "Um mesmo produto não pode aparecer mais de uma vez na venda."
            )
        return itens

    @transaction.atomic
    def create(self, validated_data):
        itens_data = validated_data.pop('itens')

        # Relê os produtos com lock, em ordem de id, para checar e baixar o
        # estoque sem condição de corrida entre vendas simultâneas.
        ids = sorted(item['produto'].id for item in itens_data)
        produtos = {
            p.id: p for p in Produto.objects.select_for_update().filter(id__in=ids).order_by('id')
        }

        # RN-01: valida o estoque de todos os itens antes de gravar qualquer coisa.
        erros = []
        for item in itens_data:
            produto = produtos[item['produto'].id]
            if item['quantidade'] > produto.quantidade_estoque:
                erros.append(
                    f"Estoque insuficiente para o produto '{produto.nome}' (id {produto.id}): "
                    f"solicitado {item['quantidade']}, disponível {produto.quantidade_estoque}."
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
