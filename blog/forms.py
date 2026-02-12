from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Role, Blog, Category, Tag


class UserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('reader', 'Reader - Read and comment on blogs'),
        ('author', 'Author - Write and publish blogs'),
    ]
    
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
            'id': 'id_name'
        })
    )
    
    email = forms.EmailField(
        max_length=150,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'id': 'id_email'
        })
    )
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_role'
        }),
        label='Select Role'
    )
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'id': 'id_password1'
        })
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'id': 'id_password2'
        })
    )
    
    class Meta:
        model = User
        fields = ['name', 'email', 'role', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            role_value = self.cleaned_data.get('role')
            role_name = role_value.capitalize()
            role, created = Role.objects.get_or_create(name=role_name)
            from .models import UserRole
            UserRole.objects.create(user=user, role=role)
        
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'id': 'id_username'
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'id': 'id_password'
        })
    )


class BlogForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter tags separated by commas (e.g., technology, coding, django)',
            'id': 'id_tags'
        }),
        label='Tags',
        help_text='Separate tags with commas'
    )
    
    class Meta:
        model = Blog
        fields = ['title', 'excerpt', 'content', 'featured_image', 'category', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter an engaging title for your blog',
                'id': 'id_title'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write a brief summary of your blog (required)',
                'rows': 3,
                'id': 'id_excerpt'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your blog content here...',
                'rows': 10,
                'id': 'id_content'
            }),
            'featured_image': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter image URL (e.g., https://example.com/image.jpg)',
                'id': 'id_featured_image'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_category'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_status'
            }),
        }
        labels = {
            'title': 'Blog Title',
            'excerpt': 'Brief Summary (Required)',
            'content': 'Blog Content',
            'featured_image': 'Featured Image URL (Optional)',
            'category': 'Category',
            'status': 'Publication Status'
        }
        help_texts = {
            'excerpt': 'A short preview of your blog post (required)',
            'content': 'The main content of your blog post',
            'featured_image': 'Enter a URL to an image to use as featured image',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.tenant_id = kwargs.pop('tenant_id', 1)
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(tenant_id=self.tenant_id)
        self.fields['category'].empty_label = "Select a category"
        
        # Make excerpt required
        self.fields['excerpt'].required = True
        
        if self.instance and self.instance.pk:
            tags = Tag.objects.filter(tenant_id=self.tenant_id, name__in=[])
            self.fields['tags_input'].initial = ', '.join([tag.name for tag in tags])
    
    def save(self, commit=True):
        blog = super().save(commit=False)
        blog.tenant_id = self.tenant_id
        
        if self.user:
            blog.author = self.user
        
        if commit:
            blog.save()
            tags_input = self.cleaned_data.get('tags_input', '')
            if tags_input:
                tag_names = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
                for tag_name in tag_names:
                    tag, created = Tag.objects.get_or_create(
                        tenant_id=self.tenant_id,
                        name=tag_name,
                        defaults={'slug': tag_name.lower().replace(' ', '-')}
                    )
        
        return blog


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name',
                'id': 'id_category_name'
            }),
        }
        labels = {
            'name': 'Category Name',
        }
    
    def __init__(self, *args, **kwargs):
        self.tenant_id = kwargs.pop('tenant_id', 1)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        category = super().save(commit=False)
        category.tenant_id = self.tenant_id
        
        if commit:
            category.save()
        
        return category