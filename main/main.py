from flask import Flask, render_template, request, redirect, url_for, flash, session
import routes

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'


# def verificar_login():
    # if not session:
    #     flash('Você deve estar logado para visualizar esta página', 'error')
    #     return redirect(url_for('login'))


@app.route('/')
def index():
    session['funcao_rota_anterior'] = 'index'
    return render_template('inicio.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('senha')
        print(email, password, 'EMAILSENHA')
        user = routes.post_login(email, password)
        print(routes.get_id_pessoa_by_token(user['access_token'])['id_pessoa'])
        if 'access_token' in user:
            # print()
            # session['id'] = routes.get_id_pessoa_by_token(user['access_token'])['id_pessoa']
            session['token'] = user['access_token']
            session['username'] = user['nome']
            session['papel'] = user['papel']

            if session['papel'] == 'admin':
                flash('Bem vindo administrador', 'success')
                return redirect(url_for('pessoas'))  # pagina do admin
            elif session['papel'] == 'cozinha':
                flash('Bem vindo cozinheiro', 'success')
                return redirect(url_for('pessoas'))  # pagina da cozinha
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
@app.route('/pessoas/<valor_>', methods=['GET'])
def pessoas(valor_=None):
    if 'papel ' not in session:

        flash('Você deve entrar com uma conta para visualizar esta página', 'error')
        return redirect(url_for('login'))
    
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
def entradas():
    # noinspection PyInconsistentReturns
    if 'papel' not in session:
        flash('Você deve entrar com uma conta para visualizar esta página', 'error')
        return redirect(url_for('login'))
    if session['papel'] != 'admin':
        flash('Você deve ser um admin para visualizar esta página', 'info')
        return redirect(url_for(session['funcao_rota_anterior']))
        

    var_entradas = routes.get_entradas(session['token'])

    if 'entradas' not in var_entradas:
        flash('Parece que algo ocorreu errado :/', 'error')
        return redirect(url_for(session['funcao_rota_anterior']))

    session['funcao_rota_anterior'] = 'entradas'
    return render_template('entradas', entradas=var_entradas['entradas'])

@app.route('/lanches', methods=['GET'])
def lanches():
    if 'papel' not in session:
        flash('Você deve entrar com uma conta para visualizar esta página', 'error')
        return redirect(url_for('login'))

    var_lanches = routes.get_lanches(session['token'])

    if 'lanches' not in var_lanches:
        flash('Parece que algo ocorreu errado :/', 'error')

        return redirect(url_for(session['funcao_rota_anterior']))


    session['funcao_rota_anterior'] = 'lanches'
    return render_template('lanches.html', lanches=var_lanches['lanches'])

@app.route('/insumos', methods=['GET'])
@app.route('/insumos/<id_insumo>', methods=['GET'])
def insumos(id_insumo=None):
    try:
        if 'papel' not in session:
            flash('Você deve entrar com uma conta para visualizar esta página', 'error')
            return redirect(url_for(session['funcao_rota_anterior']))

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
    if 'papel' not in session:
        flash('Você deve entrar com uma conta para visualizar esta página', 'error')
        return redirect(url_for(session['funcao_rota_anterior']))
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
    if 'papel' not in session:
        flash('Você deve entrar com uma conta para visualizar esta página', 'error')
        return redirect(url_for(session['funcao_rota_anterior']))

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
    if 'papel' not in session:
        flash('Você deve entrar com uma conta para visualizar esta página', 'error')
        return redirect(url_for(session['funcao_rota_anterior']))

    if session['papel'] == "cliente":
        flash('Você não tem acesso, entre com uma conta autorizada', 'info')
        return redirect(url_for(session['funcao_rota_anterior']))

    var_vendas = routes.get_vendas(session['token'])

    if 'vendas' not in var_vendas:
        flash('Parece que algo ocorreu errado :/', 'error')
        return redirect(url_for(session['funcao_rota_anterior']))

    session['funcao_rota_anterior'] = 'vendas'
    return render_template('vendas.html', pedidos=var_vendas['pedidos'])
    # if session['papel'] == "cliente" or session['papel'] == "garcom"]:

# @app.route('/pedidos', methods=['GET'])
# def pedidos():
#     # verificar_login()
#
#     get_vendas = routes.get_vendas(session['token'])
#
#     return render_template('vendas.html', vendas=get_vendas['vendas'], papel=session['papel'])




if __name__ == '__main__':
    app.run(debug=True)