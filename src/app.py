# Punto de entrada de la aplicacion flask

from flask import Flask, render_template, request
import json
import os
import pandas as pd
from indexing import IndexInverted
from preprocessing import stoplist
from utils import extract_keywords_from_text
import time  

from postgres import get_db_connection,parse_tsvector
app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

# Configuración de la base de datos e índice invertido
spotify_song = 'data/spotify_songs.csv'
index_file_name = 'data/results/merged_index.txt'

# Carga el DataFrame
df = pd.read_csv(spotify_song)
tamanio = len(df)

# Inicializa el índice invertido
index_inverted = IndexInverted(spotify_song, tamanio, block_limit=20000, stop_words=stoplist)

# Carga o crea el índice
if os.path.exists(index_file_name):
    try:
        index_inverted.load_index(index_file_name)
        print("Índice cargado.")
    except Exception as e:
        print(f"Error al cargar el índice: {e}")
else:
    try:
        index_inverted.create_index_inverted()
        print("Índice creado.")
    except Exception as e:
        print(f"Error al crear el índice: {e}")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_query():
    lyrics_query = request.form['lyrics']
    top_k = int(request.form['top_k'])
    technique = request.form['technique']

    start_time = time.time()  # Obtener el tiempo de inicio de la búsqueda

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
        cur.execute(query, (lyrics_query, top_k))
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

    else:
        tracks_with_scores = index_inverted.cosine_similarity(lyrics_query, top_k)

        formatted_results = []
        for idx, (track, score) in enumerate(tracks_with_scores):
            row = df.loc[df['track_id'] == track].iloc[0]

            if pd.isna(row['lyrics']) or not row['lyrics'].strip():
                lyrics_result = 'Columna lyrics vacia en la base de datos.'
                keywords = ''
            else:
                lyrics_result = row['lyrics']
                content = f"{row['track_name']} {row['track_artist']} {lyrics_result}"
                keywords = extract_keywords_from_text(content)

            formatted_results.append({
                'top': idx + 1,
                'score': score,
                'track_id': row['track_id'],
                'track_name': row['track_name'],
                'track_artist': row['track_artist'],
                'lyrics': lyrics_result,
                'keywords': keywords
            })

    end_time = time.time()  
    total_time = end_time - start_time 

    return render_template('results.html', query=lyrics_query, technique=technique, results=formatted_results, total_time=round(total_time, 2))

if __name__ == '__main__':
    app.run(debug=True)