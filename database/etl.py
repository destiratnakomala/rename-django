from pymongo import MongoClient

def remove_duplicates(db_name, collection_name):
    """Remove duplicates from the specified MongoDB collection."""
    # Connect to MongoDB
    client = MongoClient('localhost', 27017)
    db = client[db_name]
    collection = db[collection_name]

    # Get a sample document to determine the fields dynamically
    sample_doc = collection.find_one()

    if sample_doc:
        # Create a group key dynamically based on all fields except `_id`
        group_key = {key: f"${key}" for key in sample_doc.keys() if key != "_id"}

        # Logic to remove duplicates
        pipeline = [
            {
                "$group": {
                    "_id": group_key,  # Group by all fields except `_id`
                    "doc": {"$first": "$$ROOT"}  # Keep the first occurrence
                }
            },
            {
                "$replaceRoot": {"newRoot": "$doc"}  # Replace root with the grouped document
            }
        ]

        # Execute the aggregation pipeline
        result = list(collection.aggregate(pipeline))

        # Clear the existing collection
        collection.delete_many({})
        
        # Insert unique documents back into the collection
        collection.insert_many(result)

        print('Duplicates removed successfully.')
    else:
        print('No documents found in the collection.')

if __name__ == "__main__":
    # Accept user input for database and collection names
    db_name = input("Enter the database name: ")
    collection_name = input("Enter the collection name: ")
    
    # Call the function to remove duplicates
    remove_duplicates(db_name, collection_name)
