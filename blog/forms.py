import re
from django import forms
from django.utils.text import slugify
from django.utils.html import strip_tags
from .models import Profile, Post, Comment, Category, Tag


PASSWORD_REGEX = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$'
)

PASSWORD_HELP_TEXT = (
    "Must be at least 8 characters and include an uppercase letter, "
    "a lowercase letter, a number, and a symbol (e.g. Knit@2026)."
)


def validate_strong_password(password):
    if not password or not PASSWORD_REGEX.match(password):
        raise forms.ValidationError(PASSWORD_HELP_TEXT)


# =========================================
#   PROFILE
# =========================================

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'bio', 'avatar', 'website', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your display name'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tell people about yourself...'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, Country'}),
        }


# =========================================
#   POST
# =========================================

class PostForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        label="Tags",
        help_text="Comma separated, e.g. django, python, web",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'django, python, web',
        })
    )

    class Meta:
        model = Post
        fields = ['title', 'category', 'excerpt', 'content', 'featured_image', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'An interesting title...'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'excerpt': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Short summary (optional)'}),
            'content': forms.Textarea(attrs={'class': 'form-control knit-rich-editor', 'rows': 14}),
            'featured_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "— Uncategorized —"
        self.fields['category'].required = False
        self.fields['status'].required = False
        if self.instance.pk:
            self.fields['tags_input'].initial = ", ".join(t.name for t in self.instance.tags.all())

    def clean_title(self):
        title = (self.cleaned_data.get('title') or '').strip()
        if not title:
            raise forms.ValidationError("Please enter a title.")
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content') or ''
        # Quill sends "<p><br></p>" for empty editors — treat that as blank
        blanks = {
            '', '<p><br></p>', '<p><br/></p>', '<p></p>',
            '<br>', '<br/>', '<p><br></p><p><br></p>',
        }
        if content.strip() in blanks or not strip_tags(content).strip():
            raise forms.ValidationError("Please write some content before publishing.")
        return content

    def save_tags(self, post):
        raw = self.cleaned_data.get('tags_input', '') or ''
        names = [n.strip() for n in raw.split(',') if n.strip()]
        tags = []
        for name in names:
            existing = Tag.objects.filter(name__iexact=name).first()
            if not existing:
                base = slugify(name) or 'tag'
                slug = base
                i = 1
                while Tag.objects.filter(slug=slug).exists():
                    i += 1
                    slug = f"{base}-{i}"
                existing = Tag.objects.create(name=name, slug=slug)
            tags.append(existing)
        post.tags.set(tags)


# =========================================
#   COMMENT
# =========================================

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write a comment...',
            }),
        }


# =========================================
#   SEARCH
# =========================================

class SearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'knit-search-input',
            'placeholder': 'Search posts, tags, authors...',
        })
    )


# =========================================
#   FORGOT / RESET PASSWORD
# =========================================

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your registered email',
            'autofocus': True,
        })
    )


class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New password',
            'id': 'id_new_password',
            'autocomplete': 'new-password',
        }),
        help_text=PASSWORD_HELP_TEXT,
    )
    confirm_password = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password',
        })
    )

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password')
        p2 = cleaned.get('confirm_password')
        if p1:
            validate_strong_password(p1)
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("The two password fields didn't match.")
        return cleaned