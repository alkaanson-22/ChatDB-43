import pymysql
import re
import ast
from pymongo import MongoClient
import json
import json5



def detect_database(query: str):
    pattern = r"\b(bike\s+store|adventureworks|fifa)\b"
    match = re.search(pattern, query, re.IGNORECASE)
    if match:
        db_map = {
            "bike store": "Bike Store",
            "adventureworks": "AdventureWorks",
            "fifa": "FIFA",
        }
        return db_map.get(match.group(1).lower())
    return None


def execute_sql_query(query: str, database: str):
    try:
        schema_map = {
            "Bike Store": "bike_store",
            "AdventureWorks": "adventure_works",
            "FIFA": "fifa",
        }
        schema_name = schema_map.get(database, "")
        print(schema_name)
        if not schema_name:
            return "Error: Invalid database"

        table_map = {
            "Bike Store": ["customers", "orders", "products"],
            "AdventureWorks": ["product", "sales"],
            "FIFA": ["players", "matches", "goals"],
        }
        tables = table_map.get(database, [])

        # Sanitize the query
        sanitized_query = re.sub(r"```(?:sql|javascript)?\s*|\s*```", "", query).strip()
        sanitized_query = re.sub(r"\s+", " ", sanitized_query).strip()
        print(sanitized_query)

        if "||" in sanitized_query:
           
            select_part = sanitized_query.lower().split("from")[0]
            if "||" in select_part:
              
                def replace_concat(match):
                    # Split the matched expression into the concatenation part and the alias (if any)
                    full_expression = match.group(0)
                    
                    alias_match = re.search(
                        r"\s+AS\s+\w+\b", full_expression, re.IGNORECASE
                    )
                    if alias_match:
                        # Extract the alias and the expression before it
                        alias = alias_match.group(0)  # e.g., " AS customer_name"
                        concat_expression = full_expression[
                            : alias_match.start()
                        ]  
                    else:
                        # No alias present
                        alias = ""
                        concat_expression = full_expression

             
                    parts = [part.strip() for part in concat_expression.split("||")]
                    # Wrap in CONCAT and reattach the alias
                    return f"CONCAT({', '.join(parts)}){alias}"

                updated_select = re.sub(
                    r"\b\w+\s*\|\|.*?(?=\s*(?:AS\s+\w+|,|FROM|WHERE|GROUP|HAVING|ORDER|\Z))",
                    replace_concat,
                    select_part,
                    flags=re.IGNORECASE,
                )
             
                sanitized_query = (
                    updated_select + " FROM" + sanitized_query.split("FROM", 1)[1]
                )
                print(
                    f"Modified query for MySQL (replaced || with CONCAT): {sanitized_query}"
                )

        final_query = sanitized_query
        print(f"Final query: {final_query}")

        # Connect to MySQL
        conn = pymysql.connect(
            host="localhost", user="sql_user", password="SafePass@123", database=schema_name
        )
        cursor = conn.cursor()
        cursor.execute(final_query)

    
        if final_query.upper().startswith("SELECT"):
            data = cursor.fetchall()
            columns = (
                [desc[0] for desc in cursor.description] if cursor.description else []
            )
            results = (data, columns)
        else:
            conn.commit()
            results = cursor.rowcount

        conn.close()
        return results
    except Exception as e:
        return f"Error executing SQL query: {e}"



def parse_mongo_js_object(js_str: str):
    try:
        return json5.loads(js_str)
    except Exception as e:
        raise ValueError(f"Error parsing JS-like object: {e}")


