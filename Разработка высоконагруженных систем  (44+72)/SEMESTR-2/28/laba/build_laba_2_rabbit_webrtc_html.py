# -*- coding: utf-8 -*-
"""laba-2-Rabbit-WebRTC.md -> laba-2-Rabbit-WebRTC.html (методичка, стиль как laba-mq.html)."""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MD_PATH = ROOT / "laba-2-Rabbit-WebRTC.md"
OUT_PATH = ROOT / "laba-2-Rabbit-WebRTC.html"

MD = MD_PATH.read_text(encoding="utf-8")
MD = MD.replace("§", "разд. ")

CSS = r"""*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Segoe UI',sans-serif;line-height:1.6;color:#333;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh}.container{max-width:1200px;margin:20px auto;padding:20px;background:white;border-radius:15px;box-shadow:0 10px 30px rgba(0,0,0,0.2)}.header{text-align:center;padding:30px;background:linear-gradient(135deg,#005EB8,#003D82);color:white;border-radius:10px;margin-bottom:30px}.header h1{font-size:2.5em;margin-bottom:10px}.student-info{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin-bottom:30px;padding:20px;background:#f8f9fa;border-radius:10px}.form-group{margin-bottom:20px}.form-group label{display:block;margin-bottom:5px;font-weight:bold;color:#003D82}.form-group input,.form-group textarea{width:100%;padding:12px;border:2px solid #e1e5e9;border-radius:8px;font-size:16px}.section{margin-bottom:40px;padding:25px;background:#fff;border-left:5px solid #005EB8;border-radius:0 10px 10px 0;box-shadow:0 2px 10px rgba(0,0,0,0.1)}.section>h2{color:#003D82;margin-bottom:20px;font-size:1.8em}.section>h3{color:#005EB8;margin:20px 0 10px;font-size:1.3em}.section>h4{color:#333;margin:15px 0 8px;font-size:1.1em}.section blockquote{margin:12px 0;padding:12px 16px;background:#f0f7fc;border-left:4px solid #005EB8;border-radius:0 8px 8px 0;color:#333}.section blockquote p{margin:6px 0}.code-block{background:#282c34;color:#e2e8f0;padding:20px;border-radius:8px;margin:15px 0;font-family:'Courier New',monospace;overflow-x:auto;white-space:pre-wrap;font-size:14px}ul.list-plain{list-style:none;padding-left:0}ul.list-plain li{padding:8px 0 8px 30px;position:relative}ul.list-plain li::before{content:'▸';position:absolute;left:0;color:#005EB8;font-size:18px}ol.pad{padding-left:20px}ol.pad li{padding:5px 0}table{width:100%;border-collapse:collapse;margin:15px 0}table th,table td{border:1px solid #ddd;padding:12px;text-align:left}table th{background:#005EB8;color:white}table tr:nth-child(even){background:#f8f9fa}.checkbox-item{margin:15px 0;padding:15px 20px;background:linear-gradient(135deg,#005EB8,#003D82);border-radius:10px;display:flex;align-items:center}.checkbox-item input[type="checkbox"]{appearance:none;width:26px;height:26px;border:3px solid white;border-radius:6px;margin-right:15px;cursor:pointer;background:transparent;flex-shrink:0}.checkbox-item input[type="checkbox"]:checked{background:#fff url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23005EB8"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>') center/18px no-repeat;border-color:#fff}.checkbox-item label{color:white;font-weight:500;cursor:pointer}.save-btn{background:linear-gradient(135deg,#005EB8,#003D82);color:white;border:none;padding:15px 30px;font-size:18px;border-radius:10px;cursor:pointer;display:block;margin:30px auto}code.k{background:#f0f0f0;padding:2px 6px;border-radius:4px;font-size:0.9em}.note{background:#e3f2fd;padding:15px;border-radius:8px;margin:15px 0;border-left:4px solid #2196f3}.warning{background:#fff8e1;padding:15px;border-radius:8px;margin:15px 0;border-left:4px solid #ff9800}.toc{margin:20px 0;padding:20px;background:#f5f5f5;border-radius:8px}.toc a{color:#005EB8;text-decoration:none}.toc a:hover{text-decoration:underline}.md-h1{font-size:1.85em;color:#003D82;margin:0 0 16px}"""


def gfm_heading_anchor(title: str) -> str:
    """Якорь в духе GFM: латиница/кириллица/цифры, фрагменты через дефис."""
    t = title.strip().lower()
    # пути в `...`: убираем / и . чтобы совпадало с оглавлением (app/db.py → appdbpy)
    t = re.sub(r"`([^`]*)`", lambda m: re.sub(r"[/\\.]", "", m.group(1)), t)
    parts = re.split(r"[^a-zа-яё0-9]+", t)
    parts = [p for p in parts if p]
    return "-".join(parts)


