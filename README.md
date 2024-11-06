PopNewsCorn

![ Alt Text](https://github.com/user-attachments/assets/2a190934-f138-4065-a285-abe4354a98d0)

This project is a Python script that fetches news articles based on specific queries and geolocations, summarizes the content, translates it if necessary, and saves the results for further processing.

Table of Contents
 

Prerequisites
Setup Instructions
1. Clone the Repository
2. Create a Virtual Environment
3. Activate the Virtual Environment
4. Install Dependencies
5. Configure API Keys and Database Connection
config.yaml Example
6. Create DB (One Time Process)
7. Running the Script
Obtaining API Keys
Hugging Face API Token
SerpAPI Key
Notes
Contact
Prerequisites
 

Python 3.7 or higher
Internet connection
Setup Instructions
 

1. Clone the Repository
 
First, clone the repository to your local machine. If you have not already, navigate to the directory where you want to store the project and run:


git clone https://github.com/yourusername/yourrepository.git  
 
Replace https://github.com/yourusername/yourrepository.git with the actual repository URL if applicable.

2. Create a Virtual Environment
 
Navigate to the project directory and create a virtual environment to manage the project's dependencies without affecting your global Python installation.


cd yourrepository  # Replace with your repository name  
python -m venv venv  
 
This will create a new directory called venv in your project folder.

3. Activate the Virtual Environment
 
Activate the virtual environment.

On Windows:


venv\Scripts\activate  
 

On macOS and Linux:


source venv/bin/activate  
 
After activation, your command prompt should be prefixed with (venv).

4. Install Dependencies
 
Ensure that you have the latest version of pip, then install the required Python packages.


pip install --upgrade pip  
pip install -r requirements.txt  


5. Configure API Keys and Database Connection
 
Create a config.yaml file in the root directory of your project. This file will store your API keys and database connection information. Make sure not to share this file publicly, as it contains sensitive information.

config.yaml Example

HUGGINGFACE_API_TOKEN: 'your_huggingface_api_token'  
SERPAPI_KEY: 'your_serpapi_key'  
DATABASE:  
  HOST: 'your_database_host'  
  PORT: 'your_database_port'  
  NAME: 'your_database_name'  
  USER: 'your_database_user'  
  PASSWORD: 'your_database_password'  
 
Replace the placeholders with your actual API tokens and database credentials.

HUGGINGFACE_API_TOKEN: Your Hugging Face API token.
SERPAPI_KEY: Your SerpAPI key.
DATABASE: Your database connection details.

Important: Do not share your config.yaml file or include it in version control systems like Git. Consider adding config.yaml to your .gitignore file.

6.Cretae a DB (One Time Process)

export PYTHONPATH="${PYTHONPATH}:$(pwd)"  

python scipt\create_db.py  

7.Running the Script
 
With everything set up, you can run the script using:

export PYTHONPATH="${PYTHONPATH}:$(pwd)"  

python scipt\news_script.py  
 
The script will fetch news articles based on the queries and geolocations specified, summarize them, and translate them if necessary. The results will be saved to a JSON file named news_data.json.

Obtaining API Keys
 

Hugging Face API Token
 
To use the Hugging Face inference API for translation and summarization, you need a Hugging Face API token.

Sign up or log in to Hugging Face.
Go to your API tokens page.
Generate a new API token with the necessary permissions.
Copy the token and paste it into the config.yaml file under HUGGINGFACE_API_TOKEN.
SerpAPI Key
 
SerpAPI is used to fetch Google News search results.

Sign up for an account at SerpAPI.
Once logged in, go to your dashboard.
Copy your API key.
Paste it into the config.yaml file under SERPAPI_KEY.
Notes
 

Database Configuration: If you intend to save the results to a database, ensure that the DATABASE configuration in config.yaml is correctly filled out with your database details. The news_script.py script provided currently saves the results to a JSON file (news_data.json). You can modify the script to save to a database if needed.
Logging: The script logs its operations to a file named news_script.log. Check this file for detailed logs if you encounter any issues.
Customizing Queries and Locations: You can customize the list of search queries and geolocations by editing the queries and geolocations lists in the main() function of news_script.py.
Dependencies: Ensure that all required Python packages are installed. If you encounter ModuleNotFoundError issues, double-check that all dependencies are installed in your virtual environment.
Contact
 
If you have any questions or need further assistance, feel free to contact:

Email: your.email@example.com
GitHub: yourusername
