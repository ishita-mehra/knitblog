from django.contrib.syndication.views import Feed
from django.utils.html import strip_tags
from .models import Post


class LatestPostsFeed(Feed):
    title = "KnitBlog — Latest Posts"
    link = "/posts/"
    description = "Fresh writing, thoughts and conversations from the KnitBlog community."

    def items(self):
        return (
            Post.objects
            .filter(status='published', original_post__isnull=True)
            .select_related('author', 'category')
            .prefetch_related('tags')
            .order_by('-created_at')[:20]
        )

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt or strip_tags(item.content)[:300]

    def item_link(self, item):
        return item.get_absolute_url()

    def item_author_name(self, item):
        return item.author.username

    def item_pubdate(self, item):
        return item.published_at or item.created_at

    def item_categories(self, item):
        cats = [t.name for t in item.tags.all()]
        if item.category:
            cats.append(item.category.name)
        return cats