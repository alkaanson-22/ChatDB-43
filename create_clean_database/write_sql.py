import os
import pandas as pd
from sqlalchemy import create_engine
import pymysql
import ssl


def create_database_if_not_exists(db_url, folder_name):
    # Extract the database name from the db_url
    db_name = db_url.split("/")[-1]

    # Create a connection to MySQL server (without specifying the database)
    # connection = pymysql.connect(
    #     host="localhost",
    #     user="alka",  # Change to your MySQL username
    #     password="SQL_Project@123",  # Change to your MySQL password
    #     cursorclass=pymysql.cursors.DictCursor,
    # )
    connection = pymysql.connect(
        host="localhost",
        user="sql_user",  # ✅ Use the new MySQL user
        password="SafePass@123",
        ssl={"ssl": {}}  # ✅ Force use of cryptography
    )

    try:
        with connection.cursor() as cursor:
            # Check if the database exists
            cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
            result = cursor.fetchone()

            if result is None:
                # If the database doesn't exist, create it
                cursor.execute(f"CREATE DATABASE {db_name}")
                print(f"Database {db_name} created.")
            else:
                print(f"Database {db_name} already exists.")

        # Commit any changes and close the connection
        connection.commit()

    finally:
        connection.close()


def csv_to_sql(csv_file, db_url, table_name):
    # Step 1: Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)
    print(df)

    # Step 2: Create the SQLAlchemy engine
    engine = create_engine(db_url)
    print(engine)

    # Step 3: Create the table in the SQL database (if it doesn't exist)
    # SQLAlchemy will automatically create the table from the DataFrame schema if it doesn't exist.
    df.to_sql(
        table_name,
        con=engine,
        index=False,
        if_exists="replace",  # 'replace' drops the table if it exists
    )

    print(
        f"✅ Data from {csv_file} successfully inserted into {table_name} in the database."
    )


def process_csv_folder(folder_path, db_url):
    # Ensure that the database exists
    folder_name = os.path.basename(folder_path)
    create_database_if_not_exists(db_url, folder_name)

    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        # Check if the file is a CSV file
        if filename.endswith(".csv"):
            # Define the full path to the CSV file
            csv_file = os.path.join(folder_path, filename)
            print(csv_file)

            # Derive table name from the CSV file name (remove .csv extension)
            table_name = os.path.splitext(filename)[0]
            print(table_name)

            # Call the function to insert the CSV data into SQL
            csv_to_sql(csv_file, db_url, table_name)


# Example usage
folder_path = "data/fifa_csv"  # Path to your folder containing CSV files
# db_url = "mysql+pymysql://alka:SQL_Project%40123@localhost/fifa"
db_url = "mysql+pymysql://sql_user:SafePass%40123@localhost/fifa"
# Replace with your MySQL connection URL

# Call the function to process all CSV files in the folder
process_csv_folder(folder_path, db_url)
