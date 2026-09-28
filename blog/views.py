from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Q, Count
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.http import require_POST
import logging
import traceback

from .models import (
    Profile, Post, FriendRequest, Like, Comment,
    Category, Tag, SavedPost,
)
from .forms import (
    ProfileUpdateForm, PostForm, CommentForm, SearchForm,
    PasswordResetRequestForm, SetNewPasswordForm, validate_strong_password,
)


# =========================================
#   HELPERS
# =========================================

def _paginate(request, queryset, per_page=6):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get('page'))


def _published_posts():
    return (
        Post.objects
        .filter(status='published')
        .select_related('author', 'author__profile', 'category')
        .prefetch_related('tags', 'likes', 'comments')
    )


def _get_friends(user):
    """Return a list of User objects who are accepted friends of `user`."""
    freqs = (
        FriendRequest.objects
        .filter((Q(sender=user) | Q(receiver=user)) & Q(status='accepted'))
        .select_related('sender', 'sender__profile', 'receiver', 'receiver__profile')
    )
    return [fr.receiver if fr.sender == user else fr.sender for fr in freqs]


# =========================================
#   HOME / BLOG
# =========================================

def index(request):
    latest = _published_posts()[:6]
    categories = Category.objects.annotate(
        n=Count('posts', filter=Q(posts__status='published'))
    ).filter(n__gt=0)[:8]
    popular_tags = Tag.objects.annotate(
        n=Count('posts', filter=Q(posts__status='published'))
    ).filter(n__gt=0).order_by('-n')[:12]

    context = {
        'latest_posts': latest,
        'categories': categories,
        'popular_tags': popular_tags,
    }
    return render(request, 'index.html', context)


def post_list(request):
    qs = _published_posts()
    page_obj = _paginate(request, qs)
    categories = Category.objects.all()
    popular_tags = Tag.objects.all()[:20]

    context = {
        'page_obj': page_obj,
        'page_title': 'All Posts',
        'categories': categories,
        'popular_tags': popular_tags,
    }
    return render(request, 'post_list.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    qs = _published_posts().filter(category=category)
    page_obj = _paginate(request, qs)

    context = {
        'page_obj': page_obj,
        'page_title': f'Category: {category.name}',
        'categories': Category.objects.all(),
        'popular_tags': Tag.objects.all()[:20],
    }
    return render(request, 'post_list.html', context)


def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    qs = _published_posts().filter(tags=tag)
    page_obj = _paginate(request, qs)

    context = {
        'page_obj': page_obj,
        'page_title': f'Tag: #{tag.name}',
        'categories': Category.objects.all(),
        'popular_tags': Tag.objects.all()[:20],
    }
    return render(request, 'post_list.html', context)


def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects.select_related('author', 'author__profile', 'category')
                    .prefetch_related('tags', 'likes'),
        slug=slug
    )

    if post.status == 'draft' and post.author != request.user:
        messages.error(request, "This post is not available.")
        return redirect('post-list')

    Post.objects.filter(pk=post.pk).update(views=post.views + 1)

    top_comments = (
        post.comments.filter(is_approved=True, parent__isnull=True)
        .select_related('author', 'author__profile')
        .prefetch_related('replies__author', 'replies__author__profile')
    )

    related = (
        _published_posts().filter(category=post.category).exclude(pk=post.pk)[:3]
        if post.category else _published_posts().exclude(pk=post.pk)[:3]
    )

    user_has_shared = False
    user_has_saved = False
    if request.user.is_authenticated:
        user_has_shared = Post.objects.filter(
            author=request.user, original_post=post
        ).exists()
        user_has_saved = SavedPost.objects.filter(
            user=request.user, post=post
        ).exists()

    context = {
        'post': post,
        'comments': top_comments,
        'comment_form': CommentForm(),
        'related_posts': related,
        'user_has_liked': request.user.is_authenticated and post.likes.filter(user=request.user).exists(),
        'user_has_shared': user_has_shared,
        'user_has_saved': user_has_saved,
    }
    return render(request, 'post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                form.save_tags(post)
                messages.success(request, "Post created successfully.")
                return redirect(post.get_absolute_url())
            except Exception as exc:
                logging.getLogger('django').error(
                    "Post create failed: %s\n%s", exc, traceback.format_exc()
                )
                messages.error(request, f"Could not create post: {exc}")
        else:
            messages.error(request, "Please fix the errors below and try again.")
    else:
        form = PostForm()

    return render(request, 'post_form.html', {'form': form, 'is_edit': False})


@login_required
def post_update(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            try:
                post = form.save()
                form.save_tags(post)
                messages.success(request, "Post updated successfully.")
                return redirect(post.get_absolute_url())
            except Exception as exc:
                logging.getLogger('django').error(
                    "Post update failed: %s\n%s", exc, traceback.format_exc()
                )
                messages.error(request, f"Could not update post: {exc}")
        else:
            messages.error(request, "Please fix the errors below and try again.")
    else:
        form = PostForm(instance=post)

    return render(request, 'post_form.html', {'form': form, 'is_edit': True, 'post': post})


@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)

    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted.")
        return redirect('knitting-space')

    return render(request, 'post_confirm_delete.html', {'post': post})


# =========================================
#   SEARCH
# =========================================

def search(request):
    form = SearchForm(request.GET or None)
    results = Post.objects.none()
    query = ''

    if form.is_valid():
        query = form.cleaned_data.get('q', '').strip()
        if query:
            results = _published_posts().filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(tags__name__icontains=query) |
                Q(category__name__icontains=query) |
                Q(author__username__icontains=query)
            ).distinct()

    page_obj = _paginate(request, results)

    return render(request, 'search.html', {
        'form': form,
        'query': query,
        'page_obj': page_obj,
        'result_count': results.count() if query else 0,
    })


