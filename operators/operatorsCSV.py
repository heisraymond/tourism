"""
   This file will extract data from MongoDB and store
   it in a CSV file as an excel file.
"""
import os
import sys
import csv

# Add parent directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mongodb import operatorCollection

# Fetch all documents from MongoDB
data = list(operatorCollection.find())

# Remove MongoDB's default "_id" field
for doc in data:
    doc.pop('_id', None)

# Get all possible keys (columns) from the documents
# This ensures you don't miss any keys even if some documents are missing them
all_keys = set()
for doc in data:
    all_keys.update(doc.keys())
all_keys = all_keys  

# Write to CSV
with open("operator_data.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=all_keys)
    writer.writeheader()
    writer.writerows(data)
