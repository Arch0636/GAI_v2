def format_bytes(bytes_value):
    if bytes_value < 1024:
        return f"{bytes_value} B"
    elif bytes_value < 1024**2:
        return f"{bytes_value / 1024:.2f} KB"
    elif bytes_value < 1024**3:
        return f"{bytes_value / (1024**2):.2f} MB"
    else:
        return f"{bytes_value / (1024**3):.2f} GB"
