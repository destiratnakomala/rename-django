# core/forms.py

from django import forms

class MongoDBConnectionForm(forms.Form):
    host = forms.CharField(max_length=100, initial='localhost', required=True)
    port = forms.IntegerField(initial=27017, required=True)

class CreateDatabaseForm(forms.Form):
    database_name = forms.CharField(max_length=100, required=True, label='Database Name')
    collection_name = forms.CharField(max_length=100, required=True, label='Collection Name')



class DatabaseForm(forms.Form):
    db_name = forms.CharField(label='Database Name', max_length=100, required=True)

class CollectionForm(forms.Form):
    collection_name = forms.CharField(label='Collection Name', max_length=100, required=True)

class UploadFileForm(forms.Form):
    file = forms.FileField(label='Upload File', required=True)
