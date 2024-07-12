import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        dbname="project2BD",
        user="postgres",
        password="admin",
        host="172.18.0.2",
        port="5432"
    )
    return conn

def parse_tsvector(tsvector):
    # Convierte tsvector a lista de palabras clave
    keywords = []
    for token in tsvector.split():
        keyword = token.split(':')[0].replace("'", "")
        keywords.append(keyword)
    return keywords