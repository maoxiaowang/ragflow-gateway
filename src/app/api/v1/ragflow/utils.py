from urllib.parse import quote


def get_content_disposition(filename: str) -> str:
    """
    返回可以处理中文/特殊字符的 Content-Disposition
    """
    quoted_name = quote(filename)
    return f"attachment; filename*=UTF-8''{quoted_name}"
