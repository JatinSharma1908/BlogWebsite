from django.urls import path
from . import views

urlpatterns = [
    # Public routes
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Blog Management (Authors)
    path('blog/create/', views.create_blog_view, name='create_blog'),
    path('blog/<int:blog_id>/edit/', views.edit_blog_view, name='edit_blog'),
    path('blog/<int:blog_id>/delete/', views.delete_blog_view, name='delete_blog'),
    path('blog/<int:blog_id>/submit/', views.submit_blog_for_review, name='submit_blog'),
    path('my-blogs/', views.my_blogs_view, name='my_blogs'),
    
    # Category Management
    path('categories/', views.manage_categories_view, name='manage_categories'),
    
    # Blog Moderation (Moderators/Admin)
    path('moderate/blogs/', views.moderate_blogs_view, name='moderate_blogs'),
    path('moderate/blog/<int:blog_id>/approve/', views.approve_blog_view, name='approve_blog'),
    path('moderate/blog/<int:blog_id>/reject/', views.reject_blog_view, name='reject_blog'),
    
    # Comment Moderation (Moderators/Admin/Authors)
    path('moderate/comments/', views.moderate_comments_view, name='moderate_comments'),
    path('moderate/comment/<int:comment_id>/approve/', views.approve_comment_view, name='approve_comment'),
    path('moderate/comment/<int:comment_id>/reject/', views.reject_comment_view, name='reject_comment'),
    
    # Public Blog Pages
    path('blogs/', views.blog_list_view, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail_view, name='blog_detail'),
    path('category/<slug:slug>/', views.category_blogs_view, name='category_blogs'),
]