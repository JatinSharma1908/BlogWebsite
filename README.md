# BlogWebsite

> **A premium Django-based blogging platform with role-based access control, category management, and a clean editorial design.**

---

## Screenshots

### Login Page


<img width="1706" height="949" alt="Screenshot 2026-03-17 at 11 09 49 PM" src="https://github.com/user-attachments/assets/90109580-edb5-4858-b92c-0588c8d71781" />



---

### Dashboards — Author & Reader


<img width="3998" height="1109" alt="Group 1" src="https://github.com/user-attachments/assets/8d545014-a441-4916-83d9-5292b947cb38" />



---

### Blog Browsing Experience


<img width="3436" height="949" alt="Group 1 (1)" src="https://github.com/user-attachments/assets/bafcfcea-a2ad-4302-a091-d9271713c4f6" />



---

## Features

| Feature | Description |
|---|---|
|  **Auth & Roles** | Custom user model with email login, Author & Reader roles |
|  **Blog Management** | Create, edit, delete posts with draft/published/archived status |
|  **Categories & Tags** | Organize content with auto-slug generation |
|  **Comments** | Reader comments with moderation (pending/approved/spam) |
|  **Role Dashboards** | Author stats dashboard + Reader activity dashboard |
|  **Premium UI** | Royal purple theme, glass-morphism cards, smooth animations |
|  **Admin Panel** | Full Django admin with superuser controls |

---

## Tech Stack

- **Backend:** Django 5.x (Python)
- **Database:** SQLite (dev) — PostgreSQL ready
- **Frontend:** Bootstrap 5.3 + Custom CSS
- **Icons:** Bootstrap Icons
- **Fonts:** Google Fonts (Inter)

---

## Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/blogwebsite.git
cd blogwebsite

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create a superuser (admin)
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

Then visit **http://127.0.0.1:8000** in your browser.

---

##  Project Structure

```
blogWebsite/
├── config/                  # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── blog/                    # Main application
│   ├── models.py            # Database models
│   ├── views.py             # View functions
│   ├── forms.py             # Form definitions
│   ├── urls.py              # App URL routes
│   ├── admin.py             # Admin configuration
│   │
│   ├── templates/blog/      # HTML templates
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── dashboard.html
│   │   ├── create_blog.html
│   │   ├── edit_blog.html
│   │   ├── my_blogs.html
│   │   └── manage_categories.html
│   │
│   └── static/css/
│       └── style.css        # Royal purple theme
│
├── manage.py
└── requirements.txt
```

---

##  URL Routes

| Route | Access | Description |
|---|---|---|
| `/` | Public | Home / Landing page |
| `/register/` | Public | User registration |
| `/login/` | Public | User login |
| `/dashboard/` | Login required | Role-specific dashboard |
| `/blogs/` | Login required | Browse all published blogs |
| `/blog/create/` | Author only | Create a new post |
| `/blog/<id>/edit/` | Author only | Edit own post |
| `/blog/<id>/delete/` | Author only | Delete own post |
| `/my-blogs/` | Author only | Manage own posts |
| `/categories/` | Author only | Manage categories |

---

##  User Roles

###  Author
- Create, edit, and delete own blog posts
- Manage categories and tags
- Set post status (draft / published / archived)
- Moderate comments on own posts

###  Reader
- Browse and read all published blogs
- Post comments (pending admin approval)
- View own comment history

###  Admin (Superuser)
- Full access to Django admin panel
- Manage all users, roles, and content
- Moderate all comments

---


##  Planned Features

- [ ] Public blog listing & detail pages
- [ ] Rich text editor (TinyMCE / CKEditor)
- [ ] Image file uploads (Pillow)
- [ ] Search functionality
- [ ] User profile pages
- [ ] Email notifications
- [ ] Blog analytics
- [ ] RSS feed
- [ ] REST API (Django REST Framework)
- [ ] Auto-save drafts

---

##  Deployment Checklist

```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECRET_KEY = os.environ.get('SECRET_KEY')

# Switch to PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        ...
    }
}
```

- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use environment variables for `SECRET_KEY`
- [ ] Migrate to PostgreSQL
- [ ] Run `python manage.py collectstatic`
- [ ] Set up HTTPS
- [ ] Configure gunicorn / uwsgi
- [ ] Set up Sentry for error logging

---

## Troubleshooting

| Issue | Fix |
|---|---|
| Categories not showing in dropdown | Create categories first via `/categories/` |
| User can't create blogs | Ensure user has `Author` role assigned |
| Static files not loading | Run `python manage.py collectstatic`, check `STATICFILES_DIRS` |
| Database locked error | Close all SQLite connections, restart dev server |

---

##  License

This project is open source. See [LICENSE](LICENSE) for details.

Dependencies and their licenses:
- Django — BSD License
- Bootstrap — MIT License
- Bootstrap Icons — MIT License
- Google Fonts (Inter) — OFL License

---

## 🙌 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

```bash
# Fork the repo, then:
git checkout -b feature/your-feature-name
git commit -m "Add: your feature description"
git push origin feature/your-feature-name
# Open a Pull Request
```

---

<p align="center">Made with ❤️ using Django & Bootstrap</p>
