#!/usr/bin/env python3
"""Check SOAP documents and build the SOAP register.

Usage:
  scripts/soap.py check              exit 1 if any SOAP breaks a rule below
  scripts/soap.py register           rewrite docs/soap/REGISTER.md
  scripts/soap.py register --check   exit 1 if REGISTER.md is out of date

A SOAP is any file named SOAP-NNN-*.md under examples/ or docs/soap/.
Needs PyYAML (pip install pyyaml).
"""
import os
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SOAP_DIRS = [ROOT / "examples", ROOT / "docs" / "soap"]
REGISTER = ROOT / "docs" / "soap" / "REGISTER.md"

STATUSES = ["Draft", "In review", "Approved", "Rejected", "Implemented", "Superseded", "Escalated"]
OPEN = {"Draft", "In review", "Approved"}
GATED = {"In review", "Approved", "Implemented"}  # gate must be ticked and confirmed
REQUIRED_KEYS = ["id", "status", "change_type", "solution", "author", "approvers",
                 "gate_confirmed_by", "gate_confirmed_on", "date", "components"]
SECTIONS = ["Sizing gate", "Summary", "Current state", "Proposed change", "Options considered",
            "Security and compliance", "Impact", "Implementation and rollout",
            "Risks and assumptions", "Decision"]
CLASSDEFS = [
    "classDef added fill:#d8f5d0,stroke:#2e7d32,color:#1b5e20",
    "classDef changed fill:#fff3c4,stroke:#f9a825,color:#5d4037",
    "classDef removed fill:#fde0dc,stroke:#c62828,color:#7f0000,stroke-dasharray: 5 5",
]
MAX_DELTA_ROWS = 3
MAX_PROSE_WORDS = 1000  # README budget is ~600; this is the hard ceiling


def soap_files():
    for d in SOAP_DIRS:
        yield from sorted(d.glob("SOAP-[0-9][0-9][0-9]-*.md"))


def split_front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, text
    return yaml.safe_load(m.group(1)) or {}, text[m.end():]


def section(body, name, level=2):
    """Text of a heading's section, up to the next heading of the same or higher level."""
    hashes = "#" * level
    m = re.search(rf"^{hashes} {re.escape(name)}\s*$(.*?)(?=^#{{1,{level}}} |\Z)", body, re.M | re.S)
    return m.group(1) if m else ""


def strip_code(body):
    return re.sub(r"^```.*?^```", "", body, flags=re.M | re.S)


def prose_words(body):
    words = 0
    for line in strip_code(body).splitlines():
        s = line.strip()
        if not s or s.startswith(("|", "#", "- [")):  # tables, headings, checklists
            continue
        words += len(s.split())
    return words


def table_rows(text):
    rows = [l for l in text.splitlines() if l.strip().startswith("|")]
    return [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows[2:]]


def load(path):
    text = path.read_text(encoding="utf-8")
    fm, body = split_front_matter(text)
    title = re.search(r"^# (.+)$", body, re.M)
    return fm, body, title.group(1) if title else path.stem


