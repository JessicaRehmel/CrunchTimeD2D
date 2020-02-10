from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('book_detail/<slug:bookId>/', views.view_book_detail, name='view_book_detail'),
    path('submit_onix/', views.submit_onix, name='submit_onix'),
]

#r'^polls/(?P<poll_id>\d+)/$'
#r'^polls/(?P<string>[\w\-]+)/$'