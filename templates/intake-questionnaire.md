# SAR Intake Questionnaire

*The delivery team completes this form. Submit it as early as possible, ideally at design inception. Answer "Unknown" rather than leaving a field blank, because unknowns are useful review input.*

## A. General

| Field | Response |
|---|---|
| System / change name | |
| Brief description (2–3 sentences) | |
| Risk owner (business owner) | |
| Delivery lead | |
| Target go-live / data onboarding date | |
| New system or change to existing? (If a change, link the previous SAR.) | |
| Review trigger(s) from §1.5 | |

## B. Data

| Question | Response |
|---|---|
| What data does the system store, process or transmit? | |
| Highest data classification (Public / Internal / Confidential / Restricted) | |
| Regulated data? (personal data, PCI, PHI, financial, other) Approximate record volumes? | |
| Data residency requirements | |
| Will production data be used in non-production environments? | |
| Data shared with third parties? Who, and what data? | |

## C. Users and exposure

| Question | Response |
|---|---|
| User populations (internal staff / customers / partners / anonymous public) | |
| Internet-facing entry points (URLs, APIs, file uploads) | |
| Authentication method for each population | |
| Privileged / administrative users and how they access the system | |

## D. Cloud platform

| Question | Response |
|---|---|
| Cloud provider(s) and region(s) | |
| Target accounts / subscriptions / projects per environment | |
| Is the system deployed onto the standard landing zone? | |
| Cloud services used (list each) | |
| Any services not on the approved services list? | |
| Connectivity to on-premises or other clouds | |
| Workload identity approach (roles, managed identities, service accounts) | |
| Secrets and key management approach | |

## E. Delivery lifecycle

| Question | Response |
|---|---|
| Source control platform and repository URLs | |
| IaC tool(s) and version(s) | |
| Are golden/approved IaC modules used? Which? | |
| IaC state backend and location | |
| CI/CD platform; shared template or bespoke pipeline? | |
| How does the pipeline authenticate to the cloud? (OIDC / static keys / other) | |
| Runner type (hosted / self-hosted; ephemeral / persistent) | |
| Security scanning in the pipeline (SAST / SCA / IaC / container / secrets) | |
| Artefact registry; are artefacts signed? Is an SBOM generated? | |
| How is configuration managed and promoted between environments? | |
| Can anyone change production outside the pipeline? Who, and how? | |

## F. Resilience and dependencies

| Question | Response |
|---|---|
| RTO / RPO | |
| Backup approach and location | |
| Critical third-party / SaaS dependencies | |

## G. Attachments checklist

- [ ] Context diagram (system in its environment)
- [ ] Component / data-flow diagram with trust boundaries (a draft is fine)
- [ ] Repository access for the reviewer (IaC, app, pipeline, config)
- [ ] Any existing ADRs or design documents
