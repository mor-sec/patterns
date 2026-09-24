# Security Architecture Review Record

| Field | Value |
|---|---|
| SAR reference | SAR-YYYY-NNN |
| System / change | |
| Tier | 1 / 2 / 3 (with rationale) |
| Risk owner | |
| Delivery lead | |
| Security architect | |
| Decision authority | |
| Review dates (start → decision) | |
| Status | Draft / In review / Decided / Closed (handed over) |

## 1. Executive summary

*Three to six sentences written for the risk owner: what the system is, the overall residual risk position, the recommendation, and the key conditions.*

**Recommendation:** Approved / Approved with conditions / Not approved

| Residual risk | Count |
|---|---|
| Critical | |
| High | |
| Medium | |
| Low | |

## 2. Scope

- **In scope:**
- **Out of scope:**
- **Inherited controls relied on** (with platform SAR references):

## 3. Context

- Business purpose:
- Data inventory and classification (or link):
- Impact profile, C / I / A:
- Applicable risk appetite:
- Regulatory drivers:

## 4. Architecture summary

*Link or embed diagrams: context, component/DFD, network, identity, and delivery pipeline.*

## 5. Threat model

Link to the [threat model](threat-model.md) and summarise its key threats.

## 6. Assessment by domain

Rate each domain: ✅ Meets / ⚠️ Partially meets / ❌ Does not meet / ➖ N/A or inherited.

| Domain | Rating | Summary | Findings |
|---|---|---|---|
| 4.1 Shared responsibility and service selection | | | |
| 4.2 Tenancy, landing zone and blast radius | | | |
| 4.3 Identity and access | | | |
| 4.4 Network and exposure | | | |
| 4.5 Data protection and keys | | | |
| 4.6 Secrets management | | | |
| 4.7 Compute and workload isolation | | | |
| 4.8 Application and API edge | | | |
| 4.9 Logging and detection by design | | | |
| 4.10 Resilience and recoverability | | | |
| 4.11 Third parties and SaaS | | | |
| 4.12 Compliance and residency | | | |
| 5.0 Source control | | | |
| 5.1 Infrastructure as code | | | |
| 5.2 Build and supply chain | | | |
| 5.3 Configuration | | | |

**DLC maturity (§5.4):** Current level ___ / target level ___

## 7. Findings and risks

Full detail lives in the [risk register](risk-register.csv). Summarise High and Critical items here.

| ID | Finding | Risk statement | Residual | Treatment | Owner | Due / milestone |
|---|---|---|---|---|---|---|
| F-01 | | | | | | |

## 8. Conditions of approval

| # | Condition | Must be met before | Verified by | Status |
|---|---|---|---|---|
| C-1 | | Production go-live | | Open |

## 9. Security architecture decisions

List ADRs raised or referenced during the review.

## 10. Handover to operational security

| Item | Design provides | Operational security to operate | Acknowledged |
|---|---|---|---|
| Control-plane audit logs | Org trail → log archive, 1 year hot / 7 years cold | Detection use cases for the prod deploy role | |
| Data-plane logs | | | |
| CSPM / IaC / image findings | | Triage ownership | |
| Break-glass | | Custody, testing, alert response | |
| Privileged roles | | Recertification (quarterly) | |
| Key rotation | | Rotation monitoring | |
| Drift detection | | Finding triage | |
| Penetration test | Scope: ___ | Schedule before / after go-live | |
| Accepted risks | Refs, with expiry dates | Expiry tracking | |

## 11. Re-review triggers

These are the standard triggers from §2.3 Stage 8, plus any specific to this system:

## 12. Sign-off

| Role | Name | Decision | Date |
|---|---|---|---|
| Security architect | | Recommend: | |
| Risk owner | | Acknowledge residual risk | |
| Decision authority (Tier 1) | | | |
| Operational security (handover) | | Acknowledged | |
