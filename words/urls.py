from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('categories_and_dicts', views.categories_dicts, name='categories_and_dicts'),
    path('category/<int:pk>', views.category, name='category'),
    path('dictionary/<int:pk>', views.dictionary, name='dictionary'),
]