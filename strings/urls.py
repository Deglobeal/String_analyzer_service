from django.urls import path
from . import views

urlpatterns = [
    # Handle both POST and GET for /strings
    path('strings', views.StringsView.as_view(), name='strings'),
    
    # Natural language filter - moved BEFORE the detail pattern to avoid conflicts
    path('strings/filter-by-natural-language', views.natural_language_filter, name='natural-language-filter'),
    
    # Handle GET and DELETE for specific string
    path('strings/<str:string_value>', views.StringDetailView.as_view(), name='string-detail'),
]