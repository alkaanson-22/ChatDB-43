# ChatDB-43 : Streamlit Application to Convert Natural Language to Executable SQL/Mongo Queries 

## Overview
This application enables users to convert natural language questions into executable SQL or MongoDB queries using Google’s Gemini Flash API. It supports schemas from AdventureWorks, Bike Store, and FIFA datasets, and provides results via a Streamlit web interface.

---

## Prerequisites

- Python 3.10 or later  
- MongoDB and MySQL installed locally  
- Gemini Flash API key from [Google AI Studio](https://makersuite.google.com/app)

---

## Installation Steps

#### Dataset Loading Instructions

The project includes a `data/` directory containing three datasets:
- **FIFA**
- **AdventureWorks**
- **Bike Store**

Each dataset is provided in both `.csv` and `.json` formats to support SQL and MongoDB loading.

Before running the app, you must load the datasets into their respective databases (MongoDB and MySQL).

### Step 1: Start Your Databases
```bash
# To start MongoDB, run:
sudo systemctl start mongodb
mongosh  # Launch MongoDB shell

# To start MySQL, run:
sudo systemctl start mysql
mysql -u root -p   #enter your username and password to log in
```

### Step 2: Load Data into Databases
Navigate to the folder that contains the loading scripts and run the following commands:
```bash
cd create_clean_database

# Load data into MongoDB
python write_mongo.py

# Load data into MySQL
python write_sql.py
```

### Step 3: To create a virtual environment and install required dependencies
```bash
# Clone or extract project
cd Project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### File Structure

- [`app.py`](app.py) — Streamlit interface for capturing user queries and displaying results  
- [`query_generator.py`](query_generator.py) — Gemini prompt generation and response parsing  
- [`query_executor.py`](query_executor.py) — Executes MongoDB and SQL queries  
- [`schemas.py`](schemas.py) — Schema mapping dictionary for tables and collections  


### Step 4: Adding API Key

To authenticate with the Gemini Flash API, you need to insert your API key in `query_generator.py` as shown below:

```python
os.environ["GOOGLE_API_KEY"] = "<your-api-key-here>"
```
### Step5 : Running the App

Once you've set up your environment and dependencies, launch the Streamlit application:

```bash
streamlit run app.py

