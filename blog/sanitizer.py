"""
HTML sanitizing for rich-text post content (Quill output).

Requires:  pip install nh3
"""
import nh3

ALLOWED_TAGS = {
    "p", "br", "strong", "em", "u", "s", "h1", "h2", "h3",
    "ul", "ol", "li", "blockquote", "pre", "code", "a", "img", "span",
}

ALLOWED_ATTRIBUTES = {
    "a": {"href", "target"},
    "img": {"src", "alt"},
    "*": {"class"},  # Quill uses ql-* classes for code blocks / indents
}

# "data" is allowed only so Quill's inline base64 images survive;
# the filter below restricts it to data:image/* on <img src> only.
ALLOWED_SCHEMES = {"http", "https", "mailto", "data"}


def _attribute_filter(tag, attr, value):
    v = value.strip().lower()
    if v.startswith("data:"):
        if tag == "img" and attr == "src" and v.startswith("data:image/"):
            return value
        return None  # drop data: anywhere else (e.g. <a href="data:...">)
    return value


def clean_html(value):
    """Return `value` with everything outside the whitelist removed."""
    if not value:
        return ""
    return nh3.clean(
        value,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes=ALLOWED_SCHEMES,
        attribute_filter=_attribute_filter,
        link_rel="noopener noreferrer nofollow",
    )
