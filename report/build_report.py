#!/usr/bin/env python3
"""Сборка PDF-отчёта: README.md -> HTML (титульник + стили) -> PDF (Chrome headless)."""
import base64, mimetypes, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPORT = ROOT / "report"
md_text = (ROOT / "README.md").read_text(encoding="utf-8")

# убрать строку с ссылкой на репозиторий из тела (она уйдёт в шапку) — оставляем как есть,
# просто рендерим весь README.
import markdown
html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])

# встроить картинки как data-URI, чтобы PDF был автономным
def embed(m):
    src = m.group(1)
    p = (ROOT / src).resolve()
    if not p.exists():
        return m.group(0)
    mime = mimetypes.guess_type(str(p))[0] or "image/png"
    data = base64.b64encode(p.read_bytes()).decode()
    return f'src="data:{mime};base64,{data}"'

html_body = re.sub(r'src="([^"]+)"', embed, html_body)

COVER = """
<section class="cover">
  <div class="univ">
    Федеральное государственное автономное образовательное учреждение высшего образования<br>
    «Национальный исследовательский университет ИТМО»
  </div>
  <div class="discipline">Дисциплина «Информационная безопасность»</div>
  <div class="work">Работа 4: Анализ уязвимостей веб-приложения с помощью OWASP ZAP</div>
  <div class="author">
    Выполнил: Молодиченко Семен Андреевич<br>
    Группа: P3313
  </div>
  <div class="city">Санкт-Петербург<br>2026</div>
</section>
<div class="pagebreak"></div>
"""

STYLE = """
<style>
  @page { size: A4; margin: 20mm 18mm; }
  * { box-sizing: border-box; }
  body { font-family: "PT Serif","Times New Roman",Georgia,serif; font-size: 11.5pt;
         line-height: 1.5; color: #1a1a1a; }
  h1 { font-size: 20pt; color: #0a3d62; border-bottom: 2px solid #0a3d62;
        padding-bottom: 6px; margin-top: 26px; }
  h2 { font-size: 15pt; color: #0a3d62; margin-top: 22px; }
  h3 { font-size: 12.5pt; color: #222; margin-top: 16px; }
  p, li { text-align: justify; }
  code { font-family: "SF Mono",Menlo,Consolas,monospace; font-size: 9.5pt;
          background: #f2f4f7; padding: 1px 4px; border-radius: 3px; }
  pre { background: #0b1021; color: #e6edf3; padding: 12px 14px; border-radius: 6px;
         overflow-x: auto; page-break-inside: avoid; }
  pre code { background: none; color: inherit; font-size: 9pt; white-space: pre-wrap;
             word-break: break-word; }
  table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 9.5pt;
           page-break-inside: avoid; }
  th, td { border: 1px solid #c3ccd6; padding: 6px 8px; text-align: left;
            vertical-align: top; }
  th { background: #e8eef5; color: #0a3d62; }
  tr:nth-child(even) td { background: #f7f9fc; }
  blockquote { border-left: 3px solid #0a3d62; margin: 12px 0; padding: 4px 14px;
               background: #f4f7fb; color: #333; font-size: 10.5pt; }
  img { max-width: 100%; border: 1px solid #c3ccd6; border-radius: 4px;
        margin: 10px auto; display: block; page-break-inside: avoid; }
  a { color: #0a4bd0; text-decoration: none; }
  .cover { height: 255mm; display: flex; flex-direction: column; text-align: center;
            font-family: "Times New Roman",serif; }
  .cover .univ { font-size: 13pt; line-height: 1.5; margin-top: 8mm; }
  .cover .discipline { font-size: 13pt; margin-top: 70mm; }
  .cover .work { font-size: 16pt; font-weight: bold; margin-top: 10mm; }
  .cover .author { font-size: 13pt; margin-top: auto; text-align: right; }
  .cover .city { font-size: 13pt; margin-top: 18mm; }
  .pagebreak { page-break-after: always; }
</style>
"""

html = f'<!doctype html><html lang="ru"><head><meta charset="utf-8">{STYLE}</head><body>{COVER}{html_body}</body></html>'
out_html = REPORT / "report.html"
out_html.write_text(html, encoding="utf-8")
print("HTML:", out_html)

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
out_pdf = REPORT / "report.pdf"
subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={out_pdf}", out_html.as_uri()], check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("PDF:", out_pdf)
