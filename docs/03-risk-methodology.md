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

## 3.7 Cyber risk taxonomy

Every risk is filed under one category of a two-level taxonomy. This lets risks from different TRAs be added up in the register, shows which kinds of risk recur across the portfolio, and makes sure categories that are easy to miss get considered on every assessment. The agent reads the taxonomy from [risk_taxonomy.yaml](../tra-agent/src/tra_core/data/risk_taxonomy.yaml), and the register's `domain` column carries the category.

### How to categorise a risk

- **Root cause, not consequence.** File the risk where the weakness is, because that is also who usually owns the fix. A deployment key committed to a repository that leads to a data breach is *SDL.4 Secrets and configuration in code*, not *DAT.1 Unauthorised disclosure*. Consequences are rated through impact (3.2), not categorised.
- **One category per risk.** If a risk seems to need two, it is usually two risks, or one of them is the consequence.
- **Level 2 is recorded.** Level 1 is used for reporting and aggregation.
- **Prefer the more specific category.** For example, a supplier in a foreign jurisdiction goes under *FOC*, not *SUP.3*, when the concern is foreign direction rather than the supplier's security practice.

### Sources

No single published taxonomy fits a cloud SAR on its own, so this one combines the following sources:

| Source | What it contributes |
|---|---|
| NIST SP 800-30 Rev. 1 | Threat source types (adversarial, accidental, structural, environmental). These are why the taxonomy includes non-adversarial categories such as SUP.5 and PHY.2. |
| ISO/IEC 27005:2022 | Risk identification from risk sources and events, and the link to the ISO 27001 risk register. |
| SEI, *A Taxonomy of Operational Cyber Security Risks*, v2 (2014) | The four classes: actions of people, systems and technology failures, failed internal processes and external events. These map to PEO, INF/APP, SDL/GOV and SUP/PHY. |
| ENISA Threat Taxonomy | Coverage check for physical, unintentional, disaster, failure, outage, interception and legal threats. |
| NIST CSF 2.0 (2024) | Supply chain risk management as a governance outcome (GV.SC). |
| NIST SP 800-161 Rev. 1, Update 1 (2024) | Supply chain risk factors: malicious functionality, counterfeits, poor development practice and limited visibility (SUP.1 to SUP.4, SUP.6). |
| NIST SP 800-218 SSDF v1.1, with v1.2 in draft (December 2025) | Secure development practices behind SDL.1 to SDL.5. |
| ASD ISM (September 2026) | Software development, cyber supply chain and cryptography guidelines, including ISM-2073 (PQC transition plan) and ISM-1917 (ML-KEM and ML-DSA support by 2030). |
| ASD, *Planning for post-quantum cryptography* | Cease traditional asymmetric cryptography by the end of 2030, with milestones at the end of 2026 and 2028. Also harvest-now-decrypt-later and the LATICE transition steps. |
| PSPF Direction 001-2024 and Home Affairs FOCI risk assessment guidance | The FOCI definition and the requirement to identify and manage FOCI risk in technology procurement and maintenance. |
| MITRE ATT&CK, MITRE ATLAS, OWASP Top 10 for LLM Applications | Threat techniques. Each library threat carries a default category, so threats map to categories. |

### The taxonomy

Categories marked **always consider** must be addressed on every TRA. If no risk is recorded in one, the quality critic raises a minor finding, and the practitioner confirms at G2 that it was considered and does not apply.

| Level 1 | Level 2 categories | Always consider |
|---|---|---|
| **IAM** Identity and access | IAM.1 Authentication weakness · IAM.2 Excessive or unreviewed privilege · IAM.3 Workload and token misuse · IAM.4 Identity lifecycle | |
| **DAT** Data protection | DAT.1 Unauthorised disclosure · DAT.2 Integrity of records · DAT.3 Aggregation and classification · DAT.4 Privacy and retention · DAT.5 Data residency and sovereignty | |
| **APP** Application and API | APP.1 Injection and input handling · APP.2 Broken authorisation · APP.3 Client-side and third-party script · APP.4 Business logic abuse | |
| **INF** Infrastructure and cloud configuration | INF.1 Misconfiguration and drift · INF.2 Network exposure and segmentation · INF.3 Unpatched or end-of-support component · INF.4 Control-plane compromise | |
| **SDL** Software development | SDL.1 Insecure design · SDL.2 Code defects and testing gaps · SDL.3 Build and pipeline integrity · SDL.4 Secrets and configuration in code · SDL.5 Change and release control | Yes |
| **SUP** Supply chain | SUP.1 Software component compromise · SUP.2 Service provider compromise · SUP.3 Supplier security posture · SUP.4 Hardware and component integrity · SUP.5 Concentration, lock-in and exit · SUP.6 Fourth party and subcontractor | Yes |
| **FOC** Foreign ownership, control or influence | FOC.1 Ownership and control · FOC.2 Extraterritorial legal compulsion · FOC.3 Privileged foreign access · FOC.4 Directed sabotage or disruption | Yes |
| **CRY** Cryptography and post-quantum transition | CRY.1 Harvest now, decrypt later · CRY.2 Quantum-vulnerable signatures and trust · CRY.3 Crypto agility and inventory · CRY.4 Weak or legacy cryptography · CRY.5 Key management | Yes |
| **DET** Detection, logging and response | DET.1 Logging gaps or tampering · DET.2 Detection and alerting gaps · DET.3 Response readiness · DET.4 Non-repudiation | |
| **RES** Resilience and availability | RES.1 Denial of service and capacity · RES.2 Destructive attack and ransomware · RES.3 Recovery and continuity | |
| **AIM** AI and autonomous agents | AIM.1 Prompt injection and jailbreak · AIM.2 Model data leakage · AIM.3 Excessive agency · AIM.4 Poisoning and model integrity · AIM.5 Over-reliance and output quality | |
| **PEO** People | PEO.1 Social engineering · PEO.2 Malicious insider · PEO.3 Error and skills | |
| **GOV** Governance and compliance | GOV.1 Regulatory and contractual non-compliance · GOV.2 Unowned or expired risk acceptance · GOV.3 Technical debt and obsolescence | |
| **PHY** Physical and environmental | PHY.1 Physical access and theft · PHY.2 Environmental and utility failure | |

