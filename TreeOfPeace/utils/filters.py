from datetime import datetime

def format_date(value):
    """Convert timestamp to date only."""

    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d')
    return value
