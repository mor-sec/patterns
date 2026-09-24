# 0. Decision Framework: Budget, Complexity and Service Levels

Every pattern in this series is scored on the same four dimensions, so that patterns can be compared and a design can be challenged in a consistent way at review. This chapter defines those dimensions, the cost model for AI workloads, and the role that each platform (AWS, Snowflake, Neo4j) is expected to play.

> **Figures are indicative.** Cost bands are order-of-magnitude run-rate figures for planning and challenge, not quotes. Model prices, service tiers and quotas change often. Before a budget is committed, validate it with the AWS Pricing Calculator, the Snowflake credit consumption table and the Neo4j Aura price list.

---

## 0.1 Budget bands (monthly run cost, excluding people)

| Band | Monthly run cost | Typical situation |
|---|---|---|
| **B1: Experiment** | < $1k | Prototype, proof of value, a single team, a small user base, usually pay-per-use only |
| **B2: Departmental** | $1k – $10k | Production for one business unit. Modest volumes, and a few fixed-cost components are acceptable |
| **B3: Business-critical** | $10k – $50k | Organisation-wide or customer-facing. Provisioned capacity and redundancy are justified |
| **B4: Enterprise-scale** | > $50k | High-volume, multi-region, or self-hosted models. Needs a FinOps owner and unit-cost targets |

Always state a budget as two numbers:

1. **Fixed floor.** This is what the solution costs at zero traffic. It covers always-on search clusters, graph databases, provisioned throughput, NAT gateways, running warehouses and GPU endpoints. **The floor decides whether a pattern fits B1 or B2.**
2. **Unit cost.** This is the cost per business transaction (per question answered, per document processed, per case resolved). **Unit cost decides whether the solution stays viable as it scales.**

### Cost model for generative AI requests

```
cost per transaction =
    Σ over model calls [ (input tokens × input price) + (output tokens × output price) ]
  + retrieval cost (vector/graph/search queries)
  + orchestration cost (Lambda / Step Functions / AgentCore / containers)
  + guardrail and evaluation cost (per text unit / per judged sample)
  + amortised fixed floor ÷ transactions
```

Agents and multi-step chains multiply the first term. A single "question" can mean 5 to 30 model calls, and the context re-sent on each call often makes input tokens the dominant cost. Estimate **calls per transaction** explicitly.

### Cost levers (from highest to lowest typical impact)

| Lever | Typical effect | Applies to |
|---|---|---|
| **Model tiering / routing.** Use the smallest model that passes the evaluation suite, and escalate only on hard cases | 3–20× on the model line | All patterns |
| **Batch inference** (Bedrock batch jobs) instead of on-demand | Discounted (commonly ~50%) for non-interactive work | P02, P03, offline evaluation |
| **Service tier selection.** Bedrock *Flex* for latency-tolerant jobs; *Priority* only where an SLO needs it | Discount or premium relative to Standard | P02, P07, P08 |
| **Prompt caching** of stable system prompts, tool definitions and documents | Large reduction on repeated input tokens, plus lower latency | P04–P09 |
| **Context discipline.** Retrieve fewer, better chunks, rerank, and summarise conversation history | Proportional to the tokens removed | RAG and agents |
| **Semantic / exact response caching** | Removes calls entirely for repeated questions | High-volume Q&A (P04, P05, P09) |
| **Scale-to-zero components** (Lambda, S3 Vectors, OpenSearch Serverless NextGen, Snowflake auto-suspend, Aura pause) | Removes the fixed floor | B1/B2 |
| **Provisioned throughput / self-hosting** | Cheaper *only* above a sustained utilisation break-even | P10, and B4 variants of others |

---

## 0.2 Complexity levels

Complexity is the **build and run burden**: the number of components, the skills needed, the operational toil, and the number of ways the system can fail.

