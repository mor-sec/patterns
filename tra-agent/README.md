# TRA agent: platform-neutral core

A multi-agent service that drafts threat and risk assessments (TRAs) from design artefacts, for security practitioners to review. It follows ISO/IEC 27005, uses STRIDE per element plus MITRE ATLAS for AI components, rates risk on the [SAR 5x5 matrix](../docs/03-risk-methodology.md) with AUD thresholds, and maps controls to ISO 27001:2022, the ASD Essential Eight (ML2), the ISM and PCI DSS v4.0.1.

The agent drafts; people decide. Every TRA stops at three human gates, and only a human can pass them:

| Gate | After stage | Who | Policy enforced in code |
|---|---|---|---|
| G1 | Intake | Practitioner | Human identity, role, clearance at or above the TRA's classification |
| G2 | Evaluation | Practitioner | As G1; Tier 1 needs two different practitioners on the same TRA version |
| G3 | Acceptance | Risk owner | As G1, plus phishing-resistant MFA within the last 10 minutes |

This package is the core only. It runs on a workstation today; the AgentCore and Foundry adapters (step 3 of the build plan) wrap the same code for deployment.

## Quick start (offline, no cloud account)

The repo includes a fictional design ([examples/artefacts/payments-portal-design.md](examples/artefacts/payments-portal-design.md)) and recorded model output, so you can run the whole lifecycle without credentials.

```bash
cd tra-agent
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest -q

R=tests/fixtures/replay_payments.json
tra-agent --replay $R new --title "Customer payments portal" \
  --artefact git:payments-portal-design.md --git-root examples/artefacts --user alice
tra-agent --replay $R gate TRA-2026-001 G1 approve --user alice --rationale "Scope confirmed"
tra-agent --replay $R gate TRA-2026-001 G2 approve --user alice --rationale "Reviewed"
tra-agent --replay $R gate TRA-2026-001 G2 approve --user bob --rationale "Second review"
tra-agent --replay $R gate TRA-2026-001 G3 approve --user carol --role risk_owner --strong-auth \
  --rationale "Accept treatment plan"
tra-agent report TRA-2026-001 --out out/
tra-agent verify-audit
```

`out/` then holds the TRA report (Markdown with a Mermaid DFD), the TRA as JSON, and the risk register in the SAR CSV format. The example design hides an instruction telling "automated reviewers" to rate everything Low; the quality critic flags it.

## Running with real models

Edit [config/models.yaml](config/models.yaml), then drop `--replay`:

- **Claude on Bedrock (default).** Uses the AU geographic inference profiles, which route only between Sydney and Melbourne. Needs `pip install -e ".[aws]"` and AWS credentials with `bedrock:InvokeModel` on those profiles.
- **GPT on Azure.** Set the Foundry endpoint and a regional deployment in Australia East. Needs `pip install -e ".[azure]"` and an Entra ID identity with the Cognitive Services User role. Claude on Foundry is Global or US Data Zone only, so don't route classified work to it.

Each agent can use a different model; for example, run the quality critic on GPT for model diversity.

## How it fits together

```
tra_core/
  schemas.py        TRA, system model, threats, controls, risks (Pydantic)
  risk.py           SAR 5x5 matrix, modifiers, AUD impact scale, tiering, acceptance authority
  classification.py PSPF labels: OFFICIAL: Sensitive max, label propagation, TRA floor
  stride.py         STRIDE-per-element applicability
  checks.py         deterministic checks run on every agent output and before each gate
  identity.py       Principal: human or workload acting for a human (built from validated tokens)
  gates.py          G1/G2/G3 policy
  workflow.py       stage machine
  audit.py          append-only, hash-chained audit log
  llm.py            ModelClient: Bedrock Converse, Azure OpenAI, replay; per-agent routing
  tools.py          read-only tools; local and MCP clients
  mcp_servers.py    MCP servers: reference (threats, controls) and artefacts (Git, Confluence)
  artefacts.py      Git and Confluence sources; refuse unlabelled or PROTECTED material
  agents/           six specialists and their prompts
  orchestrator.py   runs stages, calls specialists through an Invoker, stops at gates
  register.py       SAR CSV register (an Eramba writer can replace it)
  report.py         Markdown report and Mermaid DFD
  data/             threat library and control crosswalk (versioned YAML)
```

Design choices worth knowing:

- **Models never choose tools.** Each specialist calls the tools it needs in code and passes the results to its model. A prompt injection can't make an agent call something it wasn't going to call, and every tool call is logged.
- **Models never produce ratings.** They propose likelihood and impact with a rationale and citations; code computes the rating, applies the classification impact floor and checks that residual is not above inherent.
- **Artefacts are untrusted.** Their text is wrapped in `<artefact>` tags with an instruction never to follow it, and must carry a PSPF label to be read at all.
- **Invalid output is retried, then fails.** Schema and domain errors go back to the model up to three times; after that the stage fails rather than passing on bad data.
- **Specialists are A2A-ready.** Each takes a JSON `SpecialistRequest` and returns JSON, so the platform adapters can host them behind A2A endpoints without code changes.

## Reference data

- [threat_library.yaml](src/tra_core/data/threat_library.yaml): 32 threats across identity, data, application, delivery and AI/agents, with ATLAS IDs and links to SAR delivery-lifecycle IDs.
- [controls.yaml](src/tra_core/data/controls.yaml): 35 common controls crosswalked to ISO 27001:2022, Essential Eight, PCI DSS v4.0.1. The **ISM column is deliberately empty**: populate it from the current ISM release. The ASD Essentials column is ready for the successor baseline (expected around Q2 2027). Have the control owner verify the mappings before relying on them.

## Not done yet

- Platform adapters (AgentCore Runtime and Gateway, Foundry hosted agents), A2A hosting, IaC and the build guide: step 3.
- Golden-set evaluation, adversarial test suite and CI gates: step 4.
- The Confluence source has not been run against a live site.
- The portal UI. The CLI stands in for it locally; identity flags on the CLI are for local development only.
