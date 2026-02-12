from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Blog Management
    path('blog/create/', views.create_blog_view, name='create_blog'),
    path('blog/<int:blog_id>/edit/', views.edit_blog_view, name='edit_blog'),
    path('blog/<int:blog_id>/delete/', views.delete_blog_view, name='delete_blog'),
    path('my-blogs/', views.my_blogs_view, name='my_blogs'),
    
    # Category Management
    path('categories/', views.manage_categories_view, name='manage_categories'),
    
    # Public Blog Pages
    path('blogs/', views.blog_list_view, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail_view, name='blog_detail'),
    path('category/<slug:slug>/', views.category_blogs_view, name='category_blogs'),
]