import csv
import json
import os
from typing import List, Dict
from datetime import datetime


class CSVtoJSONConverter:
    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path
        self.json_file_path = os.path.splitext(csv_file_path)[0] + ".json"

    def infer_type(self, value: str):
        """Convert value to appropriate data type for MongoDB-style JSON"""
        if value is None or value.strip() == "" or value.lower() == "null":
            return None

        value = value.strip()

        # Try integer
        try:
            if value.isdigit() or (value[0] == '-' and value[1:].isdigit()):
                return int(value)
        except ValueError:
            pass

        # Try float
        try:
            if '.' in value:
                return float(value)
        except ValueError:
            pass

        # Try ISO date
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S"):
            try:
                dt = datetime.strptime(value, fmt)
                return dt.isoformat()
            except ValueError:
                continue

        # Return as string
        return value

    def convert(self) -> List[Dict]:
        result = []

        try:
            with open(self.csv_file_path, "r", encoding="utf-8") as csv_file:
                csv_reader = csv.DictReader(csv_file)

                if not csv_reader.fieldnames:
                    raise ValueError("CSV file is empty or has no headers")

                csv_reader.fieldnames = [field.strip() for field in csv_reader.fieldnames]
                print(f"Using headers as keys: {csv_reader.fieldnames}")

                for row in csv_reader:
                    cleaned_row = {}
                    for key, value in row.items():
                        inferred = self.infer_type(value)
                        if inferred is not None:
                            cleaned_row[key.strip()] = inferred
                    if cleaned_row:
                        result.append(cleaned_row)

            with open(self.json_file_path, "w", encoding="utf-8") as json_file:
                json.dump(result, json_file, indent=2)

            print(f"Successfully converted '{self.csv_file_path}' to '{self.json_file_path}'")
            return result

        except FileNotFoundError:
            print(f"Error: File '{self.csv_file_path}' not found")
            return []
        except Exception as e:
            print(f"Error during conversion: {str(e)}")
            return []


# Example usage
def main():
    your_csv_path = "data/adventure_works_csv/Sales.csv"
    converter = CSVtoJSONConverter(your_csv_path)
    result = converter.convert()

    if result:
        print("\nConverted data:")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
