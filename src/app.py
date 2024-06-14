# Punto de entrada de la aplicacion flask

from flask import Flask, render_template, request
import json
import os

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

@app.route('/')
def index():
    return render_template('index.html')
# SIMULACION
@app.route('/search', methods=['POST'])
def search_query():
    lyrics = request.form['lyrics']
    top_k = int(request.form['top_k'])
    technique = request.form['technique']

    # Leer los resultados simulados del archivo JSON
    json_path = os.path.join(os.path.dirname(__file__), '../data/results/outputEsperado.json')
    with open(json_path, 'r') as f:
        simulated_results = json.load(f)

    # Filtramos los resultados según top_k
    results = simulated_results[:top_k]

    # Simulación de tiempo total (en segundos)
    total_time = 0.1

    return render_template('results.html', query=lyrics, technique=technique, results=results, total_time=total_time)


if __name__ == '__main__':
    app.run(debug=True)