# Modulo encargado de la tokenizacion, filtrado de stopword y stemming
import nltk
import re
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import pandas as pd

stoplist = set(stopwords.words('english'))
stemmer = SnowballStemmer('english')
# addition stopwords
additional_stopwords = {',','!','?'}
stoplist.update(additional_stopwords)


def preprocessing_content(content):
    # Tokenizar
    terms = nltk.word_tokenize(content)
    terms_count = {} # Contar frecuencias de términos
    for term in terms:
        # Normalizar: convertir a minúsculas y quitar puntuación
        normalized_term = re.sub(r'\W+', '', term.lower())
        # Eliminar términos vacíos después de la normalización
        if not normalized_term:
            continue
        # Stemming
        stemmed_term = stemmer.stem(normalized_term)
        # Stopwords y términos no alfabéticos
        if stemmed_term not in stoplist and stemmed_term.isalpha():
            if stemmed_term in terms_count:
                terms_count[stemmed_term] += 1
            else:
                terms_count[stemmed_term] = 1
    return terms_count

def preprocessing(csv_file_name, token_stream_file_name):
    datacsv = pd.read_csv(csv_file_name)
    with open(token_stream_file_name, mode="w") as token_stream_file:
        for index, row in datacsv.iterrows():
            track_id = str(row["track_id"])  # Convertir termID a string
            track_name = row["track_name"] 
            track_artist = row["track_artist"]
            lyrics = row["lyrics"]
            # Concatenar track_name, track_artist y lyrics para formar el contenido
            content = f"{track_name} {track_artist} {lyrics}"
            processed_terms = preprocessing_content(content)
            # Escribir en token_stream
            for term, freq in processed_terms.items():
                token_stream_file.write(f"('{term}', '{track_id}', {freq})\n")

