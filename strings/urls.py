from django.urls import path
from . import views

urlpatterns = [
    # POST endpoint for creating strings
    path('analyze', views.create_analyze_string, name='create-analyze-string'),
    
    # GET endpoint for retrieving all strings with filtering
    path('strings', views.get_all_strings, name='get-all-strings'),
    
    # GET endpoint for specific string
    path('strings/<str:string_value>', views.get_string, name='get-string'),
    
    # DELETE endpoint for specific string  
    path('strings/<str:string_value>/delete', views.delete_string, name='delete-string'),
    
    # Natural language filtering endpoint
    path('strings/filter/natural', views.filter_by_natural_language, name='filter-natural-language'),
]