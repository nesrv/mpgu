"""One-off: laba-mq.md -> laba-mq.html (методичка, стиль как laba_rq_celery.html)."""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MD_PATH = ROOT / "laba-mq.md"
OUT_PATH = ROOT / "laba-mq.html"

MD = MD_PATH.read_text(encoding="utf-8")
MD = MD.replace("§", "разд. ")

CSS = r"""*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Segoe UI',sans-serif;line-height:1.6;color:#333;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh}.container{max-width:1200px;margin:20px auto;padding:20px;background:white;border-radius:15px;box-shadow:0 10px 30px rgba(0,0,0,0.2)}.header{text-align:center;padding:30px;background:linear-gradient(135deg,#005EB8,#003D82);color:white;border-radius:10px;margin-bottom:30px}.header h1{font-size:2.5em;margin-bottom:10px}.student-info{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin-bottom:30px;padding:20px;background:#f8f9fa;border-radius:10px}.form-group{margin-bottom:20px}.form-group label{display:block;margin-bottom:5px;font-weight:bold;color:#003D82}.form-group input,.form-group textarea{width:100%;padding:12px;border:2px solid #e1e5e9;border-radius:8px;font-size:16px}.section{margin-bottom:40px;padding:25px;background:#fff;border-left:5px solid #005EB8;border-radius:0 10px 10px 0;box-shadow:0 2px 10px rgba(0,0,0,0.1)}.section>h2{color:#003D82;margin-bottom:20px;font-size:1.8em}.section>h3{color:#005EB8;margin:20px 0 10px;font-size:1.3em}.section>h4{color:#333;margin:15px 0 8px;font-size:1.1em}.code-block{background:#282c34;color:#e2e8f0;padding:20px;border-radius:8px;margin:15px 0;font-family:'Courier New',monospace;overflow-x:auto;white-space:pre-wrap;font-size:14px}ul.list-plain{list-style:none;padding-left:0}ul.list-plain li{padding:8px 0 8px 30px;position:relative}ul.list-plain li::before{content:'▸';position:absolute;left:0;color:#005EB8;font-size:18px}ol.pad{padding-left:20px}ol.pad li{padding:5px 0}table{width:100%;border-collapse:collapse;margin:15px 0}table th,table td{border:1px solid #ddd;padding:12px;text-align:left}table th{background:#005EB8;color:white}table tr:nth-child(even){background:#f8f9fa}.checkbox-item{margin:15px 0;padding:15px 20px;background:linear-gradient(135deg,#005EB8,#003D82);border-radius:10px;display:flex;align-items:center}.checkbox-item input[type="checkbox"]{appearance:none;width:26px;height:26px;border:3px solid white;border-radius:6px;margin-right:15px;cursor:pointer;background:transparent;flex-shrink:0}.checkbox-item input[type="checkbox"]:checked{background:#fff url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23005EB8"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>') center/18px no-repeat;border-color:#fff}.checkbox-item label{color:white;font-weight:500;cursor:pointer}.save-btn{background:linear-gradient(135deg,#005EB8,#003D82);color:white;border:none;padding:15px 30px;font-size:18px;border-radius:10px;cursor:pointer;display:block;margin:30px auto}code.k{background:#f0f0f0;padding:2px 6px;border-radius:4px;font-size:0.9em}.note{background:#e3f2fd;padding:15px;border-radius:8px;margin:15px 0;border-left:4px solid #2196f3}.warning{background:#fff8e1;padding:15px;border-radius:8px;margin:15px 0;border-left:4px solid #ff9800}.toc{margin:20px 0;padding:20px;background:#f5f5f5;border-radius:8px}.toc a{color:#005EB8;text-decoration:none}.toc a:hover{text-decoration:underline}.md-h1{font-size:1.85em;color:#003D82;margin:0 0 16px}"""


