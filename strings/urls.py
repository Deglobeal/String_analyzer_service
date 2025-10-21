from django.urls import path
from . import views

urlpatterns = [
    # Combined endpoint for POST (create) and GET (list)
    path('strings', views.strings_list_handler, name='strings-list'),
    
    # Combined endpoint for GET (specific) and DELETE
    path('strings/<str:string_value>', views.strings_detail_handler, name='strings-detail'),
    
    # Natural language filtering
    path('strings/filter-by-natural-language', views.filter_by_natural_language, name='filter-by-natural-language'),
]