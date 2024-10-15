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
from .forms import UploadFileForm
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse


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
    # Directory where uploaded files are stored
    upload_directory = os.path.join(settings.MEDIA_ROOT)

    # Get the list of uploaded CSV files
    uploaded_files = [f for f in os.listdir(upload_directory) if f.endswith('.csv')]
    
    common_columns = []
    manipulated_result = None

    if request.method == 'POST':
        selected_files = request.POST.getlist('files')  # Get selected file names
        join_column = request.POST.get('join_column')  # Get the selected join column


        if len(selected_files) < 2:
            # Return an error message or handle the case where less than 2 files are selected
            return render(request, 'manipulate_data.html', {
                'uploaded_files': uploaded_files,
                'error': 'Please select at least two files for manipulation.'
            })

        # Read the selected CSV files into DataFrames
        dataframes = []
        for file in selected_files:
            file_path = os.path.join(upload_directory, file)
            df = pd.read_csv(file_path)
            dataframes.append(df)

        # Find common columns only if there are selected files
        if dataframes:
            common_columns = set(dataframes[0].columns)
            for df in dataframes[1:]:
                common_columns.intersection_update(df.columns)
            common_columns = list(common_columns)  # Convert set back to list

        # Perform manipulation if join column is selected and is in common columns
        if join_column in common_columns:
            merged_df = dataframes[0]
            for df in dataframes[1:]:
                merged_df = merged_df.merge(df, on=join_column, how='outer')



            #save file into result folder
            manipulation_path_file = os.path.join(settings.BASE_DIR, 'core/static/result/manipulation_result.csv')

            merged_df.to_csv(manipulation_path_file, index=False)
            # Convert manipulated DataFrame to HTML
            manipulated_result = merged_df.to_html(classes='table table-striped', index=False)
            


    context = {
        'uploaded_files': uploaded_files,
        'common_columns': common_columns,
        'manipulated_result': manipulated_result,
    }


    return render(request, 'manipulate_data.html', context)



@login_required
def get_common_columns(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        selected_files = body.get('files', [])
        upload_directory = os.path.join(settings.MEDIA_ROOT)

        
        dataframes = []
        
        # Read the selected CSV files into DataFrames
        for file in selected_files:
            file_path = os.path.join(upload_directory, file)
            df = pd.read_csv(file_path)
            dataframes.append(df)

        # Find common columns
        if dataframes:
            common_columns = set(dataframes[0].columns)
            for df in dataframes[1:]:
                common_columns.intersection_update(df.columns)
            common_columns = list(common_columns)  # Convert set back to list
        else:
            common_columns = []

        return JsonResponse({'common_columns': common_columns})

    return JsonResponse({'common_columns': []}, status=400)