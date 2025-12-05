import requests

url = "http://10.135.232.23:5002"


def get_bebidas(token_):
    base_url = f"{url}/bebidas"
    response = requests.get(base_url, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro': response.status_code}

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
        print(response.json())
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
# original
def get_pessoa_by_id(token_, id_pessoa):
    response = requests.get(f"{url}/id_pessoa/{id_pessoa}", headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro': response.status_code}


def get_categoria_by_id_categoria(token_, id_categoria): # Feito
    base_url = f"{url}/categorias/categoria{id_categoria}"
    response = requests.get(base_url, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        print(response.json())
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def get_insumo_by_id_insumo(token_, id_insumo): # Feito
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
        return response.json().get("sucesso")
    else:
        print(response.status_code)
        print({'erro':response.json()})
        return {'erro':response.status_code}
# a = get_id_pessoa_by_token('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NDg4NzMyOCwianRpIjoiN2QwNGFmZmEtYzUwOC00NjllLTk4NWItYzNiNGI0MDhiOTE3IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImRAIiwibmJmIjoxNzY0ODg3MzI4LCJjc3JmIjoiMDE5NjczMmEtODE0Yi00MTllLTlhMjktOTAwMTA5NDM0YmQ4IiwiZXhwIjoxNzY0ODg4MjI4fQ.hcEh3jGtF3vssxcouVYTnMKQB5vHhaMJRqOpzl_zL3g')
# print(a)
########################
########################

# POST

def post_bebidas(token_, nome_bebida, valor, categoria_id, descricao):
    response = requests.post(f"{url}/bebidas", json={
        "nome_bebida":nome_bebida,
        "valor":valor,
        "id_categoria":categoria_id,
        'descricao':descricao
    }, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 201:
        return response.json()
    else:
        # print(response.status_code)
        # # print(response.json())
        # return {'erro':response.status_code}
        return 'erro'


def post_cadastro_pessoas(token_, nome, cpf, email, senha, salario, papel):
    response = requests.post(f"{url}/cadastro_pessoas_login", json={
        "email":email,
        "senha":senha,
        "nome_pessoa":nome,
        "cpf":cpf,
        "salario":salario,
        "papel":papel
    }, headers={'Authorization': f'Bearer {token_}'})
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

def post_entradas_insumos(token_, insumo_id, qtd_entrada, data_entrada, nota_fiscal, valor_entrada):
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

def post_entradas_bebidas(token_, bebida_id, qtd_entrada, data_entrada, nota_fiscal, valor_entrada):
    response = requests.post(f"{url}/entradas", json={
        "bebida_id":bebida_id,
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
    response = requests.post(
        f"{url}/lanche_insumos",
        json={"lanche_id": lanche_id, "insumo_id": insumo_id, "qtd_insumo": qtd_insumo},
        headers={'Authorization': f'Bearer {token_}'}
    )

    # sucesso
    if response.status_code == 201:
        return response.json()

    # erro → retorna a mensagem do backend
    try:
        return response.json()
    except:
        return {"error": f"Erro inesperado ({response.status_code})"}


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

def put_fechar_mesa(token_, numero_mesa):
    response = requests.put(f"{url}/pedidos/mesa", json={"numero_mesa": numero_mesa},
                            headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def put_editar_status_pedidos(token_, id_pedido, status_pedido):
    response = requests.put(f"{url}/pedidos/{id_pedido}", json={"status_pedido": status_pedido},
                            headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def put_editar_lanche(token_, id_lanche, nome_lanche, descricao_lanche, valor_lanche):
    response = requests.put(f"{url}/lanches/{id_lanche}", json={
        "nome_lanche":nome_lanche,
        "descricao_lanche":descricao_lanche,
        "valor_lanche":valor_lanche
    }, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def put_editar_insumo(token_, id_insumo, nome_insumo, categoria_id):
    response = requests.put(f"{url}/insumos/{id_insumo}", json={
        "nome_insumo":nome_insumo,
        "categoria_id":categoria_id,
    }, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def put_editar_categoria(token_, id_categoria, nome_categoria):
    response = requests.put(f"{url}/categorias/{id_categoria}", json={
        "nome_categoria":nome_categoria
    }, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def put_editar_pessoa(token_, id_pessoa, nome_pessoa, cpf, salario, papel, senha_hash, email, status):
    payload = {
        "nome_pessoa": nome_pessoa,
        "cpf": cpf,
        "salario": salario,
        "papel": papel,
        "senha_hash": senha_hash,
        "email": email,
        "status_pessoa": status
    }

    try:
        response = requests.put(f"{url}/pessoas/{id_pessoa}", json=payload,
                                headers={'Authorization': f'Bearer {token_}'})
    except Exception as e:
        print("Erro ao chamar API (requests.put):", e)
        return {"erro": "request_exception", "mensagem": str(e)}

    print("PUT /pessoas/{} -> status: {}".format(id_pessoa, response.status_code))
    print("Payload enviado:", payload)
    try:
        resp_json = response.json()
        print("Resposta JSON:", resp_json)
    except ValueError:
        resp_json = {"raw_text": response.text}
        print("Resposta (não-JSON):", response.text)

    if response.status_code == 200:
        return resp_json
    else:
        return {"erro": response.status_code, "resposta": resp_json}

def delete_lanche_insumo(token_, lanche_id, insumo_id):
    response = requests.delete(
        f"{url}/lanche_insumo",
        json={"lanche_id": lanche_id, "insumo_id": insumo_id},
        headers={'Authorization': f'Bearer {token_}'}
    )

    # deu bom
    if response.status_code == 200:
        return response.json()

    try:
        return response.json()
    except:
        return {"error": f"Erro inesperado ({response.status_code})"}




# def post_cadastrar_pedido(token_, nome_pedido, categoria_id):
#     response = requests.post(f"{url}/pedidos", json={})

# print(get_insumos(post_login('vini@', '123')))

# print(get_categorias(post_login("d@", "123")['access_token']))