from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('book_detail/', views.view_book_detail, name='view_book_detail'),

]
