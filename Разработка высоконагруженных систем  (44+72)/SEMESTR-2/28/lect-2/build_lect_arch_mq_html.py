# -*- coding: utf-8 -*-
"""lect-arch-mq.md -> lect-arch-mq.html (Reveal.js, стили в духе laba-mq.html: #005EB8 / #003D82)."""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MD_PATH = ROOT / "lect-arch-mq.md"
OUT_PATH = ROOT / "lect-arch-mq.html"

REVEAL = "https://cdn.jsdelivr.net/npm/reveal.js@4.6.1"
HIGHLIGHT = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css"

BGS = ("#f0f4f8", "#ffffff", "#e8eef5")


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


def lines_to_html(text: str) -> str:
    text = text.strip()
    if not text:
        return ""
    lines = text.split("\n")
    parts: list[str] = []
    i = 0
    in_ul = in_ol = False
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
                parts.append(
                    f'<pre><code class="language-{html.escape(lang)}">{esc}</code></pre>'
                )
            continue

        if not s:
            i += 1
            continue

        if s.startswith("|") and s.count("|") >= 2:
            close_ul()
            close_ol()
            if is_markdown_table_separator_row(s):
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


def parse_fenced_blocks(block: str) -> list[tuple[int, int, str, str]]:
    """Список (start, end, lang, body) для каждого ```fence ```."""
    out: list[tuple[int, int, str, str]] = []
    i = 0
    n = len(block)
    while i < n:
        if block[i] == "`" and block[i : i + 3] == "```":
            j = i + 3
            while j < n and block[j] not in "\n\r":
                j += 1
            lang = block[i + 3 : j].strip()
            if j < n and block[j] == "\n":
                j += 1
            start_body = j
            close = block.find("```", start_body)
            if close == -1:
                break
            body = block[start_body:close]
            out.append((i, close + 3, lang, body))
            i = close + 3
            while i < n and block[i] in "\n\r":
                i += 1
        else:
            i += 1
    return out


def split_slide_block(block: str, slide_num: int, slide_title: str) -> list[tuple[str, str]]:
    """
    Возвращает список (подзаголовок для h2, markdown-фрагмент).
    Разносим mermaid и yaml (Docker Compose) на отдельные слайды при наличии.
    """
    block = block.lstrip("\n")
    fenced = parse_fenced_blocks(block)
    if not fenced:
        return [(slide_title, block)]

    has_mermaid_or_yaml = any(
        fb[2].lower() in ("mermaid", "yaml", "yml") for fb in fenced
    )
    if not has_mermaid_or_yaml:
        return [(slide_title, block)]

    pieces: list[tuple[str, str]] = []
    cursor = 0
    mermaid_idx = 0
    yaml_idx = 0

    for start, end, lang, body in fenced:
        lang_l = lang.lower()
        text_before = block[cursor:start].rstrip()
        if text_before.strip():
            pieces.append((slide_title, text_before))
        if lang_l == "mermaid":
            mermaid_idx += 1
            sub = "схема" if mermaid_idx == 1 else f"схема ({mermaid_idx})"
            pieces.append((f"{slide_title} — {sub}", f"```mermaid\n{body}```"))
        elif lang_l in ("yaml", "yml"):
            yaml_idx += 1
            label = "Docker Compose" if yaml_idx == 1 else f"Docker Compose ({yaml_idx})"
            pieces.append((f"{slide_title} — {label}", f"```yaml\n{body}```"))
        else:
            pieces.append((f"{slide_title} — код ({lang})", f"```{lang}\n{body}```"))
        cursor = end

    tail = block[cursor:].strip()
    if tail:
        pieces.append((f"{slide_title} — детали", tail))

    merged: list[tuple[str, str]] = []
    for sub, frag in pieces:
        if frag.strip():
            merged.append((sub, frag))
    return merged if merged else [(slide_title, block)]


