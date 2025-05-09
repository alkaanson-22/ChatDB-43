# Natural Language Query to Database Project

## Overview
This application enables users to convert natural language questions into executable SQL or MongoDB queries using Google’s Gemini Flash API. It supports schemas from AdventureWorks, Bike Store, and FIFA datasets, and provides results via a Streamlit web interface.

---

## Prerequisites

- Python 3.10 or later  
- MongoDB and MySQL installed locally  
- Gemini Flash API key from [Google AI Studio](https://makersuite.google.com/app)

---

## Installation Steps

### 1. Start Your Databases
Make sure MongoDB and MySQL services are up and running:

```bash
# To start MongoDB, run:
sudo systemctl start mongodb
mongosh  # Launch MongoDB shell

# To start MySQL, run:
sudo systemctl start mysql
mysql -u root -p   #enter your username and password to log in
```

#### 2. To create a virtual environment and install required dependencies
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


#### 3. Adding API Key

To authenticate with the Gemini Flash API, you need to insert your API key in `query_generator.py` as shown below:

```python
os.environ["GOOGLE_API_KEY"] = "<your-api-key-here>"
```
### 4. Running the App

Once you've set up your environment and dependencies, launch the Streamlit application:

```bash
streamlit run app.py

