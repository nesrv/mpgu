# -*- coding: utf-8 -*-
"""lect-design.md -> lect-design.html (Reveal.js, стиль как lect_deploy_django + тёмно-серый / зелёный)."""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MD_PATH = ROOT / "lect-design.md"
OUT_PATH = ROOT / "lect-design.html"

# Тёмно-серые фоны слайдов (чередование)
BGS = ("#252a30", "#2d343a", "#1e2328")

REVEAL = "https://cdn.jsdelivr.net/npm/reveal.js@4.6.1"
HIGHLIGHT = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css"


def md_inline_rich(s: str) -> str:
    ph: dict[str, str] = {}

    def link_sub(m: re.Match[str]) -> str:
        k = f"@@L{len(ph)}@@"
        ph[k] = (
            f'<a href="{html.escape(m.group(2), quote=True)}" target="_blank" rel="noopener">'
            f"{html.escape(m.group(1))}</a>"
        )
        return k

    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_sub, s)
    s = html.escape(s)
    for k, v in ph.items():
        s = s.replace(k, v)
    s = re.sub(r"\*\*(.+?)\*\*", lambda m: f"<strong>{m.group(1)}</strong>", s)
    s = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", s)
    return s


def lines_to_html(text: str) -> str:
    text = text.strip()
    if not text:
        return ""

    parts: list[str] = []
    lines = text.split("\n")
    i = 0

    in_ul = False
    in_ol = False
    table_rows: list[str] = []

    def close_ul() -> None:
        nonlocal in_ul
        if in_ul:
            parts.append("</ul>")
            in_ul = False

    def close_ol() -> None:
        nonlocal in_ol
        if in_ol:
            parts.append("</ol>")
            in_ol = False

    def flush_table() -> None:
        nonlocal table_rows
        if table_rows:
            parts.append("<table>" + "".join(table_rows) + "</table>")
            table_rows = []

    while i < len(lines):
        raw = lines[i]
        s = raw.strip()

        if s.startswith("```"):
            close_ul()
            close_ol()
            flush_table()
            lang = s[3:].strip() or "text"
            i += 1
            body: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                body.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            code = "\n".join(body)
            esc = html.escape(code)
            if lang == "mermaid":
                parts.append(f'<pre class="mermaid">{esc}</pre>')
            else:
                parts.append(f'<pre><code class="language-{html.escape(lang)}">{esc}</code></pre>')
            continue

        if not s:
            i += 1
            continue

        if s.startswith("|") and s.count("|") >= 2:
            close_ul()
            close_ol()
            if re.match(r"^\|\s*[-:| ]+\|\s*$", s):
                i += 1
                continue
            cells = [c.strip() for c in s.strip("|").split("|")]
            if not table_rows:
                table_rows.append(
                    "<tr>" + "".join(f"<th>{md_inline_rich(c)}</th>" for c in cells) + "</tr>"
                )
            else:
                table_rows.append(
                    "<tr>" + "".join(f"<td>{md_inline_rich(c)}</td>" for c in cells) + "</tr>"
                )
            i += 1
            continue

        flush_table()

        if s.startswith(("# ", "## ", "### ")):
            close_ul()
            close_ol()
            if s.startswith("### "):
                parts.append(f"<h3>{md_inline_rich(s[4:].strip())}</h3>")
            elif s.startswith("## "):
                parts.append(f"<h3>{md_inline_rich(s[3:].strip())}</h3>")
            else:
                parts.append(f"<h3>{md_inline_rich(s[2:].strip())}</h3>")
            i += 1
            continue

        if s.startswith("- ") or s.startswith("* "):
            close_ol()
            if not in_ul:
                parts.append("<ul>")
                in_ul = True
            parts.append(f"<li>{md_inline_rich(s[2:].strip())}</li>")
            i += 1
            continue

        if re.match(r"^\d+\.\s+", s):
            close_ul()
            if not in_ol:
                parts.append("<ol>")
                in_ol = True
            content = re.sub(r"^\d+\.\s+", "", s)
            parts.append(f"<li>{md_inline_rich(content)}</li>")
            i += 1
            continue

        close_ul()
        close_ol()
        parts.append(f"<p>{md_inline_rich(raw.rstrip())}</p>")
        i += 1

    close_ul()
    close_ol()
    flush_table()
    return "\n".join(parts)


