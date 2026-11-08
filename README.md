# API Para Gerenciamento de Produtos e Vendas

API REST desenvolvida com Django REST Framework para o gerenciamento de produtos e vendas. O projeto permite administrar o estoque de produtos, registrar vendas e consultar os registros por meio de endpoints HTTP.

## Funcionalidades

### Produtos
- Cadastro de produto;
- Listagem de produtos;
- Consulta de produto;
- Atualização de produto;
- Exclusão de produto.

### Vendas
- Registro de venda;
- Listagem de vendas;
- Consulta de venda.

## Requisitos

Para executar o projeto, é necessário ter instalado:

- Python 3.10 ou versão mais recente;
- Pip 22.0 ou versão mais recente;
- Virtualenv 20.19 ou versão mais recente.

## Como executar o projeto

**Passo 1 – Criar um ambiente virtual Python**

```bash
python3 -m venv venv
```

**Passo 2 – Ativar o ambiente virtual**

```bash
. venv/bin/activate
```

**Passo 3 – Instalar as dependências**

```bash
pip install -r requirements.txt
```

**Passo 4 – Executar o servidor interno**

```bash
python manage.py runserver
```

Após iniciar o servidor, a API estará disponível em:

`http://127.0.0.1:8000/`

## Tecnologias utilizadas

- Python
- Django
- Django REST Framework
- SQLite