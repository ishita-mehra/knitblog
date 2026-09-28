from django.contrib import admin
from django.urls import path
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from blog import views
from blog.sitemaps import PostSitemap, CategorySitemap, TagSitemap, StaticSitemap
from blog.feeds import LatestPostsFeed

sitemaps = {
    'posts': PostSitemap,
    'categories': CategorySitemap,
    'tags': TagSitemap,
    'static': StaticSitemap,
}

urlpatterns = [
    path("", views.index, name="home"),

    # Blog
    path("posts/", views.post_list, name="post-list"),
    path("posts/new/", views.post_create, name="post-create"),
    path("posts/<slug:slug>/", views.post_detail, name="post-detail"),
    path("posts/<slug:slug>/edit/", views.post_update, name="post-update"),
    path("posts/<slug:slug>/delete/", views.post_delete, name="post-delete"),

    # Taxonomy
    path("category/<slug:slug>/", views.category_detail, name="category-detail"),
    path("tag/<slug:slug>/", views.tag_detail, name="tag-detail"),

    # Search
    path("search/", views.search, name="search"),

    # Interactions
    path("post/like/<int:post_id>/", views.like_post, name="like-post"),
    path("post/comment/<int:post_id>/", views.add_comment, name="add-comment"),
    path("comment/<int:comment_id>/delete/", views.delete_comment, name="delete-comment"),
    path("post/share/<int:post_id>/", views.share_post, name="share-post"),
    path("post/save/<int:post_id>/", views.save_post, name="save-post"),

    # Auth
    path("get-started/", views.get_started, name="get-started"),
    path("login/", views.user_login, name="login"),
    path("signup/", views.user_signup, name="signup"),
    path("logout/", views.user_logout, name="logout"),
    path("password-reset/", views.password_reset_request, name="password-reset"),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        views.password_reset_confirm,
        name="password-reset-confirm"
    ),

    # Profiles
    path("profile/edit/", views.edit_profile, name="edit-profile"),
    path("profile/<str:username>/", views.user_profile, name="profile-detail"),
    path("users/", views.user_list, name="user-list"),

    # Friends
    path("friend/send/<int:user_id>/", views.send_friend_request, name="send-friend-request"),
    path("friend/accept/<int:request_id>/", views.accept_friend_request, name="accept-friend-request"),
    path("friend/remove/<int:user_id>/", views.cancel_or_remove_friend, name="remove-friend"),

    # Dashboard
    path("knitting-space/", views.knitting_space, name="knitting-space"),

    # SEO
    path("sitemap.xml", sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path("robots.txt", TemplateView.as_view(
        template_name="robots.txt", content_type="text/plain"
    ), name='robots'),
    path("feed/", LatestPostsFeed(), name='post-feed'),
]