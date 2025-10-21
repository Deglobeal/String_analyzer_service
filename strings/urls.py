# strings/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('strings', views.strings_list_handler, name='strings-list-handler'),  # GET & POST
    path('strings/<str:string_value>', views.strings_detail_handler, name='strings-detail-handler'),  # GET & DELETE
    path('strings/filter-by-natural-language', views.filter_by_natural_language, name='filter-natural-language'),
]
