# 1. Scope, Principles and Roles

## 1.1 Purpose

The Security Architecture Review (SAR) gives the business an informed, documented view of the **security risk a new or changed cloud system introduces**. It also makes sure that the system's **design and delivery pipeline** reduce that risk to within appetite *before* it reaches production.

The review is about **risk and design**. It asks three questions:

1. *What could go wrong, and how bad would it be?* (threats, impact, likelihood)
2. *Does the architecture, including how it is built and configured, prevent, contain or detect it by design?*
3. *Is the remaining risk understood and owned by someone with the authority to accept it?*

## 1.2 Scope

### In scope

- **Solution architecture**: components, data flows, trust boundaries, integrations, third parties.
- **Cloud platform design**: landing zone and account/subscription/project placement, identity and access, network topology, data protection and key management, workload isolation, managed-service configuration, and the shared-responsibility split.
- **Delivery lifecycle (the "DLC")**:
  - **IaC**: authoring, modules, state, secrets handling, policy-as-code, plan/apply controls, drift strategy.
  - **Build**: source control, CI/CD pipeline integrity, runner isolation, dependency and artefact supply chain, signing and provenance.
  - **Configuration**: baselines, parameter and secret stores, environment separation and promotion, immutable vs mutable config, and how drift is prevented or detected *by design*.
- **Security-relevant non-functional requirements (NFRs)**: resilience, recoverability, data residency, and regulatory constraints.

### Out of scope (owned by operational security after handover)

- Operating the SOC, SIEM content and alert tuning, and incident response.
- Continuous vulnerability scanning, patch cadence and exception handling for running estates.
- Periodic access recertification and joiner/mover/leaver execution.
- Running penetration tests and red-team exercises (the SAR *sets the requirement* for them).
- Collecting control-operation evidence for audit.

> **Boundary rule:** if a control is a *property of the design or pipeline*, the SAR assesses it. If it is an *activity people perform on a running system*, the SAR records it as a **handover requirement** and does not assess how it is carried out.

## 1.3 Principles

1. **Risk-led, not checklist-led.** Checklists prompt thinking. Findings are rated by business risk, not by how many checklist items are missing.
2. **Shift left, stay proportionate.** Engage at design inception. Review depth scales with risk tier, and low-risk changes should not wait on heavy process.
3. **Secure by default, paved roads first.** Prefer approved platform patterns (landing zone, golden modules, pipeline templates). A design on the paved road needs only a lighter review of the parts it reuses.
4. **Everything as code.** Infrastructure, configuration, policy and pipeline definitions are version-controlled, peer-reviewed and reproducible. Things built by hand are findings.
5. **Least privilege and blast-radius minimisation.** Identities, network paths and accounts are scoped so that a single compromise has a bounded impact.
6. **Assume breach of the pipeline.** The build system is a production system. Its compromise equals compromise of everything it deploys.
7. **Guardrails over gates.** Automated preventive controls (policy-as-code, service control policies, organisation policies) are preferred to manual approvals.
8. **Decisions are recorded.** Significant design choices and accepted risks are captured as ADRs and risk acceptances with named owners and expiry dates.

## 1.4 Roles and responsibilities

| Role | Responsibilities |
|---|---|
| **Risk owner** (business/service owner) | Owns the system's risk; sets context and impact; accepts residual risk within their delegated authority. |
| **Solution / delivery lead** | Completes the intake; supplies diagrams, IaC and pipeline definitions; fixes findings. |
| **Security architect (reviewer)** | Tiers the review; facilitates the threat model; assesses the design and DLC; rates risk; writes the review record. |
| **Cloud platform team** | Owns the landing zone, guardrails and golden modules/pipelines; confirms that inherited controls are in place. |
| **Security architecture authority / design authority** | Decision gate for Tier 1; arbitrates disputes; approves deviations from standards. |
| **Operational security** | Receives the handover pack; confirms it can operate the required controls. |
| **CISO / risk committee** | Accepts risks above the risk owner's delegated authority. |

### RACI

| Activity | Risk owner | Delivery lead | Security architect | Platform team | Design authority | Op. security |
|---|---|---|---|---|---|---|
| Intake and tiering | I | R | A | C | I | – |
| Threat model | C | R | A | C | – | C |
| Cloud design review | I | R | A | C | I | – |
| DLC (IaC/build/config) review | I | R | A | C | – | – |
| Risk rating | C | C | A/R | C | I | – |
| Remediation | I | A/R | C | C | – | – |
| Risk acceptance | A/R | C | C | – | C | I |
| Decision gate | C | I | R | I | A (Tier 1) | I |
| Handover | I | R | A | C | – | C |

*R = Responsible, A = Accountable, C = Consulted, I = Informed*

## 1.5 Review triggers

A SAR is **required** when any of the following apply:

- A new system, product or service is hosted in the cloud.
- A new cloud provider, account/subscription/project boundary, or region is introduced.
- New or changed processing of data classified **Confidential** or above, or of regulated data (personal data, cardholder data, health data).
- A new internet-facing entry point, or a new third-party/SaaS integration with data exchange.
- A change to identity architecture (federation, new privileged roles, cross-account trust, workload identity).
- Use of a cloud service not yet on the approved services list.
- A new or materially changed **delivery pipeline**, IaC toolchain, or deployment mechanism.
- A deviation from a paved-road pattern or security standard.
- Material change to a previously reviewed architecture (see §2 re-review triggers).

A SAR is **not required** for changes wholly within an already-reviewed architecture that do not alter trust boundaries, data classification, identities or the pipeline. These are covered by standard change control and automated guardrails.
