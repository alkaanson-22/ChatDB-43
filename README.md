# Natural Language Query to Database Project

## Overview
This app translates English-language queries into executable SQL or MongoDB commands using Google’s Gemini Flash API. It supports structured and semi-structured databases like AdventureWorks, Bike Store, and FIFA, allowing users to interact with their data using plain English via a Streamlit interface.

---

## Prerequisites

- Python 3.10 or later  
- MongoDB and MySQL installed and running locally  
- Gemini Flash API access

> 🔑 To get your Gemini API key, log in to [Google AI Studio](https://makersuite.google.com/app) and navigate to API access settings.

---

## Installation Steps

### 1. Start Your Databases

```bash
# Start MongoDB
sudo systemctl start mongodb

# Start MySQL and log in
sudo systemctl start mysql
mysql -u root -p
