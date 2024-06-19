from indexing import IndexInverted
from preprocessing import stoplist
import pandas as pd
import os

index_file_name = 'data/results/merged_index.txt'

if os.path.exists(index_file_name):
    # Load the existing index
    spotify_song = 'data/spotify_songs.csv'
    df = pd.read_csv(spotify_song)
    tamanio = len(df)
    index_inverted = IndexInverted(spotify_song, tamanio, block_limit=20000, stop_words=stoplist)
    index_inverted.load_index(index_file_name)
    print("Índice cargado.")
else:
    # Create the index
    spotify_song = 'data/spotify_songs.csv'
    df = pd.read_csv(spotify_song)
    tamanio = len(df)
    index_inverted = IndexInverted(spotify_song, tamanio, block_limit=20000, stop_words=stoplist)
    index_inverted.create_index_inverted()
    print("Índice creado.")

topK = 10
query = "Nicky Romero I close my eyes and dream You're all I see You, you're all I need"
documents_with_scores = index_inverted.cosine_similarity(query, topK)
for document, score in documents_with_scores:
    print(f"Track_id: {document}, Score: {score}")