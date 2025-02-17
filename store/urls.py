<<<<<<< HEAD
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.beat_list, name='beat_list'),
    path('explore/', views.genres, name='genres'),
    path('beat/<int:pk>/', views.beat_detail, name='beat_detail'),
    path('upload/', views.beat_upload, name='beat_upload'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/<str:username>/follow/', views.follow_user, name='follow_user'),
    path('profile/<str:username>/unfollow/', views.unfollow_user, name='unfollow_user'),
    path('beat/<int:pk>/delete/', views.delete_beat, name='delete_beat'),
    path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('beat/<int:pk>/edit/', views.beat_edit, name='beat_edit'),
    path('beat/<int:pk>/delete/', views.beat_delete, name='beat_delete'),
    path('api/favorites/<int:beat_id>/', views.favorite_beat, name='favorite_beat'),
    path('api/favorites/check/<int:beat_id>/', views.check_favorite, name='check_favorite'),
    path('api/cart/add/', views.add_to_cart, name='add_to_cart'),
    path('api/cart/check/<int:beat_id>/', views.check_cart, name='check_cart'),
    path('beat/<int:beat_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:comment_id>/upvote/', views.upvote_comment, name='upvote_comment'),
    path('comment/<int:comment_id>/replies/', views.get_comment_replies, name='get_comment_replies'),
]

=======
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.beat_list, name='beat_list'),
    path('explore/', views.genres, name='genres'),
    path('beat/<int:pk>/', views.beat_detail, name='beat_detail'),
    path('upload/', views.beat_upload, name='beat_upload'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('beat/<int:pk>/delete/', views.delete_beat, name='delete_beat'),
    path('login/', auth_views.LoginView.as_view(template_name='store/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('beat/<int:pk>/edit/', views.beat_edit, name='beat_edit'),
    path('beat/<int:pk>/delete/', views.beat_delete, name='beat_delete'),
]

>>>>>>> 43e6d2dca8d245f001e712240bfadecec0527f1e
