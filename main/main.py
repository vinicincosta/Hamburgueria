from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.routing import BuildError

import routes_web
import datetime
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'


def verificar_token():
    if 'token' not in session:
        flash('Você deve entrar com uma conta para visualizar esta página', 'error')
        return redirect(url_for(session['funcao_rota_anterior']))
    return None

@app.route('/')
def index():
    session['funcao_rota_anterior'] = 'login'
    return render_template('inicio.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('senha')
            print(email, password, 'EMAILSENHA')

            user = routes_web.post_login(email, password)

            if 'access_token' in user:

                session['user_id'] = routes_web.get_id_pessoa_by_token(user['access_token'])
                session['token'] = user['access_token']
                session['username'] = user['nome']
                session['papel'] = user['papel']
                print(session['user_id'])
                print(f'teste de erro{session['user_id']}')

                if session['papel'] == 'admin':
                    flash('Bem vindo administrador', 'success')
                    return redirect(url_for('faturamento'))
                elif session['papel'] == 'cozinha':
                    flash('Bem vindo cozinheiro', 'success')
                    return redirect(url_for('pedidos'))
                else:
                    flash('Você não tem acesso a esse sistema', "error")
                    return redirect(url_for('login'))

            else:
                # se não enviar email e senha é erro 400
                # se as credencias forem invalidas 401
                if user.get('erro') == '401':
                    flash('Verifique seu email e senha', 'error')
                else:
                    flash('Parece que algo deu errado', 'error')

                return render_template('login.html')

        except Exception as e:
            print("Erro no login:", e)
            flash("Erro inesperado ao tentar fazer login", "error")
            return render_template('login.html')

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
def pessoas():
    retorno = verificar_token()
    if retorno:
        return retorno
    if session['papel'] != 'admin':
        flash('Parece que você não tem acesso a essa página, entre com uma conta que possua acesso', 'info')
        return redirect(url_for(session['funcao_rota_anterior']))
    var_pessoas = routes_web.get_pessoas(session['token'])

    if 'pessoas' not in var_pessoas:
        flash('Parece que algo ocorreu errado :/', 'error')
        return redirect(url_for(session['funcao_rota_anterior']))

    session['funcao_rota_anterior'] = 'pessoas'
    form = request.args.get('form', None)
    exibir = request.args.get('exibir', False)
    if form is not None:
        if exibir in ['true', 'True', True, 1, '1']:
            exibir = False
        else:
            exibir = True
    # page = request.args.get("page", 1, type=int)
    # per_page = request.args.get("per_page", 10, type=int)
    return render_template('pessoas.html', exibir=exibir, pessoas=var_pessoas['pessoas'])

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


    var_entradas = routes_web.get_entradas(session['token'])

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
    var_lanches = routes_web.get_lanches(session['token'])

    if 'lanches' not in var_lanches:
        flash('Parece que algo ocorreu errado :/', 'error')

        return redirect(url_for(session['funcao_rota_anterior']))
    # return jsonify({'lanches': var_lanches['lanches']})
    form_id = request.args.get('form_id', None)
    valor_ = request.args.get('valor_', False)
    exibir = request.args.get('exibir', False)
    session['funcao_rota_anterior'] = 'lanches'
    if form_id is not None:
        if form_id == 'exibir':
            if not exibir or exibir in ['False', 'false']:
                exibir = True
            else:
                exibir = False
        elif form_id == 'valor':
            if not valor_ or valor_ in ['false', 'False']:
                valor_ = True
            else:
                valor_ = False

    return render_template('lanches.html', lanches=var_lanches['lanches'], valor_=valor_, exibir=exibir)

@app.route('/insumos', methods=['GET'])
#@app.route('/insumos/<id_insumo>', methods=['GET'])
def insumos():
    try:
        retorno = verificar_token()
        if retorno:
            return retorno

        if session['papel'] == "cliente" or session['papel'] == "garcom":
            flash('Você não tem acesso, entre com uma conta autorizada', 'info')
            return redirect(url_for(session['funcao_rota_anterior']))
        
        id_insumo = request.args.get('id_insumo', None)
        form = request.args.get('form', None)
        exibir_todos = request.args.get('exibir_todos', False)
        exibir_tabela = request.args.get('exibir_tabela', False)

        if id_insumo is None:
            var_insumos = routes_web.get_insumos(session['token'])

        else:
            #id_insumo = int(id_insumo)
            var_insumos = routes_web.get_insumo_by_id_insumo(int(id_insumo), session['token'])

        if 'insumos' not in var_insumos:
            flash('Parece que algo ocorreu errado :/', 'error')
            return redirect(url_for(session['funcao_rota_anterior']))
        if form is not None:
            if form == 'exibir_todos':
                if exibir_todos in ['False', False]:
                    exibir_todos = True
                else:
                    exibir_todos = False
            else:
                if exibir_tabela in ['False', False]:
                    exibir_tabela = True
                else:
                    exibir_tabela = False
                    

        session['funcao_rota_anterior'] = 'insumos'
        return render_template('insumos.html', insumos=var_insumos['insumos'], exibir_todos=exibir_todos, exibir_tabela=exibir_tabela)
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
    var_categorias = routes_web.get_categorias(session['token'])

    if 'categorias' not in var_categorias:
        flash('Parece que algo ocorreu errado :/', 'error')
        return redirect(url_for(session['funcao_rota_anterior']))
    exibir_tabela = request.args.get('exibir_tabela', False)
    session['funcao_rota_anterior'] = 'categorias'
    return render_template('categorias.html', lanches=var_categorias['categorias'], exibir_tabela=not exibir_tabela)

@app.route('/pedidos', methods=['GET'])
def pedidos():
    retorno = verificar_token()
    if retorno:
        return retorno
    if session['papel'] == "cliente":
        flash('Você não tem acesso, entre com uma conta autorizada', 'info')
        return redirect(url_for(session['funcao_rota_anterior']))

    var_pedidos = routes_web.get_pedidos(session['token'])
    if 'pedidos' not in var_pedidos:
        flash('Parece que algo ocorreu errado :/', 'error')
        return redirect(url_for(session['funcao_rota_anterior']))
    
    exibir_tabela = request.args.get('exibir_tabela', False)
    form = request.args.get('form', None)
    exibir_concluidos = request.args.get('exibir_concluidos', False)

    if form is not None:
        if form == 'exibir_tabela':
            if exibir_tabela in ['False', False]:
                exibir_tabela = True
            else:
                exibir_tabela = False
        else:
            if exibir_concluidos in ['False', False]:
                exibir_concluidos = True
            else:
                exibir_concluidos = False

    session['funcao_rota_anterior'] = 'pedidos'
    print(f'teste do bagui{var_pedidos['pedidos']}')
    return render_template('pedidos.html', pedidos=var_pedidos['pedidos'], exibir_tabela=exibir_tabela, exibir_concluidos=exibir_concluidos)

@app.route('/bebidas', methods=['GET', 'POST'])
def bebidas():
    retorno = verificar_token()
    if retorno:
        return retorno
    if session['papel'] == "cliente":
        flash('Você não tem acesso, entre com uma conta autorizada', 'info')
        return redirect(url_for(session['funcao_rota_anterior']))

    var_bebidas = routes_web.get_bebidas(session['token'])
    if 'bebidas' not in var_bebidas:
        flash('Parece que algo ocorreu errado :/1', 'error')
        return redirect(url_for(session['funcao_rota_anterior']))
    
    exibir_tabela = request.args.get('exibir_tabela', False)
    form = request.args.get('form', None)
    exibir_todos = request.args.get('exibir_todos', False)

    if form is not None:
        if form == 'exibir_tabela':
            if exibir_tabela in ['False', False]:
                exibir_tabela = True
            else:
                exibir_tabela = False
        else:
            if exibir_todos in ['False', False]:
                exibir_todos = True
            else:
                exibir_todos = False
    categorias = routes_web.get_categorias(session['token'])
    if 'categorias' in categorias:
        session['funcao_rota_anterior'] = 'bebidas'
        return render_template('bebidas.html', bebidas=var_bebidas['bebidas'], exibir_tabela=exibir_tabela, exibir_todos=exibir_todos, categorias=categorias['categorias'])
    flash('Parece que algo ocorreu errado :/', 'error')
    return redirect(url_for('bebidas'))

@app.route('/vendas', methods=['GET'])
def vendas():
    retorno = verificar_token()
    if retorno:
        return retorno

    if session['papel'] == "cliente":
        flash('Você não tem acesso, entre com uma conta autorizada', 'info')
        return redirect(url_for(session['funcao_rota_anterior']))

    # ===== PAGINAÇÃO =====
    page = request.args.get("page", 1, type=int)  # página atual
    per_page = 12                                 # quantidade por página

    var_vendas = routes_web.get_vendas(session['token'])

    data_hoje = datetime.date.today()

    if 'vendas' not in var_vendas:
        flash('Parece que algo ocorreu errado :/', 'error')
        return redirect(url_for(session['funcao_rota_anterior']))

    # Lista completa recebida da API
    vendas = var_vendas['vendas']

    # Total de itens
    total = len(vendas)

    # Cálculo do intervalo
    start = (page - 1) * per_page
    end = start + per_page

    # Fatia apenas os itens da página atual
    vendas_pagina = vendas[start:end]

    # Flags para botões do template
    has_prev = page > 1
    has_next = end < total

    session['funcao_rota_anterior'] = 'vendas'

    return render_template(
        'vendas.html',
        vendas=vendas_pagina,
        data_de_hoje=data_hoje,
        page=page,
        has_prev=has_prev,
        has_next=has_next
    )

@app.route('/lanche_insumos', methods=['GET'])
def lanche_insumos():
    try:
        retorno = verificar_token()
        if retorno:
            return retorno

        if session['papel'] in ["cliente", "garcom"]:
            flash('Você não tem acesso, entre com uma conta autorizada', 'info')
            return redirect(url_for(session['funcao_rota_anterior']))

        form = request.args.get('form', None)
        exibir_tabela = request.args.get('exibir_tabela', False)

        # Pega dados principais
        lista_lanches = routes_web.get_lanches(session['token'])['lanches']
        lista_insumos = routes_web.get_insumos(session['token'])['insumos']
        lista_relacao = routes_web.get_lanche_insumos(session['token'])['lanche_insumos']

        # Dicionários de lookup
        dict_lanches = {l['id_lanche']: l['nome_lanche'] for l in lista_lanches}
        dict_insumos = {i['id_insumo']: i['nome_insumo'] for i in lista_insumos}

        # Adiciona nomes na relação
        for item in lista_relacao:
            item['lanche_nome'] = dict_lanches.get(item['lanche_id'], "Desconhecido")
            item['insumo_nome'] = dict_insumos.get(item['insumo_id'], "Desconhecido")

        # Controle dos filtros
        if form is not None:
            if form == 'exibir_tabela':
                exibir_tabela = not (exibir_tabela in ['True', True])

        # Lógica de paginação
        page = int(request.args.get('page', 1))  # Página atual (padrão: 1)
        per_page = 5  # Itens por página (ajuste conforme necessário)
        total_items = len(lista_relacao)
        total_pages = (total_items + per_page - 1) // per_page  # Calcula total de páginas

        # Garante que a página esteja dentro dos limites
        if page < 1:
            page = 1
        if page > total_pages and total_pages > 0:
            page = total_pages

        # Fatia a lista para a página atual
        start = (page - 1) * per_page
        end = start + per_page
        lista_relacao_paginada = lista_relacao[start:end]
        print("pagina: ",page)

        session['funcao_rota_anterior'] = 'lanche_insumos'

        return render_template(
            'lanche_insumos.html',
            lanche_insumos=lista_relacao_paginada,  # Agora usa a lista paginada
            exibir_tabela=exibir_tabela,
            page=page,
            total_pages=total_pages,
            per_page=per_page
        )

    except ValueError:
        flash('Parece que algo ocorreu errado :/', 'error')
        return redirect(url_for(session['funcao_rota_anterior']))

@app.route('/deletar_lanche_insumo/<int:lanche_id>/<int:insumo_id>', methods=['POST'])
def deletar_lanche_insumo(lanche_id, insumo_id):
    retorno = verificar_token()
    if retorno:
        return retorno

    resultado = routes_web.delete_lanche_insumo(session['token'], lanche_id, insumo_id)

    if not resultado or "error" in resultado:
        flash(resultado.get("error", "Erro ao deletar relação!"), "error")
    else:
        flash("Relação deletada com sucesso!", "success")

    return redirect(url_for('lanche_insumos'))


@app.route('/lanche_insumos/cadastrar', methods=['GET','POST'])
def cadastrar_lanche_insumos():
    retorno = verificar_token()
    if retorno:
        return retorno

    if session['papel'] != "admin":
        flash('Você não tem acesso, entre com uma conta autorizada', 'info')
        return redirect(url_for(session['funcao_rota_anterior']))

    if request.method == 'POST':
        lanche_id = request.form['lanche_id']
        insumo_id = request.form['insumo_id']
        qtd_insumo = request.form['qtd_insumo']

        salvar_lanche_insumo = routes_web.post_lanche_insumos(
            session['token'], lanche_id, insumo_id, qtd_insumo
        )

        print(f"log: {salvar_lanche_insumo}")
        # SUCESSO
        if 'success' in salvar_lanche_insumo:
            flash('Receita adicionada com sucesso', 'success')
            return redirect(url_for('cadastrar_lanche_insumos'))

        # ERRO 409
        if salvar_lanche_insumo.get("error") == "Esse insumo já está vinculado a esse lanche":
            flash("Esse insumo já está vinculado a esse lanche", "error")
            return redirect(url_for('cadastrar_lanche_insumos'))

        # QUALQUER OUTRO ERRO
        flash("Erro ao inserir receita", "error")
        return redirect(url_for('cadastrar_lanche_insumos'))

    else:
        session['funcao_rota_anterior'] = 'cadastrar_lanche_insumos'

        lanches = routes_web.get_lanches(session['token'])
        insumos = routes_web.get_insumos(session['token'])

        return render_template(
            'cadastrar_lanche_insumo.html',
            lanches=lanches.get('lanches', []),
            insumos=insumos.get('insumos', [])
        )



@app.route('/pessoas/cadastrar', methods=['GET', 'POST'])
def cadastrar_pessoas():
    retorno = verificar_token()
    if retorno:
        return retorno
    if session['papel'] != "admin":
        flash('Você não tem acesso, entre com uma conta autorizada', 'info')
        return redirect(url_for(session['funcao_rota_anterior']))
    if request.method == 'POST':
        cpf = request.form['CPF']
        nome = request.form['Nome']
        email = request.form['Email']
        senha = request.form['Senha']
        salario = request.form['salario']
        papel = request.form['Cargo']

        cadastrar = routes_web.post_cadastro_pessoas(session['token'], nome, cpf, email, senha, salario, papel)
        if 'success' in cadastrar:
            flash('Pessoa adicionada com sucesso', 'success')
            return redirect(url_for('pessoas'))

        # Verificar na documentação possiveis erros para tratar
        return redirect(url_for('cadastrar_pessoas'))
    # if session['papel'] == "cliente" or session['papel'] == "garcom"]:
    else:
        session['funcao_rota_anterior'] = 'cadastrar_pessoas'
        return render_template('cadastrar_pessoa.html')

@app.route('/lanches/cadastrar', methods=['POST', 'GET'])
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
        salvar_lanche = routes_web.post_lanches(session['token'], nome_lanche, descricao_lanche, valor_lanche)
        if 'success' in salvar_lanche:
            flash('Pessoa adicionada com sucesso', 'success')
            return redirect(url_for('lanches'))

        # Verificar na documentação possiveis erros para tratar
        return redirect(url_for('cadastrar_pessoas'))
    else:
        session['funcao_rota_anterior'] = 'cadastrar_lanches'
        return render_template('cadastrar_lanches.html')

@app.route('/insumos/cadastrar', methods=['POST', 'GET'])
def cadastrar_insumos():
    retorno = verificar_token()
    if retorno:
        return retorno
    if session['papel'] != "admin":
        flash('Você não tem acesso, entre com uma conta autorizada', 'info')
        return redirect(url_for(session['funcao_rota_anterior']))
    if request.method == 'POST':
        nome_insumo = request.form.get('nome_insumo')
        custo_insumo = request.form.get('custo_insumo')
        categoria_id = request.form.get('categoria_id')
        salvar_insumo = routes_web.post_insumos(session['token'], nome_insumo, custo_insumo, categoria_id)
        if 'success' in salvar_insumo:# 201
            flash('Insumo adicionada com sucesso', 'success')
            return redirect(url_for('insumos'))

        # Verificar na documentação possiveis erros para tratar
        return redirect(url_for('cadastrar_insumos'))
    else:
        categorias = routes_web.get_categorias(session['token'])
        if 'categorias' in categorias:
            session['funcao_rota_anterior'] = 'cadastrar_insumos'
            return render_template('cadastrar_insumos.html', categorias=categorias['categorias'])
        flash('Parece que algo ocorreu errado', 'error')
        return redirect(url_for('insumos'))


@app.route('/entradas/cadastrar_entradas', methods=['POST', 'GET'])
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
        bebida_id = request.form['bebida_id']
        data_entrada = datetime.datetime.now()
        nota_fiscal = request.form['nota_fiscal']
        valor_entrada = request.form['valor_entrada']

        if not nota_fiscal or not valor_entrada or not qtd_entrada:
            flash('Preencha todos os campos', 'error')
            return redirect(url_for('cadastrar_entradas'))
        if not bebida_id and not insumo_id:
            flash('Preencha todos os campos', 'error')
            return redirect(url_for('cadastrar_entradas'))
        if insumo_id:
            salvar_entrada = routes_web.post_entradas_insumos(session['token'], qtd_entrada, insumo_id, data_entrada, nota_fiscal, valor_entrada)
        else:
            salvar_entrada = routes_web.post_entradas_bebidas(session['token'], qtd_entrada, bebida_id, data_entrada, nota_fiscal, valor_entrada)

        if 'success' in salvar_entrada:
            flash('Entrada adicionada com sucesso', 'success')
            return redirect(url_for('entradas'))

        return redirect(url_for('cadastrar_entradas'))
    else:
        insumos = routes_web.get_insumos(session['token'])
        bebidas = routes_web.get_bebidas(session['token'])
        if 'insumos' in insumos and 'bebidas' in bebidas:
            session['funcao_rota_anterior'] = 'cadastrar_entradas'
            return render_template('cadastrar_entradas.html', insumos=insumos['insumos'], bebidas=bebidas['bebidas'])
        flash('Parece que algo ocorreu errado', 'error')
        return redirect(url_for('entradas'))

@app.route('/categorias/cadastrar', methods=['POST', 'GET'])
def cadastrar_categorias():
    retorno = verificar_token()
    if retorno:
        return retorno
    if session['papel'] != "admin":
        flash('Você não tem acesso, entre com uma conta autorizada', 'info')
        return redirect(url_for(session['funcao_rota_anterior']))
    if request.method == 'POST':
        nome_categoria = request.form['nome_categoria']
        if not nome_categoria:
            flash('Preencha todos os campos!', 'error')
            return redirect(url_for('cadastrar_categorias'))
    
        salvar_categoria = routes_web.post_categorias(session['token'], nome_categoria)
        if 'success' in salvar_categoria:
            flash('Categoria adicionada com sucesso', 'success')
            return redirect(url_for('categorias'))
        flash('Parece que algo ocorreu errado!', 'error')
        return redirect(url_for('cadastrar_categorias'))
    else:
        session['funcao_rota_anterior'] = 'cadastrar_categorias'
        return render_template('cadastrar_categorias.html')
@app.route('/vendas_por_funcionarios')
def get_vendas_por_funcionarios():
    return render_template('vendas_funcionarios.html')
@app.route("/formulario_teste")
def formulario_teste():
    return render_template("formulario_teste.html")

@app.route('/bebidas/cadastrar', methods=['GET', 'POST'])
def cadastrar_bebidas():
    retorno = verificar_token()
    if retorno:
        return retorno
    if session['papel'] != "admin":
        flash('Você não tem acesso, entre com uma conta autorizada', 'info')
        return redirect(url_for(session['funcao_rota_anterior']))
    if request.method == 'POST':
        nome_bebida = request.form['nome_bebida']
        valor = request.form['valor']
        categoria_id = request.form['categoria_id']
        descricao = request.form['descricao']
        if not nome_bebida or not valor or not categoria_id:
            flash('Preencha todos os campos!', 'error')
            return redirect(url_for('cadastrar_bebidas'))

        salvar_bebida = routes_web.post_bebidas(session['token'], nome_bebida, valor, categoria_id, descricao)
        print('salvou')
        print(salvar_bebida)
        if 'success' in salvar_bebida:

            print('entrou em sucesso')
            flash('Bebida adicionada com sucesso', 'success')
            return redirect(url_for('bebidas'))

        flash('Parece que algo ocorreu errado', 'error')
        return redirect(url_for('cadastrar_bebidas'))
    else:
        categorias = routes_web.get_categorias(session['token'])

        if 'categorias' in categorias:
            # print()
            session['funcao_rota_anterior'] = 'cadastrar_bebidas'
            return render_template('cadastrar_bebidas.html', categorias=categorias['categorias'])
        flash('Parece que algo ocorreu errado :/', 'error')
        return redirect(url_for('bebidas'))
#
@app.route("/faturamento")
def faturamento():
    return render_template("faturamento.html")
@app.route('/vendas_por_usuario')
def vendas_usuario():
    return render_template('grafico_usuario.html')
@app.route('/venda_por_mes')
def venda_mes():
    return render_template('grafico_mensal.html')

@app.route('/venda_garcom')
def venda():
    return render_template('graficoestilizado.html')
#
# original do dener
# @app.route('/editar_pessoa/<id_pessoa>', methods=['GET', 'POST'])
# def editar_pessoa(id_pessoa):
#     try:
#         retorno = verificar_token()
#         if retorno:
#             return retorno
#         if session['papel'] != "admin" and session['user_id'] != id_pessoa:
#             flash('Você não tem acesso, entre com uma conta autorizada', 'info')
#             return redirect(url_for(session['funcao_rota_anterior']))
#         pessoa = routes_web.get_pessoa_by_id(session['token'], id_pessoa)
#         pessoa = pessoa['pessoa']
#         if request.method == 'POST':
#             if session['papel'] == "admin":
#                 papel = request.form.get('papel')
#                 salario = int(request.form.get('salario'))
#
#                 if session['user_id'] == id_pessoa:
#                     senha = request.form.get('senha')
#                     email = request.form.get('email')
#                     routes_web.put_editar_pessoa(session['token'], id_pessoa, pessoa['nome_pessoa'], pessoa['cpf'], salario, papel, generate_password_hash(senha), email, pessoa['status'])
#                 else:
#                     status = request.form.get('status')
#                     routes_web.put_editar_pessoa(session['token'], id_pessoa, pessoa['nome_pessoa'], pessoa['cpf'], salario, papel, pessoa['senha'], pessoa['email'], status)
#
#             else:
#                 email = request.form.get('email')
#                 senha = request.form.get('senha')
#                 routes_web.put_editar_pessoa(session['token'], id_pessoa, pessoa['nome_pessoa'], pessoa['cpf'], pessoa['salario'], pessoa['papel'], generate_password_hash(senha), email, pessoa['status'])
#         else:
#             session['funcao_rota_anterior'] = 'pessoas'
#             return render_template('editar_pessoa.html', pessoa=pessoa)
#
#     except Exception as erro:
#         print(f'será que é esse erro?{erro}')
#         flash('Parece que algo deu errado', 'error')
#         return redirect(url_for(session['funcao_rota_anterior']))




@app.route('/mudar_status/<id_pedido>', methods=['GET', 'POST'])
def mudar_status( id_pedido):

    a = routes_web.put_editar_status_pedidos(session['token'],id_pedido)
    flash(f'pedido#{id_pedido} editado com sucesso', 'success')
    return redirect(url_for('pedidos'))


@app.route('/editar_pessoa/<id_pessoa>', methods=['GET', 'POST'])
def editar_pessoa(id_pessoa):
    try:
        # Garante que id_pessoa é int para comparações
        try:
            id_pessoa_int = int(id_pessoa)
        except ValueError:
            flash("ID de pessoa inválido", "error")
            return redirect(url_for(session.get('funcao_rota_anterior', 'index')))

        retorno = verificar_token()
        if retorno:
            return retorno

        # Protege comparação de tipos
        session_user_id = session.get('user_id')
        try:
            session_user_id_int = int(session_user_id) if session_user_id is not None else None
        except ValueError:
            session_user_id_int = None

        if session.get('papel') != "admin" and session_user_id_int != id_pessoa_int:
            flash('Você não tem acesso, entre com uma conta autorizada', 'info')
            return redirect(url_for(session.get('funcao_rota_anterior', 'index')))

        # Busca pessoa (verifica retorno)
        print("a: ",id_pessoa_int)
        resposta = routes_web.get_pessoa_by_id(session['token'], id_pessoa_int)
        if not resposta or 'pessoa' not in resposta:
            flash('Não foi possível obter dados da pessoa', 'error')
            return redirect(url_for(session.get('funcao_rota_anterior', 'index')))
        pessoa = resposta['pessoa']
        print(pessoa)

        if request.method == 'POST':
            # Nome do campo no HTML é "cargo" — primeiro tenta esse, depois 'papel' (compatibilidade)
            papel = request.form.get('cargo') or request.form.get('papel') or pessoa.get('papel')
            # Salário: tenta converter, se falhar usa o existente
            salario_raw = request.form.get('salario')
            try:
                salario = int(salario_raw) if salario_raw not in (None, '') else int(pessoa.get('salario', 0))
            except Exception:
                flash('Salário inválido', 'error')
                return redirect(url_for('editar_pessoa', id_pessoa=id_pessoa_int))

            # Pega a senha atual armazenada (pode ser 'senha_hash' ou 'senha' dependendo do que a API retorna)
            senha_existente = pessoa.get('senha_hash') or pessoa.get('senha') or ''

            # Branch admin
            if session.get('papel') == "admin":
                # Se admin editando a própria conta -> permite trocar email/senha também
                if session_user_id_int == id_pessoa_int:
                    senha_form = request.form.get('senha')
                    email_form = request.form.get('email') or pessoa.get('email')
                    if senha_form:
                        senha_hash = generate_password_hash(senha_form)
                    else:
                        senha_hash = senha_existente
                    email = email_form
                    status_final = pessoa.get('status_pessoa') or pessoa.get('status')
                else:
                    # admin editando outro usuário
                    status_final = request.form.get('status') or pessoa.get('status_pessoa') or pessoa.get('status')
                    # Mantém senha/email existentes quando admin edita outro sem alterar senha
                    senha_hash = senha_existente
                    email = pessoa.get('email')
            else:
                # usuário comum editando a própria conta
                senha_form = request.form.get('senha')
                email = request.form.get('email') or pessoa.get('email')
                if senha_form:
                    senha_hash = generate_password_hash(senha_form)
                else:
                    senha_hash = senha_existente
                status_final = pessoa.get('status_pessoa') or pessoa.get('status')

            # Chama a função de PUT já instrumentada
            resultado = routes_web.put_editar_pessoa(
                session['token'],
                id_pessoa_int,
                pessoa.get('nome_pessoa'),   # você não altera nome no form, mantém
                pessoa.get('cpf'),
                salario,
                papel,
                senha_hash,
                email,
                status_final
            )

            print("Resultado do put_editar_pessoa:", resultado)

            # Verifica se houve erro
            if isinstance(resultado, dict) and resultado.get('erro'):
                flash(f"Erro ao editar pessoa: {resultado}", "error")
                return redirect(url_for('editar_pessoa', id_pessoa=id_pessoa_int))

            flash("Pessoa editada com sucesso!", "success")
            return redirect(url_for(session.get('funcao_rota_anterior', 'pessoas')))

        else:
            session['funcao_rota_anterior'] = 'pessoas'
            return render_template('editar_pessoa.html', pessoa=pessoa)

    except Exception as erro:
        print(f'será que é esse erro? {erro}')
        flash('Parece que algo deu errado', 'error')
        return redirect(url_for(session.get('funcao_rota_anterior', 'pessoas')))














# @app.route('/editar_pessoa/<id_pessoa>', methods=['GET', 'POST'])
# def editar_pessoa(id_pessoa):
#     # Garante um valor padrão seguro para a rota anterior
#     # Isso é CRUCIAL para evitar o BuildError/404 no bloco 'except'
#     if 'funcao_rota_anterior' not in session:
#         session['funcao_rota_anterior'] = 'index'  # Fallback seguro
#
#     try:
#         retorno = verificar_token()
#         if retorno:
#             return retorno
#
#         # --- Lógica de Segurança (Início) ---
#         # NOTE: Assumindo que 'admin' e 'user_id' e 'papel' estão na sessão
#         # Para fins de demonstração, setando valores se não existirem
#         if 'papel' not in session: session['papel'] = 'admin'
#         if 'user_id' not in session: session['user_id'] = '1'
#
#         if session['papel'] != "admin" and session['user_id'] != id_pessoa:
#             flash('Você não tem acesso, entre com uma conta autorizada', 'info')
#             # Neste ponto, se 'funcao_rota_anterior' for inválida, dará erro.
#             # Garantimos o fallback no 'except' abaixo.
#             return redirect(url_for(session['funcao_rota_anterior']))
#         # --- Lógica de Segurança (Fim) ---
#
#         pessoa = routes_web.get_pessoa_by_id(session['token'], id_pessoa)
#         pessoa = pessoa['pessoa']
#
#         if request.method == 'POST':
#             # ... toda a sua lógica de POST ...
#             # Se o POST for bem-sucedido, redirecionar para a rota de listagem 'pessoas'
#             flash('Funcionário editado com sucesso!', 'success')
#             return redirect(url_for('pessoas'))
#
#         else:  # request.method == 'GET'
#             # Só define 'pessoas' como rota anterior ao exibir o formulário.
#             session['funcao_rota_anterior'] = 'pessoas'
#             return render_template('editar_pessoa.html', pessoa=pessoa)
#
#     except BuildError:
#         # Erro específico do Flask quando a rota em url_for não existe.
#         print(
#             f"Erro de Rota (BuildError): O nome da rota '{session.get('funcao_rota_anterior', 'undefined')}' é inválido. Redirecionando para /.")
#         flash('Erro de Rota. Redirecionado para a página inicial.', 'error')
#         return redirect(url_for('index'))  # Redireciona para um fallback seguro (ex: rota inicial)
#
#     except Exception as erro:
#         print(erro)
#         flash('Parece que algo deu errado', 'error')
#
#         # Tenta redirecionar para a rota anterior, usando o 'index' como fallback final.
#         return redirect(url_for(session.get('funcao_rota_anterior', 'index')))

@app.route('/categorias/editar<id_categoria>', methods=['GET', 'POST'])
def editar_categoria(id_categoria):
    try:
        retorno = verificar_token()
        if retorno:
            return retorno
        if session['papel'] != "admin":
            flash('Você não tem acesso, entre com uma conta autorizada', 'info')
            return redirect(url_for(session['funcao_rota_anterior']))
        categoria = routes_web.get_categoria_by_id_categoria(session['token'], id_categoria)
        categoria = categoria['categoria']
        if request.method == 'POST':
            nome = request.form.get('nome_categoria')

            routes_web.put_editar_categoria(session['token'], id_categoria, nome)
        else:
            session['funcao_rota_anterior'] = 'categorias'
            return render_template('editar_categoria.html', categoria=categoria)

    except Exception as erro:
        print(erro)
        flash('Parece que algo deu errado', 'error')
        return redirect(url_for(session['funcao_rota_anterior']))

@app.route('/insumos/editar<id_insumo>', methods=['GET', 'POST'])
def editar_insumo(id_insumo):
    try:
        retorno = verificar_token()
        if retorno:
            return retorno
        if session['papel'] != "admin":
            flash('Você não tem acesso, entre com uma conta autorizada', 'info')
            return redirect(url_for(session['funcao_rota_anterior']))
        insumo = routes_web.get_insumo_by_id_insumo(session['token'], id_insumo)
        insumo = insumo['insumo']
        categorias = routes_web.get_categorias(session['token'])
        if request.method == 'POST':
            nome = request.form.get('nome_insumo')
            categoria_id = request.form.get('categoria_id')

            routes_web.put_editar_insumo(session['token'], id_insumo, nome, categoria_id)
        else:
            if 'insumo' in insumo and 'categorias' in categorias:
                session['funcao_rota_anterior'] = 'editar_pessoa'
                return render_template('editar_insumo.html', insumo=insumo, categorias=categorias)
            raise RuntimeError
    except Exception as erro:
        print(erro)
        flash('Parece que algo deu errado', 'error')
        return redirect(url_for(session['funcao_rota_anterior']))

if __name__ == '__main__':
    app.run(debug=True)