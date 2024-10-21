from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId

def remove_duplicates(collection):
    """Remove duplicates from the specified MongoDB collection."""
    sample_doc = collection.find_one()
    if sample_doc:
        group_key = {key: f"${key}" for key in sample_doc.keys() if key != "_id"}
        pipeline = [
            {
                "$group": {
                    "_id": group_key,
                    "doc": {"$first": "$$ROOT"}
                }
            },
            {
                "$replaceRoot": {"newRoot": "$doc"}
            }
        ]
        result = list(collection.aggregate(pipeline))
        collection.delete_many({})  # Remove all documents
        collection.insert_many(result)  # Insert unique documents back
        print('Duplicates removed successfully.')
    else:
        print('No documents found in the collection.')

def remove_column(collection, column_name):
    """Remove a specified column from the collection."""
    collection.update_many({}, {"$unset": {column_name: ""}})
    print(f'Column "{column_name}" removed from all documents.')

def aggregate_columns(collection, column_a, column_b, new_column_name, operation):
    """Create a new column based on the arithmetic operation between two specified columns."""
    
    # Define the aggregation operation based on user input
    operation_stage = {}
    if operation == 'sum':
        operation_stage = {"$add": [f"${column_a}", f"${column_b}"]}
    elif operation == 'subtract':
        operation_stage = {"$subtract": [f"${column_a}", f"${column_b}"]}
    elif operation == 'multiply':
        operation_stage = {"$multiply": [f"${column_a}", f"${column_b}"]}
    elif operation == 'divide':
        operation_stage = {"$divide": [f"${column_a}", f"${column_b}"]}
    else:
        print(f'Operation "{operation}" not recognized.')
        return

    # Use aggregation to calculate and update the field
    pipeline = [
        {
            "$addFields": {
                new_column_name: operation_stage
            }
        },
        {
            "$out": collection.name  # This will overwrite the existing collection with updated fields
        }
    ]

    # Perform the aggregation and update the collection
    collection.aggregate(pipeline)
    
    # Display the updated documents
    updated_docs = list(collection.find())
    print(f'Column "{new_column_name}" created using the "{operation}" operation between "{column_a}" and "{column_b}".')
    print("\nUpdated documents:")
    for doc in updated_docs:
        print(doc)

def filter_documents(collection, field_name, operator, value):
    """Filter documents based on a specified field and value, keeping only those that match."""
    try:
        value = float(value)  # Ensure numeric comparison when needed
    except ValueError:
        pass  # Keep it as a string if conversion to float fails

    query = {}
    if operator == '==':
        query = {field_name: value}
    elif operator == '>=':
        query = {field_name: {"$gte": value}}
    elif operator == '<=':
        query = {field_name: {"$lte": value}}
    elif operator == '>':
        query = {field_name: {"$gt": value}}
    elif operator == '<':
        query = {field_name: {"$lt": value}}
    else:
        print(f'Operator "{operator}" not recognized.')
        return

    # Display filtered documents for verification
    filtered_documents = list(collection.find(query))
    print(f'Filtered documents based on {field_name} {operator} {value}:')
    for doc in filtered_documents:
        print(doc)

    # Remove documents that don't match the filter
    collection.delete_many({"$nor": [query]})  # Delete documents that don't match the query
    print(f"Collection updated: only documents where {field_name} {operator} {value} are retained.")

def sort_documents(collection, sort_field, order='asc'):
    """Sort documents based on a specified field and update the collection with the sorted order."""
    sort_order = ASCENDING if order == 'asc' else DESCENDING
    sorted_documents = list(collection.find().sort(sort_field, sort_order))

    # Print sorted documents for verification
    print(f'Sorted documents by "{sort_field}" in {"ascending" if order == "asc" else "descending"} order:')
    for doc in sorted_documents:
        print(doc)

    # Delete all documents from the collection
    collection.delete_many({})

    # Reinsert the documents in the sorted order
    collection.insert_many(sorted_documents)
    print(f'Collection updated with documents sorted by "{sort_field}" in {"ascending" if order == "asc" else "descending"} order.')

def rename_column(collection, old_name, new_name):
    """Rename a specified column in the collection."""
    collection.update_many({}, {"$rename": {old_name: new_name}})
    print(f'Column "{old_name}" renamed to "{new_name}".')

def change_data_type(collection, column_name, new_type):
    """Change the data type of a specified column in the collection."""
    # Here we handle basic types: 'int', 'float', 'str'
    if new_type == 'int':
        collection.update_many({}, [{'$set': {column_name: {'$toInt': f'${column_name}'}}}])
    elif new_type == 'float':
        collection.update_many({}, [{'$set': {column_name: {'$toDouble': f'${column_name}'}}}])
    elif new_type == 'str':
        collection.update_many({}, [{'$set': {column_name: {'$toString': f'${column_name}'}}}])
    else:
        print(f'Unsupported data type "{new_type}".')
        return
    print(f'Data type of column "{column_name}" changed to "{new_type}".')

def execute_script(collection, script):
    """Execute a custom script on the collection."""
    try:
        # Use exec to run the script within a limited scope
        exec_locals = {"collection": collection}  # Provide the collection to the script
        exec(script, {}, exec_locals)
        print("Script executed successfully.")
    except Exception as e:
        print(f"Error executing script: {e}")


def main():
    db_name = input("Enter the database name: ")
    collection_name = input("Enter the collection name: ")

    # Connect to MongoDB
    client = MongoClient('localhost', 27017)
    db = client[db_name]
    collection = db[collection_name]

    while True:
        print("\nSelect an operation:")
        print("1. Remove Duplicates")
        print("2. Remove Column")
        print("3. Aggregate Columns")
        print("4. Filter Documents")
        print("5. Sort Documents")
        print("6. Rename Column")
        print("7. Change Data Type")
        print("8. Execute Script")
        print("9. Exit")

        choice = input("Enter your choice (1-9): ")

        if choice == '1':
            remove_duplicates(collection)

        elif choice == '2':
            column_name = input("Enter the name of the column to remove: ")
            remove_column(collection, column_name)

        elif choice == '3':
            column_a = input("Enter the name of Column A: ")
            column_b = input("Enter the name of Column B: ")
            new_column_name = input("Enter the name of the new column for the operation result: ")
            operation_agg = input("Enter the operation (sum, subtract, multiply, divide): ")

            aggregate_columns(collection, column_a, column_b, new_column_name, operation_agg)

        elif choice == '4':
            field_name = input("Enter the field name to filter by: ")
            operator = input("Enter the operator (==, >=, <=, >, <): ")
            value = input("Enter the value to filter: ")
            filter_documents(collection, field_name, operator, value)

        elif choice == '5':
            sort_field = input("Enter the field name to sort by: ")
            order = input("Enter sort order (asc/desc): ").lower()
            sort_documents(collection, sort_field, order)

        elif choice == '6':
            old_name = input("Enter the current column name: ")
            new_name = input("Enter the new column name: ")
            rename_column(collection, old_name, new_name)

        elif choice == '7':
            column_name = input("Enter the name of the column to change type: ")
            new_type = input("Enter the new data type (int, float, str): ")
            change_data_type(collection, column_name, new_type)

        elif choice == '8':
            script = input("Enter your script: ")
            execute_script(collection, script)

        elif choice == '9':
            print("Exiting.")
            break

        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