| Level | Team profile | Components | Typical time to first production release |
|---|---|---|---|
| **C1: Low** | 1–2 generalist engineers | Managed services only, one model, no custom retrieval | 2–6 weeks |
| **C2: Moderate** | Small product team with an AI-literate engineer | Managed retrieval, a pipeline, an evaluation harness | 1–3 months |
| **C3: High** | Product team plus data/ML engineering support | Custom retrieval, multiple stores, orchestration, CI for prompts and evaluation | 3–6 months |
| **C4: Very high** | Dedicated platform / ML team, an on-call rotation | Self-hosted models, multi-region, custom training, agents with write access to systems of record | 6+ months |

**Rule of thumb:** pick the lowest complexity level that meets the service level and quality targets. Every level added roughly doubles the evaluation and operational surface.

---

## 0.3 Service level tiers

AI systems need **quality**, **freshness** and **cost** objectives as well as the classic availability and latency objectives. A system that is "up" but confidently wrong has failed its SLO.

| Tier | Availability (monthly) | Latency objective | RTO / RPO | Quality objective | Typical architecture implications |
|---|---|---|---|---|---|
| **SL0: Best effort** | None | None | Rebuildable | Spot-checked | Prototype. Single AZ acceptable. No on-call |
| **SL1: Bronze** | 99.0% | p95 end-to-end < 30 s (async OK) | 24 h / 24 h | Offline evaluation passes before release | Single region, managed services, on-demand model access, business-hours support |
| **SL2: Silver** | 99.5 – 99.9% | Interactive: time-to-first-token (TTFT) p95 < 2–3 s, complete p95 < 15 s | 4 h / 1 h | Offline evaluation plus online sampling of production traffic, with alerting on regression | Multi-AZ everything. Cross-region inference profiles. Retries with fallback model. Quotas raised in advance |
| **SL3: Gold** | ≥ 99.95% | TTFT p95 < 1 s, complete p95 < 5–8 s | < 1 h / ≤ 15 min | Continuous evaluation, canary releases for prompt and model changes, human review queue | Multi-region (active/standby or active/active). Provisioned or Priority-tier capacity. Graceful degradation mode. 24×7 on-call |

### Composite availability

A request path is only as available as the **product** of its serial dependencies. For example, with assumed figures: API edge 99.95% × compute 99.95% × vector store 99.9% × model endpoint 99.9% × graph DB 99.9% ≈ **99.55%**. That falls short of SL3 unless you add redundancy or degraded modes. Record the real SLA of each dependency at review time.

Techniques that raise composite availability, roughly from cheapest to most expensive:

1. **Retries with jittered back-off**, plus a **fallback model**. A different model family or a different Region's inference profile reduces correlated failure.
2. **Cross-region inference profiles** in Bedrock, which absorb regional capacity pressure. Confirm that data residency permits the Regions in the profile.
3. **Graceful degradation.** Return search results without generation, return cached answers, or queue the request and notify later.
4. **Decoupling with queues**, so the interactive path does not depend on ingestion or enrichment.
5. **Multi-region deployment** of stateless tiers, and replication of stores. This is expensive for graph and vector stores.
6. **Provisioned throughput or the Priority tier** to protect latency under contention.

### AI-specific SLIs to define for every pattern

| SLI | Definition |
|---|---|
| TTFT | Time from request to the first streamed token (interactive patterns) |
| End-to-end latency | Request to complete response or task completion |
| Groundedness / faithfulness | % of sampled answers fully supported by the retrieved context |
| Answer correctness / task success | % correct against a golden set, or human-rated |
| Refusal / guardrail intervention rate | % of requests blocked or refused (both too high and too low are signals) |
| Freshness | Age of the newest source document reflected in the index or graph |
| Cost per transaction | As defined in §0.1, tracked against a target |
| Throttle rate | % of model calls that received throttling errors (an early capacity warning) |

---

## 0.4 Data classification and residency

Data classification moves a pattern up the complexity and cost scales. See [scope and principles](../docs/01-scope-and-principles.md).

