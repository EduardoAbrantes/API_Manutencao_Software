from rest_framework import serializers

from .services import registrar_venda

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

    def create(self, validated_data):
        return registrar_venda(validated_data['itens'])