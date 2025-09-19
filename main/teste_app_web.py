from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('inicio.html')

@app.route('/cards', methods=['GET'])
@app.route('/cards/<valor_>', methods=['GET'])
def cards(valor_=None):
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