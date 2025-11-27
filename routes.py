import json
from datetime import datetime

import requests

base_url = "http://10.135.232.47:5002"


# LOGIN
def post_login(email, senha):
    url = f"{base_url}/login"
    try:
        # Verifica se os campos estão preenchidos
        if not email or not senha:
            return None, None, None, "Email e senha são obrigatórios"

        response = requests.post(
            url,
            json={'email': email, 'senha': senha},
            timeout=10  # Timeout de 10 segundos
        )

        # Tratamento dos códigos de status
        if response.status_code == 200:
            dados = response.json()
            print(f"Dados retornados: {dados}")  # Adicione este print para depuração
            token = dados.get('access_token')
            papel = dados.get('papel')
            nome = dados.get('nome')  # Captura o nome

            # Verifica se o nome está presente
            if nome is None:
                print("Nome não encontrado na resposta da API.")
                nome = "Nome não disponível"  # Ou qualquer valor padrão que você queira

            return token, papel, nome, None
        elif response.status_code == 401:
            return None, None, None, "Email ou senha incorretos"
        elif response.status_code == 400:
            return None, None, None, "Credenciais inválidas"
        else:
            return None, None, None, f"Erro no servidor: {response.status_code}"

    except requests.exceptions.RequestException as e:
        return None, None, None, f"Erro de conexão: {str(e)}"
    except Exception as e:
        return None, None, None, f"Erro inesperado: {str(e)}"


def post_pessoas(nome_pessoa, cpf, papel, senha, salario, email, status_pessoa):
    url = f"{base_url}/cadastro_pessoas_login"
    nova_pessoa = {
        'nome_pessoa': nome_pessoa,
        'cpf': cpf,
        'papel': papel,  # O papel pode ser 'Admin' ou 'usuario', conforme a API
        'senha': senha,
        'salario': salario,
        'status_pessoa': status_pessoa,
        'email': email,
    }

    try:
        response = requests.post(url, json=nova_pessoa)

        if response.status_code == 201:
            return response.json(), None  # Cadastro bem-sucedido
        else:
            return None, response.json().get('msg', 'Erro desconhecido')  # Mensagem de erro da API
    except requests.exceptions.RequestException as e:
        return None, f'Erro de conexão: {str(e)}'


def cadastrar_lanche_post(novo_lanche):
    url = f"{base_url}/lanches"

    response = requests.post(url, json=novo_lanche)
    print(response.json())
    if response.status_code == 201:
        dados_post_lanche = response.json()

        print(f'Nome Lanche: {dados_post_lanche["nome_lanche"]}\n'
              f'Valor: {dados_post_lanche["valor"]}\n'
              f'Descrição: {dados_post_lanche["descricao"]}\n')
    else:
        print(f'Erro: {response.status_code}')


def listar_lanche(token):
    url = f'{base_url}/lanches'
    response = requests.get(url, headers={'Authorization': f'Bearer {token}'})

    if response.status_code == 200:
        dados_get_lanche = response.json()
        print(dados_get_lanche)
        return dados_get_lanche['lanches']
    else:
        print(f'Erro: {response.status_code}')
        return response.json()


# listar_lanche()

def listar_pedidos(token):
    url = f'{base_url}/pedidos'
    response = requests.get(url, headers={'Authorization': f'Bearer {token}'})

    if response.status_code == 200:
        dados_get_pedidos_ = response.json()
        print(dados_get_pedidos_)
        return dados_get_pedidos_
    else:
        print(f'Erro: {response.status_code}')
        return response.json()


def listar_bebidas(token):
    url = f'{base_url}/bebidas'
    response = requests.get(url, headers={'Authorization': f'Bearer {token}'})

    if response.status_code == 200:
        dados_get_bebidas = response.json()
        print(dados_get_bebidas)
        return dados_get_bebidas['bebidas']
    else:
        print(f'Erro: {response.status_code}')
        return response.json()


def listar_pessoas():
    url = f'{base_url}/pessoas'
    response = requests.get(url)

    if response.status_code == 200:
        dados_get_pessoa = response.json()
        print(dados_get_pessoa)
        return dados_get_pessoa['pessoas']
    else:
        print(f'Erro: {response.status_code}')
        return response.json()


# def cadastrar_pedido_app(id_lanche, id_bebida, qtd_lanche, detalhamento, numero_mesa, observacoes, id_pessoa):
#     url = f"{base_url}/pedidos"
#
#     payload = {
#         "data_pedido": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "numero_mesa": numero_mesa,
#         "id_pessoa": id_pessoa,
#         "qtd_lanche": qtd_lanche,
#         "detalhamento": detalhamento,
#         "observacoes": observacoes if observacoes else {"adicionar": [], "remover": []},
#     }
#
#     if id_lanche is not None:
#         payload["id_lanche"] = int(id_lanche)
#     if id_bebida is not None:
#         payload["id_bebida"] = int(id_bebida)
#
#     print("DEBUG payload enviar pedido:", json.dumps(payload, indent=2, ensure_ascii=False))  # 👈 ADICIONE ISSO
#
#     try:
#         response = requests.post(url, json=payload)
#         if response.status_code != 201:
#             print("DEBUG cadastrar_pedido_app:", response.status_code, response.text)
#             return {"error": response.text}
#         return response.json()
#     except Exception as e:
#         print("ERRO cadastrar_pedido_app:", str(e))
#         return {"error": str(e)}


