from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_root, name='api-root'),  # Add this line
    path('analyze', views.create_analyze_string, name='create-analyze-string'),
    path('strings', views.get_all_strings, name='get-all-strings'),
    path('strings/<str:string_value>', views.get_string, name='get-string'),
    path('strings/<str:string_value>/delete', views.delete_string, name='delete-string'),
    path('strings/filter/natural', views.filter_by_natural_language, name='filter-natural-language'),
]