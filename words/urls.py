from django.urls import path, re_path
from . import views, io_dict

urlpatterns = [
    path('', views.index, name='index'),
#    path('allwords/', views.DictionaryEntriesView.as_view(), name='allwords'),
    path('allwords/', views.all_entries, name='allwords'),
#    path('allwords/edit', views.edit_entries, name='allwords-edit'),
    path('categories_and_dicts', views.categories_dicts, name='categories_and_dicts'),
    path('category/<int:pk>', views.category, name='category'),
    path('dictionary/<int:pk>', views.dictionary, name='dictionary'),
#    path('entry/<uuid:pk>/edit/', views.edit_entry, name='edit-entry'),
    path('entry/add/', views.add_entry, name='add-entry'),
    re_path(r'^entry/add/(?P<pk>\d+)$', views.add_entry, name='add-entry'),
    path('filters/', views.filters, name='filters'),
    path('per_page_url/', views.change_per_page, name='per_page_url'),
    path('export_to_file/', io_dict.export_to_file, name='export_to_file'),
]