| Classification | Minimum expectations for AI patterns |
|---|---|
| Public / Internal | Managed model access, standard logging, guardrails for abuse |
| Confidential | Private connectivity (VPC endpoints / PrivateLink) to Bedrock, Snowflake and Neo4j. KMS customer-managed keys. Prompt/response logging with redaction. Document-level access control enforced **at retrieval time**. The Regions in any cross-region inference profile checked against residency requirements |
| Restricted / Regulated | All of the above, plus: an explicit model/provider approval, no data leaving the approved jurisdiction, human-in-the-loop for consequential decisions, an audit trail of the prompts, context and outputs used for each decision, and a documented evaluation of bias and error rates |

---

## 0.5 Platform roles

### AWS (primary platform)

AWS hosts the **runtime path**: user-facing APIs, orchestration, model access, retrieval stores, agents, observability and security controls. The default building blocks are:

| Concern | Default | Alternatives |
|---|---|---|
| Model access | Amazon Bedrock (Converse API, cross-region inference profiles, service tiers, batch inference, prompt caching) | SageMaker AI endpoints for self-hosted/fine-tuned models; Bedrock Custom Model Import |
| Safety controls | Bedrock Guardrails (content filters, denied topics, PII redaction, contextual grounding checks) | Custom classifiers on SageMaker; model-native safety |
| Managed RAG | Bedrock Knowledge Bases | Custom pipeline (P05) |
| Vector store | S3 Vectors (lowest floor); OpenSearch Serverless (hybrid lexical+vector, low latency) | Aurora PostgreSQL pgvector; Neo4j vector index; OpenSearch managed domains |
| Agents | Bedrock AgentCore (Runtime, Gateway, Identity, Memory, Observability) | Step Functions-orchestrated tool calls; containerised agent frameworks on ECS/EKS |
| Orchestration | Step Functions, EventBridge, SQS | MWAA (Airflow) for data-heavy DAGs |
| Compute | Lambda; ECS Fargate for long-running or streaming | EKS where a platform team already runs it |
| Edge / API | API Gateway or ALB, with AWS WAF and CloudFront | AppSync for GraphQL/real-time |
| Observability | CloudWatch (including generative AI observability), X-Ray / OpenTelemetry, Bedrock model invocation logging to S3 | Third-party LLM observability tooling, if approved |

### Snowflake (data pipeline and prototyping, optional)

Use Snowflake where the **data already lives in it** and the consumers are analysts or data products:

- **Pipelines.** Snowpipe/Snowpipe Streaming from S3, Dynamic Tables, Streams and Tasks for curated, governed data feeding AI.
- **In-warehouse AI.** Cortex AI SQL functions (for example `AI_COMPLETE`, `AI_CLASSIFY`, `AI_EXTRACT`, summarisation and embeddings) for batch enrichment and prototyping without moving data.
- **Retrieval and analytics agents.** Cortex Search (managed hybrid search), Cortex Analyst (text-to-SQL over semantic views), Cortex Agents / Snowflake Intelligence.
- **Prototype front ends.** Streamlit in Snowflake.
- **Governance.** Row access and masking policies, object tagging and lineage. These controls are applied *before* data leaves for AWS runtime stores.

Snowflake is **not required**. Every pattern includes an AWS-only variant: S3 + Glue/Athena + Iceberg tables, with Bedrock in place of Cortex. Where both are used, prefer **Apache Iceberg tables on S3** as the hand-off format so that neither platform locks data in. Connect Snowflake to AWS over **AWS PrivateLink** for Confidential data and above.

Decide based on **where the data gravity is**. Moving large volumes out of Snowflake to embed them in AWS costs egress, duplicate storage and two governance models. Calling Cortex from an AWS-hosted user experience costs an extra network hop and a second availability dependency.

### Neo4j (knowledge graph, optional)

Use Neo4j only when **relationships are the answer**, not merely a route to it:

- Multi-hop questions ("which suppliers of components used in product X are exposed to sanctions list Y?").
- Entity resolution, lineage, dependency, network and fraud analysis.
- Explainable retrieval, where the path through the graph is itself evidence.
- Constraining agents to a governed ontology of entities and permitted actions.

