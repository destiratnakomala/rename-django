import csv
import json
import os
import pandas as pd
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.http import JsonResponse
from pymongo.errors import ConnectionFailure
from pymongo import MongoClient
from .forms import MongoDBConnectionForm, CreateDatabaseForm
from .form import UploadFileForm
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from pymongo.errors import BulkWriteError




def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Save user data to a CSV file
            user_data_file = os.path.join(settings.BASE_DIR, 'core/static/user_data.csv')

            with open(user_data_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([user.username, user.email])  # Save username and email (not password)

            return redirect('login')  # Redirect to login after registration
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home after login
    return render(request, 'login.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

# #----------------DATABASE CONNECTION MONGO------------------




def connect_to_mongo(host, port):
    """Establish a connection to the MongoDB server."""
    try:
        mongo_client = MongoClient(host, port)
        mongo_client.admin.command('ping')
        return mongo_client    
    except ConnectionFailure:
        return None


@login_required
def mongo_home(request):
    """Render the MongoDB management home page."""
    databases = []
    connection_error = None
    create_db_error = None
    host = 'localhost'
    port = 27017

    if request.method == 'POST':
        form = MongoDBConnectionForm(request.POST)
        if form.is_valid():
            host = form.cleaned_data['host']
            port = form.cleaned_data['port']

            mongo_client = connect_to_mongo(host, port)
            if mongo_client:
                databases = mongo_client.list_database_names()
            else:
                connection_error = "Failed to connect to MongoDB. Please check your credentials."
    else:
        form = MongoDBConnectionForm()

    # Handle database and collection creation
    if request.method == 'POST' and 'create_db' in request.POST:
        create_db_form = CreateDatabaseForm(request.POST)
        if create_db_form.is_valid():
            database_name = create_db_form.cleaned_data['database_name']
            collection_name = create_db_form.cleaned_data['collection_name']

            mongo_client = connect_to_mongo(host, port)
            if mongo_client:
                # Create the database and collection
                db = mongo_client[database_name]
                db.create_collection(collection_name)

                # List updated databases
                databases = mongo_client.list_database_names()
            else:
                create_db_error = "Failed to connect to MongoDB. Please check your credentials."
    else:
        create_db_form = CreateDatabaseForm()

    # Handle database viewing
    if request.method == 'POST' and 'view_db' in request.POST:
        db_name = request.POST.get('view_db')
        # Redirect to the view database page, you can create a new view to show collections
        return redirect('view_database', db_name=db_name)

    # Handle database deletion
    if request.method == 'POST' and 'delete_db' in request.POST:
        db_name = request.POST.get('delete_db')

        mongo_client = connect_to_mongo(host, port)
        if mongo_client:
            # Drop the selected database
            mongo_client.drop_database(db_name)

            # List updated databases after deletion
            databases = mongo_client.list_database_names()

    return render(request, 'mongo_home.html', {
        'form': form,
        'create_db_form': create_db_form,
        'databases': databases,
        'connection_error': connection_error,
        'create_db_error': create_db_error,
    })

@login_required
def view_database(request, db_name):
    """View collections inside a specific database and handle collection deletion."""
    collections = []
    connection_error = None
    host = 'localhost'
    port = 27017

    # Connect to MongoDB
    mongo_client = connect_to_mongo(host, port)
    if mongo_client:
        db = mongo_client[db_name]
        collections = db.list_collection_names()

        # Handle collection deletion
        if request.method == 'POST' and 'delete_collection' in request.POST:
            collection_name = request.POST.get('delete_collection')
            if collection_name in collections:
                db.drop_collection(collection_name)
                # Refresh the list of collections after deletion
                collections = db.list_collection_names()

                # Handle collection addition
        if request.method == 'POST' and 'add_collection' in request.POST:
            new_collection_name = request.POST.get('new_collection_name')
            if new_collection_name:
                db.create_collection(new_collection_name)
                # Refresh the list of collections after addition
                collections = db.list_collection_names()

        # Handle file upload
        # Handle file upload
        if request.method == 'POST' and 'upload_file' in request.FILES:
            uploaded_file = request.FILES['upload_file']
            collection_name = request.POST.get('collection_name')

            if collection_name not in collections:
                messages.error(request, 'Please select a valid collection to upload to.')
                return redirect('view_database', db_name=db_name)

            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(uploaded_file)
                elif uploaded_file.name.endswith('.txt'):
                    df = pd.read_csv(uploaded_file, delimiter='\t')
                else:
                    messages.error(request, 'Unsupported file format. Please upload a CSV, XLS, XLSX, or TXT file.')
                    return redirect('view_database', db_name=db_name)

                # Handle NaN or duplicate '_id' values
                if '_id' in df.columns:
                    df['_id'] = df['_id'].where(pd.notnull(df['_id']), None)
                    if df['_id'].duplicated().any():
                        messages.error(request, 'Duplicate _id values detected. Please ensure unique _id values.')
                        return redirect('view_database', db_name=db_name)

                # Insert DataFrame into MongoDB collection
                db[collection_name].insert_many(df.to_dict('records'))
                messages.success(request, f'Successfully uploaded {uploaded_file.name} to {collection_name}.')

            except Exception as e:
                messages.error(request, f'Error processing the uploaded file: {e}')
                return redirect('view_database', db_name=db_name)



        # Handle combine operation
        if request.method == 'POST' and 'combine_collections' in request.POST:
            selected_collections = request.POST.getlist('selected_collections')
            new_collection_name = request.POST.get('new_collection_name_join')
            common_field = request.POST.get('common_field')  # Get the common field from the form
            join_type = request.POST.get('join_type')  # Get the common field from the form

            operation_type = request.POST.get('operation_type')  # Get the selected operation type

            if len(selected_collections) < 2:
                messages.error(request, 'Please select at least two collections to combine.')
                return redirect('view_database', db_name=db_name)

            # Perform the selected operation
            dataframes = []
            for collection in selected_collections:
                df = pd.DataFrame(list(db[collection].find()))
                dataframes.append(df)

                if '_id' in df.columns:
                    df = df.dropna(subset=['_id'])  # Drop rows with NaN in '_id'
                    if df['_id'].duplicated().any():
                        messages.error(request, 'Duplicate _id values detected. Please ensure unique _id values.')
                        return redirect('view_database', db_name=db_name)


            if dataframes:
                if operation_type == 'merge':
                    merged_df = pd.concat(dataframes, axis=0)
                      # Vertical stack
                elif operation_type == 'join':
                    merged_df = dataframes[0]
                    for df in dataframes[1:]:
                        merged_df = pd.merge(merged_df, df, on=common_field, how=join_type)  # Inner join
                elif operation_type == 'combine':
                    merged_df = dataframes[0]
                    for df in dataframes[1:]:
                        merged_df = pd.concat([merged_df, df], axis=1)  # Horizontal combine
                            # Handle NaN or duplicate '_id' values


                # Create a new collection with the merged or combined data
                db[new_collection_name].insert_many(merged_df.to_dict('records'))
                messages.success(request, f'Successfully combined collections into {new_collection_name}.')

    else:
        connection_error = "Failed to connect to MongoDB."

    return render(request, 'view_database_list.html', {
        'db_name': db_name,
        'collections': collections,
        'connection_error': connection_error,
    })



@login_required
def view_collection_data(request, db_name, collection_name):
    """View documents inside a specific collection."""
    documents = []
    connection_error = None
    host = 'localhost'
    port = 27017

    # Connect to MongoDB
    mongo_client = connect_to_mongo(host, port)
    if mongo_client:
        db = mongo_client[db_name]
        documents = list(db[collection_name].find())  # Fetch all documents from the collection
    else:
        connection_error = "Failed to connect to MongoDB."

    return render(request, 'view_collection_data.html', {
        'db_name': db_name,
        'collection_name': collection_name,
        'documents': documents,
        'connection_error': connection_error,
    })




#------------------------DATABASE END 






@login_required
def upload_file(request):
    if request.method == 'POST':
        form=UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return redirect('home')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


def handle_uploaded_file(f):
    upload_dir = os.path.join(settings.BASE_DIR, 'core/static/uploads/')
    os.makedirs(upload_dir, exist_ok=True)


    file_path= os.path.join(upload_dir, f.name)
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

@login_required
def view_files(request):
    upload_dir = os.path.join(settings.BASE_DIR, 'core/static/uploads/')
    files = os.listdir(upload_dir)

    if request.method == 'POST':
        selected_files = request.POST.getlist('selected_files')  # Get the selected files
        if selected_files:  # Check if any files were selected
            return view_file_contents(request, selected_files)

        # If no files are selected, return the same page with an error message
        error_message = "Please select at least one file."
        return render(request, 'view_files.html', {'files': files, 'error': error_message})

    return render(request, 'view_files.html', {'files': files})

@login_required
def view_selected_files(request):
    if request.method == 'POST':
        selected_files = request.POST.getlist('files')
        file_contents = {}

        for filename in selected_files:
            file_path = os.path.join(settings.BASE_DIR, 'core/static/uploads/', filename)
            if os.path.exists(file_path):
                # Read the CSV file into a pandas DataFrame
                df = pd.read_csv(file_path)
                file_contents[filename] = df.to_html(classes='table table-bordered', index=False)
            else:
                return HttpResponseBadRequest(f"File not found: {filename}")

        return render(request, 'selected_files.html', {'file_contents': file_contents})
    
    return redirect('view_files')  # Redirect if not a POST request


@login_required
def view_file_contents(request, selected_files):
    file_contents = {}  # Dictionary to hold filename and its contents

    for filename in selected_files:
        file_path = os.path.join(settings.BASE_DIR, 'core/static/uploads/', filename)  # Ensure this path is correct

        try:
            # Read the CSV file into a pandas DataFrame
            df = pd.read_csv(file_path)
            file_contents[filename] = df.to_html(classes='table table-bordered', index=False)  # Store contents
        except Exception as e:
            file_contents[filename] = f"Error reading file: {str(e)}"  # Store error message





@login_required
def data_submission(request):
    upload_dir = os.path.join(settings.BASE_DIR, 'core/static/uploads/')
    files = os.listdir(upload_dir)
    file_contents = {}

    # Always initialize the form
    form = UploadFileForm()

    if request.method == 'POST':
        # Handle file upload
        if 'file' in request.FILES:
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                handle_uploaded_file(request.FILES['file'])
                return redirect('data_submission')  # Reload the page after upload

        # Handle file viewing
        elif 'files' in request.POST:
            selected_files = request.POST.getlist('files')
            for filename in selected_files:
                file_path = os.path.join(upload_dir, filename)
                if os.path.exists(file_path):
                    try:
                        df = pd.read_csv(file_path)
                        file_contents[filename] = df.to_html(classes='table table-bordered', index=False)
                    except Exception as e:
                        file_contents[filename] = f"Error reading file: {str(e)}"

    return render(request, 'data_submission.html', {
        'form': form,
        'files': files,
        'file_contents': file_contents
    })





@login_required
def manipulate_data(request):
    upload_directory = os.path.join(settings.MEDIA_ROOT, 'uploads/')
    result_directory = os.path.join(settings.MEDIA_ROOT, 'results/')
    os.makedirs(result_directory, exist_ok=True)
    
    uploaded_files = [f for f in os.listdir(upload_directory) if f.endswith('.csv')]
    
    common_columns = []
    sort_columns = []
    manipulation_results = []  # List to store multiple manipulation results
    error = None  # To store any error messages

    if request.method == 'POST':
        selected_files = request.POST.getlist('files')
        operation = request.POST.get('operation')  # Get selected operation
        join_column = request.POST.get('join_column')  # Get the selected join column
        join_type = request.POST.get('join_type', 'outer')  # Get the selected join type
        sort_column = request.POST.get('sort_column')
        ascending = request.POST.get('ascending', 'true')
        csv_name = request.POST.get('csv_name', 'result')  # Get the custom CSV name, default to 'result'



        if operation == 'join':
            if len(selected_files) < 2:
                error = 'Please select at least two files for joining.'
            else:
                # Read the selected CSV files into DataFrames
                dataframes = []
                try:
                    for file in selected_files:
                        file_path = os.path.join(upload_directory, file)
                        df = pd.read_csv(file_path)
                        dataframes.append(df)
                except Exception as e:
                    error = f'Error reading {file}: {str(e)}'
                
                if not error:
                    # Find common columns
                    common_columns = set(dataframes[0].columns)
                    for df in dataframes[1:]:
                        common_columns.intersection_update(df.columns)
                    common_columns = list(common_columns)  # Convert set back to list

                    if join_column and join_column in common_columns:
                        try:
                            merged_df = dataframes[0]
                            for df in dataframes[1:]:
                                if join_type == 'concatenate':
                                    merged_df = pd.concat([merged_df, df], ignore_index=True)
                                else:
                                    merged_df = merged_df.merge(df, on=join_column, how=join_type)
                            
                            manipulated_result = merged_df.to_html(classes='table table-striped', index=False)
                            # Save the result with the specified CSV name
                            result_csv_path = os.path.join(result_directory, f'{csv_name}.csv')
                            merged_df.to_csv(result_csv_path, index=False)

                            # Store the manipulation result with its name
                            manipulation_results.append({'name': csv_name, 'result': manipulated_result})
                        except Exception as e:
                            error = f'Error during join operation: {str(e)}'
                    else:
                        error = 'Join column is invalid or not selected.'
        
        elif operation == 'sort' and len(selected_files)==1:
            if len(selected_files) != 1:
                error = 'Please select exactly one file for sorting.'
            else:
                selected_file = selected_files[0]
                file_path = os.path.join(upload_directory, selected_file)
                try:
                    df = pd.read_csv(file_path)
                    sort_columns = list(df.columns)
                except Exception as e:
                    error = f'Error reading {selected_file}: {str(e)}'
                
                if not error:
                    if sort_column and sort_column in sort_columns:
                        try:
                            sorted_df = df.sort_values(by=sort_column, ascending=(ascending.lower() == 'true'))
                            
                            manipulated_result = sorted_df.to_html(classes='table table-striped', index=False)

                            # Save the result with the specified CSV name
                            result_csv_path = os.path.join(result_directory, f'{csv_name}.csv')
                            sorted_df.to_csv(result_csv_path, index=False)

                            # Store the manipulation result with its name
                            manipulation_results.append({'name': csv_name, 'result': manipulated_result})
                        except Exception as e:
                            error = f'Error during sort operation: {str(e)}'
                    else:
                        error = 'Sort column is invalid or not selected.'

    context = {
        'uploaded_files': uploaded_files,
        'common_columns': common_columns,
        'sort_columns': sort_columns,
        'manipulation_results': manipulation_results,  # Pass all manipulation results to the template
        'error': error,  # Pass error messages to the template
    }


    return render(request, 'manipulate_data.html', context)



@login_required
def get_common_columns(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            selected_files = body.get('files', [])

            if len(selected_files) < 2:
                return JsonResponse({'common_columns': [], 'error': 'At least two files are required for join operation.'})

            upload_directory = os.path.join(settings.MEDIA_ROOT, 'uploads/')
            dataframes = []

            # Read the selected CSV files into DataFrames
            for file in selected_files:
                file_path = os.path.join(upload_directory, file)
                if not os.path.exists(file_path):
                    return JsonResponse({'error': f'File {file} does not exist.'}, status=400)

                try:
                    df = pd.read_csv(file_path)
                    dataframes.append(df)
                except Exception as e:
                    return JsonResponse({'error': f'Error reading {file}: {str(e)}'}, status=400)

            # Compute common columns for join
            common_columns = set(dataframes[0].columns)
            for df in dataframes[1:]:
                common_columns.intersection_update(df.columns)
            common_columns = list(common_columns)

            return JsonResponse({'common_columns': common_columns})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'common_columns': []}, status=400)

@login_required
def get_sort_columns(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            selected_files = body.get('files', [])

            if len(selected_files) != 1:
                return JsonResponse({'sort_columns': [], 'error': 'Please select exactly one file for sorting.'})

            upload_directory = os.path.join(settings.MEDIA_ROOT, 'uploads/')
            file_path = os.path.join(upload_directory, selected_files[0])

            if not os.path.exists(file_path):
                return JsonResponse({'error': f'File {selected_files[0]} does not exist.'}, status=400)

            try:
                df = pd.read_csv(file_path)
                sort_columns = list(df.columns)
            except Exception as e:
                return JsonResponse({'error': f'Error reading {selected_files[0]}: {str(e)}'}, status=400)

            return JsonResponse({'sort_columns': sort_columns})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'sort_columns': []}, status=400)

# ... (Other functions remain unchanged)



@login_required
def view_manipulation_result(request):
    result_dir= os.path.join(settings.MEDIA_ROOT, 'results/')
    results = [f for f in os.listdir(result_dir) if f.endswith('.csv')]

    if request.method == 'POST':
        selected_file = request.POST.get('selected_file')
        if selected_file:
            file_path = os.path.join(result_dir, selected_file)
            if os.path.exists(file_path):
                df = pd.read_csv(file_path)
                file_contents = df.to_html(classes='table table-bordered', index=False)
                return render(request, 'view_manipulation_result.html', {'file_contents': file_contents, 'results': results})

    return render(request, 'view_manipulation_result.html', {'results': results})



