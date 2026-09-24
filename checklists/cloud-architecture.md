# Cloud Architecture Checklist

These are prompts for [§4](../docs/04-cloud-security-architecture.md). Mark each item ✅ / ⚠️ / ❌ / ➖ (N/A or inherited, with a reference). A ❌ becomes a finding **only once it has been rated for risk**. 🛑 = a hard stop from §2.3.

## Service selection and shared responsibility
- [ ] CA-01 All services are on the approved list, or have an onboarding assessment
- [ ] CA-02 Customer-side responsibilities documented for each service
- [ ] CA-03 Unapproved services and regions denied by an organisation guardrail

## Tenancy and blast radius
- [ ] CA-10 🛑 Prod and non-prod in separate accounts / subscriptions / projects
- [ ] CA-11 Workload placed in the correct OU / management group / folder, inheriting guardrails
- [ ] CA-12 No workloads in the organisation management account
- [ ] CA-13 Blast radius of full account compromise documented; inbound trusts listed

## Identity and access
- [ ] CA-20 Human access federated from the IdP with MFA; phishing-resistant MFA for privileged roles
- [ ] CA-21 🛑 No long-lived static credentials for humans, workloads or pipelines where federation is available
- [ ] CA-22 Workloads use platform-native identity
- [ ] CA-23 Deploy identity is separate from runtime identity; runtime cannot modify IAM, KMS or logging
- [ ] CA-24 Policies least-privilege; wildcards justified; permission boundaries or SCPs cap the maximum
- [ ] CA-25 Privilege escalation paths analysed (pass-role / act-as, policy edit, trust edit, key creation)
- [ ] CA-26 Cross-account and third-party trusts constrained (external ID, org ID, source ARN, OIDC `sub`)
- [ ] CA-27 Resource policies restrict principals to the organisation / account
- [ ] CA-28 Break-glass accounts defined, isolated and hardware-MFA protected
- [ ] CA-29 Privileged access is just-in-time and time-bound

## Network
- [ ] CA-30 Every internet ingress passes a managed edge (WAF / DDoS / TLS)
- [ ] CA-31 Data stores and PaaS reachable only via private endpoints; public network access disabled
- [ ] CA-32 Egress restricted and inspected; no unrestricted `0.0.0.0/0` egress from sensitive tiers
- [ ] CA-33 No management ports open to the internet; admin via SSM / Bastion / IAP
- [ ] CA-34 Segmentation between tiers using identity or tag-based rules
- [ ] CA-35 Endpoint policies / data perimeter restrict access to organisation-owned resources
- [ ] CA-36 Hybrid connectivity routed through inspection; on-prem trust assumptions documented

## Data protection and keys
- [ ] CA-40 🛑 Restricted data not in any publicly reachable store
- [ ] CA-41 Encryption at rest everywhere; CMK for Confidential and above
- [ ] CA-42 Key administrators separated from key users; key policy conditions applied
- [ ] CA-43 Keys separated per environment and classification
- [ ] CA-44 TLS 1.2+ on all hops, including internal
- [ ] CA-45 Backups encrypted, isolated from the prod identity plane, immutable where required
- [ ] CA-46 Public / cross-account snapshot sharing blocked
- [ ] CA-47 No unmasked prod data in non-prod
- [ ] CA-48 Retention and deletion designed in

## Secrets
- [ ] CA-50 All secrets in a managed secret store, retrieved at runtime by workload identity
- [ ] CA-51 Secrets scoped per service; rotation automated where supported

## Compute and workloads
- [ ] CA-60 Golden, hardened images built by pipeline
- [ ] CA-61 IMDSv2 / metadata protections enforced
- [ ] CA-62 Containers non-root, read-only root filesystem, no privileged or hostPath
- [ ] CA-63 Admission policy enforces baseline and signature verification
- [ ] CA-64 Kubernetes API endpoint private or restricted; workload identity; network policies
- [ ] CA-65 Tenant isolation strength matches tenant sensitivity

## Application edge
- [ ] CA-70 Standard authentication (OIDC/OAuth) with token validation at gateway and service
- [ ] CA-71 Object-level authorisation enforced server-side
- [ ] CA-72 Rate limiting, schema validation, security headers defined in code

## Logging by design
- [ ] CA-80 Org-wide control-plane audit logging, all regions, to the log archive account
- [ ] CA-81 Data-plane logging for sensitive stores
- [ ] CA-82 Logs immutable; workload and pipeline identities cannot disable or modify them
- [ ] CA-83 CSPM / threat detection enabled via the landing zone
- [ ] CA-84 Log sources, destinations and retention listed in the handover pack

## Resilience
- [ ] CA-90 RTO / RPO align with the impact profile
- [ ] CA-91 Environment can be rebuilt from code into a clean account
- [ ] CA-92 Backup restore and rebuild procedures designed (testing is operational)

## Third parties and compliance
- [ ] CA-95 Third-party data flows, assurance and contracts recorded
- [ ] CA-96 Third-party access federated / scoped; exit plan exists
- [ ] CA-97 Residency enforced by guardrail where mandated; regulatory mapping recorded
