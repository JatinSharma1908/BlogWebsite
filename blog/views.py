from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, BlogForm, CategoryForm
from .models import Blog, Comment, UserRole, Category, Tag
from django.utils.text import slugify


def register_view(request):
    """User registration view"""
    
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'blog/register.html', {'form': form})


def login_view(request):
    """User login view"""
    
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.name}!')
                
                # Redirect to next parameter or dashboard
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'blog/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view"""
    
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def home_view(request):
    """Home page view"""
    
    # If user is logged in, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    return render(request, 'blog/home.html')


@login_required
def dashboard_view(request):
    """User dashboard view"""
    
    user = request.user
    
    # Get user roles
    user_roles = UserRole.objects.filter(user=user).select_related('role')
    roles = [ur.role.name for ur in user_roles]
    
    # Check if user is an author
    is_author = 'Author' in roles
    
    # Initialize context
    context = {
        'user': user,
        'roles': roles,
        'is_author': is_author,
    }
    
    # If user is an author, get their blog statistics
    if is_author:
        # Get user's blogs
        user_blogs = Blog.objects.filter(author=user)
        
        # Statistics
        total_blogs = user_blogs.count()
        published_blogs = user_blogs.filter(status='published').count()
        draft_blogs = user_blogs.filter(status='draft').count()
        
        # Get total comments on user's blogs
        total_comments = Comment.objects.filter(blog__author=user).count()
        pending_comments = Comment.objects.filter(blog__author=user, status='pending').count()
        
        # Recent blogs
        recent_blogs = user_blogs.order_by('-created_at')[:5]
        
        context.update({
            'total_blogs': total_blogs,
            'published_blogs': published_blogs,
            'draft_blogs': draft_blogs,
            'total_comments': total_comments,
            'pending_comments': pending_comments,
            'recent_blogs': recent_blogs,
        })
    else:
        # For readers, show categories slider and recent comments
        user_comments = Comment.objects.filter(email=user.email).order_by('-created_at')[:5]
        categories = Category.objects.filter(tenant_id=1).order_by('name')
        context['recent_comments'] = user_comments
        context['categories'] = categories
    
    return render(request, 'blog/dashboard.html', context)


@login_required
def create_blog_view(request):
    """Create new blog post"""
    
    # Check if user is an author
    user_roles = UserRole.objects.filter(user=request.user).select_related('role')
    roles = [ur.role.name for ur in user_roles]
    
    if 'Author' not in roles:
        messages.error(request, 'Only authors can create blog posts.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = BlogForm(request.POST, user=request.user, tenant_id=1)
        if form.is_valid():
            blog = form.save()
            messages.success(request, f'Blog "{blog.title}" created successfully!')
            return redirect('my_blogs')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BlogForm(user=request.user, tenant_id=1)
    
    return render(request, 'blog/create_blog.html', {'form': form})


@login_required
def edit_blog_view(request, blog_id):
    """Edit existing blog post"""
    
    blog = get_object_or_404(Blog, id=blog_id, author=request.user)
    
    if request.method == 'POST':
        form = BlogForm(request.POST, instance=blog, user=request.user, tenant_id=blog.tenant_id)
        if form.is_valid():
            blog = form.save()
            messages.success(request, f'Blog "{blog.title}" updated successfully!')
            return redirect('my_blogs')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BlogForm(instance=blog, user=request.user, tenant_id=blog.tenant_id)
    
    return render(request, 'blog/edit_blog.html', {'form': form, 'blog': blog})


@login_required
def my_blogs_view(request):
    """List all blogs by current user"""
    
    # Check if user is an author
    user_roles = UserRole.objects.filter(user=request.user).select_related('role')
    roles = [ur.role.name for ur in user_roles]
    
    if 'Author' not in roles:
        messages.error(request, 'Only authors can access this page.')
        return redirect('dashboard')
    
    blogs = Blog.objects.filter(author=request.user).order_by('-created_at')
    
    context = {
        'blogs': blogs,
    }
    
    return render(request, 'blog/my_blogs.html', context)


@login_required
def delete_blog_view(request, blog_id):
    """Delete a blog post"""
    
    blog = get_object_or_404(Blog, id=blog_id, author=request.user)
    
    if request.method == 'POST':
        blog_title = blog.title
        blog.delete()
        messages.success(request, f'Blog "{blog_title}" deleted successfully!')
        return redirect('my_blogs')
    
    return render(request, 'blog/delete_blog.html', {'blog': blog})


@login_required
def manage_categories_view(request):
    """Manage categories"""
    
    # Check if user is an author
    user_roles = UserRole.objects.filter(user=request.user).select_related('role')
    roles = [ur.role.name for ur in user_roles]
    
    if 'Author' not in roles:
        messages.error(request, 'Only authors can manage categories.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, tenant_id=1)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created successfully!')
            return redirect('manage_categories')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm(tenant_id=1)
    
    categories = Category.objects.filter(tenant_id=1).order_by('name')
    
    context = {
        'form': form,
        'categories': categories,
    }
    
    return render(request, 'blog/manage_categories.html', context)