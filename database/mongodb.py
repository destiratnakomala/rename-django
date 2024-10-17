from pymongo import MongoClient
import json
import pandas as pd

def connect_to_mongo():
    """Establish a connection to the MongoDB server."""
    mongo_client = MongoClient('localhost', 27017)
    return mongo_client

def list_databases(client):
    """List all databases in the MongoDB server."""
    databases = client.list_database_names()
    print("\nCurrent databases:")
    for db in databases:
        print(f"- {db}")
    return databases

def create_database(client):
    """Prompt the user to enter a new database name and create it."""
    db_name = input("Enter the name of the database you want to create: ")
    db = client[db_name]
    print(f"Database '{db_name}' created.")
    return db_name, db  # Return both the name and the db object

def create_collection(db):
    """Prompt the user to enter a new collection name and create it."""
    collection_name = input("Enter the name of the collection you want to create: ")
    collection = db[collection_name]
    print(f"Collection '{collection_name}' created.")
    return collection_name  # Return the collection name

def upload_file_to_collection(collection):
    """Prompt the user to upload a file and insert data into the collection."""
    file_path = input("Enter the path to the JSON or CSV file you want to upload: ")

    # Check the file extension
    if file_path.endswith('.json'):
        with open(file_path) as file:
            data = json.load(file)
            if isinstance(data, dict):  # If it's a single document
                collection.insert_one(data)
                print("Data uploaded to the collection.")
            elif isinstance(data, list):  # If it's a list of documents
                collection.insert_many(data)
                print("Data uploaded to the collection.")
            else:
                print("Unsupported JSON format.")
    
    elif file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
        collection.insert_many(df.to_dict(orient='records'))
        print("Data uploaded to the collection.")
    
    else:
        print("Unsupported file type. Please upload a JSON or CSV file.")

def show_collections(db):
    """Show all collections in the specified database."""
    collections = db.list_collection_names()
    print("\nCollections in the database:")
    for collection in collections:
        print(f"- {collection}")
    return collections

def show_collection_data(collection):
    """Display all documents in the specified collection."""
    documents = collection.find()
    print("\nDocuments in the collection:")
    for doc in documents:
        print(doc)

def main():
    """Main function to run the interactive MongoDB script."""
    mongo_client = connect_to_mongo()
    
    while True:
        # List current databases
        databases = list_databases(mongo_client)
        
        # Ask if user wants to create a new database or select an existing one
        action = input("Do you want to (1) create a new database or (2) select an existing one? (enter 1 or 2): ").strip()
        
        if action == '1':
            # Create a new database
            db_name, db = create_database(mongo_client)
            
            # Create a collection in the new database
            collection_name = create_collection(db)
            
            # Check if the user wants to upload a file to the collection
            upload_choice = input("Do you want to upload a file to the collection? (yes/no): ").strip().lower()
            if upload_choice == 'yes':
                upload_file_to_collection(db[collection_name])
        
        elif action == '2':
            # Select an existing database
            db_name = input("Enter the name of the database you want to select: ")
            if db_name in databases:
                db = mongo_client[db_name]
                collections = show_collections(db)
                
                # Select a collection and show its data
                collection_name = input("Enter the name of the collection you want to view: ")
                if collection_name in collections:
                    show_collection_data(db[collection_name])
                else:
                    print(f"Collection '{collection_name}' does not exist in database '{db_name}'.")
            else:
                print(f"Database '{db_name}' does not exist.")

        # Check if the user wants to continue
        another_db = input("Do you want to perform another action? (yes/no): ").strip().lower()
        if another_db != 'yes':
            print("Exiting...")
            break

    # Close the MongoDB connection
    mongo_client.close()

if __name__ == "__main__":
    main()
