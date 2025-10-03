import requests

url = "http://10.135.235.49:5000"

def get_lanches(token_):
    base_url = f"{url}/lanches"
    response = requests.get(base_url, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def get_insumos(token_):
    base_url = f"{url}/insumos"
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

def get_categorias(token_):
    base_url = f"{url}/categorias"
    response = requests.get(base_url, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def get_entradas(token_):
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

def get_pessoas(token_):
    base_url = f"{url}/pessoas"
    response = requests.get(base_url, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

def get_insumo_by_id_insumo(id_insumo, token_):
    base_url = f"{url}/get_insumo_id/{id_insumo}"
    response = requests.get(base_url, headers={'Authorization': f'Bearer {token_}'})
    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}



def post_login(email, password):
    response = requests.post(f"{url}/login", json={"email": f"{email}", "senha": f"{password}"})
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(response.status_code)
        print(response.json())
        return {'erro':response.status_code}

print(get_insumos(post_login('vini@', '123')))
print(get_pessoas(post_login('l@', '123')))