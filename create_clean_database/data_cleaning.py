import pymysql
import re
import os
import json
from functools import lru_cache
from typing import Optional

# Database connection parameters
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "wela1104",
    "database": "adventure_works",
}

# Limits and batch size
BATCH_SIZE = 1000  # Batch processing size for updates
MAX_OPERATIONS_PER_SESSION = 50  # Query limit: max database operations
operation_counter_file = "operation_counter.json"


def initialize_operation_counter():
    if not os.path.exists(operation_counter_file):
        with open(operation_counter_file, "w") as f:
            json.dump({"operations": 0}, f)


def get_operation_count() -> int:
    initialize_operation_counter()
    with open(operation_counter_file, "r") as f:
        data = json.load(f)
    return data.get("operations", 0)


def increment_operation_count(count: int = 1):
    initialize_operation_counter()
    with open(operation_counter_file, "r") as f:
        data = json.load(f)
    data["operations"] = data.get("operations", 0) + count
    with open(operation_counter_file, "w") as f:
        json.dump(data, f)


def reset_operation_counter():
    with open(operation_counter_file, "w") as f:
        json.dump({"operations": 0}, f)


def connect_to_database():
    try:
        conn = pymysql.connect(**db_config)
        print("Successfully connected to the database.")
        return conn
    except pymysql.Error as e:
        print(f"Error connecting to the database: {e}")
        return None


@lru_cache(maxsize=128)
def get_column_info(table_name: str, column_name: str) -> Optional[tuple]:
    conn = connect_to_database()
    if not conn:
        return None
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"SHOW COLUMNS FROM {table_name} WHERE Field = %s", (column_name,)
        )
        column_info = cursor.fetchone()
        return column_info
    finally:
        cursor.close()
        conn.close()


def clean_column_dollar_signs(conn, table_name: str, column_name: str):
    # Check operation limit (token usage proxy)
    operation_count = get_operation_count()
    if operation_count >= MAX_OPERATIONS_PER_SESSION:
        print(
            f"Error: Maximum number of database operations ({MAX_OPERATIONS_PER_SESSION}) reached."
        )
        return

    cursor = conn.cursor()
    try:
        # Step 1: Check the current data type of the column (cached)
        column_info = get_column_info(table_name, column_name)
        if not column_info:
            print(f"Column {column_name} not found in table {table_name}.")
            return

        current_type = column_info[1]
        print(f"Current data type of {table_name}.{column_name}: {current_type}")

        # Step 2: If the column is already DECIMAL, check for dollar signs
        if "decimal" in current_type.lower():
            print(
                f"{column_name} is already a DECIMAL type. Checking for dollar signs..."
            )
            cursor.execute(
                f"SELECT {column_name} FROM {table_name} WHERE {column_name} LIKE '%$%' LIMIT 1"
            )
            if cursor.fetchone():
                print(
                    f"Dollar signs found in {table_name}.{column_name}, but column is already DECIMAL. This shouldn't happen."
                )
            else:
                print(
                    f"No dollar signs found in {table_name}.{column_name}. No changes needed."
                )
            return

        # Step 3: Add a temporary column to hold numeric values
        temp_column = f"{column_name}_numeric"
        cursor.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {temp_column} DECIMAL(10,2)"
        )
        print(f"Added temporary column {temp_column} to {table_name}.")
        increment_operation_count()

        # Step 4: Count total rows to process
        cursor.execute(
            f"SELECT COUNT(*) FROM {table_name} WHERE {column_name} IS NOT NULL"
        )
        total_rows = cursor.fetchone()[0]
        print(f"Total rows to process in {table_name}.{column_name}: {total_rows}")

        # Step 5: Update rows in batches
        for offset in range(0, total_rows, BATCH_SIZE):
            cursor.execute(
                f"""
                UPDATE {table_name}
                SET {temp_column} = CAST(REPLACE({column_name}, '$', '') AS DECIMAL(10,2))
                WHERE {column_name} IS NOT NULL
                LIMIT {BATCH_SIZE} OFFSET {offset}
            """
            )
            conn.commit()
            rows_updated = cursor.rowcount
            print(f"Updated {rows_updated} rows in batch (offset {offset}).")
            increment_operation_count()

        # Step 6: Drop the old column and rename the new column
        cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
        cursor.execute(
            f"ALTER TABLE {table_name} CHANGE COLUMN {temp_column} {column_name} DECIMAL(10,2)"
        )
        conn.commit()
        print(f"Replaced {column_name} with numeric values (DECIMAL(10,2)).")
        increment_operation_count()

    except pymysql.Error as e:
        print(f"Error processing {table_name}.{column_name}: {e}")
        conn.rollback()
    finally:
        cursor.close()


def main():
    conn = connect_to_database()
    if not conn:
        return

    try:
        print("\nProcessing product.StandardCost...")
        clean_column_dollar_signs(conn, "product", "StandardCost")

        print("\nProcessing sales.Sales...")
        clean_column_dollar_signs(conn, "sales", "Sales")

    finally:
        conn.close()
        print("\nDatabase connection closed.")
        print(f"Total database operations performed: {get_operation_count()}")


if __name__ == "__main__":
    main()