# =========================================
#   INTERACTIONS
# =========================================

@login_required
@require_POST
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like_qs = Like.objects.filter(user=request.user, post=post)
    if like_qs.exists():
        like_qs.delete()
    else:
        Like.objects.create(user=request.user, post=post)
    return redirect(request.META.get('HTTP_REFERER', post.get_absolute_url()))


@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        parent_id = request.POST.get('parent')
        if parent_id:
            parent = Comment.objects.filter(id=parent_id, post=post).first()
            if parent:
                comment.parent = parent
        comment.save()
        messages.success(request, "Comment added.")
    else:
        messages.error(request, "Could not add comment.")
    return redirect(post.get_absolute_url() + '#comments')


@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author == request.user or comment.post.author == request.user:
        post = comment.post
        comment.delete()
        messages.success(request, "Comment removed.")
        return redirect(post.get_absolute_url() + '#comments')
    messages.error(request, "You cannot delete this comment.")
    return redirect('home')


# =========================================
#   SHARE — toggle (like repost)
# =========================================

@login_required
@require_POST
def share_post(request, post_id):
    original = get_object_or_404(Post, id=post_id)

    # Can't share a post that is itself a share — always share the root post
    if original.original_post_id:
        original = original.original_post

    if original.author == request.user:
        messages.error(request, "You can't share your own post.")
        return redirect(request.META.get('HTTP_REFERER', original.get_absolute_url()))

    existing = Post.objects.filter(
        author=request.user, original_post=original
    ).first()

    if existing:
        existing.delete()
        messages.success(request, "Share removed from your profile.")
    else:
        Post.objects.create(
            author=request.user,
            title=f"Shared: {original.title}",
            content=original.content,
            excerpt=original.excerpt,
            category=original.category,
            original_post=original,
            status='published',
        )
        messages.success(request, "Post shared to your profile!")

    return redirect(request.META.get('HTTP_REFERER', original.get_absolute_url()))


# =========================================
#   SAVE — toggle
# =========================================

@login_required
@require_POST
def save_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    existing = SavedPost.objects.filter(user=request.user, post=post).first()

    if existing:
        existing.delete()
        messages.success(request, "Removed from your saved posts.")
    else:
        SavedPost.objects.create(user=request.user, post=post)
        messages.success(request, "Saved to your collection.")

    return redirect(request.META.get('HTTP_REFERER', post.get_absolute_url()))


