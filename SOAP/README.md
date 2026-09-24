---
owner: architecture-practice
audience: solution architects, security architects, engineering leads, change approvers
reviewed: 2026-09-24
review-cadence: quarterly
---

# Solution on a Page (SOAP)

Front door for the SOAP template: a one-page format for changing an existing solution without writing a full Solution Architecture Design (SAD). Audience: anyone proposing, reviewing, or approving an incremental architecture change.

## What a SOAP is

A SOAP describes one bounded change to a solution that already has an approved design: adding a security control, replacing a component with a managed service, wiring a new integration, decommissioning something, or hardening resilience. It captures the delta, the security and compliance effect, the rollout and rollback, and the approvals, on a single page. When approved it becomes the source for updating the master design, so the SAD stays current without being rewritten.

A SOAP is not a SAD in miniature. The sizing gate at the top of every SOAP keeps it honest: if a box cannot be ticked, the change is bigger than a page.

## Which document to write

| The change is… | Write a… | Because |
|---|---|---|
| A new solution, a new bounded context, or a change spanning several | **SAD** | Needs full context, NFRs, and a complete topology |
| A decision with no topology change (library choice, naming, a policy) | **ADR** | Records the reasoning; nothing to draw or roll out |
| An incremental change to an existing solution's components, controls, or integrations | **SOAP** | Needs a delta, an impact assessment, and a rollout plan, but not a full design |
| A configuration or operational change with no architectural effect | **Change ticket** | Standard change process is enough |

When in doubt, start a SOAP. The sizing gate will tell you if it needs to become a SAD.

## Sizing gate

A change stays on a page only when all of these hold. They are repeated as a checklist in the template.

- Touches at most three components inside one bounded context or deployment unit, and the change delta table has at most three rows.
- Does not change a contract other teams consume, unless every consumer is listed.
- Adds no new fail-closed dependency to the build, deploy or runtime path of teams outside the owning team.
- If more than two other teams are affected, names them all and starts with a report-only or small-wave stage.
- Does not change data classification or residency, extend retention, or introduce new personal data.
- Adds no new supplier or third-party data flow unless its third-party risk assessment is complete and linked.
- Weakens no security control.
- Cost delta is within the service owner's delegated authority.
- Can be rolled back without reversing a data migration.
- Does not contradict an accepted ADR.

The author ticks the boxes; the architecture owner confirms them before the SOAP goes to review. If the architecture owner will not confirm the gate, the SOAP is escalated.

## How to write one

1. Copy [`soap-template.md`](soap-template.md) to `docs/soap/SOAP-NNN-short-title.md` in the solution's repo, using the next sequential number.
2. Fill the front matter and header, and tick the sizing gate first. If a box stays unticked, set the status to Escalated and write an ADR or SAD. Ask the architecture owner to confirm the gate before opening the review.
3. Draw only the affected slice. Link to the master diagram for everything else. Use the `added`, `changed`, `removed` classes from the template so the delta reads at a glance.
4. Fill the security and compliance table with control IDs from the control catalog, not prose. "Strengthens A.8.20" is reviewable; "improves network security" is not.
5. Name every consumer under Impact. The most common cause of a failed change is a consumer nobody told.
6. Write the rollback before the rollout, and name the point of no return: the step after which the rollback stops working. If you cannot describe the rollback in one line, the change is not ready.
7. List the records to update on approval as a checklist. Each one gets ticked with a link to the pull request or commit that updated it, and the SOAP is Implemented only when all of them are. This is the line that stops the SAD drifting.
8. Run `scripts/soap.py check` and `scripts/soap.py register`.

Budget: around 600 words of prose plus one or two diagrams. Tables carry the facts, prose carries the reasoning.

## Lifecycle

| Status | Meaning |
|---|---|
| Draft | Author is still filling it in |
| In review | Approvers named in the header are reviewing; comments go on the pull request |
| Approved | All approvers have signed the decision table; work can start |
| Rejected | Recorded with the reason, kept for the audit trail |
| Implemented | Change is live and every listed record is ticked with a link to its update |
| Superseded by SOAP-NNN | A later SOAP replaces this one; never edit an approved SOAP's substance |
| Escalated to ADR/SAD-NNN | The sizing gate failed or was not confirmed; the content becomes input to the ADR or SAD |

## Worked examples

- [SOAP-001 — Front the customer portal with a WAF and move secrets to a managed store](examples/SOAP-001-portal-waf-and-managed-secrets.md). A security-control change.
- [SOAP-002 — Replace self-hosted RabbitMQ with Amazon SQS for order events](examples/SOAP-002-replace-rabbitmq-with-sqs.md). A modernisation change.
- [SOAP-003](docs/soap/SOAP-003-socket-github-pull-request-gate.md), [SOAP-004](docs/soap/SOAP-004-socket-desktop-and-assistant-toolchain.md) and [SOAP-005](docs/soap/SOAP-005-socket-firewall-registry-path.md) — one programme split into three changes that can each be rolled back on its own. SOAP-005 shows an escalation: it adds a fail-closed dependency to every team's build, so it fails the gate and moves to a SAD addendum.

All SOAPs in this repo are listed in the generated [register](docs/soap/REGISTER.md).

## Repository layout

- `README.md` is this file.
- `soap-template.md` is the template. The copyable body is inside the fenced block.
- `examples/` holds worked SOAPs.
- `docs/soap/` holds the Socket.dev SOAPs and the generated `REGISTER.md`.
- `docs/superpowers/specs/` holds the design note for the template itself.
- `scripts/` holds the SOAP checker and register generator (`soap.py`), the Mermaid check and its Puppeteer config.
- `.github/workflows/checks.yml` runs every check on each pull request.

## Checks

- Lint: `npx -y markdownlint-cli2 "**/*.md"`
- Mermaid: `scripts/check-mermaid.sh` renders every diagram with mermaid-cli and fails on any that do not parse.
- SOAP content: `scripts/soap.py check` validates front matter, required sections, the diagram classes, the change delta size, the sizing gate and its confirmation, records evidence for Implemented SOAPs, unfilled placeholders, and a 1,000-word prose ceiling.
- Register: `scripts/soap.py register` rebuilds `docs/soap/REGISTER.md` and flags open SOAPs that change the same component; `--check` fails if it is stale.

`soap.py` needs Python 3 with PyYAML (`pip install pyyaml`).

## Related

- Design note: [docs/superpowers/specs/2026-09-03-solution-on-a-page-design.md](docs/superpowers/specs/2026-09-03-solution-on-a-page-design.md)
- ADR template and markdown style guide: the AI-DLC standards repo, `standards/adr-template.md` and `standards/markdown-style-guide.md`
