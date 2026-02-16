from django.contrib import admin
from .models import User, Role, Permission, RolePermission, UserRole, Category, Tag, Blog, Comment


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'is_active', 'is_staff', 'created_at', 'display_roles')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('name', 'email')
    readonly_fields = ('created_at', 'last_login')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('email', 'name', 'password')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def display_roles(self, obj):
        """Display all roles for this user"""
        roles = obj.get_roles()
        return ', '.join(roles) if roles else 'No roles'
    display_roles.short_description = 'Roles'


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user_count')
    search_fields = ('name',)
    
    def user_count(self, obj):
        """Count users with this role"""
        return UserRole.objects.filter(role=obj).count()
    user_count.short_description = 'Users'


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'permission')
    list_filter = ('role',)
    search_fields = ('role__name', 'permission__name')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role', 'user_email')
    list_filter = ('role',)
    search_fields = ('user__name', 'user__email', 'role__name')
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'tenant_id', 'name', 'slug', 'blog_count')
    list_filter = ('tenant_id',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    
    def blog_count(self, obj):
        """Count blogs in this category"""
        return Blog.objects.filter(category=obj).count()
    blog_count.short_description = 'Blogs'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'tenant_id', 'name', 'slug')
    list_filter = ('tenant_id',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'category', 'status', 'submitted_at', 'reviewed_by', 'published_at', 'created_at')
    list_filter = ('status', 'created_at', 'submitted_at', 'reviewed_at', 'category')
    search_fields = ('title', 'excerpt', 'author__name', 'author__email')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'submitted_at', 'reviewed_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('tenant_id', 'title', 'slug', 'excerpt', 'content', 'featured_image')
        }),
        ('Publishing', {
            'fields': ('status', 'author', 'category', 'published_at')
        }),
        ('Moderation', {
            'fields': ('submitted_at', 'reviewed_at', 'reviewed_by', 'rejection_reason'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_blogs', 'reject_blogs', 'publish_blogs']
    
    def approve_blogs(self, request, queryset):
        """Bulk approve blogs"""
        from django.utils import timezone
        updated = queryset.filter(status='pending_review').update(
            status='published',
            reviewed_at=timezone.now(),
            reviewed_by=request.user,
            published_at=timezone.now()
        )
        self.message_user(request, f'{updated} blog(s) approved and published.')
    approve_blogs.short_description = 'Approve selected blogs'
    
    def reject_blogs(self, request, queryset):
        """Bulk reject blogs"""
        from django.utils import timezone
        updated = queryset.filter(status='pending_review').update(
            status='rejected',
            reviewed_at=timezone.now(),
            reviewed_by=request.user,
            rejection_reason='Bulk rejection from admin panel'
        )
        self.message_user(request, f'{updated} blog(s) rejected.')
    reject_blogs.short_description = 'Reject selected blogs'
    
    def publish_blogs(self, request, queryset):
        """Bulk publish blogs (for admins)"""
        from django.utils import timezone
        updated = queryset.update(
            status='published',
            published_at=timezone.now()
        )
        self.message_user(request, f'{updated} blog(s) published.')
    publish_blogs.short_description = 'Publish selected blogs (Admin override)'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'blog', 'status', 'reviewed_by', 'created_at')
    list_filter = ('status', 'created_at', 'reviewed_at')
    search_fields = ('name', 'email', 'comment', 'blog__title')
    readonly_fields = ('created_at', 'reviewed_at')
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('tenant_id', 'blog', 'name', 'email', 'comment')
        }),
        ('Moderation', {
            'fields': ('status', 'reviewed_at', 'reviewed_by')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    actions = ['approve_comments', 'reject_comments', 'mark_as_spam']
    
    def approve_comments(self, request, queryset):
        """Bulk approve comments"""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='approved',
            reviewed_at=timezone.now(),
            reviewed_by=request.user
        )
        self.message_user(request, f'{updated} comment(s) approved.')
    approve_comments.short_description = 'Approve selected comments'
    
    def reject_comments(self, request, queryset):
        """Bulk reject comments"""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='rejected',
            reviewed_at=timezone.now(),
            reviewed_by=request.user
        )
        self.message_user(request, f'{updated} comment(s) rejected.')
    reject_comments.short_description = 'Reject selected comments'
    
    def mark_as_spam(self, request, queryset):
        """Mark comments as spam"""
        from django.utils import timezone
        updated = queryset.update(
            status='spam',
            reviewed_at=timezone.now(),
            reviewed_by=request.user
        )
        self.message_user(request, f'{updated} comment(s) marked as spam.')
    mark_as_spam.short_description = 'Mark as spam'