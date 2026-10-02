# KnitBlog

A social blogging platform built with Django. KnitBlog combines the simplicity of a personal blog with the warmth of a small social network — write posts, share them with friends, and keep meaningful conversations close.

**Live Demo:** [https://knitblog.com](https://knitblog.com)
**Author:** Ishita Mehra
**LinkedIn:** [linkedin.com/in/ishitamehra16](https://www.linkedin.com/in/ishitamehra16)
**Contact:** itzishita2003@gmail.com

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Data Models](#data-models)
6. [URL Routes](#url-routes)
7. [Local Development Setup](#local-development-setup)
8. [Environment Variables](#environment-variables)
9. [Deployment](#deployment)
10. [Security](#security)
11. [Testing](#testing)
12. [Contributing](#contributing)
13. [License](#license)

---

## Overview

KnitBlog is a full-stack Django web application designed as a personal blogging and light social platform. It supports rich-text post creation, threaded comments, likes, shares, saved posts, and a friend-request system — all wrapped in a custom, mobile-friendly interface.

The project is intended for:

- **Readers:** Browse and search published posts without creating an account. Read freely, follow writers, and get updates via RSS.
- **Writers:** Sign up to publish rich-text posts with images, tags, and categories. Manage drafts, track views, and grow an audience.
- **Community:** Send friend requests, like and comment on posts, share posts to your own profile (repost system), and build a personalized feed.

---

## Features

### For Readers (No Account Required)

- Browse all published posts on the Explore page
- Search posts by title, content, tag, category, or author
- Read full post content with images, headings, and rich formatting
- View author profiles with bio, location, website, and posts
- Subscribe to the site via RSS feed
- Access the sitemap for search engine indexing

### For Registered Users

- **Rich-text editor** powered by Quill — headings, lists, quotes, code blocks, images, links
- **Post management** — create, edit, delete, and save drafts
- **Categories and tags** for organizing content
- **Likes** on any post
- **Threaded comments** with reply support
- **Share / repost** — share another writer's post to your own profile (Instagram-style)
- **Save posts** to a private collection
- **Friend requests** — send, accept, reject, or remove friends
- **Personalized dashboard** ("Knitting Space") with sections for Home, Discover, My Posts, Likes, Saved, Friends, and Requests
- **Profile customization** — avatar, display name, bio, location, website
- **Password reset** via email
- **Change password** through Django admin or the reset flow

### For Administrators

- Django admin panel for managing users, posts, comments, categories, tags, likes, saved posts, and friend requests
- Bulk edit post statuses directly from the admin list view
- Image thumbnails in the post list
- Date hierarchy filter for posts
- Full CRUD on every model

### Developer-Facing Enhancements

- **HTML sanitization** with `nh3` — user-generated rich-text content is stripped of unsafe tags, scripts, and malicious URLs before saving
- **Open redirect protection** — all redirects via `Referer` or `?next=` are validated against allowed hosts
- **CSRF-safe actions** — every state-changing endpoint (like, comment, share, save, friend requests) is protected by `@require_POST` and `{% csrf_token %}`
- **Rotating "Note from the Maker"** — a lightweight developer-to-user note that rotates daily, seeded per-user, dismissible via localStorage
- **RSS feed and sitemap** — automatic, with shared/repost entries filtered out
- **Email-based password reset** with Gmail SMTP
- **Environment-based configuration** — no secrets in source code

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | Django 5.x |
| Database (dev) | SQLite 3 |
| Database (prod) | PostgreSQL |
| Rich Text Editor | Quill 2.0 |
| HTML Sanitizer | nh3 |
| Image Handling | Pillow |
| Frontend Styling | Bootstrap 5, custom CSS |
| Icons | Bootstrap Icons |
| Static File Serving | WhiteNoise |
| WSGI Server | Gunicorn |
| Email | Gmail SMTP (TLS, port 587) |
| Hosting | Railway |
| Version Control | Git / GitHub |

---

## Project Structure

```
knit_blog/
├── blog/                            # Main application
│   ├── migrations/                  # Database migrations
│   ├── admin.py                     # Admin panel configuration
│   ├── apps.py                      # App config
│   ├── context_processors.py        # Notifications + maker note
│   ├── feeds.py                     # RSS feed
│   ├── forms.py                     # All forms (PostForm, CommentForm, etc.)
│   ├── maker_notes.py               # Rotating developer notes
│   ├── models.py                    # Profile, Post, Like, Comment, etc.
│   ├── sanitizer.py                 # HTML sanitization with nh3
│   ├── sitemaps.py                  # XML sitemap definitions
│   ├── urls.py                      # App-level URL routes
│   └── views.py                     # All view functions
│
├── knit_blog/                       # Project configuration
│   ├── settings.py                  # Settings (env-var driven)
│   ├── urls.py                      # Root URL configuration
│   ├── asgi.py
│   └── wsgi.py
│
├── templates/                       # All HTML templates
│   ├── _maker_note.html             # Maker note partial
│   ├── _post_card.html              # Reusable post card
│   ├── _space_sidebar.html          # Dashboard sidebar partial
│   ├── base.html                    # Base layout
│   ├── index.html                   # Home page
│   ├── post_list.html               # Explore / listings
│   ├── post_detail.html             # Single post view
│   ├── post_form.html               # Create / edit post
│   ├── post_confirm_delete.html     # Delete confirmation
│   ├── profile.html                 # Public profile
│   ├── edit_profile.html            # Profile edit form
│   ├── knitting_space.html          # Dashboard
│   ├── login.html
│   ├── signup.html
│   ├── get_started.html
│   ├── password_reset_request.html
│   ├── password_reset_confirm.html
│   ├── search.html
│   ├── user_list.html
│   └── robots.txt
│
├── static/                          # Project-level static files
│   └── img_1.png
│
├── media/                           # User uploads (dev)
│   ├── avatars/
│   └── posts/
│
├── .env                             # Environment variables (gitignored)
├── .env.example                     # Template for .env
├── .gitattributes
├── .gitignore
├── build.sh                         # Deployment build script
├── Procfile                         # Process definition
├── railway.toml                     # Railway deployment config
├── requirements.txt
├── manage.py
└── README.md
```

---

## Data Models

### Profile

Extends Django's `User` with additional fields.

| Field | Type | Notes |
|---|---|---|
| `user` | OneToOne(User) | CASCADE |
| `name` | CharField(100) | Display name |
| `bio` | TextField(300) | Short bio |
| `avatar` | ImageField | Optional |
| `website` | URLField | Optional |
| `location` | CharField(100) | Optional |
| `created_at` | DateTimeField | Auto |

Properties: `display_name`, `initial`.

### Category

| Field | Type |
|---|---|
| `name` | CharField(80, unique) |
| `slug` | SlugField(90, unique) |

### Tag

| Field | Type |
|---|---|
| `name` | CharField(50, unique) |
| `slug` | SlugField(60, unique) |

### Post

| Field | Type | Notes |
|---|---|---|
| `author` | ForeignKey(User) | CASCADE |
| `title` | CharField(200) | |
| `slug` | SlugField(220, unique) | Auto-generated |
| `excerpt` | CharField(300) | Auto from content if blank |
| `content` | TextField | Sanitized HTML |
| `featured_image` | ImageField | Optional |
| `category` | ForeignKey(Category) | Nullable |
| `tags` | ManyToMany(Tag) | |
| `status` | CharField | `draft` or `published` |
| `original_post` | ForeignKey(self) | For reposts/shares |
| `views` | PositiveInteger | Incremented per visit |
| `created_at`, `updated_at`, `published_at` | DateTimeField | |
| `reading_time` | Property | Word count / 200 |

### Like

Unique pair of `(user, post)`.

### Comment

| Field | Type | Notes |
|---|---|---|
| `post` | ForeignKey(Post) | CASCADE |
| `author` | ForeignKey(User) | |
| `parent` | ForeignKey(self) | For threaded replies |
| `content` | TextField(1000) | Plain text |
| `is_approved` | BooleanField | |
| `created_at` | DateTimeField | |

### FriendRequest

| Field | Type | Notes |
|---|---|---|
| `sender` | ForeignKey(User) | |
| `receiver` | ForeignKey(User) | |
| `status` | CharField | `pending` or `accepted` |
| `created_at` | DateTimeField | |

### SavedPost

Unique pair of `(user, post)`.

---

## URL Routes

| Path | View | Description |
|---|---|---|
| `/` | `index` | Home |
| `/posts/` | `post_list` | Explore all posts |
| `/posts/new/` | `post_create` | Create post (auth) |
| `/posts/<slug>/` | `post_detail` | View post |
| `/posts/<slug>/edit/` | `post_update` | Edit post (owner only) |
| `/posts/<slug>/delete/` | `post_delete` | Delete post (owner only) |
| `/category/<slug>/` | `category_detail` | Posts in category |
| `/tag/<slug>/` | `tag_detail` | Posts with tag |
| `/search/` | `search` | Search |
| `/post/like/<id>/` | `like_post` | Toggle like (POST) |
| `/post/comment/<id>/` | `add_comment` | Add comment (POST) |
| `/comment/<id>/delete/` | `delete_comment` | Delete comment (POST) |
| `/post/share/<id>/` | `share_post` | Toggle share (POST) |
| `/post/save/<id>/` | `save_post` | Toggle save (POST) |
| `/login/`, `/signup/`, `/logout/` | Auth views | |
| `/password-reset/` | Reset request | |
| `/password-reset-confirm/<uidb64>/<token>/` | Reset confirm | |
| `/profile/<username>/` | `user_profile` | Public profile |
| `/profile/edit/` | `edit_profile` | Edit own profile |
| `/users/` | `user_list` | All users |
| `/friend/send/<id>/` | Send request (POST) | |
| `/friend/accept/<id>/` | Accept request (POST) | |
| `/friend/remove/<id>/` | Remove friend (POST) | |
| `/knitting-space/` | Dashboard | |
| `/sitemap.xml` | Sitemap | |
| `/robots.txt` | Robots | |
| `/feed/` | RSS feed | |

---

## Local Development Setup

### Prerequisites

- Python 3.11 or 3.12
- pip
- Git

### 1. Clone the repository

```bash
git clone https://github.com/ishita-mehra/knitblog.git
cd knitblog
```

### 2. Create and activate a virtual environment

**Windows (Command Prompt):**
```bash
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**
```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

See the [Environment Variables](#environment-variables) section for details on each key.

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create an admin account

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. Admin panel is at [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin).

---

## Environment Variables

All secrets and environment-specific settings are read from environment variables. A `.env` file is loaded automatically in development.

| Variable | Purpose | Example |
|---|---|---|
| `SECRET_KEY` | Django cryptographic key | A 50-character random string |
| `DEBUG` | Enable debug mode | `True` in dev, `False` in production |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hostnames | `127.0.0.1,localhost` |
| `EMAIL_HOST_USER` | Gmail address for sending password-reset emails | `yourname@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Gmail App Password (16 characters, no spaces) | `abcdefghijklmnop` |
| `DEFAULT_FROM_EMAIL` | "From" address in outgoing emails | Same as `EMAIL_HOST_USER` |
| `DATABASE_URL` | PostgreSQL URL (production only) | Set automatically by Railway |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name (if using Cloudinary) | |
| `CLOUDINARY_API_KEY` | Cloudinary API key | |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret | |

### Generating a SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Setting up Gmail for password reset

1. Enable 2-Step Verification at [myaccount.google.com/security](https://myaccount.google.com/security)
2. Generate an App Password at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) — name it "KnitBlog"
3. Copy the 16-character password and paste it into `EMAIL_HOST_PASSWORD` (remove spaces)

---

## Deployment

The project is configured for deployment on Railway or Render.

### Build command

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

### Start command

```bash
gunicorn knit_blog.wsgi:application --bind 0.0.0.0:$PORT
```

### Railway deployment steps

1. Sign up at [railway.app](https://railway.app) with GitHub
2. Click **New Project** → **Deploy from GitHub repo** → select the repo
3. Add a **PostgreSQL** database from the project canvas
4. Open the web service → **Variables** tab → add all production env vars (see above). Leave `ALLOWED_HOSTS` blank for the first deploy.
5. Wait for the first build. It will likely fail with a `DisallowedHost` error — that's expected.
6. Go to **Settings** → **Networking** → **Generate Domain**. Copy the domain (e.g. `knitblog-production-xxxx.up.railway.app`).
7. Update `ALLOWED_HOSTS` to that domain. Railway redeploys automatically.
8. Open the Railway shell (three-dot menu → Shell) and run:
   ```bash
   /opt/venv/bin/python manage.py createsuperuser
   ```
   Fill in the prompts.
9. Visit your live URL.

### Handling media files

Railway's filesystem is ephemeral — uploaded images are lost on every redeploy. Two options:

**Option A (simple, temporary):** Serve media through Django in `knit_blog/urls.py`:

```python
from django.urls import re_path
from django.views.static import serve
from django.conf import settings

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
```

Images work but disappear on every redeploy.

**Option B (recommended, permanent):** Use Cloudinary for media storage.

1. Sign up at [cloudinary.com](https://cloudinary.com)
2. Install: `pip install cloudinary django-cloudinary-storage`
3. Add to `INSTALLED_APPS`:
   ```python
   'cloudinary_storage',
   'cloudinary',
   ```
4. Update `STORAGES`:
   ```python
   STORAGES = {
       "default": {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"},
       "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
   }
   ```
5. Add `CLOUDINARY_STORAGE` credentials from env vars
6. Set `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` on Railway

---

## Security

KnitBlog implements several security measures. Highlights:

- **HTML sanitization** — user-submitted rich-text content passes through `nh3` before being saved, stripping `<script>`, `javascript:` URLs, and unsafe attributes
- **CSRF protection** — every state-changing endpoint requires POST and a valid CSRF token
- **Open redirect prevention** — all redirects via `?next=` or `Referer` are validated against `ALLOWED_HOSTS`
- **Environment-based secrets** — no secret keys, API credentials, or email passwords in the repository
- **Production hardening** — when `DEBUG=False`, the following are automatically enabled:
  - HTTPS redirect
  - Secure cookies (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`)
  - HSTS with subdomains and preload
  - Content-Type nosniff
  - Referrer policy `same-origin`
  - X-Frame-Options `DENY`
  - `CSRF_TRUSTED_ORIGINS` built from `ALLOWED_HOSTS`

### Reporting a vulnerability

If you find a security issue, please email itzishita2003@gmail.com with steps to reproduce. Do not open a public GitHub issue for security vulnerabilities.

---

## Testing

Run the Django test suite:

```bash
python manage.py test
```

Run the production readiness check:

```bash
python manage.py check --deploy
```

If you're adding tests, place them in `blog/tests.py` or create a `blog/tests/` package. Each model and view should ideally have coverage for:

- Happy path (valid input → expected result)
- Permission boundaries (anonymous, non-owner, owner)
- Form validation failures
- Edge cases (empty post, invalid slug, self-friend request)

---

## Contributing

Contributions are welcome. To propose a change:

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes, following the existing code style
4. Add tests where applicable
5. Commit with a clear message:
   ```bash
   git commit -m "Add: brief description of the change"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Open a Pull Request against `main` with a description of the change and any relevant screenshots

Please do not commit `.env`, `db.sqlite3`, `media/`, or `staticfiles/`.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Acknowledgements

- Django Software Foundation
- Quill rich text editor
- Bootstrap and Bootstrap Icons
- Nh3 HTML sanitizer
- Railway for hosting
- Everyone who has read, shared, or contributed to KnitBlog

---

## Contact

**Ishita Mehra**
LinkedIn: [linkedin.com/in/ishitamehra16](https://www.linkedin.com/in/ishitamehra16)
Email: itzishita2003@gmail.com

If you build something with KnitBlog, or use it as a learning reference, a short note is always appreciated.

---

Built with care, one commit at a time.
