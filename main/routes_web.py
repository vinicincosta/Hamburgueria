import requests

# url = "http://10.135.233.139:5002"
url = "http://10.135.232.24:5002"
# url ="http://192.168.15.9:5002"


def get_lanches(token_): # Feito
    base_url = f"{url}/lanches"
    response = requests.get(base_url, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def get_insumos(token_): # Feito
    base_url = f"{url}/insumos"
    response = requests.get(base_url, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def get_pedidos(token_): # Feito
    base_url = f"{url}/pedidos"
    response = requests.get(base_url, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}


def get_receita(token_):
    base_url = f"{url}/vendas/receitas"
    response = requests.get(base_url, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def get_lanche_insumos(token_):
    base_url = f"{url}/lanche_insumos"
    response = requests.get(base_url, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def get_categorias(token_): # Feito
    base_url = f"{url}/categorias"
    response = requests.get(base_url, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def get_entradas(token_): # Feito
    base_url = f"{url}/entradas"
    response = requests.get(base_url, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def listar_vendas_by_id_mesa(id_mesa, token_):
    base_url = f"{url}/vendas/{id_mesa}"
    response = requests.get(base_url, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def get_vendas(token_):
    base_url = f"{url}/vendas"
    response = requests.get(base_url, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def get_pessoas(token_): # Feito
    base_url = f"{url}/pessoas"
    response = requests.get(base_url, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def get_insumo_by_id_insumo(id_insumo, token_): # Feito
    base_url = f"{url}/get_insumo_id/{id_insumo}"
    response = requests.get(base_url, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def get_id_pessoa_by_token(token_):
    response = requests.get(f"{url}/teste", headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        # print({'erro':response.json()})
        return {'erro':response.status_code}

########################
########################

# POST

def post_cadastro_pessoas(token_, nome, cpf, email, senha, salario, papel):
    response = requests.post(f"{url}/cadastro_pessoas_login", json={
        "email":email,
        "senha":senha,
        "nome_pessoa":nome,
        "cpf":cpf,
        "salario":salario,
        "papel":papel
    })#, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 201:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}


def post_lanches(token_, nome_lanche, descricao, valor):
    response = requests.post(f"{url}/lanches", json={
        "nome_lanche":nome_lanche,
        "descricao_lanche":descricao,
        "valor_lanche":valor,

    }, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 201:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def post_insumos(token_, nome_insumo, custo, categoria_id):
    response = requests.post(f"{url}/insumos", json={
        "nome_insumo":nome_insumo,
        "categoria_id":categoria_id,
        "custo": custo
    }, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 201:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def post_entradas(token_, insumo_id, qtd_entrada, data_entrada, nota_fiscal, valor_entrada):
    response = requests.post(f"{url}/entradas", json={
        "insumo_id":insumo_id,
        "qtd_entrada":qtd_entrada,
        "data_entrada":data_entrada,
        "nota_fiscal":nota_fiscal,
        "valor_entrada":valor_entrada
    }, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 201:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def post_lanche_insumos(token_, lanche_id, insumo_id, qtd_insumo):
    response = requests.post(f"{url}/lanche_insumos",
                             json={"lanche_id":lanche_id, "insumo_id":insumo_id, "qtd_insumo":qtd_insumo},
                             headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 201:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

# def post_vendas(token_, data_venda, lanche_id, pessoa_id, qtd_lanche, detalhamento):
#     response = requests.post(f"{url}/vendas", json={
#         "data_venda":data_venda,
#         "lanche_id":lanche_id,
#         "pessoa_id":pessoa_id,
#         "qtd_lanche":qtd_lanche,
#         "detalhamento":detalhamento
#     }, headers={'Authorization': f'Bearer {token_}'})
#     if response.status_code == 201:
#         return response.json()
#     else:
#         print(response.status_code)
#         print(response.json())
#         return {'erro':response.status_code}

def post_categorias(token_, nome_categoria):
    response = requests.post(f"{url}/categorias", json={"nome_categoria":nome_categoria}, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 201:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}


def post_login(email, password):
    response = requests.post(f"{url}/login", json={"email": email, "senha": password})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response)
        return {'erro':response.status_code}


########################################
########################################
# PUT


# def post_cadastrar_pedido(token_, nome_pedido, categoria_id):
#     response = requests.post(f"{url}/pedidos", json={})

# print(get_insumos(post_login('vini@', '123')))


    


# print(get_pedidos(post_login("d@", "123")['access_token']))