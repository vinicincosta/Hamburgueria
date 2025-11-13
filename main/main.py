from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import routes

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'


# def verificar_login():
    # if not session:
    #     flash('Você deve estar logado para visualizar esta página', 'error')
    #     return redirect(url_for('login'))


@app.route('/')
def index():
    session['funcao_rota_anterior'] = 'login'
    return render_template('inicio.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('senha')
        print(email, password, 'EMAILSENHA')
        user = routes.post_login(email, password)
        # print(routes.get_id_pessoa_by_token(user['access_token'])['id_pessoa'])
        if 'access_token' in user:
            # print()
            # session['id'] = routes.get_id_pessoa_by_token(user['access_token'])['id_pessoa']
            session['token'] = user['access_token']
            session['username'] = user['nome']
            session['papel'] = user['papel']

            if session['papel'] == 'admin':
                flash('Bem vindo administrador', 'success')
                return redirect(url_for('index'))  # pagina do admin
            elif session['papel'] == 'cozinha':
                flash('Bem vindo cozinheiro', 'success')
                return redirect(url_for('index'))  # pagina da cozinha
            else:
                flash('Você não tem acesso a esse sistema', "error")
                print('flasssshhh')
                return redirect(url_for('login'))
                # return redirect(url_for('login'))
        else:
            # se não enviar email e senha é erro 400
            # se as credencias forem invalidas 401
            if user['erro'] == '401':
                flash('Verifique seu email e senha', 'error')
            else:
                flash('Parece que algo deu errado', 'error')

            return render_template('login.html')  # se der errado permanece na tela de login
            # e da um flash pra avisar o erro
    else:
        session['funcao_rota_anterior'] = 'login'
        return render_template('login.html')


@app.route('/logout')
def logout():
    try:
        session.clear()
        print(session, 'session')
        return redirect(url_for('login'))
    except Exception as e:
        print(e)
        return redirect(url_for('login'))


@app.route('/pessoas', methods=['GET'])
@app.route('/pessoas<valor_>', methods=['GET'])
def pessoas(valor_=None):
    # if 'token' not in session:
    #     flash('Você deve entrar com uma conta para visualizar esta página', 'error')
    #     return redirect(url_for('login'))
    retorno = verificar_token()
    if retorno:
        return retorno
    if session['papel'] != 'admin':
        flash('Parece que você não tem acesso a essa página, entre com uma conta que possua acesso', 'info')
        return redirect(url_for(session['funcao_rota_anterior']))
        

    var_pessoas = routes.get_pessoas(session['token'])

    if 'pessoas' not in var_pessoas:
        flash('Parece que algo ocorreu errado :/', 'error')
        return redirect(url_for(session['funcao_rota_anterior']))

    session['funcao_rota_anterior'] = 'pessoas'

    if valor_ is None:
        return render_template('pessoas.html', valor_=False, pessoas=var_pessoas['pessoas'])
    else:
        if valor_ in ['true', 'True', True, 1, '1']:
            booleano = True
        else:
            booleano = False
    # page = request.args.get("page", 1, type=int)
    # per_page = request.args.get("per_page", 10, type=int)
    return render_template('pessoas.html', valor_=not booleano, pessoas=var_pessoas['pessoas'])

@app.route('/entradas', methods=['GET'])
@app.route('/entradas<valor_>', methods=['GET'])
def entradas(valor_=None):
    # noinspection PyInconsistentReturns
    retorno = verificar_token()
    if retorno:
        return retorno
    if session['papel'] != 'admin':
        flash('Você deve ser um admin para visualizar esta página', 'info')
        return redirect(url_for(session['funcao_rota_anterior']))


    var_entradas = routes.get_entradas(session['token'])

    if 'entradas' not in var_entradas:
        flash('Parece que algo ocorreu errado :/', 'error')
        return redirect(url_for(session['funcao_rota_anterior']))

    session['funcao_rota_anterior'] = 'entradas'

    # return jsonify({"entradas": var_entradas['entradas']})
    if valor_ is None:
       return render_template('entradas.html', valor_=False, entradas=var_entradas['entradas'])
    else:
       if valor_ in ['true', 'True', True, 1, '1']:
           booleano = True
       else:
           booleano = False

    return render_template('entradas.html', entradas=var_entradas['entradas'], valor_=not booleano)

@app.route('/lanches', methods=['GET'])
def lanches():
    retorno = verificar_token()
    if retorno:
        return retorno
    var_lanches = routes.get_lanches(session['token'])

    if 'lanches' not in var_lanches:
        flash('Parece que algo ocorreu errado :/', 'error')

        return redirect(url_for(session['funcao_rota_anterior']))
    # return jsonify({'lanches': var_lanches['lanches']})
    form_id = request.args.get('form_id', None)
    print('form_id', form_id)
    valor_ = request.args.get('valor_', False)
    print('valor_', valor_)
    exibir = request.args.get('exibir', False)
    print('exibir', exibir)
    session['funcao_rota_anterior'] = 'lanches'
    if form_id is not None:
        if form_id == 'exibir':
            if not exibir or exibir ['False', 'false']:
                exibir = True
            else:
                exibir = False
        elif form_id == 'valor':
            if not valor_ or valor_ in ['false', 'False']:
                valor_ = False
            else:
                valor_ = True

    return render_template('lanches.html', lanches=var_lanches['lanches'], valor_=valor_, exibir=exibir)

@app.route('/insumos', methods=['GET'])
@app.route('/insumos/<id_insumo>', methods=['GET'])
def insumos(id_insumo=None):
    try:
        retorno = verificar_token()
        if retorno:
            return retorno
        if session['papel'] == "cliente" or session['papel'] == "garcom":
            flash('Você não tem acesso, entre com uma conta autorizada', 'info')
            return redirect(url_for(session['funcao_rota_anterior']))

        if session['papel'] == "cliente" or session['papel'] == "garcom":
            flash('Você não tem acesso, entre com uma conta autorizada', 'info')
            return redirect(url_for(session['funcao_rota_anterior']))

        if id_insumo is None:
            var_insumos = routes.get_insumos(session['token'])

        else:
            id_insumo = int(id_insumo)
            var_insumos = routes.get_insumo_by_id_insumo(id_insumo, session['token'])

        if 'insumos' not in var_insumos:
            flash('Parece que algo ocorreu errado :/', 'error')
            return redirect(url_for(session['funcao_rota_anterior']))

        session['funcao_rota_anterior'] = 'insumos'
        return render_template('insumos.html', lanches=var_insumos['insumos'])
    except ValueError:
        flash('Parece que algo ocorreu errado :/', 'error')
        return redirect(url_for(session['funcao_rota_anterior']))

@app.route('/categorias', methods=['GET'])
def categorias():
    retorno = verificar_token()
    if retorno:
        return retorno
    if session['papel'] == "cliente" or session['papel'] == "garcom":
        flash('Você não tem acesso, entre com uma conta autorizada', 'info')
        return redirect(url_for(session['funcao_rota_anterior']))
    var_categorias = routes.get_categorias(session['token'])

    if 'categorias' not in var_categorias:
        flash('Parece que algo ocorreu errado :/', 'error')
        return redirect(url_for(session['funcao_rota_anterior']))

    session['funcao_rota_anterior'] = 'categorias'
    return render_template('categorias.html', lanches=var_categorias['categorias'])

@app.route('/pedidos', methods=['GET'])
def pedidos():
    retorno = verificar_token()
    if retorno:
        return retorno
    if session['papel'] == "cliente":
        flash('Você não tem acesso, entre com uma conta autorizada', 'info')
        return redirect(url_for(session['funcao_rota_anterior']))

    var_pedidos = routes.get_pedidos(session['token'])
    if 'pedidos' not in var_pedidos:
        flash('Parece que algo ocorreu errado :/', 'error')
        return redirect(url_for(session['funcao_rota_anterior']))
    session['funcao_rota_anterior'] = 'pedidos'
    return render_template('pedidos.html', pedidos=var_pedidos['pedidos'])

@app.route('/vendas', methods=['GET'])
def vendas():
    retorno = verificar_token()
    if retorno:
        return retorno
    if session['papel'] == "cliente":
        flash('Você não tem acesso, entre com uma conta autorizada', 'info')
        return redirect(url_for(session['funcao_rota_anterior']))

    var_vendas = routes.get_vendas(session['token'])

    if 'vendas' not in var_vendas:
        flash('Parece que algo ocorreu errado :/', 'error')
        return redirect(url_for(session['funcao_rota_anterior']))

    session['funcao_rota_anterior'] = 'vendas'
    return render_template('vendas.html', pedidos=var_vendas['pedidos'])


@app.route('/pessoas/cadastrar', methods=['GET', 'POST'])
def cadastrar_pessoas():
    retorno = verificar_token()
    if retorno:
        return retorno
    if session['papel'] != "admin":
        flash('Você não tem acesso, entre com uma conta autorizada', 'info')
        return redirect(url_for(session['funcao_rota_anterior']))
    if request.method == 'POST':
        cpf = request.form['cpf']
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        salario = request.form['salario']
        papel = request.form['papel']

        cadastrar = routes.post_cadastro_pessoas(session['token'], nome, cpf, email, senha, salario, papel)
        if 'success' in cadastrar:
            flash('Pessoa adicionada com sucesso', 'success')
            return redirect(url_for('pessoas'))

        # Verificar na documentação possiveis erros para tratar
        return redirect(url_for('cadastrar_pessoas'))
    # if session['papel'] == "cliente" or session['papel'] == "garcom"]:
    else:
        session['funcao_rota_anterior'] = 'cadastrar_pessoas'
        return render_template('cadastrar_pessoa.html')

@app.route('/lanches/cadastrar', methods=['POST'])
def cadastrar_lanches():
    retorno = verificar_token()
    if retorno:
        return retorno
    if session['papel'] != "admin":
        flash('Você não tem acesso, entre com uma conta autorizada', 'info')
        return redirect(url_for(session['funcao_rota_anterior']))
    if request.method == 'POST':
        nome_lanche = request.form['nome_lanche']
        descricao_lanche = request.form['descricao_lanche']
        valor_lanche = request.form['valor_lanche']
        salvar_lanche = routes.post_lanches(session['token'], nome_lanche, descricao_lanche, valor_lanche)
        if 'success' in salvar_lanche:
            flash('Pessoa adicionada com sucesso', 'success')
            return redirect(url_for('pessoas'))

        # Verificar na documentação possiveis erros para tratar
        return redirect(url_for('cadastrar_pessoas'))
    else:
        session['funcao_rota_anterior'] = 'cadastrar_lanches'
        return render_template('cadastrar_lanches.html')

@app.route('/insumos/cadastrar', methods=['POST'])
def cadastrar_insumos():
    retorno = verificar_token()
    if retorno:
        return retorno
    if session['papel'] != "admin":
        flash('Você não tem acesso, entre com uma conta autorizada', 'info')
        return redirect(url_for(session['funcao_rota_anterior']))
    if request.method == 'POST':
        nome_insumo = request.form['nome_insumo']
        custo_insumo = request.form['custo_insumo']
        categoria_id = request.form['categoria_id']
        salvar_insumo = routes.post_insumos(session['token'], nome_insumo, custo_insumo, categoria_id)
        if 'success' in salvar_insumo:# 201
            flash('Insumo adicionada com sucesso', 'success')
            return redirect(url_for('insumos'))

        # Verificar na documentação possiveis erros para tratar
        return redirect(url_for('cadastrar_insumos'))
    else:
        session['funcao_rota_anterior'] = 'cadastrar_insumos'
        return render_template('cadastrar_insumo.html')


@app.route('/entradas/cadastrar_entradas', methods=['POST'])
def cadastrar_entradas():
    retorno = verificar_token()
    if retorno:
        return retorno
    if session['papel'] != "admin":
        flash('Você não tem acesso, entre com uma conta autorizada', 'info')
        return redirect(url_for(session['funcao_rota_anterior']))
    if request.method == 'POST':
        qtd_entrada = request.form['qtd_entradas']
        insumo_id = request.form['insumo_id']
        data_entrada = request.form['data_entrada']
        nota_fiscal = request.form['nota_fiscal']
        valor_entrada = request.form['valor_entrada']

        salvar_entrada = routes.post_entradas(session['token'], qtd_entrada, insumo_id, data_entrada, nota_fiscal, valor_entrada)
        if 'success' in salvar_entrada:
            flash('Entrada adicionada com sucesso', 'success')
            return redirect(url_for('entradas'))

        return redirect(url_for('cadastrar_entradas'))
    else:
        session['funcao_rota_anterior'] = 'cadastrar_entradas'
        return render_template('cadastrar_entradas.html')

@app.route('/categorias/cadastrar', methods=['POST'])
def cadastrar_categorias():
    retorno = verificar_token()
    if retorno:
        return retorno
    if session['papel'] != "admin":
        flash('Você não tem acesso, entre com uma conta autorizada', 'info')
        return redirect(url_for(session['funcao_rota_anterior']))
    if request.method == 'POST':
        nome_categoria = request.form['nome_categoria']
        salvar_categoria = routes.post_categorias(session['token'], nome_categoria)
        if 'success' in salvar_categoria:
            flash('Categoria adicionada com sucesso', 'success')
            return redirect(url_for('categorias'))
        return redirect(url_for('cadastrar_categorias'))
    else:
        session['funcao_rota_anterior'] = 'cadastrar_categorias'
        return render_template('cadastrar_categorias.html')

def verificar_token():
    if 'token' not in session:
        flash('Você deve entrar com uma conta para visualizar esta página', 'error')
        return redirect(url_for(session['funcao_rota_anterior']))
    return None


# @app.route('/pessoas/editar', methods=['GET'])
# def pessoas_editar():

# @app.route('/pedidos', methods=['GET'])
# def pedidos():
#     # verificar_login()
#
#     get_vendas = routes.get_vendas(session['token'])
#
#     return render_template('vendas.html', vendas=get_vendas['vendas'], papel=session['papel'])

if __name__ == '__main__':
    app.run(debug=True)