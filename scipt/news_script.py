# news_script.py

import sys
import os
import json
import requests
import logging
import yaml
from huggingface_hub import InferenceClient
from langdetect import detect
from opencc import OpenCC
from newspaper import Article
import dateparser
from serpapi import GoogleSearch
import psycopg2
from psycopg2 import sql

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
	sys.path.insert(0, project_root)

# Get API configuration
config_path = os.path.join(project_root, 'config.yaml')
with open(config_path, 'r') as f:
	config = yaml.safe_load(f)

# Access the API tokens from the config dictionary
HUGGINGFACE_API_TOKEN = config.get('HUGGINGFACE_API_TOKEN')
SERPAPI_KEY = config.get('SERPAPI_KEY')

if not HUGGINGFACE_API_TOKEN or not SERPAPI_KEY:
	raise ValueError("Please set the HUGGINGFACE_API_TOKEN and SERPAPI_KEY in your config.yaml file.")

# Setup logging
logging.basicConfig(filename='news_script.log', level=logging.INFO)

cc = OpenCC('s2t')

# Initialize the Inference Client
inference_client = InferenceClient(token=HUGGINGFACE_API_TOKEN)


# Function to translate text to Traditional Chinese
def translate_text_to_chinese(text):
	try:
		response = inference_client.translation(
			text,
			model="Helsinki-NLP/opus-mt-en-zh"
		)
		translated_text = response
		# Convert Simplified Chinese to Traditional Chinese
		translated_text = cc.convert(translated_text)
		return True, translated_text
	except Exception as e:
		return False, {'error': str(e)}


# Function to translate text to English
def translate_text_to_english(text):
	try:
		response = inference_client.translation(
			text,
			model="Helsinki-NLP/opus-mt-multi-zh-en"
		)
		translated_text = response
		return True, translated_text
	except Exception as e:
		return False, {'error': str(e)}


# Function to summarize text
def summarize_text(text):
	try:
		# Truncate text to a maximum length (e.g., 1024 characters)
		max_length = 1024
		text = text[:max_length]
		response = inference_client.summarization(
			text,
			model="facebook/bart-large-cnn"
		)
		summary_text = response
		return True, summary_text
	except Exception as e:
		return False, {'error': str(e)}


# Function to extract article content, summarize, and translate
def get_news_summary(url):
	try:
		article = Article(url)
		article.download()
		article.parse()
		full_text = article.text  # Original text

		# Detect language and translate to English if necessary
		lang = detect(full_text)
		if lang != 'en':
			res, text_or_error = translate_text_to_english(full_text)
			if not res:
				return False, {'error': text_or_error['error']}
			full_text_english = text_or_error
		else:
			full_text_english = full_text

		# Summarize the English text
		res, summary_or_error = summarize_text(full_text_english)
		if not res:
			return False, {'error': summary_or_error['error']}
		summary_english = summary_or_error

		# Translate summary and full text to Traditional Chinese
		res_full_text, full_text_chinese_or_error = translate_text_to_chinese(full_text_english)
		if not res_full_text:
			return False, {'error': full_text_chinese_or_error['error']}
		full_text_chinese = full_text_chinese_or_error

		res_summary, summary_chinese_or_error = translate_text_to_chinese(summary_english)
		if not res_summary:
			return False, {'error': summary_chinese_or_error['error']}
		summary_chinese = summary_chinese_or_error

		return True, {
			'summary': summary_english,
			'full_text': full_text_english,
			'summary_chinese': summary_chinese,
			'full_text_chinese': full_text_chinese
		}
	except Exception as e:
		return False, {'error': str(e)}


