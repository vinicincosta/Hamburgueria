from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('inicio.html')

@app.route('/redirectcards/<valor>')
def redirect_cards(valor):
    if valor in ['true', 'True', True, 1, '1']:
        booleano = True
    else:
        booleano = False
    print('sss',booleano)

    # return render_template('cards.html', valor=booleano)
    return redirect(url_for('cards', valor=booleano))
@app.route('/cards/<valor>')
def cards(valor):
    print('valor', valor)
    if valor in ['true', 'True', True, 1, '1']:
        booleano = True
    else:
        booleano = False
    print('www',booleano)
    # return render_template('cards.html', valor=booleano)
    return render_template('cards.html', valor=booleano)

# def chama_tabela():
#     url_for('tabela')
# @app.route('/tabela')
# def tabela():
#     return render_template('tabela.html')

# @app.route('/tabela?<valor>', methods = ['GET'])
# def tabela_is_true(valor):
#     print(valor)
#     render_template('cards.html', valor=valor)

if __name__ == '__main__':
    app.run(debug=True)