def parse_document(md: str) -> tuple[str, str, list[tuple[str, str, str]], str]:
    """title_line, intro_html, slides [(h2, bg, inner)], appendix_html."""
    m_first_slide = re.search(r"^## Слайд \d+\.", md, re.MULTILINE)
    head = md[: m_first_slide.start()] if m_first_slide else md

    title_line = "Лекция"
    for line in head.split("\n"):
        if line.startswith("# "):
            title_line = line[2:].strip()
            break

    intro_md = head
    for line in head.split("\n"):
        if line.startswith("# "):
            intro_md = "\n".join(
                ln for ln in head.split("\n")[1:] if ln.strip() and not ln.startswith("# ")
            )
            break
    intro_html = lines_to_html(intro_md) if intro_md.strip() else ""

    rest = md[m_first_slide.start() :] if m_first_slide else ""
    matches = list(re.finditer(r"^## Слайд (\d+)\.\s*([^\n]+)$", rest, re.MULTILINE))

    slides: list[tuple[str, str, str]] = []
    slide_i = 0
    for i, m in enumerate(matches):
        num, stitle = m.group(1), m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(rest)
        raw_block = rest[start:end]
        if "## Приложение" in raw_block:
            raw_block = raw_block.split("## Приложение")[0]
        if raw_block.strip().startswith("---"):
            raw_block = re.sub(r"^\s*---\s*\n", "", raw_block, count=1)

        chunks = split_slide_block(raw_block, int(num), stitle)
        for sub_title, frag in chunks:
            bg = BGS[slide_i % len(BGS)]
            slide_i += 1
            h2 = f"Слайд {num}. {html.escape(sub_title)}"
            inner = f'<div class="slide-card"><h2 class="slide-h2">{h2}</h2>{lines_to_html(frag)}</div>'
            slides.append((h2, bg, inner))

    appendix = ""
    m_app = re.search(r"^## Приложение[\s\S]*", md, re.MULTILINE)
    if m_app:
        appendix = lines_to_html(m_app.group(0))

    return title_line, intro_html, slides, appendix


CUSTOM_CSS = """
:root {
  --mq-blue: #005EB8;
  --mq-blue-dark: #003D82;
  --mq-text: #1a1a2e;
  --mq-border: rgba(0, 94, 184, 0.35);
}
html, body, .reveal-viewport, .reveal, .reveal .slides, .reveal .slides section,
.reveal .slide-background-content {
  overflow: hidden !important;
}
.reveal .slides {
  width: 90% !important;
  height: 92% !important;
  left: 50% !important;
  transform: translateX(-50%) !important;
}
.reveal .slides section {
  display: flex !important;
  flex-direction: column !important;
  justify-content: flex-start !important;
  align-items: center !important;
  padding: 20px 28px !important;
  font-size: 0.88em !important;
  max-width: 100% !important;
  overflow: auto !important;
  box-sizing: border-box !important;
  line-height: 1.45 !important;
  text-align: left !important;
  color: var(--mq-text) !important;
}
.title-slide {
  text-align: center !important;
  justify-content: center !important;
  background: linear-gradient(135deg, var(--mq-blue), var(--mq-blue-dark)) !important;
  color: white !important;
  border-radius: 12px;
  padding: 40px !important;
  max-width: 92% !important;
  margin: 0 auto !important;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}
.title-slide h1 {
  color: white !important;
  font-size: 1.5em !important;
  border: none !important;
  margin-bottom: 0.6em !important;
}
.title-slide p, .title-slide li { color: rgba(255,255,255,0.95) !important; font-size: 0.95em !important; }
.slide-card {
  width: 100%;
  max-width: 1100px;
  background: #fff;
  border-left: 5px solid var(--mq-blue);
  border-radius: 0 10px 10px 0;
  padding: 18px 22px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}
.slide-h2 {
  color: var(--mq-blue-dark) !important;
  font-size: 1.05em !important;
  margin: 0 0 14px 0 !important;
  padding-bottom: 10px !important;
  border-bottom: 2px solid var(--mq-border) !important;
  text-transform: none !important;
}
.reveal h3 { color: var(--mq-blue) !important; font-size: 1em !important; margin: 12px 0 8px !important; }
.reveal p, .reveal ul, .reveal ol { font-size: 0.92em !important; margin: 0.35em 0 !important; }
.reveal ul, .reveal ol { padding-left: 1.4em !important; }
.reveal pre {
  max-height: 62vh !important;
  overflow: auto !important;
  margin: 10px 0 !important;
  border-radius: 8px !important;
  border: 1px solid #ddd !important;
  text-align: left !important;
  background: #282c34 !important;
}
.reveal pre code {
  font-size: 0.62em !important;
  line-height: 1.35 !important;
  white-space: pre !important;
  display: block !important;
  padding: 12px 14px !important;
}
.reveal table {
  font-size: 0.78em !important;
  width: 100% !important;
  border-collapse: collapse !important;
  margin: 10px 0 !important;
}
.reveal table th, .reveal table td {
  border: 1px solid #ddd !important;
  padding: 8px 10px !important;
}
.reveal table th {
  background: var(--mq-blue) !important;
  color: white !important;
}
.reveal table tr:nth-child(even) { background: #f8f9fa !important; }
.reveal code:not(pre code) {
  background: #f0f0f0 !important;
  padding: 1px 5px !important;
  border-radius: 4px !important;
  font-size: 0.9em !important;
}
.reveal .mermaid {
  background: #f8fafc;
  border: 1px solid var(--mq-border);
  border-radius: 8px;
  padding: 10px;
  margin: 10px 0;
  max-height: 58vh;
  overflow: auto;
  font-size: 12px;
}
.reveal .controls { color: var(--mq-blue) !important; }
.reveal .progress span { background: var(--mq-blue) !important; }
"""