# =========================================
#   PROFILE
# =========================================

def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    all_posts = (
        Post.objects.filter(author=profile_user)
        .select_related(
            'category',
            'original_post',
            'original_post__author',
            'original_post__author__profile',
        )
        .prefetch_related('tags', 'likes', 'comments')
        .order_by('-created_at')
    )

    if request.user != profile_user:
        all_posts = all_posts.filter(status='published')

    original_posts = all_posts.filter(original_post__isnull=True)
    shared_posts = all_posts.filter(original_post__isnull=False)

    friends_count = FriendRequest.objects.filter(
        (Q(sender=profile_user) | Q(receiver=profile_user)) & Q(status='accepted')
    ).count()

    friend_status = None
    incoming_request_id = None

    if request.user.is_authenticated and request.user != profile_user:
        existing = FriendRequest.objects.filter(
            Q(sender=request.user, receiver=profile_user) |
            Q(sender=profile_user, receiver=request.user)
        ).first()
        if existing:
            if existing.status == 'accepted':
                friend_status = 'friends'
            elif existing.sender == request.user:
                friend_status = 'sent'
            else:
                friend_status = 'received'
                incoming_request_id = existing.id

    # Friends list is ONLY shown to the profile owner
    my_friends = []
    if request.user == profile_user:
        my_friends = _get_friends(profile_user)

    context = {
        'profile_user': profile_user,
        'user_posts': all_posts,                # kept for backwards compatibility
        'original_posts': original_posts,
        'shared_posts': shared_posts,
        'total_posts': original_posts.count(),
        'total_shares': shared_posts.count(),
        'friends_count': friends_count,
        'friend_status': friend_status,
        'incoming_request_id': incoming_request_id,
        'my_friends': my_friends,
        'show_friends': request.user == profile_user,
    }
    return render(request, 'profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile-detail', username=request.user.username)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'edit_profile.html', {'form': form})


@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id).select_related('profile')
    return render(request, 'user_list.html', {'users': users})


# =========================================
#   FRIEND REQUESTS
# =========================================

@login_required
def send_friend_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    if receiver != request.user:
        exists = FriendRequest.objects.filter(
            Q(sender=request.user, receiver=receiver) |
            Q(sender=receiver, receiver=request.user)
        ).exists()
        if not exists:
            FriendRequest.objects.create(sender=request.user, receiver=receiver)
            messages.success(request, f"Friend request sent to {receiver.username}!")
        else:
            messages.info(request, "A connection or request already exists.")
    return redirect('profile-detail', username=receiver.username)


@login_required
def accept_friend_request(request, request_id):
    freq = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)
    freq.status = 'accepted'
    freq.save()
    messages.success(request, f"You are now friends with {freq.sender.username}!")
    return redirect(request.META.get('HTTP_REFERER', 'knitting-space'))


@login_required
def cancel_or_remove_friend(request, user_id):
    target = get_object_or_404(User, id=user_id)
    deleted, _ = FriendRequest.objects.filter(
        Q(sender=request.user, receiver=target) |
        Q(sender=target, receiver=request.user)
    ).delete()
    if deleted:
        messages.success(request, "Connection removed.")
    return redirect(request.META.get('HTTP_REFERER', 'knitting-space'))


# =========================================
#   KNITTING SPACE (dashboard)
# =========================================

