# API Pattern Scoring Sheet: <API name>

Use this sheet to compare candidate [API patterns](../api-patterns/README.md) for one problem. It puts the method in the [decision framework §0.8](../api-patterns/00-decision-framework.md#08-evaluating-suitability-for-a-specific-problem) into practice. Its results feed the [API pattern selection record](api-pattern-selection.md). The structure matches the [AI pattern scoring sheet](ai-pattern-scoring-sheet.md), with criteria weighted towards security, authentication and ease of integration.

| Field | Value |
|---|---|
| API / owner | |
| Date / version | |
| Candidate patterns | (2–4; always include the lightest plausible pattern) |
| Weight profile | Default / Sensitive / Public product / Internal platform |
| Scored by | (at least the solution architect and security architect; a consumer representative for integration ease) |

---

## Stage 0: Problem profile

| Attribute | Rating | Evidence / notes |
|---|---|---|
| Classification | OFFICIAL / OFFICIAL-SENSITIVE | |
| Consumer types (users, internal services, partners, public developers) | | |
| Exposure | Private / Partner / Public | |
| Required authentication assurance (per consumer type) | L1 / L2 / L3 / L4 | |
| Required authorisation granularity | Coarse / Fine / Field-level | |
| Protocols | REST / GraphQL / WebSocket / gRPC / events / TCP | |
| Service level tier | SL0–SL3 | |
| Residency constraint | | |
| Budget band and volume (today, and at 10×) | | |
| Team complexity capacity | C1–C4 | |
| Integration target (time to first successful call) | | |

---

## Stage 1: Gates (pass / fail)

A **fail on any gate eliminates the candidate**, unless the design is changed so that the gate passes. A gate is never converted into a score.

| Gate | Pass when… | Cand. A | Cand. B | Cand. C |
|---|---|---|---|---|
| G1 Classification baseline | The pattern can meet every control in the [§0.4 baseline](../api-patterns/00-decision-framework.md#04-data-classification-official-and-official-sensitive) for the classification | | | |
| G2 Authentication assurance | The pattern's max assurance ≥ the required L-level for **every** consumer type, natively or with the stated additions | | | |
| G3 Exposure | The pattern supports where the consumers are (private / partner / public) | | | |
| G4 Service level and residency | Composite availability (including IdP) meets the tier; SL3 has a residency decision | | | |
| G5 Fixed floor | The fixed floor at the required service level fits the budget band | | | |
| G6 Protocol | The pattern carries the required protocols | | | |
| G7 Operability | The team can build and run the complexity level (or funded support is in the plan), including on-call for SL2+ | | | |

---

## Stage 2: Weighted fit

Score each surviving candidate **1–5 for fit to this problem** (5 = best), with evidence.

### Criteria, anchors and weight profiles

| # | Criterion | 1 (poor fit) | 3 (adequate) | 5 (strong fit) | Default | Sensitive | Public product | Internal platform |
|---|---|---|---|---|---|---|---|---|
| W1 | **Protocol and consumer fit** | Protocol or consumer model mismatched | Fits with workarounds | Designed for exactly these consumers and protocols | 10 | 10 | 15 | 15 |
| W2 | **Authentication assurance headroom** | Required level reached only through non-native workarounds | Required level met natively | Exceeds the required level natively | 15 | 25 | 10 | 10 |
| W3 | **Authorisation granularity fit** | Coarser than needed | Required granularity with custom code | Required granularity supported natively and testably | 10 | 15 | 5 | 10 |
| W4 | **Integration ease** | Time to first call > 4 weeks, or bespoke mechanisms | 1–4 weeks; standard with some friction | < 1 week; self-service onboarding | 15 | 5 | 25 | 15 |
| W5 | **Service level headroom** | Only just meets the tier; no degraded mode | Meets the tier with a tested degraded mode | Exceeds the tier; failure modes understood | 10 | 10 | 15 | 10 |
| W6 | **Unit cost and elasticity** | Exceeds the band at target volume | Within the band today; tight at 10× | Comfortably within the band at 10× | 10 | 5 | 10 | 10 |
| W7 | **Complexity against team capacity** | ≥ 2 levels above capacity | 1 level above, with funded support | At or below capacity | 10 | 5 | 5 | 15 |
| W8 | **Auditability** | Caller identity not attributable | Access logs with caller identity | Per-record audit and authorisation decision logs | 5 | 15 | 5 | 5 |
| W9 | **Lock-in / exit cost** | High, with no mitigation | Medium, or High with mitigations | Low | 5 | 5 | 0 | 5 |
| W10 | **Change and versioning** | Breaking changes hard to avoid or coordinate | Versioning possible with effort | Native versioning, canaries and deprecation signalling | 5 | 5 | 10 | 5 |
| W11 | **Time to value** | Beyond the business deadline | Meets the deadline with little slack | Well within the deadline | 5 | 0 | 0 | 0 |
| | **Total weight** | | | | **100** | **100** | **100** | **100** |

Choose the profile: **Sensitive** for OFFICIAL-SENSITIVE data; **Public product** for APIs whose success depends on developer adoption; **Internal platform** for service-to-service APIs inside the organisation. Record a reason for any change to the weights.

### Scores

| # | Criterion | Weight | Cand. A score | Evidence | Cand. B score | Evidence | Cand. C score | Evidence |
|---|---|---|---|---|---|---|---|---|
| W1 | Protocol and consumer fit | | | | | | | |
| W2 | Authentication assurance headroom | | | | | | | |
| W3 | Authorisation granularity fit | | | | | | | |
| W4 | Integration ease | | | | | | | |
| W5 | Service level headroom | | | | | | | |
| W6 | Unit cost and elasticity | | | | | | | |
| W7 | Complexity against team capacity | | | | | | | |
| W8 | Auditability | | | | | | | |
| W9 | Lock-in / exit cost | | | | | | | |
| W10 | Change and versioning | | | | | | | |
| W11 | Time to value | | | | | | | |
| | **Weighted score** (Σ weight × score ÷ 5, range 20–100) | | | | | | | |

### Interpretation rules

- **≥ 75: strong fit.** 60–74: acceptable, with mitigations recorded. < 60: poor fit.
- **Assurance floor:** for OFFICIAL-SENSITIVE data, a candidate with W2 ≤ 2 cannot be selected. The required assurance must be met natively, not through workarounds.
- **Integration cap:** for Partner or Public exposure, a candidate with W4 ≤ 2 can be selected only if Stage 3 shows a pilot consumer reaching a first successful call within the integration target.
- **Low-score rule:** any score of 1 on a criterion weighted ≥ 10 needs a mitigation or an explicit acceptance in the selection record.
- **Close calls:** scores within 5 points are a tie. Decide on Stage 3 evidence, and prefer the lower-complexity candidate.

---

## Stage 3: Validation

| Check | Target | Cand. A | Cand. B |
|---|---|---|---|
| Pilot consumer onboarding: time to first successful call | | | |
| Load test at 2× expected peak: p99 latency and error rate | | | |
| Negative authentication tests (expired, wrong audience, wrong issuer, replayed or unbound credential) | All rejected | | |
| Negative authorisation tests (OWASP API1/API3/API5: other callers' records, extra properties, admin functions) | All rejected | | |
| Rate limiting and resource consumption (API4) | 429s as designed; no back-end saturation | | |
| Failover / AZ-loss game day (and Region failover for A11) | Within RTO; no data loss beyond RPO | | |
| Credential or certificate rotation without downtime | Passes | | |

**Decision:** <pattern(s)>, because <evidence>. Record it in the [selection record](api-pattern-selection.md).

---

## Stage 4: Post-implementation review (3–6 months after go-live)

| Measure | Selection-time estimate | Actual | Variance → action |
|---|---|---|---|
| Availability / p99 latency | | | |
| Unit cost per million requests; fixed floor | | | |
| Time to first successful call (median across new consumers) | | | |
| Auth failure and 429 rates | | | |
| Security findings (pen test, incidents) | | | |

Where actual results differ materially from the published pattern ratings, raise a change to the pattern document.

---

## Worked example (illustrative)

**Problem:** an eligibility-check API for **partner local authorities**. Councils' case-management systems query a department's benefits data about their own residents.

| Attribute | Rating |
|---|---|
| Classification | OFFICIAL-SENSITIVE (personal data) |
| Consumers | Partner organisations (about 150 councils, systems outside AWS) |
| Required authentication | L3 minimum |
| Required authorisation | Fine (each council sees only its own residents) |
| Protocol | REST |
| Service level, budget, team | SL2, B2, team C2 with platform support available |
| Integration target | First successful call within 10 working days of approval |

**Candidates:** A02 Managed API product, A06 mTLS B2B, A03 Private API.

**Gates:** **A03 fails G3**: partner systems are outside the organisation and cannot use organisation-scoped private endpoints. A02 passes G2 only with the mTLS and certificate-binding additions (L3). A06 passes all gates.

**Weighted fit (Sensitive profile):**

| # | Criterion | Wt | A02 | Evidence | A06 | Evidence |
|---|---|---|---|---|---|---|
| W1 | Protocol and consumer fit | 10 | 5 | REST for partner systems | 5 | Designed for partner system integration |
| W2 | Auth assurance headroom | 25 | 3 | L3 met with mTLS + binding added | 5 | L4 natively: mTLS, bound tokens, registry, allow-list |
| W3 | Authorisation granularity | 15 | 4 | Verified Permissions; partitions in code | 5 | Registry defines per-council data partitions |
| W4 | Integration ease | 5 | 5 | Portal, OAuth, self-service | 2 | Certificate onboarding per council |
| W5 | Service level headroom | 10 | 4 | Multi-AZ; tested degraded mode | 4 | Same, plus certificate expiry alarms |
| W6 | Unit cost and elasticity | 5 | 4 | No CA floor | 3 | Private CA floor |
| W7 | Complexity against team | 5 | 4 | C2 | 3 | C3 with platform support |
| W8 | Auditability | 15 | 3 | Access logs; per-record audit to build | 5 | Certificate, client and payload hash in audit trail |
| W9 | Lock-in | 5 | 3 | Usage plans and authoriser wiring | 3 | Registry and authoriser are custom |
| W10 | Change and versioning | 5 | 4 | Stages, canaries | 3 | Partner change windows slow evolution |
| W11 | Time to value | 0 | 4 | — | 2 | — |
| | **Weighted score** | | **74** | | **87** | |

**Reading the result:** A06 is a strong fit (87), but **W4 = 2 triggers the integration cap**. In the Stage 3 pilot with three councils (illustrative figures):
- The median time to first successful call was 6 working days (target 10) with an onboarding kit and sandbox.
- A valid token presented with another council's certificate was rejected with 403.
- Cross-council record requests were rejected.
- A load test at 2× peak gave p99 280 ms.

The cap is lifted.

**Decision:** A06, with bulk overnight submissions through **A08**. Mitigations recorded:

- W4: onboarding kit, sandbox and a portal for documentation.
- W6: a short-lived-certificate CA mode was evaluated to reduce the PKI floor.
- W10: a 12-month deprecation notice period agreed with partners.
