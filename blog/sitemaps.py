from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Post, Category, Tag


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Post.objects.filter(status='published', original_post__isnull=True)

    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Category.objects.all()


class TagSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Tag.objects.all()


class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.4

    def items(self):
        return ['home', 'post-list', 'get-started']

    def location(self, item):
        return reverse(item)