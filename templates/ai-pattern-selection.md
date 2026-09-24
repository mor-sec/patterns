# AI Pattern Selection Record: <Solution name>

Complete this during design, and attach it to the SAR [intake](intake-questionnaire.md). Definitions of the budget, complexity and service level terms are in the [decision framework](../ai-patterns/00-decision-framework.md).

| Field | Value |
|---|---|
| Solution / owner | |
| Date / version | |
| SAR reference | |
| Data classification (highest) | Public / Internal / Confidential / Restricted |
| Residency constraints | |

## 1. Problem and users

*What must the AI do? Who uses it? What happens if it is wrong?*

## 2. Targets

| Target | Value |
|---|---|
| Budget band | B1 / B2 / B3 / B4 |
| Fixed floor (monthly) | |
| Expected volume (transactions/month, peak/sec) | |
| Unit cost target (per transaction) | |
| Service level tier | SL0 / SL1 / SL2 / SL3 |
| Availability / latency (TTFT, end-to-end p95) | |
| RTO / RPO | |
| Quality SLI and target (for example groundedness ≥ 95%, task success ≥ 85%) | |
| Freshness SLO | |
| Team complexity capacity | C1 / C2 / C3 / C4 |
| Consequence of error | E1 / E2 / E3 / E4 |
| Regulatory profile | R0 / R1 / R2 (R3 = do not build) |
| Data prerequisites (each: Ready / Partial / Absent) | |
| Reviewer capacity for review queues (hours/week) | |
| Value metric and baseline | |

## 3. Pattern selection

Attach the [scoring sheet](ai-pattern-scoring-sheet.md) when two or more patterns were plausible, or when the SAR tier is 1–2.

| Candidate | Gates (all pass? which failed) | Weighted score (profile) | Bake-off result |
|---|---|---|---|
| | | | |

| Pattern(s) chosen | Why |
|---|---|
| | |

| Lighter pattern(s) considered | Why rejected (evidence) |
|---|---|
| | |

## 4. Platform decisions

| Platform | Used? | Role / justification |
|---|---|---|
| AWS services (list) | Yes | |
| Snowflake | Yes / No | |
| Neo4j (deployment option) | Yes / No | |

## 5. Composite availability and degraded mode

| Serial dependency | SLA / SLO |
|---|---|
| | |
| **Composite** | |

*Degraded mode(s):*

## 6. Cost model

| Line | Fixed / month | Variable (per transaction) | Assumptions |
|---|---|---|---|
| Model tokens (calls × tokens) | | | |
| Retrieval / graph / search | | | |
| Compute / orchestration | | | |
| Guardrails / evaluation | | | |
| Snowflake credits | | | |
| **Total** | | | |

## 7. Accepted weaknesses

*Criteria scored 1 with weight ≥ 10, or a task fit cap overridden by bake-off evidence: the mitigation or acceptance for each.*

## 8. Evolution triggers

*Which metrics will trigger a move to a different pattern (for example "p95 TTFT > 3 s at 500 concurrent users → P05")?*

## 9. Approvals

| Role | Name | Date |
|---|---|---|
| Solution owner | | |
| Security architect | | |
| FinOps / budget holder | | |