def build_html(md: str) -> str:
    title_line, intro_html, slides, appendix = parse_document(md)

    parts: list[str] = []
    parts.append("<!DOCTYPE html>\n<html lang=\"ru\">\n<head>")
    parts.append('<meta charset="UTF-8">')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    parts.append(f"<title>{html.escape(title_line)}</title>")
    parts.append(f'<link rel="stylesheet" href="{REVEAL}/dist/reveal.css">')
    parts.append(f'<link rel="stylesheet" href="{REVEAL}/dist/theme/white.css">')
    parts.append(f'<link rel="stylesheet" href="{HIGHLIGHT}">')
    parts.append(f"<style>\n{CUSTOM_CSS}\n</style>")
    parts.append(
        '<script type="module">'
        'import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";'
        'mermaid.initialize({startOnLoad:false,theme:"neutral",securityLevel:"loose"});'
        "window.__mermaid=mermaid;"
        "</script>"
    )
    parts.append("</head>\n<body>\n<div class=\"reveal\"><div class=\"slides\">")

    parts.append(
        f'<section data-background-color="#667eea">'
        f'<div class="title-slide"><h1>{html.escape(title_line)}</h1>'
        f"{intro_html or '<p>Архитектура потоковых приложений · RabbitMQ</p>'}</div></section>"
    )

    for _h2, bg, inner in slides:
        parts.append(f'<section data-background-color="{bg}">{inner}</section>')

    if appendix.strip():
        parts.append(
            f'<section data-background-color="#f0f4f8">'
            f'<div class="slide-card"><h2 class="slide-h2">Приложение</h2>{appendix}</div></section>'
        )

    parts.append("</div></div>")
    parts.append(f'<script src="{REVEAL}/dist/reveal.js"></script>')
    parts.append(f'<script src="{REVEAL}/plugin/highlight/highlight.js"></script>')
    parts.append(f'<script src="{REVEAL}/plugin/notes/notes.js"></script>')
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
    margin: 0.04,
    width: 1280,
    height: 720,
    plugins: [ RevealHighlight, RevealNotes ]
  });
  if (typeof hljs !== 'undefined') { hljs.highlightAll(); }
  function runMermaidForSlide() {
    var cur = Reveal.getCurrentSlide();
    if (!cur || !window.__mermaid) return;
    var nodes = cur.querySelectorAll('.mermaid:not([data-processed])');
    if (nodes.length) {
      try { window.__mermaid.run({ nodes: nodes }); } catch (e) { console.warn(e); }
    }
  }
  Reveal.on('slidechanged', function() {
    if (typeof hljs !== 'undefined') { hljs.highlightAll(); }
    runMermaidForSlide();
  });
  Reveal.on('ready', function() {
    if (typeof hljs !== 'undefined') { hljs.highlightAll(); }
    runMermaidForSlide();
  });
</script>
"""
    )
    parts.append("</body>\n</html>")
    return "\n".join(parts)


def main() -> None:
    md_text = MD_PATH.read_text(encoding="utf-8")
    out = build_html(md_text)
    OUT_PATH.write_text(out, encoding="utf-8")
    print("Written", OUT_PATH, "sections:", out.count("<section "))


if __name__ == "__main__":
    main()
