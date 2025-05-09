schemas = {
    "adventure_works": {
        "sql": """
Table: Product
Fields:
- ProductKey (PK)
- Product
- StandardCost
- Color
- Subcategory
- Category

Table: reseller
Fields:
- ResellerKey (PK)
- BusinessType
- Reseller
- City
- State
- Country

Table: sales
Fields:
- SalesOrderNumber (PK)
- OrderDate
- ProductKey (FK → product.ProductKey)
- ResellerKey
- EmployeeKey
- SalesTerritoryKey (FK → region.SalesTerritoryKey)
- Quantity
- UnitPrice
- Sales
- Cost
""",
        "mongodb": """
MongoDB Collections:
- product: {
    "ProductKey": "int", "Product": "string", "StandardCost": "float",
    "Color": "string", "Subcategory": "string", "Category": "string",
    "Background Color Format": "string", "Font Color Format": "string"
}
- reseller: {
    "ResellerKey": "int", "BusinessType": "string", "Reseller": "string",
    "City": "string", "State": "string", "Country": "string"
}
- sales: {
    "SalesOrderNumber": "string", "OrderDate": "string", "ProductKey": "int",
    "ResellerKey": "int", "EmployeeKey": "int", "SalesTerritoryKey": "int",
    "Quantity": "int", "UnitPrice": "float", "Sales": "float", "Cost": "float"
}

Primary Keys:
- product.ProductKey
- sales.SalesOrderNumber
- reseller.ResellerKey

Foreign Keys:
- sales.ProductKey → product.ProductKey
- sales.ResellerKey → reseller.ResellerKey
""",
    },
    "bike_store": {
        "sql": """
Table: customers
Fields:
- customer_id (PK)
- first_name
- last_name
- phone
- email
- street
- city
- state
- zip_code

Table: orders
Fields:
- order_id (PK)
- customer_id (FK → customers.customer_id)
- order_status
- order_date
- required_date
- shipped_date
- store_id
- staff_id

Table: products
Fields:
- product_id (PK)
- product_name
- brand_id (FK → brands.brand_id)
- category_id (FK → categories.category_id)
- model_year
- list_price
""",
        "mongodb": """
MongoDB Collections:
- customers: {
    "customer_id": "int", "first_name": "string", "last_name": "string",
    "email": "string", "street": "string", "city": "string",
    "state": "string", "zip_code": "int"
}
- orders: {
    "order_id": "int", "customer_id": "int", "order_status": "int",
    "order_date": "ISODate", "required_date": "ISODate", "shipped_date": "ISODate",
    "store_id": "int", "staff_id": "int", "product_id": "int"
}
- products: {
    "product_id": "int", "product_name": "string", "brand_id": "int",
    "category_id": "int", "model_year": "int", "list_price": "float"
}

Primary Keys:
- customers.customer_id
- orders.order_id
- products.product_id

Foreign Keys:
- orders.customer_id → customers.customer_id
- products.brand_id → brands.brand_id
- products.category_id → categories.category_id
""",
    },
    "fifa": {
        "sql": """
Table: players
Fields:
- player_id (PK)
- family_name
- given_name
- birth_date
- count_tournaments

Table: matches
Fields:
- match_id (PK)
- tournament_id
- match_date
- home_team_id
- away_team_id
Note: home_team_id, away_team_id reference external team data (no teams table).

Table: goals
Fields:
- goal_id (PK)
- match_id
- player_id
- team_id
- minute_label
""",
        "mongodb": """
MongoDB Collections:
- goals: {
    "goal_id": "string", "match_id": "string", "player_id": "string",
    "team_id": "string", "minute_label": "string"
}
- matches: {
    "match_id": "string", "tournament_id": "string",
    "match_date": "ISODate", "home_team_id": "string", "away_team_id": "string"
}
- players: {
    "player_id": "string", "family_name": "string", "given_name": "string",
    "birth_date": "ISODate", "count_tournaments": "int"
}

Primary Keys:
- players.player_id
- matches.match_id
- goals.goal_id

Foreign Keys:
- goals.match_id → matches.match_id
- goals.player_id → players.player_id

Note: home_team_id, away_team_id reference external team data (no teams collection).
""",
    },
}
