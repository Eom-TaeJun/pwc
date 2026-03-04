"""
MD 보고서 → PDF 변환 스크립트
사용: python scripts/export_pdf.py [--date YYYYMMDD]
"""
import sys
import argparse
from pathlib import Path
import markdown

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');

@font-face {
    font-family: 'NanumGothic';
    src: local('NanumGothic'), local('나눔고딕');
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: 'NanumGothic', 'Noto Sans CJK KR', 'Noto Sans KR', sans-serif;
    font-size: 10pt;
    line-height: 1.7;
    color: #1a1a2e;
    padding: 0;
}

@page {
    size: A4;
    margin: 18mm 16mm 18mm 16mm;
    @bottom-right {
        content: counter(page) " / " counter(pages);
        font-size: 8pt;
        color: #888;
        font-family: 'NanumGothic', sans-serif;
    }
    @top-left {
        content: "PwC Factor Pool 분석 보고서";
        font-size: 8pt;
        color: #888;
        font-family: 'NanumGothic', sans-serif;
    }
}

/* 제목 */
h1 {
    font-size: 16pt;
    font-weight: 700;
    color: #d4380d;
    border-bottom: 3px solid #d4380d;
    padding-bottom: 8px;
    margin-bottom: 12px;
    margin-top: 0;
    line-height: 1.4;
}

h2 {
    font-size: 13pt;
    font-weight: 700;
    color: #0d4f8c;
    border-left: 4px solid #0d4f8c;
    padding-left: 10px;
    margin-top: 20px;
    margin-bottom: 8px;
    page-break-after: avoid;
}

h3 {
    font-size: 11pt;
    font-weight: 700;
    color: #333;
    margin-top: 14px;
    margin-bottom: 6px;
    page-break-after: avoid;
}

h4 {
    font-size: 10pt;
    font-weight: 700;
    color: #555;
    margin-top: 10px;
    margin-bottom: 4px;
}

p {
    margin-bottom: 8px;
}

/* 테이블 */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 10px 0;
    font-size: 9pt;
    page-break-inside: avoid;
}

thead tr {
    background-color: #0d4f8c;
    color: white;
}

th {
    padding: 7px 10px;
    text-align: left;
    font-weight: 700;
}

td {
    padding: 6px 10px;
    border-bottom: 1px solid #e0e0e0;
}

tr:nth-child(even) td {
    background-color: #f5f8ff;
}

tr:last-child td {
    border-bottom: 2px solid #0d4f8c;
}

/* 인용 블록 (핵심 발견) */
blockquote {
    border-left: 4px solid #fa8c16;
    background-color: #fff7e6;
    padding: 8px 14px;
    margin: 10px 0;
    color: #7c4700;
    font-size: 9.5pt;
    page-break-inside: avoid;
}

blockquote p {
    margin: 0;
}

/* 코드 */
code {
    background-color: #f0f4ff;
    padding: 1px 5px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 8.5pt;
    color: #c41d7f;
}

pre {
    background-color: #f6f8fa;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 10px 14px;
    overflow-x: auto;
    font-size: 8pt;
    margin: 8px 0;
    page-break-inside: avoid;
}

pre code {
    background: none;
    padding: 0;
    color: #333;
}

/* 구분선 */
hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 14px 0;
}

/* 강조 */
strong { color: #0d4f8c; font-weight: 700; }
em { color: #555; }

/* 경고 기호 포함 단락 */
p:has(> strong:first-child) {
    background-color: #f0f4ff;
    border-radius: 4px;
    padding: 6px 10px;
}

ul, ol {
    padding-left: 18px;
    margin-bottom: 8px;
}

li {
    margin-bottom: 3px;
}

/* 이미지 */
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 10px auto;
    page-break-inside: avoid;
}

/* 페이지 분리 제어 */
h2 { page-break-before: auto; }
"""


def md_to_pdf(md_path: Path, pdf_path: Path):
    try:
        from weasyprint import HTML, CSS as WeasyprintCSS
    except ImportError:
        print("ERROR: weasyprint 필요 — pip install weasyprint")
        sys.exit(1)

    md_text = md_path.read_text(encoding="utf-8")

    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "toc", "nl2br", "attr_list"],
    )

    html_full = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<style>{CSS}</style>
</head>
<body>
{html_body}
</body>
</html>"""

    # HTML 중간 파일 저장 (검토용)
    html_path = pdf_path.with_suffix(".html")
    html_path.write_text(html_full, encoding="utf-8")
    print(f"HTML 저장: {html_path}")

    HTML(string=html_full, base_url=str(Path.cwd())).write_pdf(
        str(pdf_path),
        stylesheets=[WeasyprintCSS(string=CSS)],
    )
    print(f"PDF 저장: {pdf_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=None, help="YYYYMMDD 또는 YYYYMMDD_v2 등 접미사 포함 가능")
    parser.add_argument("--file", default=None, help="MD 파일 직접 지정 (경로)")
    args = parser.parse_args()

    reports_dir = Path("outputs/reports")

    if args.file:
        md_path = Path(args.file)
    elif args.date:
        md_path = reports_dir / f"factor_pool_{args.date}.md"
    else:
        candidates = sorted(reports_dir.glob("factor_pool_*.md"))
        if not candidates:
            print("ERROR: outputs/reports/factor_pool_*.md 없음")
            sys.exit(1)
        md_path = candidates[-1]

    if not md_path.exists():
        print(f"ERROR: {md_path} 없음")
        sys.exit(1)

    pdf_path = reports_dir / (md_path.stem + ".pdf")
    print(f"변환 중: {md_path.name} → {pdf_path.name}")
    md_to_pdf(md_path, pdf_path)


if __name__ == "__main__":
    main()
