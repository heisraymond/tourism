from pymongo import MongoClient

# Replace this with the connection string from MongoDB Compass
connection = "mongodb://localhost:27017"  # Default if you're running it locally

# Connect to MongoDB
client = MongoClient(connection)

# Access a database (it will be created if it doesn't exist)
db = client["tourism"]

# Access a collection (it will also be created if it doesn't exist)
collection = db["operatorURLS"]

operatorCollection = db["operatorDetails"]