def md_inline(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", lambda m: f"<strong>{m.group(1)}</strong>", s)
    s = re.sub(r"`([^`]+)`", lambda m: f'<code class="k">{m.group(1)}</code>', s)
    return s


def anchor_for_h2(title: str) -> str:
    t = title.strip()
    tl = t.lower()
    if tl.startswith("часть 1"):
        return "part1"
    if tl.startswith("часть 2"):
        return "part2"
    m = re.match(r"^(\d+)\.", t)
    if m:
        return "s" + m.group(1)
    if t.startswith("2.11") or "Имитация нагрузки" in t:
        return "s211"
    return "h-" + re.sub(r"[^a-z0-9а-яё]+", "-", tl, flags=re.I).strip("-")[:64]


def hl_class(lang: str) -> str:
    lang = (lang or "plaintext").lower().strip()
    return {
        "env": "ini",
        "txt": "plaintext",
        "text": "plaintext",
        "dockerfile": "dockerfile",
        "powershell": "powershell",
        "ini": "ini",
        "yaml": "yaml",
        "yml": "yaml",
        "nginx": "nginx",
        "css": "css",
        "html": "xml",
        "xml": "xml",
        "bash": "bash",
        "sh": "bash",
        "python": "python",
    }.get(lang, "plaintext")


def render_markdown_block(text: str) -> str:
    text = text.strip("\n")
    if not text.strip():
        return ""
    lines = text.split("\n")
    parts: list[str] = []
    i = 0
    in_ul = False
    in_ol = False
    table_rows: list[str] = []

    def close_ul():
        nonlocal in_ul
        if in_ul:
            parts.append("</ul>")
            in_ul = False

    def close_ol():
        nonlocal in_ol
        if in_ol:
            parts.append("</ol>")
            in_ol = False

    def close_table():
        nonlocal table_rows
        if table_rows:
            parts.append("<table>" + "".join(table_rows) + "</table>")
            table_rows = []

    while i < len(lines):
        line = lines[i]
        s = line.strip()

        if s == "---":
            close_ul()
            close_ol()
            close_table()
            parts.append('<hr style="margin:24px 0;border:none;border-top:1px solid #ddd"/>')
            i += 1
            continue

        if s.startswith("|") and "|" in s[1:]:
            close_ul()
            close_ol()
            sep = re.match(r"^\|\s*[-:| ]+\|\s*$", s)
            if sep:
                i += 1
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            row = "".join(f"<td>{md_inline(c)}</td>" for c in cells)
            if not table_rows:
                table_rows.append("<tr>" + "".join(f"<th>{md_inline(c)}</th>" for c in cells) + "</tr>")
            else:
                table_rows.append("<tr>" + row + "</tr>")
            i += 1
            continue
        else:
            close_table()

        if s.startswith("# "):
            close_ul()
            close_ol()
            parts.append(f'<h1 class="md-h1">{md_inline(s[2:].strip())}</h1>')
            i += 1
            continue

        if s.startswith("## "):
            close_ul()
            close_ol()
            title = s[3:].strip()
            aid = anchor_for_h2(title)
            parts.append(f'<h2 id="{aid}">{md_inline(title)}</h2>')
            i += 1
            continue

        if s.startswith("### "):
            close_ul()
            close_ol()
            h3_title = s[4:].strip()
            h3_id = ""
            if h3_title.startswith("2.11"):
                h3_id = ' id="s211"'
            parts.append(f"<h3{h3_id}>{md_inline(h3_title)}</h3>")
            i += 1
            continue

        if s.startswith("#### "):
            close_ul()
            close_ol()
            parts.append(f"<h4>{md_inline(s[5:].strip())}</h4>")
            i += 1
            continue

        if s.startswith("- "):
            close_ol()
            if not in_ul:
                parts.append('<ul class="list-plain">')
                in_ul = True
            parts.append(f"<li>{md_inline(s[2:].strip())}</li>")
            i += 1
            continue

        if re.match(r"^\d+\.\s", s):
            close_ul()
            if not in_ol:
                parts.append('<ol class="pad">')
                in_ol = True
            content = re.sub(r"^\d+\.\s*", "", s)
            parts.append(f"<li>{md_inline(content)}</li>")
            i += 1
            continue

        if s == "":
            i += 1
            continue

        close_ul()
        close_ol()
        parts.append(f"<p>{md_inline(line.rstrip())}</p>")
        i += 1

    close_ul()
    close_ol()
    close_table()
    inner = "\n".join(parts)
    return f'<div class="section">\n{inner}\n</div>\n'


# Parse ```lang\n ... ``` (closing fence has no lang)
FENCE = re.compile(r"^```(\w*)\r?\n", re.MULTILINE)


def parse_md_fenced(src: str) -> list[tuple[str, str | None, str | None]]:
    """Sequence of ('text', None, text) or ('code', lang, body)."""
    out_p: list[tuple[str, str | None, str | None]] = []
    pos = 0
    while pos < len(src):
        m = FENCE.search(src, pos)
        if not m:
            tail = src[pos:]
            if tail.strip():
                out_p.append(("text", None, tail))
            break
        pre = src[pos : m.start()]
        if pre.strip():
            out_p.append(("text", None, pre))
        lang = m.group(1) or "plaintext"
        body_start = m.end()
        close = src.find("\n```", body_start)
        if close == -1:
            out_p.append(("code", lang, src[body_start:]))
            break
        body = src[body_start:close]
        out_p.append(("code", lang, body))
        pos = close + 4
        if pos < len(src) and src[pos] == "\n":
            pos += 1
        elif pos < len(src) and src[pos : pos + 2] == "\r\n":
            pos += 2
    return out_p


pieces = parse_md_fenced(MD)
out: list[str] = []

out.append("<!DOCTYPE html>\n<html lang=\"ru\">\n<head>\n")
out.append('<meta charset="UTF-8">\n')
out.append("<title>Лабораторная работа: чат FastAPI + HTMX + RabbitMQ</title>\n")
out.append(
    '<style media="print">body{font-family:Arial,sans-serif;font-size:12px}.container{box-shadow:none;background:white}.header{background:white!important;color:black!important}.save-btn{display:none!important}.section{page-break-inside:avoid}</style>\n'
)
out.append(f"<style>\n{CSS}\n</style>\n")
out.append(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">\n'
)
CDN = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0"
out.append(f'<script src="{CDN}/highlight.min.js"></script>\n')
for lang_js in (
    "python.min.js",
    "bash.min.js",
    "yaml.min.js",
    "ini.min.js",
    "xml.min.js",
    "nginx.min.js",
    "dockerfile.min.js",
    "css.min.js",
    "powershell.min.js",
):
    out.append(f'<script src="{CDN}/languages/{lang_js}"></script>\n')

out.append("</head>\n<body>\n<div class=\"container\">\n")

out.append(
    """<div class="header">
<h1>Лабораторная работа</h1>
<h2>Простой чат на FastAPI + HTMX WebSocket · RabbitMQ · PostgreSQL</h2>
<p>FastAPI &bull; HTMX ws &bull; Docker &bull; Nginx &bull; RabbitMQ &bull; SQLAlchemy async &bull; pytest &bull; GitHub Actions</p>
</div>
<div class="student-info">
<div class="form-group"><label>ФИО:</label><input type="text" id="student-name"></div>
<div class="form-group"><label>Группа:</label><input type="text" id="group"></div>
<div class="form-group"><label>Дата:</label><input type="date" id="date"></div>
</div>
"""
)

out.append(
    """<div class="section" id="toc-top">
<h2>Содержание</h2>
<div class="toc">
<ol class="pad">
<li><a href="#part1">Часть 1: простой чат (вариант 0)</a></li>
<li><a href="#s1">1. Подготовка окружения</a></li>
<li><a href="#s2">2. Деплой на VPS</a> — <a href="#s211">2.11 Нагрузка (room.html)</a></li>
<li><a href="#part2">Часть 2: БД и брокер</a></li>
<li><a href="#s3">3. Backend (db, mq, main, worker)</a></li>
<li><a href="#s4">4. Шаблоны и стили</a></li>
<li><a href="#s5">5. Проверка по шагам</a></li>
<li><a href="#s6">6. Health и тесты</a></li>
<li><a href="#s8">8. CI (GitHub Actions)</a></li>
<li><a href="#checklist">Чек-лист</a>, <a href="#repo-link-section">Репозиторий</a>, <a href="#vyvody">Выводы</a></li>
</ol>
</div>
</div>
"""
)

for kind, lang, content in pieces:
    if kind == "text":
        blk = render_markdown_block(content or "")
        if blk:
            out.append(blk)
    else:
        cls = hl_class(lang or "plaintext")
        escaped = html.escape((content or "").rstrip("\n"))
        out.append(f'<div class="code-block"><code class="language-{cls}">{escaped}</code></div>\n')

out.append(
    """<div class="section" id="checklist">
<h2>Чек-лист</h2>
<table>
<tr><th>Этап</th><th>Статус</th></tr>
<tr><td>Часть 1 — вариант 0 (Docker, WS, шаблоны)</td><td><input type="checkbox" id="c-p1"></td></tr>
<tr><td>Разд. 2 — деплой VPS, Nginx, HTTPS</td><td><input type="checkbox" id="c-s2"></td></tr>
<tr><td>Разд. 2.11 — нагрузка 100/1000</td><td><input type="checkbox" id="c-s211"></td></tr>
<tr><td>Часть 2 — PostgreSQL, RabbitMQ, worker</td><td><input type="checkbox" id="c-p2"></td></tr>
<tr><td>Разд. 5 — проверки 5.1–5.6</td><td><input type="checkbox" id="c-s5"></td></tr>
<tr><td>Разд. 6 — pytest, ws_check</td><td><input type="checkbox" id="c-s6"></td></tr>
<tr><td>Разд. 8 — CI workflow</td><td><input type="checkbox" id="c-s8"></td></tr>
</table>
</div>
"""
)

out.append(
    """<div class="section" id="repo-link-section">
<h2>Ссылка на репозиторий</h2>
<div class="form-group"><label for="repo-url">Ссылка на репозиторий Git с полным кодом варианта с PostgreSQL и RabbitMQ:</label><input type="url" id="repo-url" name="repo-url" placeholder="https://github.com/..." autocomplete="url"></div>
</div>
"""
)

out.append(
    """<div class="section" id="vyvody">
<h2>Выводы</h2>
<div class="form-group"><label>Что изучили:</label><textarea rows="3" id="ta0" style="width:100%;padding:12px;border:2px solid #e1e5e9;border-radius:8px"></textarea></div>
<div class="form-group"><label>Сложности:</label><textarea rows="3" id="ta1" style="width:100%;padding:12px;border:2px solid #e1e5e9;border-radius:8px"></textarea></div>
</div>
"""
)

out.append('<button class="save-btn" onclick="window.print()">Сохранить в PDF</button>\n')
out.append("</div>\n")
out.append(
    r"""<script>
document.addEventListener('DOMContentLoaded',function(){
  document.querySelectorAll('.code-block code').forEach(function(el){try{hljs.highlightElement(el)}catch(e){}});
  var KEY='laba_mq_';
  ['student-name','group','date','repo-url'].forEach(function(id){
    var el=document.getElementById(id);if(!el)return;
    el.value=localStorage.getItem(KEY+id)||'';
    el.addEventListener('input',function(){localStorage.setItem(KEY+id,el.value)});
  });
  var dateEl=document.getElementById('date');
  if(dateEl&&!dateEl.value)dateEl.value=new Date().toISOString().split('T')[0];
  document.querySelectorAll('input[type="checkbox"]').forEach(function(cb){
    if(!cb.id)return;
    if(localStorage.getItem(KEY+cb.id)==='true')cb.checked=true;
    cb.addEventListener('change',function(){localStorage.setItem(KEY+cb.id,cb.checked)});
  });
  document.querySelectorAll('textarea').forEach(function(el){
    if(!el.id)return;
    el.value=localStorage.getItem(KEY+el.id)||'';
    el.addEventListener('input',function(){localStorage.setItem(KEY+el.id,el.value)});
  });
});
</script>
</body>
</html>
"""
)

OUT_PATH.write_text("".join(out), encoding="utf-8")
print("Wrote", OUT_PATH, "chars", len("".join(out)))
