

# backend/app/core/counter.py

# Simple in-memory counter
# Resets on server restart — acceptable for free tier
# Will Upgrade path: replace with Postgres later, zero other code changes needed

_counts = {
    "analyzed": 0,
    "updated": 0
}

def increment_analyzed():
    _counts["analyzed"] += 1

def increment_updated():
    _counts["updated"] += 1

def get_counts() -> dict:
    return dict(_counts)