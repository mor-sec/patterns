"""Build a single-page HTML version of the AI pattern catalogue from the repo's markdown.

    python3 tools/build_catalogue_page.py <output.html>

Sources: ai-patterns/*.md, ai-patterns/patterns/*.md, checklists/ai-workloads.md and
templates/ai-pattern-scoring-sheet.md. Finder data (FINDER below) mirrors the pattern cards;
update it when ratings change.
"""
import glob
import html
import json
import os
import re
import sys

import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AP = os.path.join(ROOT, "ai-patterns")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def slug(text):
    t = re.sub(r"<[^>]+>", "", text)
    t = html.unescape(t).strip().lower()
    t = re.sub(r"[^\w\- ]", "", t)
    return t.replace(" ", "-")


def section(md, start, stop=None):
    """Return markdown from heading line `start` up to (not incl.) heading `stop`."""
    i = md.index(start)
    j = md.index(stop, i + len(start)) if stop else len(md)
    return md[i:j]


def convert(md, shift, prefix="", drop_h1=True):
    md = re.sub(r"\s*style \w+ fill:#[0-9a-fA-F]+\n", "\n", md)  # drop light-only mermaid fills
    blocks = []

    def keep_mermaid(m):
        blocks.append(m.group(1))
        return f"\n\nMERMAIDBLOCK{len(blocks) - 1}\n\n"

    md = re.sub(r"```mermaid\n(.*?)```", keep_mermaid, md, flags=re.S)
    md = re.sub(r"^- \[ \] ", "- <span class=\"box\" aria-hidden=\"true\"></span>", md, flags=re.M)
    if drop_h1:
        md = re.sub(r"\A\s*# [^\n]*\n", "", md)
    out = markdown.markdown(md, extensions=["tables", "fenced_code", "sane_lists"])

    def head(m):
        lvl = min(int(m.group(1)) + shift, 6)
        inner = m.group(2)
        return f'<h{lvl} id="{prefix}{slug(inner)}">{inner}</h{lvl}>'

    out = re.sub(r"<h(\d)>(.*?)</h\1>", head, out, flags=re.S)
    out = re.sub(r"<p>MERMAIDBLOCK(\d+)</p>",
                 lambda m: f'<div class="diagram"><pre class="mermaid">{html.escape(blocks[int(m.group(1))])}</pre></div>', out)
    out = re.sub(r"<table>", '<div class="table-wrap"><table>', out)
    out = re.sub(r"</table>", "</table></div>", out)
    out = re.sub(r'<a href="([^"]+)">(.*?)</a>', relink, out, flags=re.S)
    return out


REPO_ONLY = {
    "ai-pattern-scoring.xlsx": "Excel workbook",
    "ai-pattern-scoring-example.xlsx": "worked-example workbook",
    "ai-pattern-scoring.csv": "CSV",
    "ai-pattern-selection.md": "selection record template",
}


def relink(m):
    href, text = m.group(1), m.group(2)
    if href.startswith("http"):
        return f'<a href="{href}">{text}</a>'
    path, _, anchor = href.partition("#")
    base = os.path.basename(path)
    pm = re.match(r"(P\d\d)-", base)
    if pm:
        return f'<a href="#{anchor or pm.group(1).lower()}">{text}</a>'
    if base in ("00-decision-framework.md", "01-shared-foundations.md"):
        target = anchor or ("framework" if base.startswith("00") else "foundations")
        return f'<a href="#{target}">{text}</a>'
    if base == "ai-workloads.md":
        return f'<a href="#checklist">{text}</a>'
    if base == "ai-pattern-scoring-sheet.md":
        return f'<a href="#scoring">{text}</a>'
    if anchor == "suitability-profile-at-a-glance":
        return f'<a href="#glance">{text}</a>'
    if base == "README.md" and ("ai-patterns" in path or path == "README.md"):
        return f'<a href="#{anchor or "top"}">{text}</a>'
    # Files that live only in the SAR repository: keep the words, drop the link.
    return f'<span class="repo-ref" title="In the SAR repository: {html.escape(path)}">{text}</span>'


# ---------------------------------------------------------------- content
readme = read(os.path.join(AP, "README.md"))
framework = read(os.path.join(AP, "00-decision-framework.md"))
foundations = read(os.path.join(AP, "01-shared-foundations.md"))
checklist = read(os.path.join(ROOT, "checklists", "ai-workloads.md"))
scoring = read(os.path.join(ROOT, "templates", "ai-pattern-scoring-sheet.md"))

choosing_md = section(readme, "## Choosing a pattern", "## Maintaining this catalogue")
choosing_md = re.sub(r"^## ", "### ", choosing_md.split("\n", 1)[1], flags=re.M)
glance_md = section(readme, "### Suitability profile at a glance", "## Choosing a pattern").split("\n", 1)[1]

scoring_md = (section(scoring, "### Criteria, anchors and weight profiles", "### Scores")
              + section(scoring, "### Interpretation rules", "---")
              + section(scoring, "## Worked example (illustrative)").replace("## Worked example", "### Worked example", 1))