def check_file(path, known_ids):
    errors = []
    rel = path.relative_to(ROOT)
    fm, body, _ = load(path)
    if fm is None:
        return [f"{rel}: no YAML front matter"]

    for key in REQUIRED_KEYS:
        if key not in fm:
            errors.append(f"{rel}: front matter is missing '{key}'")
    status = fm.get("status")
    if status not in STATUSES:
        errors.append(f"{rel}: status '{status}' is not one of {', '.join(STATUSES)}")
    if not path.name.startswith(f"{fm.get('id')}-"):
        errors.append(f"{rel}: id '{fm.get('id')}' does not match the file name")

    header = re.search(r"^\| \*\*Status\*\* \| (.+?) \|$", body, re.M)
    if not header or (status and not header.group(1).startswith(status)):
        errors.append(f"{rel}: header table status does not match front matter status '{status}'")

    found = [h for h in re.findall(r"^## (.+?)\s*$", body, re.M) if h in SECTIONS]
    if found != SECTIONS:
        missing = [s for s in SECTIONS if s not in found]
        errors.append(f"{rel}: required sections missing or out of order"
                      + (f" (missing: {', '.join(missing)})" if missing else ""))

    proposed = section(body, "Proposed change")
    diagram = re.search(r"^```mermaid\n(.*?)^```", proposed, re.M | re.S)
    if not diagram or any(c not in [l.strip() for l in diagram.group(1).splitlines()] for c in CLASSDEFS):
        errors.append(f"{rel}: proposed-change diagram does not declare the template's added/changed/removed classDefs")

    delta = table_rows(section(body, "Change delta", level=3))
    if len(delta) > MAX_DELTA_ROWS:
        errors.append(f"{rel}: change delta has {len(delta)} rows; the gate allows {MAX_DELTA_ROWS}")
    delta_names = [r[1] for r in delta if len(r) > 1]
    if sorted(delta_names) != sorted(fm.get("components") or []):
        errors.append(f"{rel}: front matter components {fm.get('components')} do not match change delta rows {delta_names}")

    gate = section(body, "Sizing gate")
    unticked = len(re.findall(r"^- \[ \]", gate, re.M))
    if status in GATED:
        if unticked:
            errors.append(f"{rel}: status is {status} but {unticked} sizing gate box(es) are unticked")
        if not fm.get("gate_confirmed_by") or not fm.get("gate_confirmed_on"):
            errors.append(f"{rel}: status is {status} but the gate has not been confirmed by the architecture owner")
    if status == "Escalated" and not fm.get("escalated_to"):
        errors.append(f"{rel}: status is Escalated but escalated_to is empty")
    if status == "Superseded" and not fm.get("superseded_by"):
        errors.append(f"{rel}: status is Superseded but superseded_by is empty")

    for dep in fm.get("depends_on") or []:
        if dep not in known_ids:
            errors.append(f"{rel}: depends_on names unknown SOAP '{dep}'")

    if status == "Implemented":
        records = section(body, "Decision").split("**Records to update", 1)[-1].split("**Follow-ups", 1)[0]
        for item in re.findall(r"^- \[.\] .+$", records, re.M):
            if not item.startswith("- [x]") or not re.search(r"\]\(|https?://", item):
                errors.append(f"{rel}: status is Implemented but a record is not ticked and linked: {item}")

    text = re.sub(r"`[^`]*`", "", strip_code(body))
    for ph in re.findall(r"<(?!br/?>)[^<>\n]+>", text):
        errors.append(f"{rel}: unfilled placeholder {ph}")

    words = prose_words(body)
    if words > MAX_PROSE_WORDS:
        errors.append(f"{rel}: {words} prose words, over the {MAX_PROSE_WORDS}-word ceiling")
    return errors


def cmd_check():
    files = list(soap_files())
    known = set()
    for p in files:
        fm, _, _ = load(p)
        if fm:
            known.add(fm.get("id"))
    errors = [e for p in files for e in check_file(p, known)]
    for e in errors:
        print(f"FAIL: {e}")
    print(f"Checked {len(files)} SOAP(s), {len(errors)} problem(s)")
    return 1 if errors else 0


def build_register():
    rows, owners = [], {}
    for p in soap_files():
        fm, _, title = load(p)
        if not fm:
            continue
        link = os.path.relpath(p, REGISTER.parent)
        name = title.split(" — ", 1)[-1]
        status = fm["status"]
        if status == "Escalated":
            status += f" → {fm.get('escalated_to')}"
        if status == "Superseded":
            status += f" → {fm.get('superseded_by')}"
        confirmed = f"{fm['gate_confirmed_by']}, {fm['gate_confirmed_on']}" if fm.get("gate_confirmed_by") else "—"
        deps = ", ".join(fm.get("depends_on") or []) or "—"
        rows.append(f"| [{fm['id']}]({link}) | {name} | {status} | {fm['solution']} | {confirmed} | {deps} |")
        if fm["status"] in OPEN:
            for c in fm.get("components") or []:
                owners.setdefault((fm["solution"], c), []).append(fm["id"])

    conflicts = [f"- {sol} · {comp}: {', '.join(ids)}" for (sol, comp), ids in sorted(owners.items()) if len(ids) > 1]
    out = [
        "# SOAP register",
        "",
        "Generated by `scripts/soap.py register` from each SOAP's front matter. Do not edit by hand.",
        "",
        "| ID | Change | Status | Solution | Gate confirmed | Depends on |",
        "|---|---|---|---|---|---|",
        *rows,
        "",
        "## Open SOAPs changing the same component",
        "",
        *(conflicts or ["None."]),
        "",
    ]
    return "\n".join(out)


def cmd_register(check_only):
    content = build_register()
    if check_only:
        current = REGISTER.read_text(encoding="utf-8") if REGISTER.exists() else ""
        if current != content:
            print("FAIL: docs/soap/REGISTER.md is out of date; run scripts/soap.py register")
            return 1
        print("Register is up to date")
        return 0
    REGISTER.write_text(content, encoding="utf-8")
    print(f"Wrote {REGISTER.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["check"]:
        sys.exit(cmd_check())
    if args[:1] == ["register"]:
        sys.exit(cmd_register("--check" in args))
    print(__doc__)
    sys.exit(2)
