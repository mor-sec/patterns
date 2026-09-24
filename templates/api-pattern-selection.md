# API Pattern Selection Record: <API name>

Complete this during design and attach it to the SAR [intake](intake-questionnaire.md). The terms are defined in the [API decision framework](../api-patterns/00-decision-framework.md).

| Field | Value |
|---|---|
| API / owner | |
| Date / version | |
| SAR reference | |
| Classification | OFFICIAL / OFFICIAL-SENSITIVE |
| Residency constraints | |

## 1. Consumers and purpose

*Who calls the API (users via our apps, internal services, partners, public developers)? What does it do? What happens if it is misused or unavailable?*

## 2. Targets

| Target | Value |
|---|---|
| Exposure | Private / Partner / Public |
| Required authentication assurance per consumer type | L1 / L2 / L3 / L4 |
| Required authorisation granularity | Coarse / Fine / Field-level |
| Protocols | |
| Service level tier | SL0 / SL1 / SL2 / SL3 |
| Availability / p99 latency | |
| RTO / RPO | |
| Budget band; fixed floor; unit cost per million requests | |
| Expected volume (average, peak requests/second) | |
| Integration target (time to first successful call) | |
| Team complexity capacity | C1 / C2 / C3 / C4 |

## 3. Pattern selection

Attach the [scoring sheet](api-pattern-scoring-sheet.md) when two or more patterns were plausible, or when the SAR tier is 1–2.

| Candidate | Gates (all pass? which failed) | Weighted score (profile) | Validation result |
|---|---|---|---|
| | | | |

| Pattern(s) chosen | Why |
|---|---|
| | |

## 4. Authentication and authorisation design

| Consumer type | Credential | Assurance level | Authorisation mechanism | Revocation method |
|---|---|---|---|---|
| | | | | |

## 5. Composite availability and degraded mode

| Serial dependency (incl. IdP, authoriser, DNS, downstreams) | SLA / SLO |
|---|---|
| | |
| **Composite** | |

*Degraded mode(s):*

## 6. Cost model

| Line | Fixed / month | Variable | Assumptions |
|---|---|---|---|
| API front door (requests) | | | |
| Edge (CloudFront, WAF, Shield) | | | |
| Identity (Cognito MAU / M2M, Private CA) | | | |
| Network (endpoints, NAT, Direct Connect, Lattice) | | | |
| Compute and data | | | |
| Logging and monitoring | | | |
| **Total** | | | |

## 7. Accepted weaknesses

*Criteria scored 1 with weight ≥ 10, integration or assurance caps overridden by validation evidence, residency trade-offs: the mitigation or acceptance for each.*

## 8. Evolution triggers

*Which metrics will trigger a move to a different pattern (for example "sustained > 50M requests/day → evaluate A05", "SL3 required → A11 with residency ADR")?*

## 9. Approvals

| Role | Name | Date |
|---|---|---|
| API owner | | |
| Security architect | | |
| Budget holder | | |
