from django.urls import path
from . import views

urlpatterns = [
    # Natural language filter - put this FIRST to avoid conflicts
    path('strings/filter-by-natural-language', views.natural_language_filter, name='natural-language-filter'),
    
    # DELETE - Delete string analysis
    path('strings/delete/<str:string_value>', views.delete_string_analysis, name='delete-string'),
    
    # GET - Get specific string analysis
    path('strings/<str:string_value>', views.get_string_analysis, name='get-string'),
    
    # POST - Create string analysis
    path('strings', views.create_string_analysis, name='create-string'),
    
    # GET - Get all strings with filters
    path('strings-list', views.get_all_strings, name='get-all-strings'),
]