# 2. Review Workflow

## 2.1 Overview

```
 ┌──────────┐   ┌──────────┐   ┌─────────────┐   ┌──────────────┐   ┌──────────────┐
 │ 0 Intake │──▶│ 1 Tier & │──▶│ 2 Context & │──▶│ 3 Threat     │──▶│ 4 Cloud      │
 │          │   │   scope  │   │  data class │   │   model      │   │  design rev. │
 └──────────┘   └──────────┘   └─────────────┘   └──────────────┘   └──────┬───────┘
                                                                           │
 ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌────────────────▼───────┐
 │ 8 Re-review  │◀──│ 7 Handover   │◀──│ 6 Decision   │◀──│ 5 DLC review           │
 │   triggers   │   │  to op. sec  │   │   gate       │   │ IaC → build → config   │
 └──────────────┘   └──────────────┘   └──────────────┘   └────────────────────────┘
                     (Risk treatment and acceptance run alongside stages 3–6)
```

Stages 3, 4 and 5 are iterative. Findings from the DLC review often change the design, and the reverse is also true. Engage **at design inception** and **again before the first production deployment**. Tier 1 systems also get a mid-point checkpoint.

## 2.2 Tiering

Tiering sets the review's depth, turnaround and decision authority. Score each factor and take the **highest** resulting tier (not an average).

| Factor | Tier 3 (Low) | Tier 2 (Medium) | Tier 1 (High) |
|---|---|---|---|
| Data classification | Public / Internal | Confidential | Restricted / regulated (PII at scale, PCI, PHI, secrets, key material) |
| Exposure | Internal only, no inbound | Authenticated external users or partners | Anonymous internet-facing, or privileged third-party access |
| Blast radius | Single workload, isolated account | Shared account or shared data platform | Shared platform/landing zone, identity plane, CI/CD platform, or network hub |
| Business criticality | Non-critical | Important | Critical or regulated service |
| Novelty | Paved road, approved services | Minor deviations | New provider/service/pattern, or significant deviation |
| Privilege | No cross-account or admin roles | Scoped cross-account roles | Org-level, identity-provider or pipeline-admin privileges |

| | Tier 3 | Tier 2 | Tier 1 |
|---|---|---|---|
| Review form | Self-assessment against checklists plus a spot check by the architect | Architect-led review plus a lightweight threat model | Full review, workshop-based threat model, and design authority decision |
| Artefacts | Intake, checklist, risk register | Plus threat model and review record | Plus security ADRs, DLC evidence, and handover pack |
| Decision authority | Security architect | Security architect | Design authority / security architecture board |
| Target turnaround | 2 working days | 5–10 working days | Scheduled engagement over the design lifecycle |

> Platform components (landing zone, identity provider, CI/CD platform, shared networking, secrets platform) are **always Tier 1**. They carry the blast radius of everything built on them.

## 2.3 Stages

### Stage 0: Intake

- **Entry:** A trigger from §1.5 applies.
- **Activities:** The delivery lead completes the [intake questionnaire](../templates/intake-questionnaire.md) and attaches a context diagram, a draft component/data-flow diagram, a repository link, and pipeline definitions if they exist.
- **Exit:** Intake accepted as complete, and a security architect assigned.

### Stage 1: Tier and scope

- **Activities:** Apply the tiering matrix. Identify inherited controls: landing zone, paved-road modules, pipeline templates. Agree which domains are in scope and which are satisfied by inheritance. Anything inherited is *referenced*, not re-reviewed, provided the platform itself has a current SAR.
- **Exit:** Tier, scope, reviewers, milestones and a decision authority are recorded in the review record.

### Stage 2: Context and data classification