def split_screen_more_lektor(block: str) -> tuple[str, str, str]:
    m_na = re.search(r"\*\*На экран[^*]*\*\*", block, re.MULTILINE)
    if not m_na:
        return "", "", ""
    rest = block[m_na.end() :]
    m_po = re.search(r"^\*\*Подробнее:\*\*", rest, re.MULTILINE)
    m_lek = re.search(r"^\*\*Лектору:\*\*", rest, re.MULTILINE)
    m_jump = re.search(r"^\*\*Переход", rest, re.MULTILINE)

    ends_scr: list[int] = []
    if m_po:
        ends_scr.append(m_po.start())
    if m_lek:
        ends_scr.append(m_lek.start())
    if ends_scr:
        screen_raw = rest[: min(ends_scr)].strip()
    else:
        screen_raw = rest.strip()
        md = re.search(r"\n---\s*\n", screen_raw)
        if md:
            screen_raw = screen_raw[: md.start()].strip()
        return screen_raw, "", ""

    def next_barrier(after: int) -> int:
        c = [len(rest)]
        if m_lek and m_lek.start() > after:
            c.append(m_lek.start())
        if m_jump and m_jump.start() > after:
            c.append(m_jump.start())
        md = re.search(r"\n---\s*\n", rest[after:])
        if md:
            c.append(after + md.start())
        return min(c)

    more_raw = ""
    if m_po:
        more_start = m_po.end()
        more_raw = rest[more_start : next_barrier(more_start)].strip()

    lek_raw = ""
    if m_lek:
        lek_start = m_lek.end()
        lek_raw = rest[lek_start : next_barrier(lek_start)].strip()

    return screen_raw, more_raw, lek_raw


def _load_md() -> str:
    return MD_PATH.read_text(encoding="utf-8")


def parse_title_and_map(md: str) -> tuple[str, str]:
    m_map = re.search(r"^## Карта лекции", md, re.MULTILINE)
    m_block_a = re.search(r"^## Блок A\.", md, re.MULTILINE)
    head = md[: m_map.start()] if m_map else ""
    map_section = (
        md[m_map.start() : m_block_a.start()].strip() if (m_map and m_block_a) else ""
    )

    title_line = "Лекция"
    for line in head.split("\n"):
        if line.startswith("# "):
            title_line = line[2:].strip()

    title_html = f'<h1 style="color:var(--acc-green)">{html.escape(title_line)}</h1>'
    if head.strip():
        intro = []
        for line in head.split("\n")[1:]:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            intro.append(f"<p>{md_inline_rich(s)}</p>")
        if intro:
            title_html += '<div class="title-intro">' + "".join(intro) + "</div>"

    title_html = (
        '<div class="title-box">'
        f"{title_html}"
        "</div>"
    )

    map_html = ""
    if map_section:
        body = re.sub(
            r"^## Карта лекции[^\n]*\n+", "", map_section, count=1, flags=re.MULTILINE
        )
        body = re.split(r"\n\*\*Замечание по структуре", body, maxsplit=1)[0].strip()
        body = re.split(r"\n\*\*Дубли", body, maxsplit=1)[0].strip()
        map_html = "<h2>Карта лекции</h2>" + lines_to_html(body)

    return title_html, map_html


def parse_slides(md: str) -> list[dict]:
    matches = list(re.finditer(r"### Слайд (\d+)\.\s*([^\n]+)", md))
    out: list[dict] = []
    for i, m in enumerate(matches):
        n_s, title = m.group(1), m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        block = md[start:end]
        if "## Ориентиры для самостоятельной работы" in block:
            block = block.split("## Ориентиры для самостоятельной работы")[0]
        if "## Памятка лектору" in block:
            block = block.split("## Памятка лектору")[0]
        screen_raw, more_raw, lek_raw = split_screen_more_lektor(block)
        out.append(
            {
                "num": int(n_s),
                "title": title,
                "screen": lines_to_html(screen_raw),
                "more": lines_to_html(more_raw) if more_raw else "",
                "lector": lines_to_html(lek_raw) if lek_raw else "",
                "bg": BGS[(int(n_s) + 1) % 3],
            }
        )
    return out


