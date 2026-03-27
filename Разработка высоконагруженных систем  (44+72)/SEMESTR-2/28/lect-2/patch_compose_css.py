# -*- coding: utf-8 -*-
import pathlib
import re

p = pathlib.Path(__file__).parent / "lect-arch-mq.html"
html = p.read_text(encoding="utf-8")

CSS = """
    /* Docker Compose: видимость и прокрутка (overflow:hidden на section раньше всё резал) */
    .reveal .slides section.compose-slide {
      overflow-y: auto !important;
      overflow-x: hidden !important;
      justify-content: flex-start !important;
      align-items: stretch !important;
      padding-top: 10px !important;
      scrollbar-width: thin !important;
    }
    .reveal .slides section.compose-slide::-webkit-scrollbar {
      display: block !important;
      width: 8px !important;
      height: 8px !important;
    }
    .reveal .slides section.compose-slide pre {
      overflow-y: auto !important;
      overflow-x: auto !important;
      max-height: 58vh !important;
      flex: 0 1 auto !important;
    }
    .reveal .slides section.compose-slide pre code {
      white-space: pre !important;
      word-break: normal !important;
      font-size: 0.52em !important;
      line-height: 1.35 !important;
      color: #e8e8e8 !important;
      display: block !important;
    }
"""

anchor = ".reveal code { color:#90EE90!important }"
if anchor not in html:
    raise SystemExit("anchor not found")
if "Docker Compose: видимость" not in html:
    html = html.replace(anchor, anchor + CSS)

# Класс только если ещё не добавлен (следом идёт <section data-background-color без compose-slide)
html = re.sub(
    r"(<!-- ══ DOCKER COMPOSE:[^\n]+-->\s*)\n<section data-background-color=",
    r'\1\n<section class="compose-slide" data-background-color=',
    html,
)
html = re.sub(
    r"(<!-- ══ СЛАЙД 17: DOCKER COMPOSE ══ -->\s*)\n<section data-background-color=",
    r'\1\n<section class="compose-slide" data-background-color=',
    html,
)

# Подсветка: yaml часто отсутствует в старом highlight — используем ini (есть в типичных бандлах)
html = html.replace('class="language-yaml"', 'class="language-ini"')

p.write_text(html, encoding="utf-8")