- **Activities:**
  - Confirm business purpose, users, and the **risk owner**.
  - Classify every data store and flow. Record residency and regulatory constraints.
  - Identify **crown-jewel assets**: data, identities, keys, pipelines.
  - Agree the **impact profile** (confidentiality, integrity, availability) using the [risk methodology](03-risk-methodology.md#32-impact).
  - Confirm the applicable **risk appetite** statement.
- **Exit:** Data inventory and impact profile agreed with the risk owner.

### Stage 3: Threat model

- **Activities:** Use the [threat model template](../templates/threat-model.md).
  1. Draw the data-flow diagram (DFD) with trust boundaries: internet, cloud account, VPC/VNet, cluster, CI/CD, third party, and the cloud provider control plane.
  2. **Include the delivery path as part of the system:** developer workstation → source control → CI → artefact registry → IaC plan/apply → cloud control plane → runtime.
  3. Enumerate threats with STRIDE per element, and add cloud-specific threat patterns (see §4 and §5): credential theft and control-plane abuse, misconfiguration exposure, cross-tenant or cross-account pivoting, pipeline poisoning, dependency compromise, state-file disclosure, and drift.
  4. For each threat, identify the existing or proposed mitigations and then rate the **residual** risk.
- **Exit:** Threats rated, mitigations mapped, and gaps raised as findings.

### Stage 4: Cloud security design review

- **Activities:** Assess the design against [the cloud domains](04-cloud-security-architecture.md) using the [cloud architecture checklist](../checklists/cloud-architecture.md). Focus on the controls that address the threat-model risks, and confirm the **shared-responsibility split** for every managed service used.
- **Evidence:** Diagrams, IaC (the design as written is the design), IAM policy documents, network definitions, and key policies.
- **Exit:** Findings recorded and rated.

### Stage 5: Delivery lifecycle review (IaC → build → configuration)

- **Activities:** Assess against the [delivery lifecycle standard](05-delivery-lifecycle.md) and the [IaC](../checklists/iac.md), [build](../checklists/build-pipeline.md) and [configuration](../checklists/configuration.md) checklists.
- **Evidence (must be real, not described):**
  - Repository settings: branch protection, required reviews, CODEOWNERS, signed commits.
  - Pipeline definitions, runner configuration, and how the pipeline's cloud identities and permissions are federated.
  - IaC state backend configuration, a sample of plan output, and policy-as-code results.
  - Artefact provenance and signatures, and SBOM samples.
  - Configuration and secret-store layout for each environment.
- **Exit:** Findings recorded and rated. Where the pipeline is a shared platform, reference that platform's SAR.

### Stage 6: Risk treatment and decision gate

- **Activities:**
  - Each finding gets a treatment: **Mitigate** (with an owner and date), **Avoid** (a design change), **Transfer**, or **Accept** (a [risk acceptance](../templates/risk-acceptance.md) signed at the right authority level).
  - The reviewer completes the [review record](../templates/architecture-review-record.md) with a recommendation.
- **Decision outcomes:**

| Outcome | Meaning |
|---|---|
| **Approved** | No open High/Critical risks. Medium and lower risks are tracked with owners. |
| **Approved with conditions** | Conditions must be met before a named milestone (usually production go-live or data onboarding). Conditions are tracked in the risk register and verified by the architect. |
| **Not approved** | Critical risk, or risk above appetite with no acceptance at the right authority. Redesign is required. |

- **Hard stops** (an automatic *Not approved* unless the CISO accepts the risk):
  - Long-lived static cloud credentials used by pipelines or workloads where federation is available.
  - Manual ("ClickOps") production infrastructure changes as the normal deployment path.
  - IaC state or build artefacts stored without encryption and access control.
  - Restricted data stored in a publicly reachable store, or encrypted with no key-access control.
  - Production deployable from an unreviewed branch, or by a single person with no second approval.
  - No environment separation between production and non-production identities or accounts.

### Stage 7: Handover to operational security

This stage marks the boundary of the SAR. The reviewer compiles a **handover pack** that lists the operational controls the design *enables*, and that operational security must *operate*:

- Log sources produced, their destination, and their retention (design) → detection use cases (operations).
- Security findings sources (CSPM, IaC scanning, image scanning) → triage ownership.
- Break-glass accounts and procedure → custodianship and testing.
- Privileged roles and entitlements → recertification schedule.
- Key rotation mechanisms → rotation monitoring.
- Pen test requirement (scope and timing) → scheduling.
- Accepted risks with expiry dates → review ownership.

Operational security confirms that it can operate these controls (it does not re-review the design). **Exit:** handover acknowledged, and the review is closed.

### Stage 8: Re-review triggers

The approval stays valid until **any** of these occurs:

- A change to trust boundaries, data classification, identities/privilege, network exposure, or the delivery pipeline.
- Adoption of a new cloud service or third party.
- Expiry of a risk acceptance.
- A security incident that affects the system and reveals a design weakness.
- 24 months pass (Tier 1) or 36 months pass (Tier 2), prompting a lightweight re-validation.

## 2.4 Service levels and metrics

Track these metrics to steer the process. They are not SOC metrics.

- Share of reviews that engage at design inception, versus at go-live.
- Median time from intake to decision, by tier.
- Share of systems on paved-road patterns (a high number reduces review load).
- Count of open High/Critical conditions past their due date.
- Count of risk acceptances expired but not re-reviewed.
- Findings by domain, which show where platform guardrails or golden modules are missing.