def md_inline(s: str) -> str:
    ph: dict[str, str] = {}

    def link_sub(m: re.Match[str]) -> str:
        k = f"@@L{len(ph)}@@"
        ph[k] = (
            f'<a href="{html.escape(m.group(2), quote=True)}">'
            f"{html.escape(m.group(1))}</a>"
        )
        return k

    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_sub, s)
    s = html.escape(s)
    for k, v in ph.items():
        s = s.replace(k, v)
    s = re.sub(r"\*\*(.+?)\*\*", lambda m: f"<strong>{m.group(1)}</strong>", s)
    s = re.sub(r"`([^`]+)`", lambda m: f'<code class="k">{m.group(1)}</code>', s)
    return s


def is_markdown_table_separator_row(line: str) -> bool:
    t = line.strip()
    if not (t.startswith("|") and t.count("|") >= 2):
        return False
    cells = [c.strip() for c in t.strip("|").split("|")]
    if not cells:
        return False
    for c in cells:
        if not re.fullmatch(r":?-+:?", c):
            return False
        core = c.replace(":", "")
        if len(core) < 3 or set(core) != {"-"}:
            return False
    return True


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
        "javascript": "javascript",
        "js": "javascript",
        "json": "json",
        "mermaid": "plaintext",
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
            if is_markdown_table_separator_row(s):
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

        if s.startswith("> "):
            close_ul()
            close_ol()
            bq_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                raw = lines[i].strip()
                bq_lines.append(raw[1:].lstrip() if raw.startswith(">") else raw)
                i += 1
            paras: list[str] = []
            cur: list[str] = []
            for bl in bq_lines:
                if not bl.strip():
                    if cur:
                        paras.append(" ".join(cur))
                        cur = []
                else:
                    cur.append(bl.strip())
            if cur:
                paras.append(" ".join(cur))
            inner = "".join(f"<p>{md_inline(p)}</p>" for p in paras)
            parts.append(f"<blockquote>{inner}</blockquote>")
            continue

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
            aid = gfm_heading_anchor(title)
            parts.append(f'<h2 id="{html.escape(aid, quote=True)}">{md_inline(title)}</h2>')
            i += 1
            continue

        if s.startswith("### "):
            close_ul()
            close_ol()
            h3_title = s[4:].strip()
            parts.append(f"<h3>{md_inline(h3_title)}</h3>")
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


FENCE = re.compile(r"^```(\w*)\r?\n", re.MULTILINE)


def parse_md_fenced(src: str) -> list[tuple[str, str | None, str | None]]:
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
out.append("<title>Методичка: реакции RabbitMQ и «прочитано» · WebRTC</title>\n")
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
    "javascript.min.js",
    "json.min.js",
):
    out.append(f'<script src="{CDN}/languages/{lang_js}"></script>\n')

out.append("</head>\n<body>\n<div class=\"container\">\n")

out.append(
    """<div class="header">
<h1>Методичка (часть 2)</h1>
<h2>Реакции через RabbitMQ и «прочитано» через HTTP · опционально WebRTC 1:1</h2>
<p>FastAPI &bull; HTMX ws &bull; RabbitMQ &bull; PostgreSQL &bull; WebSocket &bull; WebRTC</p>
</div>
<div class="student-info">
<div class="form-group"><label>ФИО:</label><input type="text" id="student-name"></div>
<div class="form-group"><label>Группа:</label><input type="text" id="group"></div>
<div class="form-group"><label>Дата:</label><input type="date" id="date"></div>
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
<tr><td>разд. 0 — базовый проект из части 1</td><td><input type="checkbox" id="c-s0"></td></tr>
<tr><td>разд. 1–2 — БД и очереди реакций</td><td><input type="checkbox" id="c-s12"></td></tr>
<tr><td>разд. 3–4 — worker реакций и точка входа</td><td><input type="checkbox" id="c-s34"></td></tr>
<tr><td>разд. 5–7 — main, room.html, стили</td><td><input type="checkbox" id="c-s57"></td></tr>
<tr><td>разд. 8–9 — .env и проверка</td><td><input type="checkbox" id="c-s89"></td></tr>
<tr><td>разд. 10 — практикум RabbitMQ</td><td><input type="checkbox" id="c-s10"></td></tr>
<tr><td>разд. 11 — WebRTC 1:1 (по желанию)</td><td><input type="checkbox" id="c-s11"></td></tr>
</table>
</div>
"""
)

out.append(
    """<div class="section" id="repo-link-section">
<h2>Ссылка на репозиторий</h2>
<div class="form-group"><label for="repo-url">Ссылка на репозиторий Git с полным кодом:</label><input type="text" id="repo-url" name="repo-url" placeholder="https://github.com/... или git@github.com:..."></div>
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
  var KEY='laba_2_rabbit_webrtc_';
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
