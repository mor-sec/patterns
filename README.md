# Security Architecture Review (SAR) Process

A risk-led process for reviewing the security architecture of cloud-hosted systems **before they are productionised**. It covers the design and the delivery lifecycle that produces the running system: from infrastructure-as-code (IaC), through build and supply chain, to configuration and environment promotion.

## What this process is (and is not)

| In scope: design-time and delivery-time assurance | Out of scope: operational security after go-live |
|---|---|
| Business context, data classification, risk appetite | SOC monitoring, alert triage, threat hunting |
| Threat modelling and risk assessment | Incident response execution |
| Cloud account/tenancy structure, identity, network, data protection | Day-to-day vulnerability and patch management |
| Shared-responsibility decisions per cloud service | Runtime access reviews and recertification |
| IaC design, state, modules, policy-as-code guardrails | Penetration testing operations (we *require* it, we don't run it) |
| CI/CD, build integrity, software supply chain | Security operations KPIs |
| Configuration baselines, secrets, environment promotion, drift *design* | BAU control operation and evidence gathering |

The SAR checks that operational controls **can** work. For example, it checks that logs are generated, centralised and tamper-evident by design. How those controls are then run is handed to operational security at the **handover gate** ([docs/02-review-workflow.md](docs/02-review-workflow.md#stage-7-handover-to-operational-security)).

## Contents

| # | Document | Purpose |
|---|---|---|
| 1 | [Scope, principles and roles](docs/01-scope-and-principles.md) | Why, what, who, and the triggers for a review |
| 2 | [Review workflow](docs/02-review-workflow.md) | The staged process, entry and exit criteria, and tiering |
| 3 | [Risk methodology](docs/03-risk-methodology.md) | How risk is rated, treated, accepted and tracked |
| 4 | [Cloud security architecture domains](docs/04-cloud-security-architecture.md) | What "good" looks like in each cloud design domain |
| 5 | [Delivery lifecycle: IaC → build → configuration](docs/05-delivery-lifecycle.md) | Securing the path from code to running infrastructure |

### AI architecture patterns

[AI solution architecture patterns](ai-patterns/README.md) is a catalogue of AWS-based reference architectures for AI solutions: serverless inference, batch enrichment, Snowflake-native prototyping, managed and enterprise RAG, GraphRAG with Neo4j, agentic workflows and agents, conversational analytics, custom models, and predictive ML. Each pattern is scored for budget, complexity and service level, and maps to SAR review expectations.

### API architecture patterns

[API solution architecture patterns](api-patterns/README.md) is a catalogue of AWS-native reference architectures for secure, highly available APIs handling OFFICIAL and OFFICIAL-SENSITIVE data: serverless and managed API products, private and service-to-service APIs, containerised APIs, mTLS B2B integration, GraphQL and real-time, asynchronous APIs, user-facing BFFs, legacy facades and multi-region active/active. Each pattern is rated for budget, complexity, service level, authentication assurance and ease of integration.

### TRA agent

[TRA agent](tra-agent/README.md) is a multi-agent service that drafts threat and risk assessments from design artefacts in Git and Confluence, using this repository's risk method and register format. People approve every TRA at three gates. The core runs locally, and the same code deploys to AWS Bedrock AgentCore (Sydney) or Microsoft Foundry (Australia East) with the included CDK and Bicep.

### Templates

- [Intake questionnaire](templates/intake-questionnaire.md): filled in by the delivery team to start a review
- [Threat model](templates/threat-model.md): trust boundaries, data flows, threats and their mitigations
- [Architecture review record](templates/architecture-review-record.md): the review's single output document
- [Risk register](templates/risk-register.csv): findings and risks in a trackable format
- [Risk acceptance](templates/risk-acceptance.md): formal acceptance of residual risk
- [Security architecture decision record (ADR)](templates/security-adr.md): records significant security design decisions
- [AI pattern scoring sheet](templates/ai-pattern-scoring-sheet.md) ([Excel workbook](templates/ai-pattern-scoring.xlsx), [worked example](templates/ai-pattern-scoring-example.xlsx), [CSV](templates/ai-pattern-scoring.csv)): gates, weighted fit and validation for comparing candidate AI patterns
- [API pattern scoring sheet](templates/api-pattern-scoring-sheet.md): gates, weighted fit and validation for comparing candidate API patterns
- [API pattern selection record](templates/api-pattern-selection.md): records the chosen API pattern, its authentication design, targets and trade-offs
- [AI pattern selection record](templates/ai-pattern-selection.md): records the chosen AI pattern, its budget and service level targets, and its trade-offs

### Checklists (reviewer aids, not substitutes for judgement)

- [Cloud architecture checklist](checklists/cloud-architecture.md)
- [IaC checklist](checklists/iac.md)
- [Build and supply chain checklist](checklists/build-pipeline.md)
- [Configuration checklist](checklists/configuration.md)
- [AI workload checklist](checklists/ai-workloads.md)
- [API workload checklist](checklists/api-workloads.md)

## Using this process: a quick start

1. The delivery team completes the **intake questionnaire** as soon as a solution is proposed (ideally at design inception, not a week before go-live).
2. The security architect **tiers** the review (Tier 1–3) from data sensitivity, exposure and blast radius. The tier sets the depth.
3. Together, run the **threat model** and **risk assessment**.
4. Review the design against the **cloud domains** and the **delivery lifecycle**, using the checklists as prompts.
5. Record findings in the **review record** and **risk register**. Each risk is mitigated, transferred, avoided or formally **accepted** by its owner.
6. The **decision gate** gives one of: Approved / Approved with conditions / Not approved.
7. The **handover** passes operational control requirements to operational security, and the architecture is re-reviewed on significant change.

## Alignment

The process is framework-neutral but maps to: NIST CSF 2.0 (Govern/Identify/Protect), NIST SP 800-160, ISO/IEC 27001:2022 Annex A (5.8, 8.25–8.28, 8.9, 8.32), CSA Cloud Controls Matrix v4, CIS Benchmarks, SLSA v1.x, NIST SSDF (SP 800-218), and the AWS, Azure and GCP Well-Architected security pillars.
