import streamlit as st
import google.generativeai as genai
import re
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "<your-api-key-here>")
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash-8b")

# Cache query generation
@st.cache_data
def generate_query(_user_query: str, query_type: str, schemas: dict, database: str):
    query_instruction = (
        "Generate a SQL query using unqualified table names (e.g., products)"
        if query_type == "sql"
        else "Generate a MongoDB query using db.<collection> (e.g., db.products)"
    )
    db_map = {
            "Bike Store": "bike_store",
            "AdventureWorks": "adventure_works",
            "FIFA": "fifa",
        }
    schema_text = f"{schemas[db_map[database]][query_type]}"

    # print(schema_text)


    sql_instructions = f"""
  - **SQL Queries**:
  - Use unqualified table names (e.g., products, NOT adventure_works.products).
  - Do NOT use `USE` or schema qualifiers (e.g., adventure_works, bike_store).
  - Support SELECT, INSERT, UPDATE, DELETE, JOIN, GROUP BY, HAVING, etc.
  - Use JOINs only for explicitly listed tables (e.g., customers, orders, products).
  - Default to key fields (e.g., product_name, list_price for products).

  - Bike Store uses MySQL. Handle date filters using MySQL functions and the 'YYYY-MM-DD' format (e.g., '2016-01-13').
    - For year: 'in 2021' → YEAR(order_date) = 2021
    - For month: 'in May' → MONTH(order_date) = 5
    - For specific date: 'on 2016-01-13' → order_date = '2016-01-13'
    - For date range: 'between 2016-01-01 and 2016-12-31' → order_date BETWEEN '2016-01-01' AND '2016-12-31'
  - Use CONCAT(first_name, ' ', last_name) for name concatenation to ensure compatibility across SQL databases and not ||.
  - Synonyms:
    - Bike Store: 'price' → list_price, 'name' → product_name, 'customer' → first_name + last_name
    - AdventureWorks: 'cost' → StandardCost, 'name' → Product, 'sales amount' → Sales, 'products' → Product 
    - FIFA: 'name' → player_name, 'score' → minute
  - Do NOT reference brands or categories in Bike Store (they don’t exist).
  - If the query references a table or column not in the schema (e.g., 'reseller' in AdventureWorks), return "".
  - Return "" for invalid requests.
  - No code block markers (```sql, ```).
  - For joins, explicity mention the table the column select belongs to, to remove ambiguity for eg: AdventureWorks: "List product sales" →
      SELECT product.Product, sales.Sales
      FROM product
      JOIN sales ON product.ProductKey = sales.ProductKey
  - Examples:
    - Bike Store: "List products" →
      SELECT product_name, brand_id, category_id
      FROM products
    - Bike Store: "List customers" →
      SELECT CONCAT(first_name, ' ', last_name) AS customer_name
      FROM customers
    - Bike Store: "Add a new customer named John Doe in California" →
      INSERT INTO customers (first_name, last_name, state)
      VALUES ('John', 'Doe', 'California')
    - Bike Store: "Update John Doe's city to Los Angeles" →
      UPDATE customers
      SET city = 'Los Angeles'
      WHERE first_name = 'John' AND last_name = 'Doe'
    - Bike Store: "Delete the customer named John Doe" →
      DELETE FROM customers
      WHERE first_name = 'John' AND last_name = 'Doe'
    - Bike Store: "Find customers in New York who placed orders in 2021" →
      SELECT CONCAT(first_name, ' ', last_name) AS customer_name, orders.order_date
      FROM customers
      JOIN orders ON customers.customer_id = orders.customer_id
      WHERE customers.state = 'New York'
      AND YEAR(orders.order_date) = 2021
    - Bike Store: "List orders with their product names" →
      SELECT orders.order_id, products.product_name
      FROM orders
      JOIN products ON orders.product_id = products.product_id
    - Bike Store: "Count orders per customer" →
      SELECT CONCAT(customers.first_name, ' ', customers.last_name) AS customer_name, COUNT(orders.order_id) AS order_count
      FROM customers
      JOIN orders ON customers.customer_id = orders.customer_id
      GROUP BY customers.customer_id, customers.first_name, customers.last_name
    - Bike Store: "Find customers who placed orders in May 2016" →
      SELECT CONCAT(customers.first_name, ' ', customers.last_name) AS customer_name
      FROM customers
      JOIN orders ON customers.customer_id = orders.customer_id
      WHERE MONTH(orders.order_date) = 5
      AND YEAR(orders.order_date) = 2016
    - Bike Store: "Find orders placed on 2016-01-13" →
      SELECT order_id, customer_id, order_date
      FROM orders
      WHERE order_date = '2016-01-13'
    - Bike Store: "Find customers who placed more than 3 orders" →
      SELECT CONCAT(customers.first_name, ' ', customers.last_name) AS customer_name, COUNT(orders.order_id) AS order_count
      FROM customers
      JOIN orders ON customers.customer_id = orders.customer_id
      GROUP BY customers.customer_id, customers.first_name, customers.last_name
      HAVING COUNT(orders.order_id) > 3
    - AdventureWorks: "List product sales" →
      SELECT product.Product, sales.Sales
      FROM product
      JOIN sales ON product.ProductKey = sales.ProductKey
    - AdventureWorks: "Calculate the total sales for Rear Brakes and HL Crankset" →
      SELECT SUM(sales.Sales) AS TotalSales
      FROM product
      JOIN sales ON product.ProductKey = sales.ProductKey
      WHERE product.Product IN ('Rear Brakes', 'HL Crankset')
    - AdventureWorks: "List resellers" →
      ""
    - FIFA: "List players who scored" →
      SELECT players.player_name, goals.minute
      FROM players
      JOIN goals ON players.player_id = goals.player_id
"""

    mongo_instructions = """
🚫 STRICT CONSTRAINTS:
- Use only the exact collection names provided in the schema. Do NOT pluralize, rename, guess, or hallucinate table names (e.g., use "orders" not "sales"; use "products" not "product").
- Do NOT make assumptions about foreign keys or implicit relationships unless they are explicitly defined in the schema.
- Always verify that every field used in the query exists in the corresponding collection schema.
- If the field or collection is not found, return an empty string "".
- Field names and collection names are **case-sensitive** and must match exactly.


✅ MONGODB SYNTAX RULES:
- Always use db.<collection> format.
- Enclose all field names and string values in double quotes ("").
- Return only plain MongoDB shell-style queries (no markdown, no comments, no explanations).
- All output must have balanced braces and valid syntax.

✅ SUPPORTED OPERATIONS:

1. 🔎 Basic Retrieval (find()):
- Return all fields → db.collection.find({}, {})
- Return specific fields → db.collection.find({}, { "field1": 1, "field2": 1, "_id": 0 })

2. 🎯 Filtering (WHERE):
- Equality: "field": "value"
- Comparison: { "$gt": value }, { "$lt": value }, { "$gte": value }, { "$lte": value }
- Date filtering:
  - Use full ISO 8601 datetime string format: "YYYY-MM-DDT00:00:00"
  - "in 1954" → "date_field": { "$gte": "1954-01-01T00:00:00", "$lt": "1955-01-01T00:00:00" }
  - "after Jan 1, 2019" → "date_field": { "$gt": "2019-01-01T00:00:00" }
  - Do not use ISODate() unless schema explicitly defines it.

3. 📊 Aggregation (aggregate):
- Use stages: $match, $group, $sum, $count, $project, $sort, $limit, $skip
- Always include _id in $group: e.g., { "_id": "$model_year" }
- Example: db.collection.aggregate([{ "$group": { "_id": "$model_year", "total": { "$sum": "$list_price" } } }])

4. 🔁 Joins using $lookup:
- Use $lookup **only** if fields from multiple collections are required to answer the query.
- Before using $lookup, check if all requested fields are available in a single collection.
- Do NOT use $lookup when all required fields are present in the current collection.
- Use $unwind after $lookup if accessing nested fields.
- Example:
  {
    "$lookup": {
      "from": "orders",
      "localField": "customer_id",
      "foreignField": "customer_id",
      "as": "orders"
    }
  }

5. 🧾 Sorting and Pagination:
- Sort by field → .sort({ "field": 1 }) for ascending, -1 for descending
- Limit results → .limit(n)
- Skip results → .skip(n)

6. ✍️ Data Modification:
- Insert:
  - db.collection.insertOne({ ... }) — required fields must exist in schema
  - db.collection.insertMany([{ ... }, { ... }])
- Update:
  - db.collection.updateOne({ filter }, { "$set": { field: value } })
  - db.collection.updateMany(...) for multiple documents
- Delete:
  - db.collection.deleteOne({ filter })
  - db.collection.deleteMany(...) for multiple deletions
- Return shell-like response (acknowledged, matchedCount, etc.)

✅ SCHEMA EXPLORATION:
- If the user asks "What collections exist?" → return: db.getCollectionNames()
- If the user asks for sample data, example records, or a preview from a collection:
  → return: db.<collection>.find({}).limit(5)
  - This should retrieve 5 sample rows (documents) from the collection.
  - Do NOT add any filters or projections — just return the top 5 documents using limit(5).

✅ FIELD SYNONYMS (Use only if the field exists in the schema):

- Bike Store:
  - "price" → "list_price"
  - "name" → "product_name"
  - "customer name" → use "first_name" and "last_name" separately

- AdventureWorks:
  - "cost" → "StandardCost"
  - "name" → "Product"
  - "sales amount" → "Sales"
  - "country-region" → "Country"

- FIFA:
  - "name" → "player_name"
  - "score" → "minute" (in goals collection)

⚠️ Do not invent new fields from synonyms. Use them only to map user intent to existing fields in the current schema.
"""


    instructions = sql_instructions if query_type == "sql" else mongo_instructions

    prompt = f"""
You are an expert database assistant converting natural language to {'SQL' if query_type == 'sql' else 'MongoDB'} queries. Follow these instructions:

Schema: {schema_text}

{instructions}

- **Output**: Return only the query, no markers, comments, or formatting. For MongoDB, ensure balanced curly braces.

{query_instruction}.

Query: {_user_query}

Return exactly:
"""

    print(f"Generating {query_type} query with Gemini API...")
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        cleaned_text = re.sub(r"```(?:sql|javascript)?\s*|\s*```", "", response_text).strip()
        if query_type == "mongodb":
            if cleaned_text.count("{") != cleaned_text.count("}"):
                print(f"❌ Mismatched braces: {cleaned_text}")
                return ""
        return cleaned_text if cleaned_text else ""
    except Exception as e:
        print(f"❌ Error generating {query_type} query with Gemini API: {e}")
        return ""

if __name__ == "__main__":
    from schemas import schemas  # ensures correct schema injection for testing
    try:
        # sample_query = "Find customers in New York who placed orders in 2021"
        sample_query = "Show resellers in Canada"
        # sql_query = generate_query(sample_query, query_type="sql", schemas=schemas)
        sql_query = generate_query(sample_query, query_type="sql", schemas=schemas, database="adventure_works")
        print(f"Generated SQL: {sql_query}")
        # mongo_query = generate_query(sample_query, query_type="mongodb", schemas=schemas)
        mongo_query = generate_query(sample_query, query_type="mongodb", schemas=schemas, database="adventure_works")
        print(f"Generated MongoDB: {mongo_query}")
    except Exception as e:
        print(f"Error during test: {e}")
