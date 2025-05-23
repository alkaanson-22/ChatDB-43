# 🚀 ChatDB-43: Natural Language to SQL/Mongo Query Converter with Streamlit

ChatDB-43 is a lightweight Streamlit web app that converts plain English questions into executable **SQL** or **MongoDB** queries using **Google’s Gemini Flash API**. It supports real-world schemas from **AdventureWorks**, **Bike Store**, and **FIFA** datasets.

---

## 📌 Features

- 🔎 Translate natural language to database queries  
- 🧠 Uses Gemini Flash API for LLM-powered interpretation  
- ⚙️ Works with both **MySQL** and **MongoDB**  
- 📊 Supports AdventureWorks, Bike Store & FIFA datasets  
- 💻 Simple, interactive web UI built with **Streamlit**  

---

## 🧰 Prerequisites

Make sure you have the following installed:

- Python **3.10+**  
- **MongoDB** and **MySQL** running locally  
- Gemini API key from [Google AI Studio](https://makersuite.google.com/app)

---

## 🔧 Setup & Installation

#### Dataset Loading Instructions
The `data/` folder contains three datasets:

- `FIFA`  
- `AdventureWorks`  
- `Bike Store`  

Each is available in `.csv` and `.json` formats for SQL and MongoDB. Load them into your local databases before running the app.

### Step 1: Start Your Databases
```bash
# Start MongoDB
sudo systemctl start mongodb
mongosh

# Start MySQL
sudo systemctl start mysql
mysql -u root -p  # Enter password when prompted
```

Before running the app, you must load the datasets into their respective databases (MongoDB and MySQL).

---
### Step 2: Load Data into Databases
Navigate to the folder that contains the loading scripts and run the following commands:
```bash
cd create_clean_database

# Load data into MongoDB
python write_mongo.py   #python3 write_mongo.py

# Load data into MySQL
python write_sql.py     #python3 write_sql.py
```
---
### Step 3: To create a virtual environment and install required dependencies
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```
---
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
---
### Step 5 : Running the App

👉 Before running the app, make sure to update your MySQL username and password in the `query_executor.py` file to match your local configuration. 

Once you've set up your environment and dependencies, launch the Streamlit application:

```bash
streamlit run app.py
```
---