patterns = []
for path in sorted(glob.glob(os.path.join(AP, "patterns", "P*.md"))):
    md = read(path)
    pid = os.path.basename(path)[:3]
    h1 = re.match(r"# (P\d\d): ([^\n]+)", md)
    summary = md.split("\n\n")[1].strip()
    patterns.append({
        "id": pid, "title": h1.group(2),
        "summary_html": markdown.markdown(summary)[3:-4],
        "body": convert(md, shift=2, prefix=pid.lower() + "-"),
    })

# Finder data: ranges and limits per pattern (mirrors the cards; "stretch" = achievable with stated uplift/controls).
FINDER = {
    "P01": dict(b=[1, 2], c=1, sl=2, slx=3, e=2, ex=3, sf="—", neo="—", shapes=["single"], notes={"sl": "SL3 needs the uplift kit", "e": "E3 only if a person reviews every output"}),
    "P02": dict(b=[1, 3], c=2, sl=2, slx=2, e=3, ex=3, sf="Optional / central", neo="Optional sink", shapes=["bulk"], notes={"e": "E3 needs the low-confidence review queue"}),
    "P03": dict(b=[1, 2], c=1, sl=1, slx=2, e=2, ex=2, sf="Central", neo="—", shapes=["prototype", "metrics"], notes={"sl": "SL2 for internal analyst tools only"}),
    "P04": dict(b=[1, 2], c=2, sl=2, slx=2, e=2, ex=3, sf="Optional source", neo="—", shapes=["documents"], notes={"e": "E3 as advisory, with citations the user verifies"}),
    "P05": dict(b=[3, 4], c=3, sl=3, slx=3, e=3, ex=3, sf="Optional source", neo="Optional", shapes=["documents"], notes={}),
    "P06": dict(b=[2, 3], c=3, sl=2, slx=3, e=3, ex=3, sf="Structured spine", neo="Central", shapes=["multihop"], notes={"sl": "SL3 needs Aura Business Critical or a self-managed cluster"}),
    "P07": dict(b=[1, 2], c=2, sl=2, slx=3, e=4, ex=4, sf="Optional", neo="Optional", shapes=["process"], notes={"sl": "SL3 feasible with durable state and uplift", "e": "E3–E4 with autonomy bands and human approval"}),
    "P08": dict(b=[2, 3], c=3, sl=2, slx=2, e=2, ex=3, sf="Optional tool", neo="Optional tool", shapes=["openended"], notes={"e": "E3 only with confirmation of every write"}),
    "P09": dict(b=[1, 2], c=2, sl=2, slx=2, e=2, ex=3, sf="Central (variant A)", neo="Optional", shapes=["metrics"], notes={"e": "E3 when a person verifies figures before acting"}),
    "P10": dict(b=[3, 4], c=4, sl=3, slx=3, e=None, ex=None, sf="Training data", neo="Optional", shapes=[], notes={}),
    "P11": dict(b=[2, 3], c=3, sl=3, slx=3, e=4, ex=4, sf="Features / scoring", neo="Graph features", shapes=["prediction"], notes={"e": "E4 with human oversight: the ML model decides"}),
}
cards = [{"id": p["id"], "title": p["title"], "summary": p["summary_html"], **FINDER[p["id"]]} for p in patterns]

sections_html = {
    "choosing": convert(choosing_md, shift=0),
    "glance": convert(glance_md, shift=0, drop_h1=False),
    "framework": convert(framework, shift=1),
    "foundations": convert(foundations, shift=1),
    "scoring": convert(scoring_md, shift=0, drop_h1=False),
    "checklist": convert(checklist, shift=1),
}
pattern_html = "\n".join(
    f'<article class="pattern" id="{p["id"].lower()}"><header class="pattern-head"><span class="pid">{p["id"]}</span>'
    f'<h3>{html.escape(p["title"])}</h3></header>{p["body"]}<p class="back"><a href="#finder">Back to the finder</a></p></article>'
    for p in patterns)

toc = [("finder", "Pattern finder"), ("choosing", "Choosing a pattern"), ("glance", "Suitability at a glance"),
       ("patterns", "The patterns")] + [(p["id"].lower(), f'{p["id"]} {p["title"]}') for p in patterns] + [
       ("framework", "Decision framework"), ("foundations", "Shared foundations"), ("scoring", "Scoring method"),
       ("checklist", "Review checklist")]
toc_html = "\n".join(
    '<li class="%s"><a href="#%s">%s</a></li>' % ("sub" if re.match(r"p\d\d$", a) else "", a, html.escape(t)) for a, t in toc)

TEMPLATE = read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "catalogue_page_template.html"))
page = (TEMPLATE
        .replace("{{TOC}}", toc_html)
        .replace("{{CARDS_JSON}}", json.dumps(cards, ensure_ascii=False).replace("</", "<\\/"))
        .replace("{{CHOOSING}}", sections_html["choosing"])
        .replace("{{GLANCE}}", sections_html["glance"])
        .replace("{{PATTERNS}}", pattern_html)
        .replace("{{FRAMEWORK}}", sections_html["framework"])
        .replace("{{FOUNDATIONS}}", sections_html["foundations"])
        .replace("{{SCORING}}", sections_html["scoring"])
        .replace("{{CHECKLIST}}", sections_html["checklist"]))
with open(sys.argv[1], "w", encoding="utf-8") as fh:
    fh.write(page)
print("wrote", sys.argv[1], len(page), "bytes")
