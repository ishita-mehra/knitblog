import hashlib
from datetime import date

from .models import FriendRequest
from .maker_notes import MAKER_NOTES


def notifications(request):
    """Adds `pending_requests_count` for the nav badge (logged-in users only)."""
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated:
        return {
            "pending_requests_count": FriendRequest.objects.filter(
                receiver=user, status="pending"
            ).count()
        }
    return {}


def maker_note(request):
    """Picks one note from MAKER_NOTES per user per day.

    The pick is deterministic (same user + same day → same note), so
    refreshing the page doesn't reshuffle the card, but tomorrow the
    user sees a different note.
    """
    if not MAKER_NOTES:
        return {}

    user = getattr(request, "user", None)
    user_key = user.id if (user is not None and user.is_authenticated) else "anon"
    seed = f"{user_key}-{date.today().isoformat()}"

    idx = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(MAKER_NOTES)
    return {"maker_note": MAKER_NOTES[idx]}