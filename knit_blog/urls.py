from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
]

# ---------------------------------------------------------
#   Media files (user uploads: avatars, featured images)
#   Served in both dev and production.
#
#   ⚠️ On Railway, the filesystem is ephemeral — files are
#   wiped on every redeploy. This works but images will be
#   lost each time you push. For persistence, use Cloudinary.
# ---------------------------------------------------------
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# ---------------------------------------------------------
#   Static files
#   In dev, Django serves them from STATICFILES_DIRS.
#   In production, WhiteNoise handles them via the middleware
#   in settings.py, so we don't add static() here.
# ---------------------------------------------------------
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)