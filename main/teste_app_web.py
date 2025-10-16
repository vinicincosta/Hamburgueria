from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import utils
app = Flask(__name__)
app.config['secret_key'] = 'secret'
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form.get('email')
        password = request.form.get('password')

        user = utils.post_login(email, password)
        if user['access_token']:
            session['token'] = user['access_token']
            session['email'] = user['email']
            session['username'] = user['username']
            session['papel'] = user['papel']

            if session['papel'] == 'admin':
                return url_for('cards') #pagina do admin
            else:
                return url_for('login')# pagina da cozinha
        else:
            # se não enviar email e senha é erro 400
            # se as credencias forem invalidas 401
            return render_template('login.html') # se der errado permanece na tela de login
                                                # e da um flash pra avisar o erro

@app.route('/cards', methods=['GET'])
@app.route('/cards/<valor_>', methods=['GET'])
def cards(valor_=None):
    if not session['token'] and not session['papel']:
        return redirect(url_for('login'))

    if valor_ is None:
        return render_template('cards.html', valor_=False)
    else:
        if valor_ in ['true', 'True', True, 1, '1']:
            booleano = True
            print('wwwTRUE', booleano)
        else:
            booleano = False
            print('wwwFalse', booleano)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)



    pessoas = utils.get_pessoas(session['token'])['pessoas']
    return render_template('cards.html', valor_=not booleano, pessoas=pessoas)


if __name__ == '__main__':
    app.run(debug=True)