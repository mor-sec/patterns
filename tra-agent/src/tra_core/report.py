"""Render a TRA as Markdown, with a Mermaid DFD drawn from the system model."""

from __future__ import annotations

import re

from tra_core.reference import Reference
from tra_core.risk import AUTHORITY, Rating
from tra_core.schemas import TRA, ElementType, SystemModel

_ORDER = {Rating.CRITICAL: 0, Rating.HIGH: 1, Rating.MEDIUM: 2, Rating.LOW: 3}


def _safe(text: str) -> str:
    return re.sub(r'["<>\[\]{}|]', " ", text).strip()


def _abbrev(label: str) -> str:
    return {"OFFICIAL_SENSITIVE": "OS", "OFFICIAL": "O", "PROTECTED": "P"}.get(label, label)


def _node(identifier: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", identifier)


def mermaid_dfd(model: SystemModel) -> str:
    """Zones become subgraphs (trust boundaries); shapes follow DFD conventions."""
    lines = ["flowchart LR"]
    for zone in model.zones:
        lines.append(f'  subgraph {_node(zone.id)}["{_safe(zone.name)}"]')
        for e in model.elements:
            if e.zone != zone.id:
                continue
            label = f"{e.id} {_safe(e.name)}<br/>{_abbrev(e.classification.value)}"
            if e.type is ElementType.EXTERNAL_ENTITY:
                lines.append(f'    {e.id}["{label}"]')
            elif e.type is ElementType.DATA_STORE:
                lines.append(f'    {e.id}[("{label}")]')
            else:
                lines.append(f'    {e.id}(["{label}"])')
        lines.append("  end")
    for f in model.flows:
        arrow = "==>" if f.crosses_boundary else "-->"
        lines.append(f'  {f.source} {arrow}|"{f.id} {_safe(f.data)[:40]} ({_abbrev(f.classification.value)})"| {f.target}')
    lines.append("  classDef ai stroke-dasharray: 4 3")
    ai = [e.id for e in model.elements if e.is_ai]
    if ai:
        lines.append(f"  class {','.join(ai)} ai")
    return "\n".join(lines)


def render(tra: TRA, reference: Reference) -> str:
    out: list[str] = []
    w = out.append
    w(f"# Threat and Risk Assessment: {tra.title}\n")
    w(f"**{tra.classification.label}**\n")
    w("| Field | Value |\n|---|---|")
    w(f"| TRA reference | {tra.id} (version {tra.version}) |")
    w(f"| Work type | {tra.work_type.value.replace('_', ' ')} |")
    w(f"| Tier | {tra.tier} |")
    w(f"| Stage | {tra.stage.value} |")
    w(f"| Requested by | {tra.requested_by} |")
    if tra.intake and tra.intake.risk_owner:
        w(f"| Risk owner | {tra.intake.risk_owner} |")
    w(f"| Content hash | `{tra.content_hash()[:16]}` |")
    w(f"| Threat library / controls | {reference.threats.version} / {reference.controls.version} |\n")

    if tra.intake:
        w("## 1. Scope\n")
        w(tra.intake.summary + "\n")
        if tra.intake.missing_information:
            w("**Information the artefacts did not provide:**\n")
            for m in tra.intake.missing_information:
                w(f"- {m}")
            w("")

    w("## 2. Artefacts assessed\n")
    w("| Source | Locator | Classification | Revision | SHA-256 |\n|---|---|---|---|---|")
    for a in tra.artefacts:
        w(f"| {a.source} | {a.locator} | {a.classification.label} | {a.revision or ''} | `{a.sha256[:12]}` |")
    w("")

    if tra.system_model:
        m = tra.system_model
        w("## 3. System model\n")
        w(m.summary + "\n")
        w("```mermaid\n" + mermaid_dfd(m) + "\n```\n")
        w("Thick arrows cross a trust boundary. Dashed outlines are AI components. O = OFFICIAL, OS = OFFICIAL: Sensitive.\n")
        w("| Flow | From | To | Data | Classification | Protocol | Authenticated | Encrypted |\n|---|---|---|---|---|---|---|---|")
        yn = {True: "yes", False: "no", None: "unknown"}
        for f in m.flows:
            w(f"| {f.id} | {f.source} | {f.target} | {f.data} | {f.classification.label} | {f.protocol or ''} | {yn[f.authenticated]} | {yn[f.encrypted]} |")
        w("\n| Asset | Kind | Classification | C / I / A |\n|---|---|---|---|")
        for a in m.assets:
            w(f"| {a.id} {a.name} | {a.kind} | {a.classification.label} | {a.confidentiality} / {a.integrity} / {a.availability} |")
        w("")

    if tra.threats:
        w("## 4. Threats\n")
        w("| ID | Element | STRIDE | ATLAS | Library | Threat |\n|---|---|---|---|---|---|")
        for t in tra.threats:
            w(f"| {t.id} | {t.element_id} | {''.join(s.value for s in t.stride)} | {', '.join(t.atlas)} | {t.library_ref or ''} | {t.statement} |")
        w("")

    if tra.controls:
        w("## 5. Controls\n")
        w("| Control | Status | Threats | Framework references | Evidence |\n|---|---|---|---|---|")
        for c in tra.controls:
            cc = reference.controls.get(c.control_id)
            refs = "; ".join(f"{k} {', '.join(v)}" for k, v in cc.references().items()) if cc else ""
            title = f"{c.control_id} {cc.title}" if cc else c.control_id
            w(f"| {title} | {c.status.value.replace('_', ' ')} | {', '.join(c.threat_ids)} | {refs} | {c.evidence} |")
        w("")

    if tra.risks:
        w("## 6. Risks\n")
        risks = sorted(tra.risks, key=lambda r: (_ORDER[r.residual_rating], r.id))
        w("| Risk | Inherent | Residual | Treatment | Acceptance authority |\n|---|---|---|---|---|")
        for r in risks:
            w(
                f"| {r.id}: {r.statement} | {r.inherent_rating.value} (L{r.inherent_likelihood} I{r.inherent_impact}) "
                f"| **{r.residual_rating.value}** (L{r.residual_likelihood} I{r.residual_impact}) | {r.treatment.value} "
                f"| {AUTHORITY[r.residual_rating].who_may_accept} |"
            )
        w("")
        for r in risks:
            w(f"**{r.id} rationale.** {r.rationale} *Cites: {', '.join(r.citations)}.*")
            if r.proposed_controls:
                w(f" Proposed controls: {', '.join(r.proposed_controls)}.")
            w("")

    if tra.critique and tra.critique.issues:
        w("## 7. Quality review findings\n")
        w("| Severity | Where | Issue | Source |\n|---|---|---|---|")
        for i in tra.critique.issues:
            w(f"| {i.severity} | {i.where} | {i.issue} | {i.source} |")
        w("")

    if tra.gates:
        w("## 8. Gate decisions\n")
        w("| Gate | Decision | By | Role | When | Rationale |\n|---|---|---|---|---|---|")
        for g in tra.gates:
            w(f"| {g.gate.value} | {g.decision} | {g.by} | {g.role} | {g.at:%Y-%m-%d %H:%M} UTC | {g.rationale} |")
        w("")

    w(f"\n**{tra.classification.label}**")
    return "\n".join(out)
