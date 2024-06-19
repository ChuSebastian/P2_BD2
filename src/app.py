# Punto de entrada de la aplicacion flask

from flask import Flask, render_template, request
import json
import os
#from spotify_api import get_spotify_token, get_track_image
from postgres import get_db_connection,parse_tsvector
app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

# Configura tus credenciales de Spotify
#CLIENT_ID = "3ea37211b94e4d00a7eb6c41c06d9a53"
#CLIENT_SECRET = "b941ce9bee514798a8a41384ecd38bb5"
#SPOTIFY_TOKEN = get_spotify_token(CLIENT_ID, CLIENT_SECRET)

@app.route('/')
def index():
    return render_template('index.html')
# SIMULACION
@app.route('/search', methods=['POST'])
def search_query():
    lyrics = request.form['lyrics']
    top_k = int(request.form['top_k'])
    technique = request.form['technique']

    if technique == 'postgres':
        # Conexión y consulta a la base de datos PostgreSQL
        conn = get_db_connection()
        cur = conn.cursor()

        query = """
            SELECT ts_rank_cd(indexed, query) AS rank, track_id, track_name, track_artist, lyrics, keywords
            FROM track, plainto_tsquery('english', %s) query
            WHERE query @@ indexed
            ORDER BY rank DESC
            LIMIT %s;
        """
        cur.execute(query, (lyrics, top_k))
        results = cur.fetchall()

        cur.close()
        conn.close()

        # Convertimos los resultados a un formato adecuado para pasar a la plantilla
        formatted_results = [
            {
                'top': index + 1,
                'score': row[0],
                'track_id': row[1],
                'track_name': row[2],
                'track_artist': row[3],
                'lyrics': row[4],
                'keywords': parse_tsvector(row[5])
            }
            for index, row in enumerate(results)
        ]

        total_time = 0.1  # Este es un valor simulado para el tiempo total
    else:
        # Simulación de resultados desde un archivo JSON
        json_path = os.path.join(os.path.dirname(__file__), '../data/results/outputEsperado.json')
        with open(json_path, 'r') as f:
            simulated_results = json.load(f)

        # Filtramos los resultados según top_k
        formatted_results = simulated_results[:top_k]

        total_time = 0.1  # Este es un valor simulado para el tiempo total

    return render_template('results.html', query=lyrics, technique=technique, results=formatted_results, total_time=total_time)

if __name__ == '__main__':
    app.run(debug=True)