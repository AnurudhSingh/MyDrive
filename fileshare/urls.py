# fileshare/urls.py

from django.urls import path, include
from . import views
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/login/', views.custom_login, name='login'),
    path('', views.dashboard, name='dashboard'),
    path('<int:folder_id>/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('create-folder/', views.create_folder, name='create_folder'),
    path('upload-file/', views.upload_file, name='upload_file'),  # Updated URL pattern
    path('upload-file/<int:folder_id>/', views.upload_file, name='upload_file'),
    path('share/<str:item_type>/<int:item_id>/', views.share, name='share'),
    path('shared-files/', views.shared_files, name='shared_files'),
    path('settings/', views.settings, name='settings'),
    path('starred/', views.starred, name='starred'),
    path('trash/', views.trash, name='trash'),
    path('rename_folder/<int:folder_id>/', views.rename_folder, name='rename_folder'),
    path('rename_file/<int:file_id>/', views.rename_file, name='rename_file'),
    path('delete_folder/<int:folder_id>/', views.delete_folder, name='delete_folder'),
    path('delete_file/<int:file_id>/', views.delete_file, name='delete_file'),
    path('restore_folder/<int:folder_id>/', views.restore_folder, name='restore_folder'),
    path('restore_file/<int:file_id>/', views.restore_file, name='restore_file'),
    path('toggle-star/<int:file_id>/', views.toggle_star, name='toggle_star'),
    path('untoggle-star/<int:file_id>/', views.untoggle_star, name='untoggle_star'),
    path('search/', views.search_files, name='search_files'),
    path('folder/<int:folder_id>/', views.view_folder, name='view_folder'),
    path('delete_permanently/<int:file_id>/', views.delete_permanently, name='delete_permanently'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
]
