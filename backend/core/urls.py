from django.urls import path
from .views import ( home, register, user_login, user_logout, upload_file, view_files, view_file_contents, view_selected_files, manipulate_data, get_common_columns, data_submission,view_manipulation_result 
                    ,mongo_home, 
                    view_database, 
                    view_collection_data

                    
    )

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('view_file/<str:filename>/', view_file_contents, name='view_file_contents'),
    path('view_selected_files/', view_selected_files, name= 'view_selected_files'), 
    path('data_submission/', data_submission, name= 'data_submission'),
    path('manipulate_data/', manipulate_data, name= 'manipulate_data'), 
    path('get_common_columns/', get_common_columns, name='get_common_columns'),
    path('view_manipulation_result/', view_manipulation_result, name= 'view_manipulation_result'),
    path('mongo/', mongo_home, name='mongo_home'),
    path('view_database/<str:db_name>/', view_database, name='view_database'),
    path('view_collection/<str:db_name>/<str:collection_name>/', view_collection_data, name='view_collection_data'),



]




