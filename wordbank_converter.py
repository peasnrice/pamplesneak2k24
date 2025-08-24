import csv
import json

csv_file_path = "data/examplewords.csv"
json_file_path = "data/examplewords.json"

data = []
with open(csv_file_path, "r") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        data.append(
            {
                "model": "gameroom.exampleword",  # Replace 'yourapp' with your actual app name
                "pk": None,  # Django will automatically assign primary keys
                "fields": {
                    "category": row["category"],
                    "difficulty": row["difficulty"],
                    "word": row["word"],
                    "note": row["note"],
                },
            }
        )

with open(json_file_path, "w") as json_file:
    json.dump(data, json_file)

# Data converted to Django fixture format and saved as 'examplewords.json'