@login_required
def knitting_space(request):
    section = request.GET.get('section', 'home')
    edit_mode = request.GET.get('edit') == 'true'

    profile, _ = Profile.objects.get_or_create(user=request.user)

    my_posts = (
        Post.objects.filter(author=request.user)
        .select_related('category')
        .prefetch_related('tags', 'likes', 'comments')
        .order_by('-created_at')
    )

    incoming_requests = (
        FriendRequest.objects.filter(receiver=request.user, status='pending')
        .select_related('sender', 'sender__profile')
        .order_by('-created_at')
    )

    # --- LIKES: two lists ---
    liked_posts = (
        Post.objects.filter(likes__user=request.user)
        .select_related('author', 'author__profile', 'category')
        .prefetch_related('tags', 'likes', 'comments')
        .order_by('-created_at')
        .distinct()
    )

    likes_received = (
        Like.objects.filter(post__author=request.user)
        .select_related('user', 'user__profile', 'post')
        .order_by('-created_at')[:80]
    )

    # --- SAVED ---
    saved_items = (
        SavedPost.objects.filter(user=request.user)
        .select_related(
            'post', 'post__author', 'post__author__profile', 'post__category'
        )
        .order_by('-created_at')
    )

    # --- FRIENDS ---
    my_friends = _get_friends(request.user)

    users = User.objects.exclude(id=request.user.id).select_related('profile')

    # --- Profile edit ---
    if request.method == 'POST' and section == 'profile':
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Your profile was updated successfully.')
            return redirect(f"{reverse('knitting-space')}?section=profile")
        else:
            messages.error(request, "Please fix the errors below.")
            edit_mode = True
    else:
        profile_form = ProfileUpdateForm(instance=profile)

    # --- Create post ---
    if request.method == 'POST' and section == 'create-post':
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            try:
                new_post = post_form.save(commit=False)
                new_post.author = request.user
                new_post.save()
                post_form.save_tags(new_post)
                messages.success(request, 'Your post was created successfully.')
                return redirect(f"{reverse('knitting-space')}?section=my-posts")
            except Exception as exc:
                logging.getLogger('django').error(
                    "Post create (space) failed: %s\n%s", exc, traceback.format_exc()
                )
                messages.error(request, f"Could not create post: {exc}")
        else:
            messages.error(request, "Please fix the errors below and try again.")
    else:
        post_form = PostForm()

    context = {
        'section': section,
        'edit_profile': edit_mode,
        'my_posts': my_posts,
        'profile_posts': my_posts,
        'incoming_requests': incoming_requests,
        'liked_posts': liked_posts,
        'likes_received': likes_received,
        'saved_items': saved_items,
        'my_friends': my_friends,
        'users': users,
        'post_form': post_form,
        'profile_form': profile_form,
    }
    return render(request, 'knitting_space.html', context)


# =========================================
#   AUTH
# =========================================

def get_started(request):
    return render(request, 'get_started.html')


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(request.GET.get('next') or 'home')
        messages.error(request, "Invalid username or password.")
        return redirect('login')
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


def user_signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Choose another.")
            return redirect('signup')

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect('signup')

        try:
            validate_strong_password(password)
        except ValidationError as exc:
            messages.error(request, exc.messages[0])
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    return render(request, 'signup.html')


# =========================================
#   PASSWORD RESET
# =========================================

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email__iexact=email).first()

            if user is not None:
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                reset_path = reverse(
                    'password-reset-confirm',
                    kwargs={'uidb64': uidb64, 'token': token},
                )
                reset_link = request.build_absolute_uri(reset_path)

                send_mail(
                    subject="Reset your KnitBlog password",
                    message=(
                        f"Hi {user.username},\n\n"
                        "We received a request to reset your KnitBlog password. "
                        f"Click the link below to choose a new one:\n\n{reset_link}\n\n"
                        "This link will expire soon for your security. "
                        "If you didn't request this, you can safely ignore this email."
                    ),
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@knitblog.com'),
                    recipient_list=[email],
                    fail_silently=True,
                )

            messages.success(
                request,
                "If that email is registered, we've sent a password reset link to it."
            )
            return redirect('login')
    else:
        form = PasswordResetRequestForm()

    return render(request, 'password_reset_request.html', {'form': form})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    link_is_valid = user is not None and default_token_generator.check_token(user, token)

    if not link_is_valid:
        messages.error(request, "This password reset link is invalid or has expired. Please request a new one.")
        return redirect('password-reset')

    if request.method == "POST":
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            messages.success(request, "Your password has been reset successfully. Please log in.")
            return redirect('login')
    else:
        form = SetNewPasswordForm()

    return render(request, 'password_reset_confirm.html', {'form': form})