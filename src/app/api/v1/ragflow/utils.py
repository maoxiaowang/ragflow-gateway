from urllib.parse import quote


def get_filename_from_response(resp) -> str:
    cd = resp.headers.get("content-disposition")
    if not cd:
        return "document"

    # 简单解析 filename
    for part in cd.split(";"):
        part = part.strip()
        if part.startswith("filename="):
            return part.split("=", 1)[1].strip('"')

    return "document"


def get_content_disposition(filename: str) -> str:
    """
    返回可以处理中文/特殊字符的 Content-Disposition
    """
    quoted_name = quote(filename)
    return f"attachment; filename*=UTF-8''{quoted_name}"
