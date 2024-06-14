# Punto de entrada de la aplicacion flask

from flask import Flask, render_template, request

app = Flask(__name__, template_folder='../frontend/templates')

@app.route('/')
def index():
    return "hola mundo"

if __name__ == '__main__':
    app.run(debug=True)