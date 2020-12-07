from django.urls import path

from posts import views


urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new_post, name='new_post'),
    path('group/<slug:slug>/', views.group_posts, name='group_posts'),
    path('group/', views.group_list, name='group_list'),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    path('<str:username>/<int:post_id>/edit/',
         views.post_edit, name='post_edit'),
    path('<str:username>/<int:post_id>/comment',
         views.add_comment, name='add_comment'),
]