CUSTOM_CSS = """
:root {
  --bg-deep: #1a1d21;
  --bg-slide-1: #252a30;
  --bg-slide-2: #2d343a;
  --bg-slide-3: #1e2328;
  --acc-green: #4ade80;
  --acc-green-dim: #22c55e;
  --text-soft: #e2e8f0;
  --card-edge: rgba(74, 222, 128, 0.45);
}
html, body, .reveal-viewport, .reveal, .reveal .slides, .reveal .slides section,
.reveal .slide-background-content {
  overflow: hidden !important;
  scrollbar-width: none !important;
}
html::-webkit-scrollbar, body::-webkit-scrollbar, .reveal::-webkit-scrollbar,
.reveal .slides::-webkit-scrollbar, .reveal .slides section::-webkit-scrollbar {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
}
.reveal .slides {
  width: 80% !important;
  height: 90% !important;
  position: absolute !important;
  left: 50% !important;
  top: 0 !important;
  transform: translateX(calc(-50% + 5%)) scale(1.2) !important;
  transform-origin: top center !important;
}
.reveal .slides section {
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
  align-items: center !important;
  padding: 24px 32px !important;
  font-size: 0.95em !important;
  max-width: 100% !important;
  width: 100% !important;
  overflow: hidden !important;
  box-sizing: border-box !important;
  line-height: 1.5 !important;
  text-align: center !important;
  color: var(--text-soft) !important;
}
.reveal .slides section .slide-main,
.reveal .slides section .slide-main * {
  color: var(--text-soft);
}
.reveal h1 {
  font-size: 1.65em !important;
  margin-top: 0 !important;
  margin-bottom: 0.5em !important;
  color: var(--acc-green) !important;
  text-align: center !important;
  font-weight: 700 !important;
}
.reveal h2 {
  font-size: 1em !important;
  margin-top: 0 !important;
  margin-bottom: 0.5em !important;
  text-transform: none !important;
  text-align: center !important;
  padding-bottom: 0.4em !important;
  border-bottom: 2px solid var(--card-edge) !important;
  color: var(--acc-green) !important;
  width: 100% !important;
}
.reveal h3 {
  font-size: 1.05em !important;
  margin: 0.6em 0 0.3em !important;
  text-transform: none !important;
  color: #86efac !important;
  text-align: center !important;
}
.reveal .slides section p,
.reveal .slides section div.slide-main,
.reveal .slides section div.slide-card {
  max-width: 100% !important;
  min-width: 0 !important;
  overflow-wrap: break-word !important;
  word-break: break-word !important;
  box-sizing: border-box !important;
}
.reveal .slides section ul,
.reveal .slides section ol {
  text-align: left !important;
  margin: 0 auto !important;
}
.reveal .slides section li {
  overflow-wrap: break-word !important;
  margin-bottom: 0.4em !important;
  list-style: none !important;
  position: relative !important;
  padding-left: 0.5em !important;
}
.reveal .slides section ul li::before {
  content: "\\25B8" !important;
  position: absolute !important;
  left: -1em !important;
  color: var(--acc-green) !important;
  font-size: 0.85em !important;
}
.reveal .slides section ul { padding-left: 1.5em !important; }
.reveal p, .reveal ul, .reveal ol { font-size: 0.92em !important; }
.reveal pre {
  max-height: none !important;
  overflow: hidden !important;
  margin: 12px auto !important;
  max-width: 95% !important;
  border-radius: 10px !important;
  border: 1px solid var(--card-edge) !important;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35) !important;
  padding: 2px !important;
  text-align: left !important;
  background: rgba(0, 0, 0, 0.35) !important;
}
.reveal pre code {
  font-size: 0.68em !important;
  padding: 12px 16px !important;
  line-height: 1.42 !important;
  white-space: pre-wrap !important;
  word-break: break-word !important;
}
.reveal table {
  font-size: 0.76em !important;
  max-width: 95% !important;
  border-collapse: collapse !important;
  margin: 10px auto !important;
}
.reveal table th,
.reveal table td {
  border: 1px solid rgba(74, 222, 128, 0.35) !important;
  padding: 8px 12px !important;
}
.reveal table th {
  background: rgba(74, 222, 128, 0.12) !important;
  color: var(--acc-green) !important;
}
.reveal code:not(pre code) {
  color: #86efac !important;
  background: rgba(74, 222, 128, 0.12) !important;
  padding: 1px 6px !important;
  border-radius: 4px !important;
}
.slide-card {
  background: rgba(30, 35, 40, 0.75) !important;
  border-radius: 12px !important;
  padding: 18px 24px !important;
  border-left: 5px solid var(--acc-green-dim) !important;
  border-top: 1px solid var(--card-edge) !important;
  margin-top: 12px !important;
  max-width: 95% !important;
  text-align: left !important;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.35) !important;
}
.slide-card h3 { color: #86efac !important; text-align: left !important; }
.lect-note {
  margin-top: 14px !important;
  padding: 12px 16px !important;
  font-size: 0.82em !important;
  text-align: left !important;
  max-width: 95% !important;
  border-radius: 8px !important;
  background: rgba(34, 197, 94, 0.08) !important;
  border: 1px solid var(--card-edge) !important;
  color: #bbf7d0 !important;
}
.title-box {
  background: rgba(30, 35, 40, 0.92);
  padding: 36px 44px;
  border: 2px solid var(--card-edge);
  text-align: center;
  max-width: 92%;
  border-radius: 14px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.45);
}
.title-intro {
  margin-top: 1rem;
  text-align: left;
  font-size: 0.88em;
  max-width: 720px;
  margin-left: auto;
  margin-right: auto;
  color: #cbd5e1;
}
.title-intro p { margin: 0.5em 0; }
.reveal .mermaid {
  background: #f1f5f9;
  color: #111;
  border-radius: 8px;
  padding: 12px;
  margin: 10px auto;
  max-width: 100% !important;
  font-size: 11px !important;
  text-align: left !important;
  border: 1px solid var(--card-edge);
}
.reveal .controls { color: var(--acc-green) !important; }
.reveal .progress span { background: var(--acc-green-dim) !important; }
"""