Each level 2 category's definition is in the data file.

### Software development (SDL)

This category covers weaknesses introduced before the system runs: in design, code, build and release. Assess the pipeline as a privileged identity (3.6). Look for:

- no threat model or security requirements (SDL.1, ISM-1238);
- SAST, DAST and SCA missing from the release path (SDL.2, ISM-0402);
- pipelines that run untrusted pull request code with deployment credentials, or unsigned artefacts (SDL.3);
- secrets in repositories or images (SDL.4);
- changes that reach production without review or a rollback path (SDL.5).

**Rating.** The likelihood modifier for pipeline planes applies. Impact is usually that of the production system the pipeline can change. Common controls: CC-021, CC-022, CC-023, CC-007 and CC-036.

### Supply chain (SUP)

This category covers risk that arrives through components and services the system depends on, including their own suppliers. For each supplier the design names, record:

- what access it holds (integration, support, update channel);
- what the system cannot do without it;
- what assurance exists (ISM-1452 supply chain risk assessment, ISM-1567 high-risk suppliers not used, ISM-1790 to ISM-1792 integrity and authenticity on acceptance).

Service provider compromise (SUP.2) is rated on the provider's access, not on the provider's reputation. Concentration and exit risk (SUP.5) is non-adversarial: rate likelihood on the supplier's financial and service history and the absence of a tested exit, not on attacker capability. Common controls: CC-037, CC-026, CC-022 and CC-031.

### Foreign ownership, control or influence (FOC)

FOCI risk is "the ability for vendors to be directed by a foreign government", through direct ownership, the laws of the vendor's home jurisdiction or outside pressure (Home Affairs, *FOCI risk assessment guidance*). PSPF Direction 001-2024 requires Commonwealth entities to identify and manage FOCI risk in the procurement and maintenance of technology assets. Other organisations should apply the same test to suppliers that hold OFFICIAL: Sensitive data or privileged access.

Raise a FOC risk when the design shows a supplier, parent company, support team, subprocessor or update channel in a jurisdiction whose laws can compel access or cooperation. Use Home Affairs' two steps:

1. Run the vendor review questionnaire to decide whether a full assessment is needed.
2. If it is, run the full assessment, which weighs the jurisdiction's hazard against the system's exposure.

The TRA records the outcome and cites the assessment as evidence. It does not repeat the assessment.

**Rating.** Likelihood follows the jurisdiction hazard and the vendor's access: privileged access or an update channel is higher than hosting encrypted data the vendor cannot read. Impact is at least the impact floor for the data's classification, and higher when the vendor can disrupt a critical service (FOC.4).

**Treatments** include customer-held keys, Australian-based support only, contractual FOCI clauses (the Home Affairs model clauses), an exit plan, or not using the vendor (ISM-1567). Common controls: CC-038, CC-037, CC-034 and CC-008.

### Cryptography and the post-quantum transition (CRY)

ASD recommends ceasing traditional asymmetric cryptography (RSA, DH, ECDH and ECDSA) by the end of 2030. Organisations should have a refined transition plan by the end of 2026, have started the transition by the end of 2028, and have completed it by the end of 2030. The ISM requires:

- a PQC transition plan (ISM-2073);
- ML-KEM-1024, ML-DSA-87, SHA-384, SHA-512 and AES-256 support in new cryptographic equipment, applications and libraries by 2030 (ISM-1917);
- ML-KEM-768 or -1024, and ML-DSA-65 or -87, where these algorithms are used (ISM-1995, ISM-1991).

NIST IR 8547 (initial public draft, November 2024) sets a similar direction: quantum-vulnerable algorithms deprecated after 2030 and disallowed after 2035.

For each system, ask:

- **CRY.1 Harvest now, decrypt later.** Does any data have to stay confidential beyond about 2030? If so, and it crosses a boundary under RSA or ECDH key exchange, it can be recorded now and decrypted later. Likelihood is not reduced by the current absence of a quantum computer when the data's confidentiality life outlasts the transition date.
- **CRY.2 Signatures and trust.** Do code signing, firmware, certificates or long-lived tokens rely on RSA or ECC signatures that must remain trustworthy beyond 2030?
- **CRY.3 Agility and inventory.** Is there a cryptographic inventory (a CBOM)? Can each dependency move to ML-KEM and ML-DSA by 2030, or are its algorithms hard-coded or locked in a product?
- **CRY.4 and CRY.5.** Are legacy algorithms or protocols in use, and is key management sound?

Common controls: CC-039, CC-009 and CC-008.

### Reporting and maintenance

The TRA report shows each risk's category and a "risks by category" summary. The summary lists the always-consider categories even when they are empty, so a reviewer can see they were considered. Security architecture should review the register by category each quarter. A category that keeps recurring across systems is a signal for a platform fix (3.5).

The taxonomy is versioned with the threat library and control catalogue. Review it every six months, and whenever ASD, NIST or Home Affairs change the guidance above. When a category changes, keep the old ID retired rather than reusing it, so historical register entries stay meaningful.
