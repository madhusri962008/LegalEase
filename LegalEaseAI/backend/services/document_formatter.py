from io import BytesIO
import re
import zipfile
from xml.sax.saxutils import escape



def sanitize_text(text: str) -> str:
    if text is None:
        return ""

    return str(text).replace("\r\n", "\n").replace("\r", "\n").strip()

def format_txt(text: str) -> bytes:
    return sanitize_text(text).encode("utf-8")


def _xml_text(text: str) -> str:
    return escape(text)


def format_docx(
    text: str,
    doc_type: str,
    logo_path=None
) -> bytes:

    paragraphs = []

    title = f"""
<w:p>
    <w:pPr>
        <w:jc w:val="center"/>
        <w:spacing w:after="240"/>
    </w:pPr>
    <w:r>
        <w:rPr>
            <w:b/>
            <w:sz w:val="32"/>
        </w:rPr>
        <w:t>{_xml_text(doc_type)}</w:t>
    </w:r>
</w:p>
"""

    paragraphs.append(title)

    for raw_line in sanitize_text(text).splitlines():

        line = raw_line.strip()

        if not line:
            paragraphs.append("<w:p/>")
            continue

        if line.startswith("### "):
            content = line[4:]
            size = "22"
            bold = "<w:b/>"

        elif line.startswith("## "):
            content = line[3:]
            size = "24"
            bold = "<w:b/>"

        elif line.startswith("# "):
            content = line[2:]
            size = "28"
            bold = "<w:b/>"

        elif re.match(r"^[-*•]\s+", line):
            content = re.sub(r"^[-*•]\s+", "", line)
            content = "• " + content
            size = "22"
            bold = ""

        else:
            content = line
            size = "22"
            bold = ""

        paragraphs.append(
            f"""
<w:p>
    <w:pPr>
        <w:spacing w:after="120"/>
    </w:pPr>
    <w:r>
        <w:rPr>
            {bold}
            <w:sz w:val="{size}"/>
            <w:rFonts
                w:ascii="Times New Roman"
                w:hAnsi="Times New Roman"
            />
        </w:rPr>
        <w:t>{_xml_text(content)}</w:t>
    </w:r>
</w:p>
"""
        )

    paragraphs.append(
        """
<w:p>
    <w:pPr>
        <w:jc w:val="center"/>
    </w:pPr>
    <w:r>
        <w:rPr>
            <w:i/>
            <w:sz w:val="16"/>
        </w:rPr>
        <w:t>LegalEase - AI-assisted draft - Review before legal use</w:t>
    </w:r>
</w:p>
"""
    )

    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document
    xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        {''.join(paragraphs)}
        <w:sectPr>
            <w:pgSz w:w="12240" w:h="15840"/>
            <w:pgMar
                w:top="1008"
                w:right="1080"
                w:bottom="1008"
                w:left="1080"/>
        </w:sectPr>
    </w:body>
</w:document>
"""

    styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles
    xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:docDefaults>
        <w:rPrDefault>
            <w:rPr>
                <w:rFonts
                    w:ascii="Times New Roman"
                    w:hAnsi="Times New Roman"/>
                <w:sz w:val="22"/>
            </w:rPr>
        </w:rPrDefault>
    </w:docDefaults>
</w:styles>
"""

    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types
    xmlns="http://schemas.openxmlformats.org/package/2006/content-types">

    <Default
        Extension="rels"
        ContentType="application/vnd.openxmlformats-package.relationships+xml"/>

    <Default
        Extension="xml"
        ContentType="application/xml"/>

    <Override
        PartName="/word/document.xml"
        ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>

    <Override
        PartName="/word/styles.xml"
        ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>

</Types>
"""

    root_relationships = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships
    xmlns="http://schemas.openxmlformats.org/package/2006/relationships">

    <Relationship
        Id="rId1"
        Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
        Target="word/document.xml"/>

</Relationships>
"""

    document_relationships = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships
    xmlns="http://schemas.openxmlformats.org/package/2006/relationships">

    <Relationship
        Id="rId1"
        Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles"
        Target="styles.xml"/>

</Relationships>
"""

    output = BytesIO()

    with zipfile.ZipFile(
        output,
        "w",
        zipfile.ZIP_DEFLATED
    ) as docx:

        docx.writestr(
            "[Content_Types].xml",
            content_types
        )

        docx.writestr(
            "_rels/.rels",
            root_relationships
        )

        docx.writestr(
            "word/document.xml",
            document_xml
        )

        docx.writestr(
            "word/styles.xml",
            styles_xml
        )

        docx.writestr(
            "word/_rels/document.xml.rels",
            document_relationships
        )

    return output.getvalue()


def format_pdf(
    text: str,
    doc_type: str
) -> bytes:
    """
    Minimal PDF generator without fpdf/fontTools/lxml.
    """

    lines = []

    lines.append(doc_type)
    lines.append("")
    lines.extend(
        sanitize_text(text).splitlines()
    )

    lines.append("")
    lines.append(
        "LegalEase - AI-assisted draft - Review before legal use"
    )

    # PDF text content
    pdf_lines = []

    for line in lines:
        line = line.replace(
            "\\",
            "\\\\"
        )
        line = line.replace(
            "(",
            "\\("
        )
        line = line.replace(
            ")",
            "\\)"
        )

        # Keep basic printable text
        line = line.encode(
            "latin-1",
            "replace"
        ).decode(
            "latin-1"
        )

        pdf_lines.append(line)

    content = "BT\n"
    content += "/F1 11 Tf\n"
    content += "50 760 Td\n"

    for line in pdf_lines:

        content += f"({line}) Tj\n"
        content += "0 -16 Td\n"

    content += "ET\n"

    content_bytes = content.encode(
        "latin-1"
    )

    objects = []

    objects.append(
        b"<< /Type /Catalog /Pages 2 0 R >>"
    )

    objects.append(
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"
    )

    objects.append(
        b"""<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Resources <<
    /Font <<
        /F1 4 0 R
    >>
>>
/Contents 5 0 R
>>"""
    )

    objects.append(
        b"""<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>"""
    )

    objects.append(
        b"<< /Length "
        + str(
            len(content_bytes)
        ).encode()
        + b" >>\nstream\n"
        + content_bytes
        + b"endstream"
    )

    pdf = bytearray()

    pdf.extend(
        b"%PDF-1.4\n"
    )

    offsets = [
        0
    ]

    for index, obj in enumerate(
        objects,
        start=1
    ):

        offsets.append(
            len(pdf)
        )

        pdf.extend(
            f"{index} 0 obj\n".encode()
        )

        pdf.extend(obj)

        pdf.extend(
            b"\nendobj\n"
        )

    xref_position = len(pdf)

    pdf.extend(
        f"xref\n0 {len(objects) + 1}\n".encode()
    )

    pdf.extend(
        b"0000000000 65535 f \n"
    )

    for offset in offsets[1:]:

        pdf.extend(
            f"{offset:010d} 00000 n \n".encode()
        )

    pdf.extend(
        b"trailer\n"
    )

    pdf.extend(
        f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode()
    )

    pdf.extend(
        b"startxref\n"
    )

    pdf.extend(
        f"{xref_position}\n".encode()
    )

    pdf.extend(
        b"%%EOF"
    )

    return bytes(pdf)