Deployment options on AWS:

| Option | When | Service level / budget notes |
|---|---|---|
| **Neo4j AuraDB Free / Professional** (hosted in an AWS Region) | Prototype and B1–B2 | Lowest effort. Check the tier's features for private networking and SLA |
| **Neo4j AuraDB Business Critical / Virtual Dedicated Cloud** | SL2–SL3 production | Clustered, SLA-backed, private connectivity; a higher fixed floor |
| **Neo4j Enterprise, self-managed** on EC2/EKS (AWS Marketplace) | Strict residency, custom topology, very large graphs | C3–C4. You own clustering, backups, patching and upgrades |
| **Amazon Neptune / Neptune Analytics** (AWS-native alternative) | When Neo4j-specific features (Cypher ecosystem, GDS library, existing models) are not needed; Bedrock Knowledge Bases GraphRAG uses Neptune Analytics as a fully managed option | Tighter AWS integration; different query languages and feature set |

**Do not add a graph** when the questions are single-hop lookups, when the data has no stable entities, or when nobody will own the ontology. An unmaintained knowledge graph decays faster than a vector index.

---

## 0.6 Suitability dimensions

Budget, complexity and service level describe what a pattern **costs** to build and run. They do not tell you whether it **suits the problem**. The ten dimensions below do. Each pattern publishes a rating for every dimension on its summary card, and the [scoring sheet](../templates/ai-pattern-scoring-sheet.md) compares that rating with the needs of the problem.

Some dimensions describe the **pattern's demand**: what it needs in order to work. Others describe the **problem's supply**: what actually exists. **Suitability is the gap between the two**, not the pattern's absolute rating.

### 0.6.1 Consequence of error (severity × reversibility)

This dimension decides **how much autonomy is acceptable**. Rate the problem first, then check that the pattern supports that level.

| Level | Description | Examples | Autonomy guidance |
|---|---|---|---|
| **E1: Low** | Cosmetic or easily ignored; the user notices and corrects it | Draft suggestions, internal summaries, tagging for search | Full automation acceptable |
| **E2: Moderate** | Reversible with effort; internal impact | Ticket routing, internal Q&A, knowledge article drafts | Automation with sampling and a feedback loop |
| **E3: High** | Financial, customer-facing or regulatory impact; hard to reverse | Customer communications, payments exceptions, compliance answers, access decisions | AI recommends, and a human or deterministic policy decides. Autonomy bands are widened only with evidence |
| **E4: Critical** | Legal effects on individuals, safety, or irreversible harm | Credit or eligibility decisions, fraud blocks on customers, clinical or safety advice | A testable, measurable decision model (P11) or a human decides. Generative output is assistive only. Full audit trail and contestability |

The **pattern rating** is the highest level the pattern supports, and the controls it needs to do so.

### 0.6.2 Data readiness

This is the most common cause of AI project failure. Each pattern declares its **prerequisites** (its demand). The problem is rated on whether each prerequisite exists (its supply).

| Supply rating | Meaning |
|---|---|
| **Ready** | Exists, is owned, is of known quality and is governed (classified, access-controlled) |
| **Partial** | Exists but needs curation, labelling, metadata or ownership, with a funded plan to fix this in the delivery timeline |
| **Absent** | Does not exist, or no one owns it. **This is a gate failure** for any pattern that depends on it |

Typical prerequisites: curated documents with owners and ACL metadata (P04/P05); master data and an ontology owner (P06); agreed metric definitions and a semantic model (P09); labelled outcome history (P10/P11); documented tool APIs and permission models (P08); process definitions and historical cases (P07).

### 0.6.3 Evaluability

*Can "correct" be measured?* If it cannot, the quality SLOs in §0.3 are fiction.

