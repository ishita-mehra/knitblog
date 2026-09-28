from django.contrib import admin
from django.utils.html import format_html
from blog import models


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'location', 'created_at')
    search_fields = ('user__username', 'name', 'bio')


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'views', 'published_at', 'thumb')
    list_filter = ('status', 'category', 'tags', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    list_editable = ('status',)
    readonly_fields = ('views', 'created_at', 'updated_at')
    filter_horizontal = ('tags',)
    fieldsets = (
        (None, {'fields': ('author', 'title', 'slug', 'status')}),
        ('Content', {'fields': ('excerpt', 'content', 'featured_image')}),
        ('Taxonomy', {'fields': ('category', 'tags')}),
        ('Meta', {'fields': ('original_post', 'views', 'created_at', 'updated_at')}),
    )

    def thumb(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" style="height:40px;border-radius:6px;" />', obj.featured_image.url)
        return "—"
    thumb.short_description = "Image"


@admin.register(models.Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('user__username', 'post__title')


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'parent', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    list_editable = ('is_approved',)
    search_fields = ('author__username', 'content')


@admin.register(models.FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('sender__username', 'receiver__username')


@admin.register(models.SavedPost)
class SavedPostAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    search_fields = ('user__username', 'post__title')
    list_filter = ('created_at',)