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

### Creación de la tabla 
- Primero, creas una tabla llamada track que incluirá las columnas track_id, track_name, track_artist, y lyrics. Cada columna se define para almacenar texto.

```python
CREATE TABLE IF NOT EXISTS track(
    track_id TEXT,
    track_name TEXT,
    track_artist TEXT,
    lyrics TEXT
);

```
### Carga de datos
- Los datos se cargan en la tabla desde un archivo CSV. Este archivo debe estar ubicado en el servidor de PostgreSQL y el usuario de la base de datos debe tener los permisos adecuados para leerlo.
  
```python
COPY track FROM '/tmp/spotify_songs.csv' DELIMITER ',' CSV HEADER;
```
### Habilitación de extensiones
- PostgreSQL admite extensiones que proporcionan funcionalidades adicionales. pg_trgm es una extensión que proporciona funciones y operadores para determinar la similitud de cadenas de texto basadas en trigramas, aunque en este caso particular, la extensión relevante es más probable que se relacione con funcionalidades de búsqueda de texto completo.
```python
CREATE EXTENSION IF NOT EXISTS pg_trgm;

```
### Adición de una columna indexed y población de la misma
- Se añade una nueva columna indexed de tipo tsvector a la tabla track. Esta columna almacenará los vectores de texto que son esenciales para las búsquedas de texto completo.
```python
ALTER TABLE track ADD COLUMN indexed tsvector;
UPDATE track SET 
    indexed = x.indexed 
FROM (
    SELECT track_id,
            setweight(to_tsvector('english', track_name),'A') ||
            setweight(to_tsvector('english', track_artist), 'B') ||
            setweight(to_tsvector('english', lyrics), 'C') 
            AS indexed 
    FROM track
) AS x 
WHERE track.track_id = x.track_id;

```
- En este bloque de código, cada campo de texto (track_name, track_artist, lyrics) es convertido a un tsvector con diferentes ponderaciones (A, B, C) que pueden ser utilizadas para dar más o menos importancia a cada campo en las búsquedas.

### Creación del índice
- Se crea un índice utilizando el método GIN (Generalized Inverted Index) sobre la columna indexed. Los índices GIN son particularmente efectivos para manejar datos que contienen múltiples valores en una sola columna (como vectores de texto).
  particular, la extensión relevante es más probable que se relacione con funcionalidades de búsqueda de texto completo.
```python
CREATE INDEX IF NOT EXISTS lyrics_idx_gin ON track USING gin(indexed);

```

###Búsqueda y recuperación de datos 
- Para buscar en los datos, se ajusta una configuración para deshabilitar las búsquedas secuenciales, lo cual fuerza a PostgreSQL a utilizar el índice GIN.
```python
SET enable_seqscan TO OFF;
SELECT ts_rank_cd(indexed, query) AS rank, track_id, track_name, track_artist, lyrics
FROM track, plainto_tsquery('english', 'the trees') query
WHERE query @@ indexed
ORDER BY rank DESC LIMIT 100;

```
- plainto_tsquery convierte una cadena de texto plano en una consulta de texto completo, y @@ es el operador que encuentra los documentos que coinciden con la consulta. ts_rank_cd calcula un ranking de los documentos basado en la coincidencia.
- Finalmente, se restablecen las configuraciones al estado normal para permitir que PostgreSQL optimice las búsquedas de la manera habitual.

