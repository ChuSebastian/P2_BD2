# Punto de entrada de la aplicacion flask

from flask import Flask, render_template, request, redirect
import json
import os
import pandas as pd
from indexing import IndexInverted
from preprocessing import stoplist
from utils import *
import time  
from SearchAudio.KNNseq import KNN_Sequential
from SearchAudio.KNNRtree import KNN_RTree
from SearchAudio.KNNHihgD import KNN_HighD

from postgres import get_db_connection,parse_tsvector
app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Configuración de la base de datos e índice invertido
spotify_song = 'data/spotify_songs.csv'
index_file_name = 'data/results/merged_index.txt'
features_file_name = 'data/Features'

# Carga el DataFrame
df = pd.read_csv(spotify_song)
tamanio = len(df)

# Inicializa el índice invertido
index_inverted = IndexInverted(spotify_song, tamanio, block_limit=20000, stop_words=stoplist)

# Carga o crea el índice y los features
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

# Inicializar y cargar los features
dim = 128
features = getFeatures(features_file_name,dim) # probando 128 dimensiones, es lo MAX
print("Features cargados.")
# Parametros de los KNN
m = 100
num_bits = 128
# Inicializar las estructuras KNN
knn_sequential = KNN_Sequential(features)
knn_rtree = KNN_RTree(m, features)
knn_highD = KNN_HighD(num_bits, features)
print("Estructuras KNN cargados.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_lyrics', methods=['POST'])
def search_query_lyrics():
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

@app.route('/search_audio', methods=['GET', 'POST'])
def search_query_audio():
    if request.method == 'POST':
        if 'audio_file' not in request.files:
            return redirect(request.url)
        
        audio_file = request.files['audio_file']
        top_k = int(request.form['top_k'])
        technique = request.form['technique']

        if audio_file.filename == '':
            return redirect(request.url)
        
        if audio_file and allowed_file(audio_file.filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], audio_file.filename)
            audio_file.save(filepath)

            # Preprocesamiento del audio
            if audio_file.filename.endswith('.mp3'):
                query_path = os.path.join(app.config['UPLOAD_FOLDER'], 'query.wav')
                convert_mp3_to_wav(filepath, query_path)
            else:
                query_path = filepath

            # extract features del audio wav
            query_mfcc = feature_extract(query_path, dim)

            start_time = time.time()
            results: List[Tuple[str, float]]

            if technique == 'KNNseq':
                results = knn_sequential.knn_heap_query(query_mfcc, top_k)

            elif technique == 'KNNRtree':
                results = knn_rtree.query(query_mfcc, top_k)

            elif technique == 'KNNHighD':
                results = knn_highD.knn_query(query_mfcc, top_k)
            else:
                return redirect(request.url)

            end_time = time.time()
            total_time = end_time - start_time

            # Formatear los resultados
            formatted_results = [
                {
                    'top': index + 1,
                    'track_id': result[0],
                    'similarity': result[1]
                }
                for index, result in enumerate(results)
            ]

            return render_template('results_audio.html', query=audio_file.filename, technique=technique, results=formatted_results, total_time=total_time)

    # Render the search audio page for GET requests
    return render_template('search_audio.html')

if __name__ == '__main__':
    app.run(debug=True)