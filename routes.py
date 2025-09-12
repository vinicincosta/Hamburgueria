import requests

base_url = "http://10.135.235.29:5000"

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

def post_pessoas(nome, email, senha, papel, cpf, salario, token):
    try:
        url = f"{base_url}/pessoas"
        dados = {
            "nome": nome,
            "email": email,
            "senha": senha,
            "papel": papel,
            "cpf": cpf,
            "salario": salario,
        }
        response = requests.post(url, json=dados, headers={"Authorization": f"Bearer {token}"})
        return response.status_code
    except Exception as e:
        print(e)
        return {
            "error": f"{e}",
        }

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


def listar_lanche():
    url = f'{base_url}/lanches'
    response = requests.get(url)

    if response.status_code == 200:
        dados_get_lanche = response.json()
        print(dados_get_lanche)
        return dados_get_lanche['lanches']
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


listar_pessoas()