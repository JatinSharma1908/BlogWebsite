from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, BlogForm, CategoryForm, CommentForm
from .models import Blog, Comment, UserRole, Category, Tag, User
from django.utils.text import slugify
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


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
    
    # Check if user is an author or moderator
    is_author = 'Author' in roles
    is_moderator = user.can_moderate_blogs() or user.is_superuser
    
    # Initialize context
    context = {
        'user': user,
        'roles': roles,
        'is_author': is_author,
        'is_moderator': is_moderator,
    }
    
    # If user is a moderator, show pending items
    if is_moderator:
        pending_blogs_count = Blog.objects.filter(status='pending_review').count()
        pending_comments_count = Comment.objects.filter(status='pending').count()
        
        context.update({
            'pending_blogs_count': pending_blogs_count,
            'pending_comments_count': pending_comments_count,
        })
    
    # If user is an author, get their blog statistics
    if is_author:
        # Get user's blogs
        user_blogs = Blog.objects.filter(author=user)
        
        # Statistics
        total_blogs = user_blogs.count()
        published_blogs = user_blogs.filter(status='published').count()
        draft_blogs = user_blogs.filter(status='draft').count()
        pending_blogs = user_blogs.filter(status='pending_review').count()
        rejected_blogs = user_blogs.filter(status='rejected').count()
        
        # Get total comments on user's blogs
        total_comments = Comment.objects.filter(blog__author=user).count()
        pending_comments = Comment.objects.filter(blog__author=user, status='pending').count()
        
        # Recent blogs
        recent_blogs = user_blogs.order_by('-created_at')[:5]
        
        context.update({
            'total_blogs': total_blogs,
            'published_blogs': published_blogs,
            'draft_blogs': draft_blogs,
            'pending_blogs': pending_blogs,
            'rejected_blogs': rejected_blogs,
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
    
    if 'Author' not in roles and not request.user.is_superuser:
        messages.error(request, 'Only authors can create blog posts.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = BlogForm(request.POST, user=request.user, tenant_id=1)
        if form.is_valid():
            blog = form.save()
            messages.success(request, f'Blog "{blog.title}" created successfully as draft!')
            return redirect('my_blogs')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BlogForm(user=request.user, tenant_id=1)
    
    return render(request, 'blog/create_blog.html', {'form': form})


@login_required
def edit_blog_view(request, blog_id):
    """Edit existing blog post"""
    
    blog = get_object_or_404(Blog, id=blog_id)
    
    # Check permissions
    if blog.author != request.user and not request.user.can_edit_any_blog():
        messages.error(request, 'You do not have permission to edit this blog.')
        return redirect('my_blogs')
    
    # Check if blog can be edited based on status
    if blog.status in ['pending_review', 'published'] and blog.author == request.user:
        messages.warning(request, 'This blog is under review or published. Editing will change status to draft and require re-submission.')
    
    if request.method == 'POST':
        form = BlogForm(request.POST, instance=blog, user=request.user, tenant_id=blog.tenant_id)
        if form.is_valid():
            blog = form.save(commit=False)
            
            # If blog was published or pending and is being edited by author, change to draft
            if blog.status in ['pending_review', 'published'] and blog.author == request.user:
                blog.status = 'draft'
                blog.published_at = None
                blog.submitted_at = None
                blog.reviewed_at = None
                blog.reviewed_by = None
                messages.info(request, 'Blog status changed to draft. You need to submit for review again.')
            
            blog.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, f'Blog "{blog.title}" updated successfully!')
            return redirect('my_blogs')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BlogForm(instance=blog, user=request.user, tenant_id=blog.tenant_id)
    
    return render(request, 'blog/edit_blog.html', {'form': form, 'blog': blog})


@login_required
def submit_blog_for_review(request, blog_id):
    """Submit a blog for moderation"""
    
    blog = get_object_or_404(Blog, id=blog_id, author=request.user)
    
    # Check if blog can be submitted
    if blog.status not in ['draft', 'rejected']:
        messages.error(request, 'This blog cannot be submitted for review.')
        return redirect('my_blogs')
    
    if request.method == 'POST':
        blog.status = 'pending_review'
        blog.submitted_at = timezone.now()
        blog.reviewed_at = None
        blog.reviewed_by = None
        blog.rejection_reason = None
        blog.save()
        
        # Send email notification to moderators (optional)
        send_blog_submission_notification(blog)
        
        messages.success(request, f'Blog "{blog.title}" submitted for review!')
        return redirect('my_blogs')
    
    return render(request, 'blog/submit_for_review.html', {'blog': blog})


@login_required
def my_blogs_view(request):
    """List all blogs by current user"""
    
    # Check if user is an author
    user_roles = UserRole.objects.filter(user=request.user).select_related('role')
    roles = [ur.role.name for ur in user_roles]
    
    if 'Author' not in roles and not request.user.is_superuser:
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
    
    blog = get_object_or_404(Blog, id=blog_id)
    
    # Check permissions
    if blog.author != request.user and not request.user.can_edit_any_blog():
        messages.error(request, 'You do not have permission to delete this blog.')
        return redirect('my_blogs')
    
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
    
    if 'Author' not in roles and not request.user.is_superuser:
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


# ==================== MODERATION VIEWS ====================

@login_required
def moderate_blogs_view(request):
    """View for moderators to see pending blogs"""
    
    if not request.user.can_moderate_blogs():
        messages.error(request, 'You do not have permission to moderate blogs.')
        return redirect('dashboard')
    
    # Get all pending blogs
    pending_blogs = Blog.objects.filter(status='pending_review').select_related('author', 'category').order_by('-submitted_at')
    
    context = {
        'pending_blogs': pending_blogs,
    }
    
    return render(request, 'blog/moderate_blogs.html', context)


@login_required
def approve_blog_view(request, blog_id):
    """Approve a blog post"""
    
    if not request.user.can_moderate_blogs():
        messages.error(request, 'You do not have permission to approve blogs.')
        return redirect('dashboard')
    
    blog = get_object_or_404(Blog, id=blog_id, status='pending_review')
    
    if request.method == 'POST':
        blog.status = 'published'
        blog.reviewed_at = timezone.now()
        blog.reviewed_by = request.user
        blog.published_at = timezone.now()
        blog.rejection_reason = None
        blog.save()
        
        # Send email notification to author
        send_blog_approval_notification(blog)
        
        messages.success(request, f'Blog "{blog.title}" has been approved and published!')
        return redirect('moderate_blogs')
    
    return render(request, 'blog/approve_blog.html', {'blog': blog})


@login_required
def reject_blog_view(request, blog_id):
    """Reject a blog post"""
    
    if not request.user.can_moderate_blogs():
        messages.error(request, 'You do not have permission to reject blogs.')
        return redirect('dashboard')
    
    blog = get_object_or_404(Blog, id=blog_id, status='pending_review')
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        
        if not rejection_reason:
            messages.error(request, 'Please provide a reason for rejection.')
            return render(request, 'blog/reject_blog.html', {'blog': blog})
        
        blog.status = 'rejected'
        blog.reviewed_at = timezone.now()
        blog.reviewed_by = request.user
        blog.rejection_reason = rejection_reason
        blog.save()
        
        # Send email notification to author
        send_blog_rejection_notification(blog)
        
        messages.success(request, f'Blog "{blog.title}" has been rejected.')
        return redirect('moderate_blogs')
    
    return render(request, 'blog/reject_blog.html', {'blog': blog})


@login_required
def moderate_comments_view(request):
    """View for moderators to see pending comments"""
    
    if not request.user.can_moderate_comments():
        messages.error(request, 'You do not have permission to moderate comments.')
        return redirect('dashboard')
    
    # Get all pending comments
    pending_comments = Comment.objects.filter(status='pending').select_related('blog', 'blog__author').order_by('-created_at')
    
    context = {
        'pending_comments': pending_comments,
    }
    
    return render(request, 'blog/moderate_comments.html', context)


@login_required
def approve_comment_view(request, comment_id):
    """Approve a comment"""
    
    comment = get_object_or_404(Comment, id=comment_id, status='pending')
    
    # Check permissions: moderators can approve any, authors can approve on own blogs
    can_moderate = request.user.can_moderate_comments()
    is_blog_author = comment.blog.author == request.user
    
    if not (can_moderate or is_blog_author):
        messages.error(request, 'You do not have permission to approve this comment.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        comment.status = 'approved'
        comment.reviewed_at = timezone.now()
        comment.reviewed_by = request.user
        comment.save()
        
        messages.success(request, 'Comment has been approved!')
        
        if can_moderate:
            return redirect('moderate_comments')
        else:
            return redirect('dashboard')
    
    return render(request, 'blog/approve_comment.html', {'comment': comment})


@login_required
def reject_comment_view(request, comment_id):
    """Reject a comment"""
    
    comment = get_object_or_404(Comment, id=comment_id, status='pending')
    
    # Check permissions
    can_moderate = request.user.can_moderate_comments()
    is_blog_author = comment.blog.author == request.user
    
    if not (can_moderate or is_blog_author):
        messages.error(request, 'You do not have permission to reject this comment.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        comment.status = 'rejected'
        comment.reviewed_at = timezone.now()
        comment.reviewed_by = request.user
        comment.save()
        
        messages.success(request, 'Comment has been rejected!')
        
        if can_moderate:
            return redirect('moderate_comments')
        else:
            return redirect('dashboard')
    
    return render(request, 'blog/reject_comment.html', {'comment': comment})


# ==================== PUBLIC VIEWS ====================

def blog_list_view(request):
    """Public blog listing page - shows all published blogs"""
    
    # Get all published blogs
    blogs = Blog.objects.filter(tenant_id=1, status='published').select_related('author', 'category').order_by('-published_at')
    
    # Get all categories for sidebar
    categories = Category.objects.filter(tenant_id=1).order_by('name')
    
    # Get category counts
    for category in categories:
        category.blog_count = Blog.objects.filter(category=category, status='published').count()
    
    context = {
        'blogs': blogs,
        'categories': categories,
    }
    
    return render(request, 'blog/blog_list.html', context)


@login_required
def blog_detail_view(request, slug):
    """Blog detail page - shows full blog content and handles comments"""
    
    # Get the blog by slug, must be published
    blog = get_object_or_404(Blog, slug=slug, tenant_id=1, status='published')
    
    # Get related blogs from same category
    related_blogs = Blog.objects.filter(
        category=blog.category,
        status='published',
        tenant_id=1
    ).exclude(id=blog.id).order_by('-published_at')[:3]
    
    # Get approved comments
    comments = Comment.objects.filter(blog=blog, status='approved').order_by('-created_at')
    total_comments = comments.count()
    
    # Handle comment form submission
    comment_form = CommentForm()
    comment_submitted = False

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.blog = blog
            comment.tenant_id = blog.tenant_id
            comment.status = 'pending'
            # Auto-fill name and email from the logged-in user
            comment.name = request.user.name
            comment.email = request.user.email
            comment.save()
            comment_submitted = True
            messages.success(request, 'Your comment has been submitted and is awaiting moderation.')
            return redirect('blog_detail', slug=slug)
        else:
            messages.error(request, 'Please correct the errors in your comment.')
    
    context = {
        'blog': blog,
        'related_blogs': related_blogs,
        'comments': comments,
        'total_comments': total_comments,
        'comment_form': comment_form,
        'comment_submitted': comment_submitted,
    }
    
    return render(request, 'blog/blog_detail.html', context)


def category_blogs_view(request, slug):
    """Show all blogs in a specific category"""
    
    # Get the category
    category = get_object_or_404(Category, slug=slug, tenant_id=1)
    
    # Get all published blogs in this category
    blogs = Blog.objects.filter(
        category=category,
        status='published',
        tenant_id=1
    ).select_related('author').order_by('-published_at')
    
    # Get all categories for sidebar
    categories = Category.objects.filter(tenant_id=1).order_by('name')
    
    context = {
        'category': category,
        'blogs': blogs,
        'categories': categories,
    }
    
    return render(request, 'blog/category_blogs.html', context)


# ==================== EMAIL NOTIFICATION HELPERS ====================

def send_blog_submission_notification(blog):
    """Send email to moderators when a blog is submitted"""
    try:
        moderators = User.objects.filter(
            userrole__role__name__in=['Moderator', 'Editor']
        ).distinct()
        
        admin_users = User.objects.filter(is_superuser=True)
        
        recipients = list(moderators.values_list('email', flat=True)) + list(admin_users.values_list('email', flat=True))
        
        if recipients:
            subject = f'New Blog Submission: {blog.title}'
            message = f'''
A new blog has been submitted for review:

Title: {blog.title}
Author: {blog.author.name}
Submitted: {blog.submitted_at}

Please review it at your earliest convenience.
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipients,
                fail_silently=True,
            )
    except Exception as e:
        # Log error but don't break the flow
        print(f"Error sending notification: {e}")


def send_blog_approval_notification(blog):
    """Send email to author when blog is approved"""
    try:
        subject = f'Your Blog "{blog.title}" has been Approved!'
        message = f'''
Congratulations! Your blog "{blog.title}" has been approved and is now published.

You can view it on the website.

Approved by: {blog.reviewed_by.name if blog.reviewed_by else 'Admin'}
Approved on: {blog.reviewed_at}
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [blog.author.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Error sending notification: {e}")


def send_blog_rejection_notification(blog):
    """Send email to author when blog is rejected"""
    try:
        subject = f'Your Blog "{blog.title}" Needs Revision'
        message = f'''
Your blog "{blog.title}" has been reviewed and requires some changes before it can be published.

Reason for rejection:
{blog.rejection_reason}

Please make the necessary changes and submit again.

Reviewed by: {blog.reviewed_by.name if blog.reviewed_by else 'Admin'}
Reviewed on: {blog.reviewed_at}
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [blog.author.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Error sending notification: {e}")