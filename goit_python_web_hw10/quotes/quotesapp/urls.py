from django.urls import path
from . import views

app_name = 'quotesapp'

urlpatterns = [
    path('', views.main, name='main'),
    path('add-tag/', views.add_tag, name='add-tag'),
    path('add-author/', views.add_author, name='add-author'),
    path('quote/', views.quote, name='quote'),
    path('author/<int:author_id>', views.author, name="author"),
    path('seed/', views.seed, name='seed'),
    path('seed/<str:source>', views.seed, name='seed'),
    path('page/<int:page>', views.main, name='main'),
    path('tag/<str:tag_name>', views.tag, name='tag'),
]