def cadastrar_pedido_app(id_lanche, id_bebida, qtd_lanche, detalhamento, numero_mesa, observacoes, id_pessoa):
    url = f"{base_url}/pedidos"

    #  Trata número da mesa / delivery
    if isinstance(numero_mesa, str) and numero_mesa.strip().lower() == "delivery":
        numero_mesa_val = "delivery"
    else:
        try:
            numero_mesa_val = int(numero_mesa)
        except (ValueError, TypeError):
            print(f"⚠️ numero_mesa inválido: {numero_mesa}, usando 0")
            numero_mesa_val = 0  # fallback seguro

    # Monta o payload base
    payload = {
        "data_pedido": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "numero_mesa": numero_mesa_val,
        "id_pessoa": int(id_pessoa),
        "qtd_lanche": int(qtd_lanche),
        "detalhamento": detalhamento or "",
        "observacoes": observacoes if observacoes else {"adicionar": [], "remover": []},
    }

    #  Adiciona lanche se existir
    if id_lanche not in [None, "", 0, "0"]:
        try:
            payload["id_lanche"] = int(id_lanche)
        except Exception:
            print(f"id_lanche inválido: {id_lanche}")

    #  Adiciona bebida se existir
    if id_bebida not in [None, "", 0, "0"]:
        try:
            payload["id_bebida"] = int(id_bebida)
        except Exception:
            print(f"id_bebida inválido: {id_bebida}")

    # Se não tiver lanche nem bebida, não envia
    if "id_lanche" not in payload and "id_bebida" not in payload:
        return {"error": "É necessário informar pelo menos um lanche ou uma bebida"}

    # Faz a requisição
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 201:
            print("DEBUG cadastrar_pedido_app:", response.status_code, response.text)
            return {"error": response.text}

        return response.json()

    except Exception as e:
        print("ERRO cadastrar_pedido_app:", str(e))
        return {"error": str(e)}



def cadastrar_venda_app(lanche_id, pessoa_id, bebida_id, qtd_lanche, forma_pagamento, endereco, detalhamento, observacoes=None,
                        valor_venda=0.0):
    url = f"{base_url}/vendas"  # rota da API

    payload = {
        "data_venda": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "lanche_id": lanche_id if lanche_id else None,
        "pessoa_id": pessoa_id,
        "bebida_id": bebida_id if bebida_id else None,
        "qtd_lanche": qtd_lanche,
        "detalhamento": detalhamento,
        "endereco": endereco,
        "forma_pagamento": forma_pagamento,
        "observacoes": observacoes if observacoes else {"adicionar": [], "remover": []},
        "valor_venda": valor_venda,
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code != 201:
            print("DEBUG cadastrar_venda_app:", response.status_code, response.text)
            return {"error": response.text}
        return response.json()
    except Exception as e:
        print("ERRO cadastrar_venda_app:", str(e))
        return {"error": str(e)}


def get_insumo(id_insumo):
    url = f"{base_url}/get_insumo_id/{id_insumo}"
    response = requests.get(url)

    if response.status_code == 200:
        dados_get_postagem = response.json()
        print(dados_get_postagem)
        return dados_get_postagem
    else:
        print(f'Erro: {response.status_code}')
        return response.json()


def update_insumo(id_insumo):
    url = f"{base_url}/update_insumo/{id_insumo}"
    response = requests.put(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f'Erro: {response.status_code}')
        return response.json()


def update_bebida(id_bebida):
    url = f"{base_url}/update_bebida/{id_bebida}"
    response = requests.put(url)

    if response.status_code == 200:
        return response.json()
    else:
        print(f'Erro9: {response.status_code}')
        return response.json()


def listar_insumos(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{base_url}/insumos", headers=headers)
        data = response.json()
        if "insumos" in data:
            return data["insumos"]
        else:
            print("Erro ao listar insumos:", data)
            return []
    except Exception as e:
        print("Erro de conexão:", e)
        return []


# Função global
# Função global
def listar_receita_lanche(lanche_id):
    """
    Retorna a receita base de um lanche: {insumo_id: quantidade_base}
    """
    try:
        # Consulta os insumos que fazem parte do lanche
        response = requests.get(f"{base_url}/lanche_receita/{lanche_id}")  # crie esta rota se não existir

        if response.status_code == 200:
            dados = response.json()
            receita_lista = dados["receita"]
            receita = {item["insumo_id"]: item["quantidade_base"] // 100 for item in receita_lista}
            return receita

        else:
            print(f"Erro ao buscar receita: {response.status_code}")
            return {}

    except Exception as e:
        print(f"Erro de conexão ao buscar receita: {e}")
        return {}

def carregar_receita_base(lanche_id):
    try:
        print("lanche_id: ", lanche_id)
        dados_receita = listar_receita_lanche(lanche_id) or {}
        print("dados_receita: ", dados_receita)
        receita = {}
        for ing_id, qtd in dados_receita.items():
            ing_id, qtd = int(ing_id), int(qtd)
            if ing_id > 0:
                receita[ing_id] = qtd
        return receita
    except Exception as e:
        print("Erro ao buscar receita:", e)
        return {}


def listar_vendas_mesa(token, numero_mesa):
    url = f"{base_url}/vendas_garcom/{numero_mesa}"
    response = requests.get(url, headers={'Authorization': f'Bearer {token}'})
    if response.status_code == 200:
        return response.json().get("vendas", [])
    else:
        print("Erro ao buscar pedidos da mesa:", response.text)
        return []