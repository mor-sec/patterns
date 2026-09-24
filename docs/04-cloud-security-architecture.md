# 4. Cloud Security Architecture Domains

This chapter defines what the reviewer assesses for each design domain. Each domain lists the **review questions**, the **expected pattern** (what "good" looks like), and **common findings**. Examples cite AWS / Azure / GCP equivalents where they help.

The emphasis is on **design properties** that reduce risk. Where a domain produces operational outputs (logs, findings, alerts), the SAR checks that they are *produced and routed by design*. How they are consumed belongs in the handover pack.

---

## 4.1 Shared responsibility and service selection

**Review questions**
- Which cloud services are used, and is each on the approved services list?
- For each service, which security responsibilities fall to us? (For example: patching the OS on VMs versus a managed runtime; encryption settings; network exposure defaults.)
- Is there a preference for higher-abstraction managed services that shift more responsibility to the provider?
- Are the service's regional availability and data residency consistent with the classification?

**Expected pattern**
- A service inventory with a shared-responsibility note per service.
- New services go through a service onboarding assessment, and are added to the guardrails before use.

**Common findings**
- Unapproved services with no preventive guardrail (for example, not denied by SCP / Azure Policy / org policy).
- IaaS chosen where a managed service would remove whole classes of risk, with no rationale recorded.

---

## 4.2 Tenancy, landing zone and blast radius

**Review questions**
- Which account / subscription / project hosts the workload? Is production separated from non-production at the **account level**?
- Is the workload placed in the organisation hierarchy (OU / management group / folder) so that it inherits the correct preventive guardrails?
- What is the blast radius if this account is fully compromised? What else trusts it?
- Are shared services (networking hub, logging, security tooling, CI/CD) in dedicated accounts?

**Expected pattern**
- A multi-account landing zone (AWS Control Tower / Organizations with SCPs and RCPs; Azure landing zones with management groups and Azure Policy; GCP resource hierarchy with Organization Policy).
- One workload per environment per account, or small groupings with a documented justification.
- A dedicated, access-restricted **log archive** and **security tooling** account.
- The organisation management account is not used for workloads.

**Common findings**
- Prod and non-prod in the same account, separated only by tags or naming.
- Workloads in the management/root account.
- No preventive guardrails (region restriction, denial of disabling logs, denial of public-sharing APIs).

---

## 4.3 Identity and access management

This is the **most important domain**. In the cloud, identity is the primary perimeter.

**Review questions**
- **Human access:** Is it federated from the corporate IdP with MFA (phishing-resistant for privileged roles)? Are there any IAM users or local accounts? Is privileged access just-in-time and time-bound?
- **Workload identity:** Do workloads use platform-native identities (IAM roles for service accounts, managed identities, workload identity federation) rather than static keys?
- **Pipeline identity:** Does CI/CD authenticate with OIDC federation, scoped to repository, branch or environment claims? (See §5.)
- **Least privilege:** Are policies scoped to specific actions and resources? Are wildcards justified? Are permission boundaries or SCPs used to cap the maximum privilege?
- **Privilege escalation paths:** Can any identity pass/assume a more privileged role, modify its own policy, create access keys, or change trust policies? (For example `iam:PassRole`, `iam:CreatePolicyVersion`, `Microsoft.Authorization/roleAssignments/write`, `iam.serviceAccounts.actAs`.)
- **Cross-account and third-party trust:** Are trusts scoped by an external ID, source account/organisation conditions, or OIDC subject claims? Is the confused-deputy problem addressed?
- **Break-glass:** Does it exist, is it isolated, heavily alerted *by design*, and hardware-token protected?
- **Resource policies:** Do bucket, key, queue and function policies restrict principals to the organisation or account (for example `aws:PrincipalOrgID`, `aws:SourceArn`)?

**Expected pattern**
- Zero long-lived credentials for humans or workloads.
- Role-per-function with scoped trust policies, and organisation-level guardrails that deny creation of static keys.
- Separate deploy-time identity (the pipeline) from runtime identity (the workload). The runtime identity cannot modify infrastructure.
- Access analysis tooling (IAM Access Analyzer / Entra Permissions Management / GCP Policy Analyzer) is enabled, with its output routed as a handover item.

**Common findings**
- `AdministratorAccess` / Owner granted to the pipeline or the workload.
- Trust policies with `Principal: *`, or OIDC trust without a `sub` claim condition (so any repo on the platform can assume the role).
- Static access keys in CI variables.
- Runtime roles able to modify IAM, KMS key policies or logging configuration.

---

## 4.4 Network architecture and exposure

**Review questions**
- What are the ingress paths from the internet, and does each pass through a managed edge (WAF, DDoS protection, API gateway, load balancer with TLS)?
- Are data stores and management planes reachable only privately (private endpoints / PrivateLink / Private Service Connect)?
- How is egress controlled? Can a compromised workload reach arbitrary internet destinations?
- Is segmentation between tiers enforced (security groups / NSGs / firewall rules referencing identities or tags rather than broad CIDRs)?
- How is administrative access achieved? It should be via Session Manager / Bastion / IAP, with no open SSH/RDP.
- Are hybrid connections (VPN / Direct Connect / ExpressRoute / Interconnect) routed through inspection, and is transitive trust from on-premises understood?

**Expected pattern**
- Hub-and-spoke or equivalent, with central inspection and egress control.
- Default-deny security groups and NACLs, and no `0.0.0.0/0` on non-edge resources.
- Private endpoints for PaaS data services, with public network access disabled at the resource.
- VPC endpoint policies that restrict endpoints to organisation-owned resources (data-perimeter pattern).