def execute_mongodb_query(query: str, database: str):
    try:
        db_map = {
            "Bike Store": "bike_store",
            "AdventureWorks": "adventure_works",
            "FIFA": "fifa",
        }

        db_name = db_map.get(database)
        if not db_name:
            return "Error: Invalid database"

        client = MongoClient("mongodb://localhost:27017/")
        db = client[db_name]
        query = query.strip().replace("\n", " ")

        if query == "db.getCollectionNames()":
            return db.list_collection_names()

        if not query.startswith("db."):
            return "Error: Invalid MongoDB query syntax"

        collection_name = query.split(".")[1]

        if ".insertOne(" in query:
            doc_str = query.split(".insertOne(", 1)[1].rsplit(")", 1)[0]
            cleaned = doc_str.replace("null", "None")
            doc = ast.literal_eval(cleaned)
            result = db[collection_name].insert_one(doc)
            return {
                "acknowledged": result.acknowledged,
                "insertedId": str(result.inserted_id),
            }

        if ".insertMany(" in query:
            docs_str = query.split(".insertMany(", 1)[1].rsplit(")", 1)[0]
            cleaned = docs_str.replace("null", "None")
            docs = ast.literal_eval(cleaned)
            result = db[collection_name].insert_many(docs)
            return {
                "acknowledged": result.acknowledged,
                "insertedIds": [str(_id) for _id in result.inserted_ids],
            }

        if ".updateOne(" in query:
            args_str = (
                query.split(".updateOne(", 1)[1]
                .rsplit(")", 1)[0]
                .replace("null", "None")
            )
            parts = args_str.split("},", 1)
            if len(parts) != 2:
                return "Error: Invalid updateOne syntax"
            filter_dict = ast.literal_eval(parts[0] + "}")
            update_dict = ast.literal_eval(parts[1].strip())
            result = db[collection_name].update_one(filter_dict, update_dict)
            return {
                "acknowledged": result.acknowledged,
                "matchedCount": result.matched_count,
                "modifiedCount": result.modified_count,
            }

        if ".updateMany(" in query:
            args_str = (
                query.split(".updateMany(", 1)[1]
                .rsplit(")", 1)[0]
                .replace("null", "None")
            )
            parts = args_str.split("},", 1)
            if len(parts) != 2:
                return "Error: Invalid updateMany syntax"
            filter_dict = ast.literal_eval(parts[0] + "}")
            update_dict = ast.literal_eval(parts[1].strip())
            result = db[collection_name].update_many(filter_dict, update_dict)
            return {
                "acknowledged": result.acknowledged,
                "matchedCount": result.matched_count,
                "modifiedCount": result.modified_count,
            }

        if ".deleteOne(" in query:
            filter_dict = ast.literal_eval(
                query.split(".deleteOne(", 1)[1]
                .rsplit(")", 1)[0]
                .replace("null", "None")
            )
            result = db[collection_name].delete_one(filter_dict)
            return {
                "acknowledged": result.acknowledged,
                "deletedCount": result.deleted_count,
            }

        if ".deleteMany(" in query:
            filter_dict = ast.literal_eval(
                query.split(".deleteMany(", 1)[1]
                .rsplit(")", 1)[0]
                .replace("null", "None")
            )
            result = db[collection_name].delete_many(filter_dict)
            return {
                "acknowledged": result.acknowledged,
                "deletedCount": result.deleted_count,
            }

        if ".countDocuments(" in query:
            args_str = (
                query.split(".countDocuments(", 1)[1]
                .rsplit(")", 1)[0]
                .replace("null", "None")
            )
            filter_dict = ast.literal_eval(args_str)
            result = db[collection_name].count_documents(filter_dict)
            return {"count": result}

        if ".count(" in query:
            args_str = (
                query.split(".count(", 1)[1].rsplit(")", 1)[0].replace("null", "None")
            )
            filter_dict = ast.literal_eval(args_str)
            result = db[collection_name].count_documents(filter_dict)
            return {"count": result}

        if ".drop(" in query:
            db[collection_name].drop()
            return {"dropped": True}

        if ".distinct(" in query:
            args_str = (
                query.split(".distinct(", 1)[1]
                .rsplit(")", 1)[0]
                .replace("null", "None")
            )
            parts = args_str.split(",", 1)
            field = ast.literal_eval(parts[0].strip())
            filter_dict = ast.literal_eval(parts[1].strip()) if len(parts) > 1 else {}
            result = db[collection_name].distinct(field, filter_dict)
            return result

        
        if ".find(" in query:
            try:
                segments = query.split(".")
                collection_name = segments[1]
                find_call = segments[2]

                if not find_call.startswith("find("):
                    return "Error: Invalid find syntax"

                # Parse filter and projection
                find_args = find_call[len("find(") : -1]
                args_list = eval(f"[{find_args}]") if find_args else []
                filter_dict = args_list[0] if len(args_list) > 0 else {}
                projection_dict = args_list[1] if len(args_list) > 1 else {}

                cursor = db[collection_name].find(filter_dict, projection_dict)

                result_is_count = False  # track if count() is requested

                # Process chained operations
                for part in segments[3:]:
                    if part.startswith("sort("):
                        sort_dict = eval(part[len("sort(") : -1])
                        if isinstance(sort_dict, dict):
                            cursor = cursor.sort([(k, v) for k, v in sort_dict.items()])
                    elif part.startswith("skip("):
                        cursor = cursor.skip(int(part[len("skip(") : -1]))
                    elif part.startswith("limit("):
                        cursor = cursor.limit(int(part[len("limit(") : -1]))
                    elif part.startswith("min("):
                        min_dict = eval(part[len("min(") : -1])
                        cursor = cursor.min(min_dict)
                    elif part.startswith("max("):
                        max_dict = eval(part[len("max(") : -1])
                        cursor = cursor.max(max_dict)
                    elif part.startswith("project("):
                        proj_dict = eval(part[len("project(") : -1])
                        cursor = cursor.project(proj_dict)
                    elif part.startswith("count()"):
                        result_is_count = True

                return cursor.count() if result_is_count else list(cursor)

            except Exception as e:
                return f"Error executing MongoDB .find(): {e}"

        if ".aggregate(" in query:
            try:
                import re

                # Extract collection name
                collection_match = re.match(r"db\.(\w+)\.aggregate", query)
                if not collection_match:
                    return "Error: Could not determine collection name"
                collection_name = collection_match.group(1)

                # Extract content inside aggregate([...])
                agg_match = re.search(r"\.aggregate\(\s*(\[[\s\S]*\])\s*\)", query)
                if not agg_match:
                    return "Error: Could not parse aggregate pipeline"

                pipeline_str = agg_match.group(1).strip()
                # parse_mongo_js_object(): Custom function using json5.loads() to safely convert JavaScript-like syntax into Python dictionaries/lists.
                pipeline = parse_mongo_js_object(pipeline_str)

                return list(db[collection_name].aggregate(pipeline))

            except Exception as e:
                return f"Error executing MongoDB .aggregate(): {e}"

        if ".findOne(" in query:
            filter_dict = ast.literal_eval(
                query.split(".findOne(", 1)[1].rsplit(")", 1)[0].replace("null", "None")
            )
            return db[collection_name].find_one(filter_dict)

        return "Error: Unsupported MongoDB operation"

    except Exception as e:
        return f"Error executing MongoDB query: {e}"

