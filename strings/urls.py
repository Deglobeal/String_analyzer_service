from django.urls import path
from . import views

urlpatterns = [
    path('strings', views.create_analyze_string, name='create-analyze-string'),
    path('strings/<str:string_value>', views.get_string_analysis, name='get-string-analysis'),
    path('strings', views.list_strings_with_filters, name='list-strings-with-filters'),
    path('strings/filter-by-natural-language', views.filter_by_natural_language, name='filter-by-natural-language'),
    path('strings/<str:string_value>', views.delete_string_analysis, name='delete-string-analysis'),
]