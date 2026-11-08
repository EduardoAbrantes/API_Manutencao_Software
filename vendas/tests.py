from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase

from produtos.models import Produto
from .models import Venda, ProdutoVenda


class VendaAPITest(APITestCase):

    url = "/api/vendas/"

    def setUp(self):
        self.produto_a = Produto.objects.create(
            nome="Produto A", descricao="Descrição A", preco=Decimal('10.00'), quantidade_estoque=10
        )
        self.produto_b = Produto.objects.create(
            nome="Produto B", descricao="Descrição B", preco=Decimal('2.50'), quantidade_estoque=4
        )

    def test_registrar_venda_calcula_totais_e_atualiza_estoque(self):
        dados = {"itens": [
            {"produto": self.produto_a.id, "quantidade": 3},
            {"produto": self.produto_b.id, "quantidade": 2},
        ]}

        response = self.client.post(self.url, dados, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Venda.objects.count(), 1)
        self.assertEqual(ProdutoVenda.objects.count(), 2)
        self.assertEqual(Decimal(response.data['valor_total']), Decimal('35.00'))

        subtotais = {i['produto']: Decimal(i['subtotal']) for i in response.data['itens']}
        self.assertEqual(subtotais[self.produto_a.id], Decimal('30.00'))
        self.assertEqual(subtotais[self.produto_b.id], Decimal('5.00'))

        self.produto_a.refresh_from_db()
        self.produto_b.refresh_from_db()
        self.assertEqual(self.produto_a.quantidade_estoque, 7)
        self.assertEqual(self.produto_b.quantidade_estoque, 2)

    def test_registrar_venda_com_quantidade_igual_ao_estoque(self):
        dados = {"itens": [{"produto": self.produto_b.id, "quantidade": 4}]}

        response = self.client.post(self.url, dados, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.produto_b.refresh_from_db()
        self.assertEqual(self.produto_b.quantidade_estoque, 0)

    def test_registrar_venda_com_estoque_insuficiente(self):
        dados = {"itens": [{"produto": self.produto_a.id, "quantidade": 11}]}

        response = self.client.post(self.url, dados, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Venda.objects.count(), 0)
        self.produto_a.refresh_from_db()
        self.assertEqual(self.produto_a.quantidade_estoque, 10)

    def test_estoque_insuficiente_em_um_item_nao_altera_nenhum_produto(self):
        dados = {"itens": [
            {"produto": self.produto_a.id, "quantidade": 3},
            {"produto": self.produto_b.id, "quantidade": 5},
        ]}

        response = self.client.post(self.url, dados, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Venda.objects.count(), 0)
        self.produto_a.refresh_from_db()
        self.produto_b.refresh_from_db()
        self.assertEqual(self.produto_a.quantidade_estoque, 10)
        self.assertEqual(self.produto_b.quantidade_estoque, 4)

    def test_registrar_venda_sem_itens(self):
        response = self.client.post(self.url, {"itens": []}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Venda.objects.count(), 0)

    def test_registrar_venda_com_quantidade_invalida(self):
        for quantidade in (0, -1):
            dados = {"itens": [{"produto": self.produto_a.id, "quantidade": quantidade}]}
            response = self.client.post(self.url, dados, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Venda.objects.count(), 0)

    def test_registrar_venda_com_produto_inexistente(self):
        dados = {"itens": [{"produto": 9999, "quantidade": 1}]}

        response = self.client.post(self.url, dados, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Venda.objects.count(), 0)

    def test_registrar_venda_com_produto_repetido(self):
        dados = {"itens": [
            {"produto": self.produto_a.id, "quantidade": 1},
            {"produto": self.produto_a.id, "quantidade": 1},
        ]}

        response = self.client.post(self.url, dados, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Venda.objects.count(), 0)

    def test_listar_vendas_com_seus_produtos(self):
        self.client.post(self.url, {"itens": [{"produto": self.produto_a.id, "quantidade": 1}]}, format='json')
        self.client.post(self.url, {"itens": [{"produto": self.produto_b.id, "quantidade": 2}]}, format='json')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['itens'][0]['produto'], self.produto_a.id)
        self.assertEqual(response.data[1]['itens'][0]['produto'], self.produto_b.id)

    def test_consultar_venda(self):
        criada = self.client.post(
            self.url, {"itens": [{"produto": self.produto_a.id, "quantidade": 2}]}, format='json'
        )

        response = self.client.get(f"{self.url}{criada.data['id']}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['valor_total']), Decimal('20.00'))
        self.assertEqual(len(response.data['itens']), 1)

    def test_consultar_venda_inexistente(self):
        response = self.client.get(f"{self.url}9999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_historico_mantem_preco_da_epoca_da_venda(self):
        criada = self.client.post(
            self.url, {"itens": [{"produto": self.produto_a.id, "quantidade": 1}]}, format='json'
        )
        self.produto_a.preco = Decimal('99.00')
        self.produto_a.save()

        response = self.client.get(f"{self.url}{criada.data['id']}/")

        self.assertEqual(Decimal(response.data['itens'][0]['preco_unidade']), Decimal('10.00'))
        self.assertEqual(Decimal(response.data['valor_total']), Decimal('10.00'))
