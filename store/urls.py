from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'store'

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('register/', views.register_view, name='register'),
    path('beats/', views.beat_list, name='beat_list'),
    path('explore/', views.genres, name='genres'),
    path('explore/beats/', views.explore_beats, name='explore_beats'),
    path('explore/loops/', views.explore_loops, name='explore_loops'),
    path('explore/soundkits/', views.explore_soundkits, name='explore_soundkits'),
    path('explore/presets/', views.explore_presets, name='explore_presets'),
    path('trending/', views.trending, name='trending'),
    path('genre/<str:genre_name>/', views.genre_view, name='genre'),
    path('beat/<int:pk>/', views.beat_detail, name='beat_detail'),
    path('upload/', views.beat_upload, name='beat_upload'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('favorites/', views.favorites_view, name='favorites'),
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
    path('api/cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('beat/<int:beat_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:comment_id>/upvote/', views.upvote_comment, name='upvote_comment'),
    path('comment/<int:comment_id>/replies/', views.get_comment_replies, name='get_comment_replies'),
    path('search/', views.search, name='search'),
    path('checkout/', views.checkout, name='checkout'),
    path('producers/', views.producer_list, name='producers'),
    path('cart/', views.cart_view, name='cart'),
]
