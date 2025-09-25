from datetime import datetime

import requests

base_url = "http://10.135.235.23:5000"


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



def cadastrar_venda_app(lanche_id, pessoa_id, qtd_lanche, observacoes=None):
    url = f"{base_url}/vendas"

    nova_venda = {
        "data_venda": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "lanche_id": lanche_id,
        "pessoa_id": pessoa_id,
        "qtd_lanche": qtd_lanche,
        "observacoes": observacoes if observacoes else {"adicionar": [], "remover": []}
    }

    response = requests.post(url, json=nova_venda)

    if response.status_code == 201:
        return response.json()
    else:
        return {"error": response.json(), "status": response.status_code}