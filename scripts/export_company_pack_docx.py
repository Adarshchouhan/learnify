from __future__ import annotations

import html
import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "docs" / "company-pack"
OUTPUT_DIR = ROOT / "docs" / "company-pack-docx"


CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>
"""

ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""

DOCUMENT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>
"""

STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:spacing w:after="160" w:line="276" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Aptos" w:hAnsi="Aptos"/><w:sz w:val="22"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:spacing w:after="220"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="36"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:spacing w:before="220" w:after="120"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="30"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:spacing w:before="180" w:after="100"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="26"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Code">
    <w:name w:val="Code"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:spacing w:after="80"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/><w:sz w:val="20"/></w:rPr>
  </w:style>
</w:styles>
"""


def clean_inline(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = text.replace("**", "")
    return text


def run(text: str, bold: bool = False) -> str:
    props = "<w:rPr><w:b/></w:rPr>" if bold else ""
    return f"<w:r>{props}<w:t xml:space=\"preserve\">{html.escape(text)}</w:t></w:r>"


def paragraph(text: str, style: str = "Normal", indent: int = 0, bullet: bool = False) -> str:
    ppr = f"<w:pStyle w:val=\"{style}\"/>"
    if indent:
        ppr += f"<w:ind w:left=\"{indent}\" w:hanging=\"360\"/>"
    prefix = ""
    if bullet:
        prefix = run("- ")
    return f"<w:p><w:pPr>{ppr}</w:pPr>{prefix}{run(clean_inline(text))}</w:p>"


def markdown_to_word_body(markdown: str) -> str:
    parts: list[str] = []
    in_code = False

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code = not in_code
            continue

        if not stripped:
            continue

        if in_code:
            parts.append(paragraph(stripped, "Code"))
            continue

        if stripped.startswith("# "):
            parts.append(paragraph(stripped[2:].strip(), "Title"))
        elif stripped.startswith("## "):
            parts.append(paragraph(stripped[3:].strip(), "Heading1"))
        elif stripped.startswith("### "):
            parts.append(paragraph(stripped[4:].strip(), "Heading2"))
        elif stripped.startswith("- [ ] "):
            parts.append(paragraph("[ ] " + stripped[6:].strip(), indent=720, bullet=True))
        elif stripped.startswith("- "):
            parts.append(paragraph(stripped[2:].strip(), indent=720, bullet=True))
        elif re.match(r"^\d+\.\s+", stripped):
            parts.append(paragraph(stripped, indent=720))
        else:
            parts.append(paragraph(stripped))

    return "\n".join(parts)


def write_docx(markdown_path: Path, output_path: Path) -> None:
    body = markdown_to_word_body(markdown_path.read_text(encoding="utf-8"))
    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {body}
    <w:sectPr>
      <w:pgSz w:w="12240" w:h="15840"/>
      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/>
    </w:sectPr>
  </w:body>
</w:document>
"""

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", CONTENT_TYPES)
        docx.writestr("_rels/.rels", ROOT_RELS)
        docx.writestr("word/_rels/document.xml.rels", DOCUMENT_RELS)
        docx.writestr("word/styles.xml", STYLES)
        docx.writestr("word/document.xml", document)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for markdown_path in sorted(SOURCE_DIR.glob("*.md")):
        output_path = OUTPUT_DIR / f"{markdown_path.stem}.docx"
        write_docx(markdown_path, output_path)


if __name__ == "__main__":
    main()

