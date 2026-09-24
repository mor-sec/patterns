# AI Workload Checklist

These are prompts for AI solutions built on the [AI architecture patterns](../ai-patterns/README.md). Use them alongside the [cloud architecture checklist](cloud-architecture.md). Items marked *(foundation)* are satisfied by inheritance when the workload uses a reviewed [shared foundation](../ai-patterns/01-shared-foundations.md).

## Pattern fit, budget and service levels
- [ ] AI-01 Pattern(s) selected and recorded in an [AI pattern selection record](../templates/ai-pattern-selection.md), with the lighter patterns considered and rejected for stated reasons
- [ ] AI-02 Budget stated as a fixed floor plus unit cost per transaction, with expected volume, modelled at today's volume and at 10×; within the agreed band, with hard per-task limits for super-linear patterns
- [ ] AI-03 Service level tier agreed, including quality, freshness and cost SLIs as well as availability and latency
- [ ] AI-04 Composite availability of the serial dependencies calculated; degraded mode defined and tested for SL2+
- [ ] AI-05 Budget alarms, per-session/per-user limits (steps, tokens, cost) and quota headroom in place
- [ ] AI-06 Consequence of error (E-level) and regulatory profile (R-level) rated for the problem, and supported by the chosen pattern's controls
- [ ] AI-07 Every data prerequisite of the pattern rated Ready or Partial-with-funded-plan; none Absent
- [ ] AI-08 For Tier 1–2 or contested choices: scoring sheet completed (gates, weighted fit, bake-off) and attached to the selection record
- [ ] AI-09 Review queue volume × handling time checked against reviewer capacity, with peak headroom

## Models and providers
- [ ] AI-10 Models used are on the approved model list, with data-use terms and residency confirmed *(foundation)*
- [ ] AI-11 IAM/SCP restricts model invocation to approved model and inference-profile ARNs *(foundation)*
- [ ] AI-12 Cross-region inference profile Regions checked against data residency requirements
- [ ] AI-13 Fallback model and model-deprecation plan documented
- [ ] AI-14 Self-hosted or imported weights: provenance, integrity verification, licence and artefact scanning (P10)
- [ ] AI-15 Exit plan for high lock-in components (open formats, owned prompts and evaluation sets, abstraction of model access)

## Data, retrieval and knowledge graph
- [ ] AI-20 Every source ingested into indexes/graphs has an owner, a classification and a removal process
- [ ] AI-21 Document-level access control enforced at retrieval time from the caller's verified identity (not by the prompt)
- [ ] AI-22 Entitlement tests with users of different access levels are part of the evaluation suite
- [ ] AI-23 Caches (exact/semantic) keyed by entitlement scope; no cross-user or cross-tenant answer reuse
- [ ] AI-24 Knowledge graph classified at its most sensitive combination (aggregation risk); provenance on derived facts
- [ ] AI-25 Snowflake ↔ AWS ↔ Neo4j connectivity is private (PrivateLink/VPC endpoints) for Confidential+ data; storage integrations use scoped roles
- [ ] AI-26 Deletion at the source propagates to vector indexes, graphs, caches and memory within a defined time

## Prompt injection, output handling and agency
- [ ] AI-30 Guardrails applied to user input, retrieved content, tool outputs and model output *(foundation for policy definitions)*
- [ ] AI-31 Model output treated as untrusted: validated against schemas; parameterised before reaching SQL, Cypher, shells or HTML
- [ ] AI-32 Generated SQL/Cypher runs under read-only, least-privilege roles with timeouts, row limits and cost caps
- [ ] AI-33 Agent tools classified as read / reversible write / irreversible write; irreversible writes need explicit human confirmation
- [ ] AI-34 Tools act on behalf of the user with delegated, scoped credentials; no shared super-user service accounts
- [ ] AI-35 MCP servers and third-party tools allow-listed, version-pinned, isolated and egress-controlled
- [ ] AI-36 Agent memory scoped per user/tenant with retention limits

## Evaluation and change
- [ ] AI-40 Golden evaluation set exists, owned by the business, covering quality, safety and entitlement cases
- [ ] AI-41 Prompts, model IDs, retrieval and chunking config are versioned configuration, promoted through environments
- [ ] AI-42 CI gate blocks merges on evaluation regression; results kept as release evidence
- [ ] AI-43 Production quality monitored (online sampling, feedback, override/escalation rates) with alerting

## Logging and accountability
- [ ] AI-50 Model invocation logging enabled to the log archive; prompt/response retention and redaction decided *(foundation)*
- [ ] AI-51 Traces link user identity → model calls → retrievals → tool calls → actions
- [ ] AI-52 Consequential automated decisions: human oversight, rationale and model/prompt versions recorded per decision, contestability process defined
