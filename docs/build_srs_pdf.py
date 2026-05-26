from pathlib import Path

import markdown
import fitz


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "SRS_PotionCheck.md"
HTML_OUT = ROOT / "SRS_PotionCheck.html"
PDF_OUT = ROOT / "SRS_PotionCheck.pdf"


css = """
@page {
  size: A4;
  margin: 18mm 16mm;
}
* {
  box-sizing: border-box;
}
body {
  color: #1f2937;
  font-family: Arial, Helvetica, sans-serif;
  font-size: 10.5pt;
  line-height: 1.45;
  margin: 0;
}
h1, h2, h3, h4 {
  color: #0f172a;
  line-height: 1.2;
  page-break-after: avoid;
}
h1 {
  border-bottom: 2px solid #0f766e;
  font-size: 24pt;
  margin: 0 0 8mm;
  padding-bottom: 4mm;
  text-align: center;
}
h2 {
  border-bottom: 1px solid #cbd5e1;
  font-size: 17pt;
  margin-top: 10mm;
  padding-bottom: 2mm;
}
h3 {
  font-size: 13pt;
  margin-top: 6mm;
}
p {
  margin: 0 0 3.5mm;
}
ul, ol {
  margin-bottom: 4mm;
  padding-left: 7mm;
}
table {
  border-collapse: collapse;
  margin: 4mm 0 6mm;
  width: 100%;
}
th, td {
  border: 1px solid #cbd5e1;
  padding: 2mm 2.4mm;
  vertical-align: top;
}
th {
  background: #e2f8f3;
  color: #0f172a;
  font-weight: 700;
}
code {
  background: #f1f5f9;
  border-radius: 3px;
  color: #0f172a;
  font-family: Consolas, monospace;
  font-size: 9.5pt;
  padding: 0.5mm 1mm;
}
pre {
  background: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 5px;
  overflow-wrap: anywhere;
  padding: 3mm;
  white-space: pre-wrap;
}
pre code {
  background: transparent;
  padding: 0;
}
hr {
  border: 0;
  border-top: 1px solid #cbd5e1;
  margin: 6mm 0;
}
.toc-list {
  font-size: 10pt;
  margin: 3mm 0 6mm;
}
.toc-line {
  align-items: baseline;
  display: flex;
  gap: 1.5mm;
  line-height: 1.22;
  margin: 0.7mm 0;
  width: 100%;
}
.toc-main {
  font-weight: 700;
  margin-top: 1.4mm;
}
.toc-sub {
  padding-left: 6mm;
}
.toc-title {
  white-space: nowrap;
}
.toc-dots {
  border-bottom: 1px dotted #111827;
  flex: 1 1 auto;
  min-width: 8mm;
  transform: translateY(-1.2mm);
}
.toc-page {
  min-width: 8mm;
  text-align: right;
}
"""


def main() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    body = markdown.markdown(text, extensions=["extra", "tables", "toc", "fenced_code"])
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>PotionCheck SRS</title>
  <style>{css}</style>
</head>
<body>
{body}
</body>
</html>
"""
    HTML_OUT.write_text(html, encoding="utf-8")

    writer = fitz.DocumentWriter(str(PDF_OUT))
    story = fitz.Story(body, user_css=css, em=10.5)
    media = fitz.paper_rect("a4")
    content_rect = fitz.Rect(45, 45, media.width - 45, media.height - 45)

    def rectfn(_rect_num, _filled):
        return media, content_rect, fitz.Identity

    story.write(writer, rectfn)
    writer.close()
    print(PDF_OUT)


if __name__ == "__main__":
    main()
