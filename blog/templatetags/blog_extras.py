from django import template
from django.utils.safestring import mark_safe

from blog.sanitizer import clean_html

register = template.Library()


@register.filter(name="sanitize")
def sanitize(value):
    """{{ post.content|sanitize }} -- safe replacement for |safe on user HTML."""
    return mark_safe(clean_html(value or ""))
