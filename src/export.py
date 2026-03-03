"""
목적: Factor Pool 보고서 MD → print-ready HTML 변환
입력: outputs/reports/factor_pool_YYYYMMDD.md
출력: outputs/reports/factor_pool_YYYYMMDD.html
제외: PDF 변환 (브라우저 Ctrl+P로 대체), 외부 바이너리 의존
"""
import glob
import os

import markdown

OUTPUT_DIR = "outputs/reports"

_CSS = """
<style>
  body { font-family: 'Noto Sans KR', Arial, sans-serif; max-width: 900px;
         margin: 40px auto; padding: 0 24px; color: #1a1a1a; line-height: 1.7; }
  h1 { font-size: 1.6em; border-bottom: 3px solid #003087; padding-bottom: 8px;
       color: #003087; }
  h2 { font-size: 1.2em; margin-top: 2em; color: #003087;
       border-left: 4px solid #d4a800; padding-left: 10px; }
  h3 { font-size: 1em; color: #444; }
  table { border-collapse: collapse; width: 100%; font-size: 0.88em;
          margin: 12px 0; }
  th { background: #003087; color: white; padding: 8px 12px; text-align: left; }
  td { padding: 7px 12px; border-bottom: 1px solid #e0e0e0; }
  tr:nth-child(even) td { background: #f7f9fc; }
  blockquote { border-left: 3px solid #d4a800; margin: 0; padding: 8px 16px;
               background: #fffdf0; color: #555; }
  code { background: #f0f0f0; padding: 2px 5px; border-radius: 3px;
         font-size: 0.87em; }
  img { max-width: 100%; margin: 12px 0; }
  strong { color: #003087; }
  @media print {
    body { margin: 20px; }
    h1, h2 { page-break-after: avoid; }
    table { page-break-inside: avoid; }
  }
</style>
"""


def md_to_html(md_path: str = None) -> str:
    """Convert latest (or specified) MD report to print-ready HTML."""
    if md_path is None:
        files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "factor_pool_*.md")))
        if not files:
            raise FileNotFoundError(f"No factor_pool_*.md in {OUTPUT_DIR}")
        md_path = files[-1]

    with open(md_path, encoding="utf-8") as f:
        content = f.read()

    body = markdown.markdown(content, extensions=["tables", "fenced_code"])
    title = os.path.basename(md_path).replace(".md", "")
    html = f"""<!DOCTYPE html>
<html lang="ko"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{_CSS}
</head><body>
{body}
<p style="color:#888;font-size:0.8em;margin-top:3em;border-top:1px solid #ddd;padding-top:8px">
  PDF 저장: 브라우저에서 Ctrl+P → PDF로 인쇄
</p>
</body></html>"""

    out_path = md_path.replace(".md", ".html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✓ HTML 저장: {out_path}")
    return out_path


if __name__ == "__main__":
    md_to_html()
