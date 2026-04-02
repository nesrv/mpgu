# -*- coding: utf-8 -*-
"""One-off: laba_k8s_docker_desktop.md -> laba_k8s_docker_desktop.html (reference: laba-deploy-vps-2.html)."""
import html
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
MD_PATH = HERE / "laba_k8s_docker_desktop.md"
OUT_PATH = HERE / "laba_k8s_docker_desktop.html"

LANG_MAP = {
    "powershell": "powershell",
    "python": "python",
    "yaml": "yaml",
    "dockerfile": "dockerfile",
    "text": "text",
}


def slug(s: str) -> str:
    s = re.sub(r"[^\w\s\-а-яА-ЯёЁ]", "", s.lower())
    s = re.sub(r"\s+", "-", s.strip())
    return s[:80] or "sec"


def inline_fmt(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", lambda m: "<code>" + m.group(1) + "</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    return s


def is_table_sep(cells: list) -> bool:
    if not cells:
        return False
    for c in cells:
        t = re.sub(r"\s+", "", c)
        if not t or not re.match(r"^:?-+:?$", t):
            return False
    return True


def _body_with_sections(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    in_fence = False
    fence_lang = ""
    fence_buf: list[str] = []
    para: list[str] = []
    in_ul = False
    in_ol = False
    section_open = False

    def flush_p():
        nonlocal para
        if para:
            t = " ".join(para).strip()
            if t:
                out.append("<p>" + inline_fmt(t) + "</p>")
        para = []

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    def open_section(title: str):
        nonlocal section_open
        if section_open:
            out.append("</div>")
        aid = slug(title)
        out.append(f'<div class="section" id="{aid}">')
        out.append(f"<h2>{inline_fmt(title)}</h2>")
        section_open = True
        return aid

    toc_collect: list[tuple[str, str]] = []

    while i < len(lines):
        line = lines[i]
        raw = line.rstrip()

        if raw.strip().startswith("```"):
            if not in_fence:
                flush_p()
                close_lists()
                in_fence = True
                fence_lang = raw.strip()[3:].strip() or "text"
                fence_buf = []
            else:
                code = "\n".join(fence_buf)
                hl = LANG_MAP.get(fence_lang.lower(), "text")
                out.append(
                    f'<div class="code-block"><code class="language-{hl}">{html.escape(code)}</code></div>'
                )
                in_fence = False
            i += 1
            continue

        if in_fence:
            fence_buf.append(line)
            i += 1
            continue

        if raw.strip() == "---":
            flush_p()
            close_lists()
            i += 1
            continue

        if raw.strip().startswith("|") and "|" in raw[1:]:
            flush_p()
            close_lists()
            rows: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row_line = lines[i].strip()
                cells = [c.strip() for c in row_line.split("|")[1:-1]]
                if not is_table_sep(cells):
                    rows.append(cells)
                i += 1
            if rows:
                out.append("<table>")
                for ri, row in enumerate(rows):
                    tag = "th" if ri == 0 else "td"
                    out.append("<tr>")
                    for cell in row:
                        out.append(f"<{tag}>{inline_fmt(cell)}</{tag}>")
                    out.append("</tr>")
                out.append("</table>")
            continue

        m = re.match(r"^(#{2,4})\s+(.+)$", raw)
        if m:
            flush_p()
            close_lists()
            level = len(m.group(1))
            title = m.group(2).strip()
            if level == 2:
                aid = open_section(title)
                toc_collect.append((title, aid))
            elif level == 3:
                out.append(f"<h3>{inline_fmt(title)}</h3>")
            else:
                out.append(f"<h4>{inline_fmt(title)}</h4>")
            i += 1
            continue

        ulm = re.match(r"^[-*]\s+(.+)$", raw)
        olm = re.match(r"^\d+\.\s+(.+)$", raw)
        if ulm or olm:
            flush_p()
            if ulm:
                if not in_ul:
                    if in_ol:
                        out.append("</ol>")
                        in_ol = False
                    out.append("<ul>")
                    in_ul = True
                out.append("<li>" + inline_fmt(ulm.group(1)) + "</li>")
            else:
                if not in_ol:
                    if in_ul:
                        out.append("</ul>")
                        in_ul = False
                    out.append("<ol>")
                    in_ol = True
                out.append("<li>" + inline_fmt(olm.group(1)) + "</li>")
            i += 1
            continue

        close_lists()

        if not raw.strip():
            flush_p()
            i += 1
            continue

        para.append(raw.strip())
        i += 1

    flush_p()
    close_lists()
    if section_open:
        out.append("</div>")

    global _LAST_TOC
    _LAST_TOC = toc_collect
    return "\n".join(out)


_LAST_TOC: list[tuple[str, str]] = []


def checklist_to_checkbox_items(html: str) -> str:
    """Секция 11: маркированный список → интерактивные чекбоксы (как в laba-deploy-vps-2)."""
    pattern = r'(<div class="section" id="11-чеклист">\s*<h2>11\. Чеклист</h2>)\s*<ul>(.*?)</ul>'
    m = re.search(pattern, html, flags=re.DOTALL)
    if not m:
        return html
    prefix, ul_inner = m.group(1), m.group(2)
    items = re.findall(r"<li>(.*?)</li>", ul_inner, flags=re.DOTALL)
    boxes = [prefix]
    for i, text in enumerate(items):
        tid = f"chk-k8s-dd-{i}"
        boxes.append(
            f'<div class="checkbox-item"><input type="checkbox" id="{tid}">'
            f'<label for="{tid}">{text.strip()}</label></div>'
        )
    replacement = "\n".join(boxes)
    return html[: m.start()] + replacement + html[m.end() :]


def main():
    md = MD_PATH.read_text(encoding="utf-8")
    # Drop first H1 lines - merge into header; body starts from ## 
    md_lines = md.splitlines()
    start = 0
    for j, ln in enumerate(md_lines):
        # Пропускаем обложку «# …» и подзаголовок без номера; тело с «## 1. …»
        if re.match(r"^##\s+\d", ln):
            start = j
            break
    else:
        for j, ln in enumerate(md_lines):
            if ln.startswith("## "):
                start = j
                break
    md_body = "\n".join(md_lines[start:])

    body = _body_with_sections(md_body)
    body = checklist_to_checkbox_items(body)
    toc = _LAST_TOC

    toc_html = "<ol>\n"
    for title, aid in toc:
        toc_html += f'  <li><a href="#{aid}">{html.escape(title)}</a></li>\n'
    toc_html += "</ol>\n"

    template = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Практическое занятие: Kubernetes в Docker Desktop (Windows)</title>
<style media="print">body{font-family:Arial,sans-serif;font-size:12px}.container{box-shadow:none;background:white}.header{background:white!important;color:black!important}.save-btn{display:none!important}.section{page-break-inside:avoid}</style>
<style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Segoe UI',sans-serif;line-height:1.6;color:#333;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh}.container{max-width:1200px;margin:20px auto;padding:20px;background:white;border-radius:15px;box-shadow:0 10px 30px rgba(0,0,0,0.2)}.header{text-align:center;padding:30px;background:linear-gradient(135deg,#005EB8,#003D82);color:white;border-radius:10px;margin-bottom:30px}.header h1{font-size:2.2em;margin-bottom:10px}.header p{opacity:.95;margin-top:8px}.student-info{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin-bottom:30px;padding:20px;background:#f8f9fa;border-radius:10px}.form-group{margin-bottom:20px}.form-group label{display:block;margin-bottom:5px;font-weight:bold;color:#003D82}.form-group input,.form-group textarea{width:100%;padding:12px;border:2px solid #e1e5e9;border-radius:8px;font-size:16px}.section{margin-bottom:40px;padding:25px;background:#fff;border-left:5px solid #005EB8;border-radius:0 10px 10px 0;box-shadow:0 2px 10px rgba(0,0,0,0.1)}.section h2{color:#003D82;margin-bottom:20px;font-size:1.65em}.section h3{color:#005EB8;margin:20px 0 10px;font-size:1.25em}.section h4{color:#1565c0;margin:16px 0 8px;font-size:1.1em}.code-block{background:#282c34;color:#e2e8f0;padding:20px;border-radius:8px;margin:15px 0;font-family:Consolas,'Courier New',monospace;overflow-x:auto;white-space:pre-wrap;font-size:13px;word-break:break-word}ul{list-style:none;padding-left:0}ul li{padding:8px 0 8px 30px;position:relative}ul li::before{content:'\\25b8';position:absolute;left:0;color:#005EB8;font-size:18px}ol{margin:10px 0 10px 24px}ol li{margin:8px 0;padding-left:6px}table{width:100%;border-collapse:collapse;margin:15px 0}table th,table td{border:1px solid #ddd;padding:12px;text-align:left;vertical-align:top}table th{background:#005EB8;color:white}table tr:nth-child(even){background:#f8f9fa}.checkbox-item{margin:15px 0;padding:15px 20px;background:linear-gradient(135deg,#005EB8,#003D82);border-radius:10px;display:flex;align-items:center}.checkbox-item input[type="checkbox"]{appearance:none;width:26px;height:26px;border:3px solid white;border-radius:6px;margin-right:15px;cursor:pointer;background:transparent;flex-shrink:0}.checkbox-item input[type="checkbox"]:checked{background:#fff url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23005EB8"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>') center/18px no-repeat;border-color:#fff}.checkbox-item label{color:white;font-weight:500;cursor:pointer}.save-btn{background:linear-gradient(135deg,#005EB8,#003D82);color:white;border:none;padding:15px 30px;font-size:18px;border-radius:10px;cursor:pointer;display:block;margin:30px auto}code{background:#f0f0f0;padding:2px 6px;border-radius:4px;font-size:0.9em}.section .code-block code{background:transparent;padding:0}.note{background:#e3f2fd;padding:15px;border-radius:8px;margin:15px 0;border-left:4px solid #2196f3}.toc{margin:20px 0;padding:20px;background:#f5f5f5;border-radius:8px}.toc a{color:#005EB8;text-decoration:none}.toc a:hover{text-decoration:underline}
</style>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
<style>
/* Глобальный `code { background:#f0f0f0 }` ломает hljs: светлый текст на светлом фоне */
.section .code-block > code.hljs,
.section .code-block > code {
  background: transparent !important;
  padding: 0 !important;
  border-radius: 0 !important;
}
/* Только PowerShell: все токены — синие, комментарии — отдельно (строка после # … снова видна) */
.section .code-block code.language-powershell.hljs,
.section .code-block code.language-powershell *:not(.hljs-comment) {
  color: #005EB8 !important;
}
.section .code-block code.language-powershell .hljs-comment {
  color: #5d6d7e !important;
}
@media print {
  .code-block {
    background: #eef2f7 !important;
    print-color-adjust: exact;
    -webkit-print-color-adjust: exact;
  }
  .section .code-block code.language-powershell.hljs,
  .section .code-block code.language-powershell * {
    color: #003D82 !important;
    background: transparent !important;
  }
  .section .code-block code.language-powershell .hljs-comment {
    color: #004d40 !important;
  }
}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/powershell.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/python.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/bash.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/yaml.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/dockerfile.min.js"></script>
</head>
<body>
<div class="container">
<div class="header">
<h1>🐳 Практическое занятие</h1>
<p><strong>Kubernetes внутри Docker Desktop (Windows)</strong></p>
<p>Локальный кластер • kubectl • Deployment • Service • port-forward</p>
</div>
<div class="student-info">
<div class="form-group"><label>ФИО:</label><input type="text" id="student-name"></div>
<div class="form-group"><label>Группа:</label><input type="text" id="group"></div>
<div class="form-group"><label>Дата:</label><input type="date" id="date"></div>
</div>

<div class="section" id="toc-top">
<h2>📑 Содержание</h2>
<div class="toc">
__TOC__
</div>
</div>

__BODY__

<div class="section" id="vyvody">
<h2>📊 Выводы (для отчёта)</h2>
<div class="form-group"><label>Что изучили:</label><textarea rows="3" id="ta0" style="width:100%;padding:12px;border:2px solid #e1e5e9;border-radius:8px"></textarea></div>
<div class="form-group"><label>Сложности:</label><textarea rows="3" id="ta1" style="width:100%;padding:12px;border:2px solid #e1e5e9;border-radius:8px"></textarea></div>
</div>

<button class="save-btn" type="button" onclick="window.print()">💾 Сохранить в PDF (печать)</button>
</div>

<script>
document.addEventListener('DOMContentLoaded',function(){
  document.querySelectorAll('.code-block code').forEach(function(el){try{hljs.highlightElement(el)}catch(e){}});
  ['student-name','group','date'].forEach(function(id){var el=document.getElementById(id);if(!el)return;el.value=localStorage.getItem(id)||'';el.addEventListener('input',function(){localStorage.setItem(id,el.value)})});
  var dateEl=document.getElementById('date');if(dateEl)dateEl.value=dateEl.value||new Date().toISOString().split('T')[0];
  document.querySelectorAll('input[type="checkbox"]').forEach(function(cb){if(localStorage.getItem(cb.id)==='true')cb.checked=true;cb.addEventListener('change',function(){localStorage.setItem(cb.id,cb.checked)})});
  ['ta0','ta1'].forEach(function(id){var el=document.getElementById(id);if(!el)return;el.value=localStorage.getItem(id)||'';el.addEventListener('input',function(){localStorage.setItem(id,el.value)})});
});
</script>
</body>
</html>
"""
    template = template.replace("__TOC__", toc_html).replace("__BODY__", body)

    OUT_PATH.write_text(template, encoding="utf-8")
    print("Wrote", OUT_PATH)


if __name__ == "__main__":
    main()
