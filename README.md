# Proyecto N°2 BD2
Busqueda y Recuperación de Información

# Introducción

## Objetivo del proyecto
El presente proyecto tiene como objetivo desarrollar estas estructuras de datos de manera eficiente, con motivo de realizar búsquedas rápidas en un conjunto de documentos.
Con respecto al índice invertido textual, se utiliza para asociar términos de consulta con los documentos que los contienen ya que mejora la velocidad y precisión del retorno de información, lo que facilita la recuperación eficiente de documentos relevantes en función de los términos de búsqueda.
En cuanto al índice multidimensional, se utilizar para representar características tanto de texto como de audio, lo que permite realizar consultas que involucren múltiples dimensiones, como la similitud de texto y audio en función de diferentes atributos.


## Dominio de datos
La base de datos utilizada es la Audio features and lyrics of Spotify songs, con al rededor de 18000 canciones con los campos:

|    **Campo**    |
|:---------------:|
| ```track_id```        | 
| ```track_name```  | 
| ```track_artist``` | 
| ```lyrics``` | 
| ```track_popularity``` | 
| ```track_album_id``` |
| ```track_album_name``` | 
| ```track_album_release_date``` |
| ```playlist_name``` |
| ```playlist_id``` |
| ```playlist_genre``` |
| ```playlist_subgenre``` |
| ```danceability``` |
| ```enery``` | 
| ```key``` | 
| ```loudness``` | 
| ```mode``` | 
| ```speechness``` | 
| ```acousticness``` | 
| ```instrumentalness``` | 
| ```liveness``` |
| ```valence``` |
| ```tempo``` |
| ```duration_ms``` |
| ```language``` |






## ¿Cómo se construye el índice invertido en PostgreSQL?

La construcción de un índice invertido en PostgreSQL, especialmente para el caso de texto completo en campos como nombres de pistas, artistas y letras de canciones, se realiza generalmente a través de vectores de texto (tsvector) y consultas de texto (tsquery), utilizando la funcionalidad de búsqueda de texto completo que ofrece PostgreSQL. A continuación, te explico paso a paso cómo se construye y utiliza este índice invertido en tu ejemplo

# Creación de la tabla 
-Primero, creas una tabla llamada track que incluirá las columnas track_id, track_name, track_artist, y lyrics. Cada columna se define para almacenar texto.

```python
CREATE TABLE IF NOT EXISTS track(
    track_id TEXT,
    track_name TEXT,
    track_artist TEXT,
    lyrics TEXT
);


```

