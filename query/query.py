import psycopg2


def create_news_articles_table(db_host, db_port, db_name, db_user, db_password):
	create_table_query = """  
    CREATE TABLE IF NOT EXISTS news_articles (  
        id SERIAL PRIMARY KEY,  
        title TEXT,  
        source TEXT,  
        publication_date DATE,  
        hour INTEGER,  
        minutes INTEGER,  
        region_code CHAR(2),  
        region_name VARCHAR(64),  
        summary TEXT,  
        full_text TEXT,  
        summary_chinese TEXT,  
        full_text_chinese TEXT,  
        link TEXT UNIQUE,  
        tags TEXT[]  
    );  
    """

	try:
		with psycopg2.connect(
				host=db_host,
				port=db_port,
				database=db_name,
				user=db_user,
				password=db_password
		) as connection:
			with connection.cursor() as cursor:
				cursor.execute(create_table_query)
				connection.commit()
				print("Table 'news_articles' created successfully or already exists.")
	except Exception as error:
		print(f"Error while creating PostgreSQL table: {error}")