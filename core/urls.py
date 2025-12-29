from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('board/<int:board_id>/', views.board_detail, name='board_detail'),
    path('boards/create/', views.create_board, name='create_board'),
    path('board/<int:board_id>/add-pin/', views.create_pin, name='create_pin'),
    path('pin/<int:pin_id>/', views.pin_detail, name='pin_detail'),
    path('pin/<int:pin_id>/edit/', views.edit_pin, name='edit_pin'),
    path('pin/<int:pin_id>/delete/', views.delete_pin, name='delete_pin'),
    path('profile/', views.profile, name='profile'),
    path('user/<str:username>/', views.public_profile, name='public_profile'),
    path('feed/', views.feed, name='feed'),
    path('user/<str:username>/follow/', views.toggle_follow, name='toggle_follow'),
    path('home-feed/', views.personal_feed, name='personal_feed'),
    path('pin/<int:pin_id>/save/', views.save_pin, name='save_pin'),
    path('pin/<int:pin_id>/like/', views.toggle_like, name='toggle_like'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('pin/<int:pin_id>/comment/', views.add_comment, name='add_comment'),
    path("search/", views.search, name="search"),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path("u/<str:username>/followers/", views.followers_list, name="followers_list"),
    path("u/<str:username>/following/", views.following_list, name="following_list"),
    path("board/<int:board_id>/follow/", views.toggle_board_follow, name="toggle_board_follow"),
    path("board/<int:board_id>/followers/", views.board_followers, name="board_followers"),


]
