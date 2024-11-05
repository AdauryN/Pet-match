from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create_pet/', views.create_pet, name='create_pet'),
    path('matches/', views.find_matches, name='find_matches'),
    path('send_message/<int:recipient_id>/', views.send_message, name='send_message'),
    path('inbox/', views.inbox, name='inbox'),
    path('search/', views.search, name='search'),
]