# Main script logic
def main():
	# Database connection setup
	db_config = config.get('DATABASE')
	if not db_config:
		raise ValueError("DATABASE section not found in the configuration file.")

	db_host = db_config.get('HOST')
	db_port = db_config.get('PORT')
	db_name = db_config.get('NAME')
	db_user = db_config.get('USER')
	db_password = db_config.get('PASSWORD')

	if not all([db_host, db_port, db_name, db_user, db_password]):
		raise ValueError("Please ensure all database connection details are set in config.yaml.")

	try:
		conn = psycopg2.connect(
			host=db_host,
			port=db_port,
			database=db_name,
			user=db_user,
			password=db_password
		)
		cursor = conn.cursor()
		print("Connected to the database successfully.")
	except psycopg2.Error as e:
		print(f"An error occurred while connecting to the database: {e}")
		return

	# Define your queries and geolocations
	geolocations = [
		"us", "uk", "ca", "au", "in", "hk", "sg", "jp", "kr", "fr", "de",
		"br", "za", "ae", "ru", "cn", "es", "it", "mx"
	]

	# Mapping region codes to region names
	region_codes = {
		"us": "United States",
		"uk": "United Kingdom",
		"ca": "Canada",
		"au": "Australia",
		"in": "India",
		"hk": "Hong Kong",
		"sg": "Singapore",
		"jp": "Japan",
		"kr": "South Korea",
		"fr": "France",
		"de": "Germany",
		"br": "Brazil",
		"za": "South Africa",
		"ae": "United Arab Emirates",
		"ru": "Russia",
		"cn": "China",
		"es": "Spain",
		"it": "Italy",
		"mx": "Mexico"
	}

	queries = [
		"LGBTQ+ rights",
		"religion news",
		"freedom of speech",
		"LGBTQ+ rights and religion",
		"LGBTQ+ friendly churches",
		"China Economy",
		"China Human Rights",
		"US Presidential Election",
		"Global Warming",
		"Hong Kong Human Rights and Freedom",
		"Transgender",
		"Artificial Intelligence",
		"Technology news",
		"Health and medicine",
		"Science discoveries",
		"Space exploration",
		"Environmental issues",
		"Economics and finance",
		"Education news",
		"Pop culture",
		"Music",
		"Movies",
		"Celebrity news",
		"Fashion",
		"Travel news",
		"Crime and law",
		"Human interest stories",
		"Sports news",
		"International politics",
		"Cryptocurrency",
		"Mental health",
		"Renewable energy",
		"Pandemic updates",
		"Climate change",
		"Cybersecurity",
		"Social media trends",
		"Startups and entrepreneurship",
		"Global conflicts",
		"Agriculture technology",
		"Sustainability initiatives"
	]

	# Negative keywords to exclude performing arts
	negative_terms = ["-theatre", "-theater", "-opera", "-ballet", "-circus", "-mime", "-puppet", '-"performance art"']

	news_infos = []
	for query in queries:
		logging.info(f"Results for query: {query}")
		adjusted_query = f"{query} {' '.join(negative_terms)}"
		for gl in geolocations:
			params = {
				"q": adjusted_query,
				"tbm": "nws",
				"tbs": "qdr:w",  # Past 7 days
				"gl": gl,
				"api_key": SERPAPI_KEY
			}

			search = GoogleSearch(params)
			results = search.get_dict()

			logging.info(f"Geolocation: {gl}")
			news_results = results.get('news_results', [])

			# Limit the number of articles to process per query and location
			news_results = news_results[:3]  # Adjust as needed

			for news_result in news_results:
				link = news_result.get('link')
				res, summary_info = get_news_summary(link)

				if res:
					# Parse the date string
					raw_date_str = news_result.get('date', '')
					parsed_date = dateparser.parse(raw_date_str)
					if parsed_date:
						formatted_date = parsed_date.strftime('%Y-%m-%d')
						hour = parsed_date.strftime('%H')
						minutes = parsed_date.strftime('%M')
					else:
						formatted_date = None
						hour = None
						minutes = None

					news_info = {
						'title': news_result.get('title'),
						'source': news_result.get('source'),
						'date': formatted_date,
						'hour': hour,
						'minutes': minutes,
						'region_code': gl,
						'region_name': region_codes.get(gl, 'Unknown'),
						'link': link,
						'tags': [query],  # Use the query as the tag
						# Add the summaries and full texts
						'summary': summary_info['summary'],
						'full_text': summary_info['full_text'],
						'summary_chinese': summary_info['summary_chinese'],
						'full_text_chinese': summary_info['full_text_chinese']
					}
					# Print the Chinese summary
					print(news_info['summary_chinese'])

					if "Please make sure your browser supports JavaScript" not in news_info['summary']:
						news_infos.append(news_info)

						# Insert or update the news_article in the database
						try:
							insert_query = sql.SQL("""  
                                INSERT INTO news_articles (  
                                    title, source, date, hour, minutes, region_code, region_name,  
                                    link, tags, summary, full_text, summary_chinese, full_text_chinese  
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  
                                ON CONFLICT (link) DO UPDATE SET  
                                    title = EXCLUDED.title,  
                                    source = EXCLUDED.source,  
                                    date = EXCLUDED.date,  
                                    hour = EXCLUDED.hour,  
                                    minutes = EXCLUDED.minutes,  
                                    region_code = EXCLUDED.region_code,  
                                    region_name = EXCLUDED.region_name,  
                                    tags = EXCLUDED.tags,  
                                    summary = EXCLUDED.summary,  
                                    full_text = EXCLUDED.full_text,  
                                    summary_chinese = EXCLUDED.summary_chinese,  
                                    full_text_chinese = EXCLUDED.full_text_chinese;  
                            """)
							cursor.execute(insert_query, (
								news_info['title'],
								news_info['source'],
								news_info['date'],
								news_info['hour'],
								news_info['minutes'],
								news_info['region_code'],
								news_info['region_name'],
								news_info['link'],
								news_info['tags'],
								news_info['summary'],
								news_info['full_text'],
								news_info['summary_chinese'],
								news_info['full_text_chinese']
							))
							conn.commit()
							print(f"Inserted/Updated article: {news_info['title']}")
						except psycopg2.Error as e:
							print(f"An error occurred while inserting data into the database: {e}")
							logging.error(f"Error inserting article at {link}: {e}")

						# Log the news info
					logging.info(f"Saved news: {news_info['title']}")
				else:
					error_message = summary_info.get('error', 'unknown error')
					logging.error(f"Error summarizing article at {link}: {error_message}")

				# Close the database connection
	cursor.close()
	conn.close()
	print("Database connection closed.")


if __name__ == "__main__":
	main()