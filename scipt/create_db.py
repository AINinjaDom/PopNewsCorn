# create_db.py

import yaml
import os
import psycopg2
from psycopg2 import sql
from os import getcwd, path


# Function to get database configuration
def get_db_config(config_fname="config.yaml"):
	# Get the full path to the config file
	config_path = path.join(getcwd(), config_fname)
	try:
		with open(config_path, 'r') as f:
			config = yaml.safe_load(f)
		db_config = config.get('DATABASE')
		if not db_config:
			raise ValueError("DATABASE section not found in the configuration file.")
		return db_config
	except FileNotFoundError:
		raise FileNotFoundError(f"Configuration file '{config_fname}' not found.")
	except yaml.YAMLError as e:
		raise ValueError(f"Error parsing YAML file '{config_fname}': {e}")


# Function to create the news_articles table
def create_news_articles_table(db_host, db_port, db_name, db_user, db_password):
	# Connect to the PostgreSQL database
	try:
		conn = psycopg2.connect(
			host=db_host,
			port=db_port,
			database=db_name,
			user=db_user,
			password=db_password
		)
		conn.autocommit = True
		cursor = conn.cursor()
		print("Connected to the database successfully.")

		# Define the SQL command to create the table
		create_table_query = sql.SQL("""  
            CREATE TABLE IF NOT EXISTS news_articles (  
                id SERIAL PRIMARY KEY,  
                title TEXT,  
                source TEXT,  
                date DATE,  
                hour TEXT,  
                minutes TEXT,  
                region_code TEXT,  
                region_name TEXT,  
                link TEXT UNIQUE,  
                tags TEXT[],  
                summary TEXT,  
                full_text TEXT,  
                summary_chinese TEXT,  
                full_text_chinese TEXT  
            );  
        """)

		# Execute the SQL command
		cursor.execute(create_table_query)
		print("news_articles table created or already exists.")

		# Close the cursor and connection
		cursor.close()
		conn.close()
		print("Database connection closed.")

	except psycopg2.Error as e:
		print(f"An error occurred while connecting to the database: {e}")
		raise


if __name__ == "__main__":
	# Load the database configuration
	db_config = get_db_config(config_fname="config.yaml")
	# Extract database parameters
	db_host = db_config.get('HOST')
	db_port = db_config.get('PORT')
	db_name = db_config.get('NAME')
	db_user = db_config.get('USER')
	db_password = db_config.get('PASSWORD')

	# Check that all necessary DB config values are present
	if not all([db_host, db_port, db_name, db_user, db_password]):
		raise ValueError("Please ensure all database connection details are set in config.yaml.")

	# Create the news_articles table
	create_news_articles_table(
		db_host=db_host,
		db_port=db_port,
		db_name=db_name,
		db_user=db_user,
		db_password=db_password
	)