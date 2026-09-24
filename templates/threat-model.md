# Threat Model: <System name>

| Field | Value |
|---|---|
| SAR reference | SAR-YYYY-NNN |
| Version / date | |
| Participants | |
| Method | STRIDE per element + cloud and delivery-lifecycle threat library |

## 1. Scope and assumptions

- **In scope:** <components, environments, pipeline>
- **Inherited controls assumed** (with the platform SAR reference): <landing zone guardrails, golden pipeline, etc.>
- **Assumptions:** <for example "the cloud provider control plane is trusted", "the corporate IdP enforces MFA">

## 2. Assets

| Asset | Type (data / identity / key / pipeline / service) | Classification | C / I / A impact (1–5) |
|---|---|---|---|
| Customer PII database | Data | Restricted | 5 / 4 / 3 |
| Production deploy role | Identity | – | 5 / 5 / 4 |
| IaC state (prod) | Data | Restricted | 4 / 5 / 3 |
| | | | |

## 3. Data-flow diagram

Include runtime flows **and** the delivery path. Mark every trust boundary.

```
[Internet user] ──TB1──▶ [WAF/CDN] ──▶ [API Gateway] ──TB2──▶ [Service (VPC)] ──▶ [DB (private)]
                                                                     │
                                                           [Secrets store]  [KMS]

[Developer] ──TB3──▶ [SCM] ──▶ [CI runner] ──TB4 (OIDC)──▶ [Cloud control plane] ──▶ (resources above)
                                    │
                         [Dependency proxy] ◀──TB5── [Public registries]
                                    │
                         [Artefact registry] ──▶ [Admission verification]

[IaC state backend]  (read/write by apply role only)
```

| Boundary | Description |
|---|---|
| TB1 | Internet → edge |
| TB2 | Edge → private network |
| TB3 | Developer endpoint → SCM |
| TB4 | CI → cloud control plane |
| TB5 | Public upstream → internal supply chain |

## 4. Threats

Use the stable IDs from the delivery lifecycle standard (IAC-Tn, BLD-Tn, CFG-Tn) where they apply.

| ID | Element / flow | STRIDE | Threat statement | Existing / proposed mitigations | L | I | Residual risk | Finding ref |
|---|---|---|---|---|---|---|---|---|
| T-01 | CI → cloud (TB4) | E | A PR from any branch could assume the prod deploy role because the OIDC trust lacks a `sub` condition | Restrict trust to `environment:production`; env protection rules | 2 | 5 | High → Medium after fix | F-03 |
| T-02 | IaC state | I | State file exposes the DB master password | Use managed master password; CMK; restrict state reads | 3 | 4 | High | F-05 |
| T-03 | Dependency proxy (TB5) | T | Dependency confusion on internal package names | Namespace reservation; proxy allow-list | 2 | 4 | Medium | – |
| | | | | | | | | |

## 5. Cloud and DLC threat prompts

Consider each prompt, and record it as "N/A" with a reason if it doesn't apply.

- [ ] Stolen or leaked cloud credential (human, workload, pipeline): what can it reach?
- [ ] Privilege escalation via IAM (pass-role, policy edit, trust edit)
- [ ] Public exposure through misconfiguration (storage, snapshots, DB endpoints, management ports)
- [ ] Cross-account / cross-tenant pivot through trust relationships or shared services
- [ ] Instance metadata / SSRF → credential theft
- [ ] Data exfiltration through unrestricted egress or a mis-scoped endpoint policy
- [ ] Logging disabled or tampered with by a compromised identity
- [ ] Key policy abuse or key deletion (crypto-shredding as sabotage)
- [ ] Poisoned pipeline execution through a PR or a change to the pipeline definition
- [ ] Malicious dependency, action, module, provider or base image
- [ ] Artefact substitution between build and deploy
- [ ] IaC state disclosure or tampering
- [ ] Plan/apply divergence
- [ ] Manual change or drift that bypasses guardrails
- [ ] Non-prod → prod bleed (credentials, config, data, network paths)
- [ ] Third-party / SaaS integration compromise
- [ ] Ransomware / destructive attack via the control plane, including backup deletion

## 6. Outcomes

- Findings raised: <refs>
- Accepted risks: <refs>
- Handover items: <refs>
