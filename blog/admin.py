from django.contrib import admin
from .models import User, Role, Permission, RolePermission, UserRole, Category, Tag, Blog, Comment


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'email')
    readonly_fields = ('created_at',)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'permission')
    list_filter = ('role',)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role')
    list_filter = ('role',)
    search_fields = ('user__name', 'user__email')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'tenant_id', 'name', 'slug')
    list_filter = ('tenant_id',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'tenant_id', 'name', 'slug')
    list_filter = ('tenant_id',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'category', 'status', 'published_at', 'created_at')
    list_filter = ('status', 'created_at', 'category')
    search_fields = ('title', 'excerpt', 'author__name')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('tenant_id', 'title', 'slug', 'excerpt')
        }),
        ('Publishing', {
            'fields': ('status', 'author', 'category', 'published_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'blog', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'comment', 'blog__title')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('tenant_id', 'blog', 'name', 'email', 'comment')
        }),
        ('Moderation', {
            'fields': ('status',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )