from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import logout_user
import utils
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
@app.route('/')
def index():
    return render_template('inicio.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('senha')
        print(email, password, 'EMAILSENHA')
        user = utils.post_login(email, password)
        print(user)
        if user['access_token']:
            session['token'] = user['access_token']
            # session['email'] = user['email']
            session['username'] = user['nome']
            session['papel'] = user['papel']

            if session['papel'] == 'admin':
                return redirect(url_for('cards'))  # pagina do admin
            elif session['papel'] == 'cozinha':
                return redirect(url_for('login'))  # pagina da cozinha
            else:
                flash('Você não tem acesso a esse sistema', "error")
                print('flasssshhh')
                return None
                # return redirect(url_for('login'))
        else:
            # se não enviar email e senha é erro 400
            # se as credencias forem invalidas 401
            return render_template('login.html')  # se der errado permanece na tela de login
            # e da um flash pra avisar o erro
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    try:
        # logout_user()
        session.clear()
        print(session, 'session')
        return redirect(url_for('login'))
    except Exception as e:
        print(e)
        return redirect(url_for('login'))



@app.route('/cards', methods=['GET'])
@app.route('/cards/<valor_>', methods=['GET'])
def cards(valor_=None):
    # print(session['token'], session['papel'])
    if not session:
        return redirect(url_for('login'))

    pessoas = utils.get_pessoas(session['token'])

    if 'pessoas' not in pessoas:
        return redirect(url_for('login'))

    print(pessoas)
    if valor_ is None:
        return render_template('cards.html', valor_=False, pessoas=pessoas['pessoas'])
    else:
        if valor_ in ['true', 'True', True, 1, '1']:
            booleano = True
            print('wwwTRUE', booleano)
        else:
            booleano = False
            print('wwwFalse', booleano)

    # page = request.args.get("page", 1, type=int)
    # per_page = request.args.get("per_page", 10, type=int)

    return render_template('cards.html', valor_=not booleano, pessoas=pessoas['pessoas'])


if __name__ == '__main__':
    app.run(debug=True)