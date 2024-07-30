from datetime import datetime

def format_date(value):
    """Convert timestamp to date only."""

    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d')
    return value


def truncate_content(content, length=100):
    """Truncate content to a specified length."""
    if len(content) <= length:
        return content
    else:
        return content[:length] + '...'
