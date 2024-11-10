from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('create_pet/', views.create_pet, name='create_pet'),
    path('matches/', views.find_matches, name='find_matches'),
    path('send_message/<int:recipient_id>/', views.send_message, name='send_message'),
    path('inbox/', views.inbox, name='inbox'),
    path('search/', views.search, name='search'),
    path('profile/', views.profile, name='profile'),
    path('matches/', views.find_matches, name='find_matches'),
    path('send_message/<int:recipient_id>/', views.send_message, name='send_message'),
    path('inbox/', views.inbox, name='inbox'),
    path('edit_pet/<int:pet_id>/', views.edit_pet, name='edit_pet'),
    path('delete_pet/<int:pet_id>/', views.delete_pet, name='delete_pet'),
    path('preferences/create/', views.create_preferences, name='create_preferences'),
    path('preferences/edit/<int:pet_id>/', views.edit_preferences, name='edit_preferences'),
    path('pet/<int:pet_id>/', views.pet_detail, name='pet_detail'),
    path('preferences/create/<int:pet_id>/', views.create_preferences, name='create_preferences'),
]
