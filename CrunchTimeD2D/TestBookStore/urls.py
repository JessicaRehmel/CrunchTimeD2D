from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('book_detail/', views.view_book_detail, name='view_book_detail'),
    path('submit_onix/', views.submit_onix, name='submit_onix'),
    path('process_onix/', views.process_onix, name='process_onix'),
]