| Rating | Meaning | Typical |
|---|---|---|
| **High** | Ground truth is available or cheap to create; exact or near-exact scoring | Extraction, classification, text-to-SQL (result match), ML scoring |
| **Medium** | Reference answers can be written; judged with rubrics or LLM-as-judge plus human calibration | Document Q&A, summarisation, multi-hop graph Q&A |
| **Low** | Many valid outcomes; success depends on the path taken; needs scenario-based and human evaluation | Open-ended agents, research assistants, creative generation |

A low rating does not rule a pattern out, but it **adds evaluation effort** (scenario suites, human review panels) to the plan. It can also be a reason to choose a more constrained pattern.

### 0.6.4 Cost elasticity

*How does the cost per transaction behave at 10× and 100× volume?*

| Rating | Meaning | Typical |
|---|---|---|
| **Sub-linear** | Unit cost falls with volume (the fixed platform is amortised, cache hit rates rise, dedicated capacity is better utilised) | P05, P06 serving, P10 at high utilisation, P11 |
| **Linear** | Unit cost is roughly constant; total cost tracks volume | P01, P02, P04, P07, P09 |
| **Super-linear** | Unit cost rises with task complexity or usage depth (context accumulates per step; longer sessions) | P08 agents |

Model the budget at **today's volume and at 10×**. A pattern that fits the band today but is super-linear needs hard per-task limits or a planned move to a codified workflow (P07).

### 0.6.5 Lock-in and exit cost

*How hard is it to change the model, platform or vendor later?* Model releases and pricing change every few months, so this is a real, recurring risk.

| Rating | Meaning |
|---|---|
| **Low** | Open formats and standard interfaces (Converse API, Iceberg, OpenSearch, MCP, open weights); the move is mostly configuration and re-evaluation |
| **Medium** | Some managed-service configuration to rebuild (Knowledge Base setup, AgentCore specifics); the data remains portable |
| **High** | Logic encoded in platform-specific constructs (Cortex functions and semantic views, proprietary query languages, non-exportable customised models); a rebuild is needed |

**Mitigations:** Iceberg for data hand-off, the Converse API or an internal gateway for model access, versioned prompts and evaluation sets owned outside the platform, and GQL/openCypher-compatible query patterns.

### 0.6.6 Explainability and auditability

*Can we show why an output was produced, to a user, an auditor or a regulator?*

| Rating | Meaning | Typical |
|---|---|---|
| **High** | Structured evidence: graph paths, generated SQL, feature attributions, step-level audit of the decisions made | P06, P07, P09, P11 |
| **Medium** | Cited sources; traceable inputs and outputs | P02, P03, P04, P05 |
| **Low** | Free-form reasoning; traces exist, but the model's stated rationale may not be faithful | P01, P08, P10 |

### 0.6.7 Regulatory profile

Usually a **gate** rather than a weighted score. Confirm with legal and compliance. The EU AI Act categories are used here as a reference model; map them to local equivalents.

| Level | Description | Implications |
|---|---|---|
| **R0: Minimal** | No specific AI obligations beyond general law | Standard controls |
| **R1: Transparency** | Users interact with AI or receive AI-generated content | Disclosure to users, content labelling |
| **R2: High-risk / consequential** | Decisions about individuals in areas such as credit, employment, essential services or insurance; automated decisions with legal or similarly significant effects; model risk management regimes | Human oversight, logging, documented accuracy and bias testing, data governance, contestability. Raises complexity and the SAR tier |
| **R3: Prohibited** | Uses banned by regulation or policy | Do not build |

The pattern rating is the highest level the pattern can support, and the controls needed to support it.

### 0.6.8 Model-change sensitivity

*How much breaks when a model is upgraded, deprecated or re-priced?*

| Rating | Meaning |
|---|---|
| **Low** | Narrow, schema-constrained steps; the evaluation harness catches regressions; fallback models are interchangeable |
| **Medium** | Prompt-tuned behaviour or derived data (extractions, graphs) that must be re-validated or reprocessed |
| **High** | Emergent multi-step behaviour (agents) or a self-owned model lifecycle; upgrades need full re-evaluation and often redesign |

