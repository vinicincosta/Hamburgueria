from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import utils
app = Flask(__name__)

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
        global token
        token = utils.post_login(email, password)['access_token']
        return render_template('login.html')

@app.route('/cards', methods=['GET'])
@app.route('/cards/<valor_>', methods=['GET'])
def cards(valor_=None):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    if token:
        pessoas = utils.get_pessoas(token)['pessoas']

    else:
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

        return render_template('cards.html', valor_=not booleano)
    # print('www',booleano)
    # return render_template('cards.html', valor=booleano)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)