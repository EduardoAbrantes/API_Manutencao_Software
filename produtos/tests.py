from rest_framework.test import APITestCase
from rest_framework import status
from .models import Produto
from decimal import Decimal

class ProdutoAPITest(APITestCase):

    url = "/api/produtos/"

    def test_cadastrar_produto_com_dados_validos(self):
        dados = {
            "nome": "Produto Teste",
            "descricao": "Descrição do Produto Teste",
            "preco": 9.99,
            "quantidade_estoque": 100
        }

        response = self.client.post(self.url, dados, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Produto.objects.count(), 1)

    def test_cadastrar_produto_com_preco_negativo(self):
        dados = {
            "nome": "Produto Teste",
            "descricao": "Descrição do Produto Teste",
            "preco": -5.00,
            "quantidade_estoque": 100
        }

        response = self.client.post(self.url, dados, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Produto.objects.count(), 0)

    def test_consultar_produto(self):
        produto = Produto.objects.create(
            nome="Produto Teste",
            descricao="Descrição do Produto Teste",
            preco=9.99,
            quantidade_estoque=100
        )

        url = f"{self.url}{produto.id}/"

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], produto.nome)

    def test_atualizar_produto(self):
        produto = Produto.objects.create(
            nome="Produto Teste",
            descricao="Descrição do Produto Teste",
            preco=9.99,
            quantidade_estoque=100
        )

        url = f"{self.url}{produto.id}/"
        
        dados_atualizados = {
            "nome": "Produto Atualizado",
            "descricao": "Descrição Atualizada",
            "preco": 19.99,
            "quantidade_estoque": 50
        }

        response = self.client.put(url, dados_atualizados, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        produto.refresh_from_db()
        self.assertEqual(produto.nome, "Produto Atualizado")
        self.assertEqual(produto.descricao, "Descrição Atualizada")
        self.assertEqual(produto.preco, Decimal('19.99'))
        self.assertEqual(produto.quantidade_estoque, 50)

    def test_excluir_produto(self):
        produto = Produto.objects.create(
            nome="Produto Teste",
            descricao="Descrição do Produto Teste",
            preco=9.99,
            quantidade_estoque=100
        )

        url = f"{self.url}{produto.id}/"

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Produto.objects.count(), 0)