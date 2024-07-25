from datetime import datetime

def format_date(value):
    """Convert timestamp to date only."""
    if isinstance(value, str):
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        except ValueError:
            return value
    return value
