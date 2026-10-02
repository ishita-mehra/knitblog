"""
Notes from the developer, shown in a rotating card on the home pages.

How it works:
    Each visitor sees ONE note per day. The choice is stable for the
    whole day (so refreshing doesn't change it), and different users
    may see different notes — it's a soft shuffle, not a hard rotation.

Add, edit, or remove messages freely — the system adapts automatically.

Fields per note:
    id      : unique string (used by the dismiss button's localStorage key)
    text    : the message body (plain text, supports the link below)
    link    : optional {"url": "...", "label": "..."}
    suffix  : optional text appended after the link / text
"""

LINKEDIN_URL = "https://www.linkedin.com/in/ishitamehra16"


MAKER_NOTES = [
    {
        "id": "slow_internet",
        "text": (
            "Hi, I'm Ishita — I built KnitBlog because I missed the slow, "
            "personal internet. I hope you find something here worth reading today."
        ),
    },
    {
        "id": "say_hi",
        "text": (
            "I'm Ishita — I built this site. If you ever get stuck, want a "
            "feature added, or just want to say hi, you can find me on"
        ),
        "link": {"url": LINKEDIN_URL, "label": "LinkedIn"},
        "suffix": "Happy Blogging!",
    },
    {
        "id": "why_write",
        "text": (
            "Writing online changed how I think. If you're unsure what to post "
            "about, start with the last thing that made you pause today."
        ),
    },
    {
        "id": "first_draft",
        "text": (
            "A small reminder from me: the first draft doesn't have to be good. "
            "It just has to exist. You can always edit it tomorrow."
        ),
    },
    {
        "id": "be_kind",
        "text": (
            "KnitBlog is small on purpose. Be kind to the people you meet here "
            "— they're figuring it out too."
        ),
    },
    {
        "id": "thanks",
        "text": (
            "Thank you for reading. Really. A site like this only works because "
            "people like you show up."
        ),
    },
]