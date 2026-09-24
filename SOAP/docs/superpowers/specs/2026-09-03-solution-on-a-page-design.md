---
owner: architecture-practice
audience: maintainers of the SOAP template
reviewed: 2026-09-24
---

# Solution on a Page (SOAP) — design

Design note for the SOAP template repo. Audience: whoever maintains or extends the template.

## Problem

Small architecture changes (adding a security control, swapping a component for a managed service, wiring a new integration) are today either undocumented or force a full Solution Architecture Design (SAD). The first loses the decision; the second costs more than the change. An Architecture Decision Record (ADR) captures a decision but not the shape of the change: the delta diagram, the control impact, the rollout, the rollback.

## Goal

One markdown template that captures an incremental change to an existing solution on a single page, with enough rigour that architecture and security can approve it and the master design can be updated from it.

## Non-goals

- Replacing the SAD for new solutions or multi-context changes.
- Replacing the ADR for pure decisions with no topology change.
- A tool or web app. Markdown only, so it lints and reviews like the rest of the docs estate.

## Design

- `README.md` orients a reader in two minutes: what SOAP is, the triage table (change ticket, ADR, SOAP, SAD), the sizing gate, the lifecycle, and how to fill it in.
- `soap-template.md` follows the AI-DLC standards convention: front-matter, short usage note, then the copyable body in a fenced markdown block.
- `examples/` holds two worked SOAPs, one per headline use case: adding security controls, and modernising a component. Examples are the fastest way to teach a template.
- Sections are ordered as an approver reads: identity, sizing gate, summary, current state, proposed change and delta table, options, security and compliance, impact, rollout and rollback, risks, decision and follow-ups.
- The sizing gate is a checklist at the top of the document, not guidance in the README. If any box is unchecked the change escalates. This stops the template being stretched into a SAD substitute. The author ticks it and the architecture owner confirms it, because a gate the author grades alone is a suggestion.
- Each SOAP carries YAML front matter, so a script can check it and build a register that shows status and flags two open SOAPs changing the same component.
- Security section uses ISO/IEC 27001:2022 Annex A control IDs so it links to the existing control catalog and statement of applicability.
- Diagrams are Mermaid, with a fixed class convention (added, changed, removed) so every SOAP delta diagram reads the same way.
- The decision section ends with "records to update" as a checklist with an evidence link per record, so the master SAD, diagrams and control records do not drift. A SOAP is Implemented only when every record is linked.

## Page budget

Around 600 words of prose plus one or two diagrams. Tables carry the enumerable facts. If a section needs more than that, the change is probably not a SOAP.

## Verification

- `npx -y markdownlint-cli2 "**/*.md"` passes.
- Mermaid blocks render (`scripts/check-mermaid.sh`).
- `scripts/soap.py check` passes: every SOAP fills every section without placeholders, and the gate, delta, diagram classes and records rules hold.
- `scripts/soap.py register --check` passes.
- All of the above run in CI (`.github/workflows/checks.yml`).