def build_html(md: str) -> str:
    title_inner, map_html = parse_title_and_map(md)
    slides_list = parse_slides(md)

    parts: list[str] = []
    parts.append("<!DOCTYPE html>\n<html lang=\"ru\">\n<head>")
    parts.append('<meta charset="UTF-8">')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    parts.append("<title>Лекция: системное проектирование потоковых приложений</title>")
    parts.append(f'<link rel="stylesheet" href="{REVEAL}/dist/reveal.css">')
    parts.append(f'<link rel="stylesheet" href="{REVEAL}/dist/theme/black.css">')
    parts.append(f'<link rel="stylesheet" href="{HIGHLIGHT}">')
    parts.append(f"<style>\n{CUSTOM_CSS}\n</style>")
    parts.append(
        '<script type="module">'
        f'import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";'
        'mermaid.initialize({startOnLoad:false,theme:"neutral",securityLevel:"loose"});'
        "window.__mermaid=mermaid;"
        "</script>"
    )
    parts.append("</head>\n<body>\n<div class=\"reveal\"><div class=\"slides\">")

    parts.append(f'<section data-background-color="#1e2328">{title_inner}</section>')

    if map_html:
        parts.append(f'<section data-background-color="#252a30">{map_html}</section>')

    for s in slides_list:
        bg = s["bg"]
        num = s["num"]
        h2 = f"Слайд {num}. {html.escape(s['title'])}"
        parts.append(f'<section data-background-color="{bg}">')
        parts.append(f"<h2>{h2}</h2>")
        parts.append(
            f'<div class="slide-main">{s["screen"] or "<p><em>Нет текста «На экран»</em></p>"}</div>'
        )
        if s["more"]:
            parts.append(f'<div class="slide-card"><h3>Подробнее</h3>{s["more"]}</div>')
        if s["lector"]:
            parts.append(
                f'<div class="lect-note"><strong>Лектору:</strong> {s["lector"]}</div>'
            )
        parts.append("</section>")

    parts.append("</div></div>")

    parts.append(f'<script src="{REVEAL}/dist/reveal.js"></script>')
    parts.append(f'<script src="{REVEAL}/plugin/notes/notes.js"></script>')
    parts.append(f'<script src="{REVEAL}/plugin/markdown/markdown.js"></script>')
    parts.append(f'<script src="{REVEAL}/plugin/highlight/highlight.js"></script>')
    parts.append(
        r"""
<script>
  Reveal.initialize({
    hash: true,
    transition: 'slide',
    controls: true,
    progress: true,
    slideNumber: 'c/t',
    center: false,
    margin: 0.02,
    width: 1280,
    height: 720,
    plugins: [ RevealMarkdown, RevealHighlight, RevealNotes ]
  });
  function runMermaidForSlide() {
    var cur = Reveal.getCurrentSlide();
    if (!cur || !window.__mermaid) return;
    var nodes = cur.querySelectorAll('.mermaid:not([data-processed])');
    if (nodes.length) {
      try { window.__mermaid.run({ nodes: nodes }); } catch (e) { console.warn(e); }
    }
  }
  Reveal.on('slidechanged', runMermaidForSlide);
  Reveal.on('ready', runMermaidForSlide);
</script>
"""
    )
    parts.append("</body>\n</html>")
    return "\n".join(parts)


if __name__ == "__main__":
    md_text = _load_md()
    out = build_html(md_text)
    OUT_PATH.write_text(out, encoding="utf-8")
    print("Written", OUT_PATH, "sections:", out.count("<section "))
