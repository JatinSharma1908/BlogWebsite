from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.text import slugify


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email


class Role(models.Model):
    """User roles"""
    
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.name



class Permission(models.Model):
    name = models.CharField(max_length=100, unique=True)
    roles = models.ManyToManyField(Role, through='RolePermission', related_name='role_permissions')
    
    class Meta:
        db_table = 'permissions'
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
    
    def __str__(self):
        return self.name


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Role Permission'
        verbose_name_plural = 'Role Permissions'
    
    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"


class UserRole(models.Model):
    """Many-to-many relationship between users and roles"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'user_roles'
        unique_together = ('user', 'role')
    
    def __str__(self):
        return f"{self.user.email} - {self.role.name}"


class Category(models.Model):
    """Blog categories"""
    
    tenant_id = models.IntegerField()
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120)
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        indexes = [
            models.Index(fields=['tenant_id', 'slug'], name='categories_index_0'),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    tenant_id = models.IntegerField()
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120)
    
    class Meta:
        db_table = 'tags'
        unique_together = ('tenant_id', 'slug')
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        indexes = [
            models.Index(fields=['tenant_id', 'slug'], name='tags_index_1'),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Blog(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    tenant_id = models.IntegerField()
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300)
    excerpt = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='blogs')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='blogs')
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'blogs'
        unique_together = ('tenant_id', 'slug')
        verbose_name = 'Blog'
        verbose_name_plural = 'Blogs'
        indexes = [
            models.Index(fields=['tenant_id', 'slug'], name='blogs_index_2'),
            models.Index(fields=['tenant_id', 'status'], name='idx_blogs_tenant_status'),
            models.Index(fields=['tenant_id', 'slug'], name='idx_blogs_slug'),
        ]
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title


class Comment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('spam', 'Spam'),
        ('rejected', 'Rejected'),
    ]
    
    tenant_id = models.IntegerField()
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=150)
    comment = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'comments'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.name} on {self.blog.title}"