# -*- coding: utf-8 -*-
"""
1) Перед каждым <!-- DOCKER COMPOSE: вставить </section>, если контент-слайд ещё не закрыт.
2) Убрать лишний </section> после compose (был «внешний» закрывающий при вложенности).
   — пара перед <!-- ══ …
   — пара перед следующим <section (слайд 5a → вторая часть слайда 5)
"""
import re
from pathlib import Path

HTML = Path(__file__).resolve().parent / "lect-arch-mq.html"
lines = HTML.read_text(encoding="utf-8").splitlines(keepends=True)

out = []
for line in lines:
    # Комментарии вида <!-- ══ DOCKER COMPOSE: … и <!-- ══ СЛАЙД 17: DOCKER COMPOSE
    if "DOCKER COMPOSE" in line and line.strip().startswith("<!--"):
        j = len(out) - 1
        while j >= 0 and out[j].strip() == "":
            j -= 1
        if j >= 0 and out[j].strip() != "</section>":
            out.append("</section>\n")
            out.append("\n")
    out.append(line)

text = "".join(out)

# Orphan после compose → следующий маркер слайда
while True:
    new = re.sub(
        r"</section>\r?\n\r?\n</section>\r?\n\r?\n(<!-- ══)",
        r"</section>\n\n\1",
        text,
        count=1,
    )
    if new == text:
        break
    text = new

# Orphan между compose 5a и второй половиной слайда 5
while True:
    new = re.sub(
        r"</section>\r?\n\r?\n</section>\r?\n\r?\n(<section\b)",
        r"</section>\n\n\1",
        text,
        count=1,
    )
    if new == text:
        break
    text = new

opens = text.count("<section")
closes = text.count("</section>")
if opens != closes:
    raise SystemExit(f"imbalance: open={opens} close={closes}")

HTML.write_text(text, encoding="utf-8")
print("OK: balanced", opens)
