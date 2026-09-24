# 3. Risk Methodology

This method gives consistent, defensible ratings that business risk owners can act on. It is qualitative on purpose, a 5×5 matrix, and aligns with ISO/IEC 27005 and NIST SP 800-30. Organisations that already have an enterprise risk matrix should **replace these scales with their own**, so that SAR risks aggregate into the enterprise risk register.

## 3.1 Risk statement format

Every risk is written as:

> **[Threat actor/event]** could **[action/exploit]** via **[weakness/vector]**, leading to **[impact on asset/business]**.

*Example:* An external attacker could obtain the CI pipeline's cloud deployment credentials via a malicious pull request that runs untrusted code on a privileged runner. This would lead to full control of the production account and exfiltration of customer PII.

Findings describe *what is wrong*. Risks describe *why it matters*. One risk can be driven by several findings.

## 3.2 Impact

Rate the worst **credible** outcome for each of the three dimensions (confidentiality, integrity, availability) and use the highest.

| Score | Level | Financial | Data / confidentiality | Integrity | Availability | Regulatory / reputational |
|---|---|---|---|---|---|---|
| 5 | Severe | > £5m | Mass exposure of Restricted/regulated data, or loss of key material | Undetected tampering with production code/infra or financial records | Critical service down for more than 24h, or data unrecoverable | Regulator enforcement action; national media |
| 4 | Major | £1m–£5m | Exposure of Confidential data at scale | Unauthorised change to production with delayed detection | Critical service down 4–24h | Mandatory breach notification; trade press |
| 3 | Moderate | £100k–£1m | Limited Confidential exposure | Change to non-prod that could propagate to prod | Degraded service, or an outage under 4h | Customer complaints; contractual breach |
| 2 | Minor | £10k–£100k | Internal data exposure | Isolated, easily reversed change | Minor degradation | Internal only |
| 1 | Negligible | < £10k | Public data only | No meaningful effect | Negligible | None |

*Adjust the financial thresholds to your organisation's size.*

## 3.3 Likelihood

Cloud misconfiguration and credential abuse are the leading causes of cloud breaches, so the likelihood factors weigh **exposure** and **ease of exploitation** heavily.

| Score | Level | Guidance |
|---|---|---|
| 5 | Almost certain | Exposed to the internet or to all authenticated users, and trivially exploitable (for example a public bucket, or a leaked static key). Automated scanners find it. |
| 4 | Likely | Reachable by a broad population (all employees, all CI jobs, any PR author) with known techniques. No compensating control. |
| 3 | Possible | Needs a foothold (for example a compromised workload or developer credential) plus moderate skill. |
| 2 | Unlikely | Needs privileged insider access, or the chaining of several independent controls failing. |
| 1 | Rare | Needs a cloud provider compromise, or nation-state capability with no practical exploitation path. |

**Modifiers:** Move likelihood **up** one step if the weakness is on a pipeline or identity plane (because of the blast radius), or if there is no detection capability *designed in*. Move it **down** one step if an independent preventive guardrail exists, such as an SCP or organisation policy that blocks the exploit path.

## 3.4 Risk rating

| Likelihood ↓ / Impact → | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **5** | Medium | High | High | Critical | Critical |
| **4** | Low | Medium | High | High | Critical |
| **3** | Low | Medium | Medium | High | High |
| **2** | Low | Low | Medium | Medium | High |
| **1** | Low | Low | Low | Medium | Medium |

Record both:

- **Inherent risk:** the risk assuming no controls specific to this design. Inherited platform controls *are* counted.
- **Residual risk:** the risk after the proposed or implemented mitigations. The decision is made on residual risk.

## 3.5 Treatment and acceptance authority

| Residual rating | Default treatment | Max. remediation window | Who may accept | Max. acceptance period |
|---|---|---|---|---|
| **Critical** | Must be mitigated before go-live | Blocker | CISO plus executive risk owner (risk committee) | 3 months |
| **High** | Mitigate before go-live, or accept with a dated plan | 30 days post go-live | CISO (or a delegate) plus the risk owner | 6 months |
| **Medium** | Mitigate on the roadmap | 90 days | Risk owner, with security architect concurrence | 12 months |
| **Low** | Mitigate opportunistically | Backlog | Risk owner | 24 months |

Rules:

- **Security cannot accept risk on behalf of the business.** Security *rates* and *recommends*. The risk owner *accepts*.
- Every acceptance has an **expiry date**, **compensating controls** (if any), and a **named owner**, and is recorded using the [risk acceptance template](../templates/risk-acceptance.md).
- Accepted risks are handed to operational security for expiry tracking (see Stage 7).
- Risk accepted repeatedly across systems for the same root cause should trigger a **platform fix** (such as a new guardrail or golden module) instead of more acceptances.

## 3.6 Cloud-specific risk considerations

When rating, always consider:

- **Control-plane reach.** In the cloud, API credentials *are* the network perimeter. A leaked deployment identity can often do more than a network breach.
- **Blast radius of identities.** Assess what each identity can do *transitively*: assume-role chains, pass-role and act-as permissions, and the ability to modify its own policy.
- **Speed of exploitation.** Public exposure is found by automated scanners within minutes, so there is no "security through obscurity" window.
- **Shared responsibility gaps.** Risks often sit in the customer-side configuration of managed services, not in the service itself.
- **Pipeline as privileged identity.** Anything that can influence what the pipeline runs (PR code, dependencies, base images, IaC modules, plug-ins) holds the pipeline's privileges.
- **Reproducibility.** If the environment cannot be rebuilt from code, integrity and recovery risks both go up.
