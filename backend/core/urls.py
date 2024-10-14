from django.urls import path
from .views import home, register, user_login, user_logout, upload_file, view_files, view_file_contents, view_selected_files

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('upload/', upload_file, name='upload_file'),
    path('view_files/', view_files, name='view_files'),
    path('view_file/<str:filename>/', view_file_contents, name='view_file_contents'),
    path('view_selected_files', view_selected_files, name= 'view_selected_files')
]
