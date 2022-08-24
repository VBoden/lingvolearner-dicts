from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('allwords/', views.DictionaryEntriesView.as_view(), name='allwords'),
    path('categories_and_dicts', views.categories_dicts, name='categories_and_dicts'),
    path('category/<int:pk>', views.category, name='category'),
    path('dictionary/<int:pk>', views.dictionary, name='dictionary'),
    path('entry/<uuid:pk>/edit/', views.edit_entry, name='edit-entry'),
    path('entry/add/', views.add_entry, name='add-entry'),
]