**Common findings**
- Databases or caches with public endpoints enabled, relying on authentication alone.
- Unrestricted egress, which enables exfiltration and command-and-control.
- Management ports open to the internet or corporate-wide ranges.

---

## 4.5 Data protection and key management

**Review questions**
- Is every data store identified, classified and mapped to a residency requirement?
- Is encryption at rest enabled? For Confidential and above, are **customer-managed keys** (CMK) used, with key policies separating key administrators from key users?
- Who can decrypt? Is decryption usage constrained by key policy (for example `kms:ViaService`, or encryption context)?
- Is encryption in transit TLS 1.2+ everywhere, including internal hops and service-to-service? Where is TLS terminated, and is re-encryption needed?
- Are backups and snapshots encrypted, access-controlled, blocked from public or cross-account sharing, and immutable where ransomware resilience is required (Object Lock / immutable vaults)?
- Are data lifecycle, retention and deletion designed in?
- Is sensitive data minimised, tokenised or masked in non-production environments?

**Expected pattern**
- Default encryption enforced by policy, and CMKs per data domain or classification for sensitive data.
- Block Public Access enforced at the account or organisation level.
- No production data in non-production without a masking pipeline and a documented approval.

**Common findings**
- One key shared across all environments and data classes.
- Key policies granting `kms:*` to the account root with no conditions, which makes IAM the only control.
- Snapshots shareable publicly, or copied to non-prod unmasked.

---

## 4.6 Secrets management

**Review questions**
- Where do application secrets live? (They should be in Secrets Manager / Key Vault / Secret Manager / Vault, never in code, images, IaC variables or plain environment variables baked into the image.)
- How are secrets retrieved at runtime, using the workload identity, and scoped per service?
- Is rotation automated where supported? Are database credentials dynamic or short-lived where possible?
- Are secrets created by IaC kept out of state (see §5.1)?

**Expected pattern**
- Secret references (ARNs/URIs) in config and values retrieved at runtime. Secret scanning runs on every commit and pre-receive.

---

## 4.7 Compute and workload isolation

**Review questions**
- **VMs:** Are hardened golden images built by pipeline? Is the instance metadata service locked to v2 / hop-limited? Is there no SSH key-based access?
- **Containers:** Are minimal, signed base images used? Do they run as non-root, with a read-only root filesystem, and no privileged containers or hostPath mounts? Are admission policies enforced (Kyverno / Gatekeeper / Azure Policy for AKS / Binary Authorization)?
- **Kubernetes:** Is the control-plane endpoint private or restricted? Is workload identity used (IRSA / EKS Pod Identity / AKS Workload Identity / GKE Workload Identity)? Are namespaces and network policies used for segmentation? Are secrets encrypted with KMS?
- **Serverless:** Is there a role per function, least-privilege triggers, and resource policies restricting invokers?
- Are multi-tenant workloads isolated appropriately (by account, cluster, or namespace), and is that isolation strength proportionate to tenant sensitivity?

**Expected pattern**
- Immutable infrastructure: replace, don't patch in place. Deploy only artefacts that were signed and verified at admission.

---

## 4.8 Application and API edge

**Review questions**
- What is the authentication pattern (OIDC/OAuth 2.x, with token validation at the gateway and the service)?
- Is authorisation enforced server-side at object level (BOLA/IDOR)?
- What rate limiting, schema validation and WAF managed rules are used?
- Are the CORS, CSP and security headers defined in code?

This domain is covered to the depth that it affects architecture. Detailed application security testing belongs to the AppSec programme.

---

## 4.9 Logging and detection *by design*

Operating detection belongs to operational security. The SAR checks only that the **design produces the telemetry** that operations will need.

**Review questions**
- Are control-plane audit logs (CloudTrail / Azure Activity and Entra logs / Cloud Audit Logs) enabled at the organisation level, for all regions, and delivered to the log archive account?
- Are data-plane logs enabled for sensitive stores (S3 data events, Key Vault diagnostics, Data Access logs)?
- Are logs tamper-evident and immutable (object lock, separate account, deny-delete guardrails)? Is the workload's own identity unable to disable or alter them?
- Are CSPM and threat detection services (Security Hub / GuardDuty, Defender for Cloud, Security Command Center) enabled via the landing zone?
- Are pipeline and IaC audit events (who deployed what, when, from which commit) retained and linked to cloud audit logs?

**Handover output:** A list of log sources, destinations and retention, handed to operational security.

---

## 4.10 Resilience and recoverability

**Review questions**
- Do the RTO/RPO match the business impact profile? Is the multi-AZ or multi-region design proportionate?
- Can the environment be **rebuilt from code** (IaC plus pipeline plus backups) into a clean account? This is the key ransomware and integrity control.
- Are backups isolated from the production identity plane (a separate account or vault with independent access)?
- Are there dependencies on a single region, provider or third party for critical functions?

---

## 4.11 Third parties, SaaS and integrations

**Review questions**
- What data leaves our boundary, to whom, and under what contract and assurance (SOC 2 / ISO 27001 / CSA STAR)?
- How does the third party authenticate to us (scoped roles with external ID, or federated trust), and how do we authenticate to them (no shared static credentials where federation exists)?
- Are marketplace components, AMIs, Helm charts and SaaS connectors from verified publishers and pinned?
- Is there an exit plan (data retrieval, credential revocation) designed in?

---

## 4.12 Compliance and data residency

- Map regulated data to its regime (GDPR, PCI DSS v4.x, HIPAA, DORA, NIS2, sector rules).
- Enforce region restrictions with preventive guardrails where residency is mandated.
- Record the compliance requirements the design satisfies, as input to later audit. Audit evidence collection itself is operational.
