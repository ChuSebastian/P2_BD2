# Punto de entrada de la aplicacion flask

from flask import Flask, render_template, request
import json
import os
#from spotify_api import get_spotify_token, get_track_image

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

# Configura tus credenciales de Spotify
#CLIENT_ID = "3ea37211b94e4d00a7eb6c41c06d9a53"
#CLIENT_SECRET = "b941ce9bee514798a8a41384ecd38bb5"
#SPOTIFY_TOKEN = get_spotify_token(CLIENT_ID, CLIENT_SECRET)

@app.route('/')
def index():
    return render_template('base.html')
# SIMULACION
@app.route('/search', methods=['GET', 'POST'])
def search_query():
    if request.method == 'POST':
        lyrics = request.form['lyrics']
        top_k = int(request.form['top_k'])
        technique = request.form['technique']

        # Simula resultados 
        with open('data/results/outputEsperado.json', 'r') as file:
            results = json.load(file)

        # Añade las imágenes a los resultados
        #for result in results:
        #    image_url = get_track_image(result['track_id'], SPOTIFY_TOKEN)
        #    result['image'] = image_url

        total_time = 25
        return render_template('results.html', query=lyrics, technique=technique, results=results, total_time=total_time)
    else:
        return render_template('index.html', query=None, results=None)

if __name__ == '__main__':
    app.run(debug=True)