This rating drives the **ongoing cost of ownership**. Budget for re-evaluation at every model change.

### 0.6.9 Human review demand

*Does the design depend on people reviewing, approving or curating? Is there capacity?*

| Rating | Meaning |
|---|---|
| **None/Low** | Occasional sampling and feedback only |
| **Medium** | Queues for low-confidence items, curation or confirmations |
| **High** | Approval of a large share of outputs is part of the control design |

Check capacity: expected queue volume × handling time must be less than the available reviewer hours, with headroom for peaks. Otherwise the control fails in practice: queues back up, or reviewers rubber-stamp.

### 0.6.10 Value measurability

*Can the business outcome be measured, so that the budget band is justified?* Each pattern lists its typical value metrics (time saved, straight-through rate, deflection, loss prevented). The problem is rated on whether a **baseline** exists and whether the metric can be captured **in production**.

| Rating | Meaning |
|---|---|
| **High** | A baseline exists; the metric can be instrumented automatically |
| **Medium** | A baseline can be sampled; the metric needs surveys or manual measurement |
| **Low** | No baseline; the benefit is qualitative only. Fund a measurement plan, or treat the work as an experiment (B1 only) |

---

## 0.7 How a pattern is scored

Each pattern opens with a summary card that has two parts.

**Cost and delivery profile**

| Dimension | Meaning |
|---|---|
| **Budget band** | The usual range, and the fixed floor |
| **Complexity** | C1–C4 |
| **Service level fit** | The highest tier achievable without changing to another pattern |
| **Time to first value** | To a demonstrable production pilot |
| **Snowflake role** | None / optional / central |
| **Neo4j role** | None / optional / central |
| **SAR tier** | The typical review tier (see [review workflow](../docs/02-review-workflow.md)) |

**Suitability profile** (§0.6)

| Dimension | Meaning |
|---|---|
| **Max consequence of error** | The highest E-level supported, and the conditions for it |
| **Data prerequisites** | What must exist (the pattern's demand) |
| **Evaluability** | High / Medium / Low |
| **Cost elasticity** | Sub-linear / Linear / Super-linear |
| **Lock-in / exit cost** | Low / Medium / High |
| **Explainability** | High / Medium / Low |
| **Regulatory fit** | The highest R-level supportable, and the conditions for it |
| **Model-change sensitivity** | Low / Medium / High |
| **Human review demand** | None/Low / Medium / High |
| **Typical value metrics** | What to measure to prove value |

The [catalogue](README.md#suitability-profile-at-a-glance) shows every pattern's suitability profile side by side.

---

## 0.8 Evaluating suitability for a specific problem

Use the [AI pattern scoring sheet](../templates/ai-pattern-scoring-sheet.md), or its Excel workbook [ai-pattern-scoring.xlsx](../templates/ai-pattern-scoring.xlsx), which computes the scores and applies the rules automatically. The method has four stages:

1. **Gates (pass/fail).** Hard constraints eliminate patterns: classification and residency, service level feasibility, consequence of error, regulatory profile, the fixed floor against the budget, data prerequisites, and the team's capacity to operate the pattern. **Never average a gate into a score**, because a veto hidden in an average is how unsuitable designs get approved.
2. **Weighted fit (1–5 per criterion).** Score how well each surviving pattern fits *this problem*, using a weight profile that suits the context (default, regulated, customer-facing at scale, or prototype).
3. **Validate the top two.** Run a time-boxed bake-off on the golden set (quality, cost per transaction at the target volume, p95 latency). Test **quality attribute scenarios** (for example "primary-Region model throttling at peak → users still get cited search results within 3 s"). Where P06 is proposed, include a multi-hop set that shows vector RAG failing.
4. **Close the loop.** At the post-implementation review (3–6 months after go-live), compare actual unit cost, service levels, quality and override rates with the selection record. Feed any differences back into the pattern's published ratings.
