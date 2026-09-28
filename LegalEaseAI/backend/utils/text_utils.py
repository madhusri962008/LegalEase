def sanitize_text(text: str) -> str:
    if text is None:
        return ""

    return (
        str(text)
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .strip()
    )


def text_to_html(text: str) -> str:
    if not text:
        return ""

    html = (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    return html.replace("\n", "<br>")