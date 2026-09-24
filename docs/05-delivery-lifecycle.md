# 5. Delivery Lifecycle: IaC → Build → Configuration

The delivery lifecycle (DLC) is **part of the system under review**. Whoever controls the path from a commit to a running cloud resource controls production. This chapter defines the standard the SAR assesses across three stages. Each stage lists its **threats**, **required controls**, **recommended controls**, and the **evidence** the reviewer needs.

```
Developer ──▶ Source control ──▶ CI build ──▶ Artefact registry ──┐
   │               │                │                             │
   │               │                └──▶ IaC plan ──▶ Policy ──▶ Approval ──▶ IaC apply ──▶ Cloud control plane
   │               │                                                                             │
   └── secrets ────┴── config repo ──▶ Config/param store ──▶ Deploy (by digest) ─────────────────┴──▶ Runtime
                                                                     ▲
                                            Drift detection ◀────────┘ (designed in; operated post-handover)
```

Reference frameworks: **SLSA v1.x** (build provenance levels), **NIST SSDF SP 800-218**, **CIS Software Supply Chain Security Guide**, **OpenSSF Scorecard**, **OWASP Top 10 CI/CD Security Risks**.

---

## 5.0 Source control (the common foundation)

All three stages start from source control, so these controls apply to IaC, application and configuration repositories alike.

| Threat | Required control |
|---|---|
| Unreviewed change reaches prod | Protected default/release branches; ≥1 independent approving review (≥2 for Tier 1 platform repos); CODEOWNERS for security-sensitive paths (IaC, pipeline definitions, IAM, policies); dismiss stale approvals on new commits |
| Pipeline definition tampering | Pipeline files under CODEOWNERS; pipeline changes need security-aware review; reusable/templated pipelines pinned by commit SHA |
| Account takeover of a developer | SSO + phishing-resistant MFA to the SCM; no personal access tokens with broad scope (fine-grained, expiring tokens only) |
| Force-push / history rewrite | Force-push and branch deletion disabled on protected branches |
| Secrets committed | Push protection / pre-receive secret scanning; pre-commit hooks recommended |
| Impersonation of commits | Signed commits (Sigstore gitsign / SSH / GPG) — **required** for Tier 1, recommended otherwise |
| Admin bypass | Branch protection enforced for administrators; SCM org admin count minimised and audited |

**Evidence:** Export of repository or branch protection rulesets, CODEOWNERS file, SCM organisation security settings.

---

## 5.1 Infrastructure as Code (IaC)

Tools covered include Terraform/OpenTofu, CloudFormation, CDK, Bicep/ARM, Pulumi and Crossplane. The principles are tool-agnostic.

### 5.1.1 Threats

| ID | Threat |
|---|---|
| IAC-T1 | Insecure resource configuration defined in code and deployed at scale (public storage, open security groups, missing encryption, over-privileged IAM) |
| IAC-T2 | **State file disclosure.** State contains resource attributes, and often plaintext secrets (DB passwords, generated keys) |
| IAC-T3 | **State tampering or lock abuse**, used to hide malicious resources or corrupt the deployment |
| IAC-T4 | Malicious or compromised **third-party modules/providers** (registry typosquatting, unpinned versions, hijacked maintainers) |
| IAC-T5 | Over-privileged **apply identity**: a compromised pipeline can do anything in the account or organisation |
| IAC-T6 | **Plan/apply divergence**: what was reviewed differs from what was applied |
| IAC-T7 | **Code execution during plan** (external data sources, provisioners, provider plug-ins) from untrusted branches |
| IAC-T8 | **Drift**: manual console changes bypass all review and guardrails |
| IAC-T9 | Secrets hard-coded in IaC variables, `tfvars` or parameters committed to the repo |

### 5.1.2 Required controls

**Design and authoring**
1. All infrastructure in scope is defined in IaC. Manual creation is allowed only in break-glass cases, and then reconciled back into code.
2. Consume **approved golden modules** or patterns (for example a private module registry) that are secure by default. Deviations from a golden module need an ADR.
3. Module and provider versions are **pinned** (exact version plus lock file such as `.terraform.lock.hcl` with hashes). Only from an approved registry or mirror.
4. No secrets in IaC source. Reference secret-store ARNs/URIs. Where IaC must *create* a secret, generate it in the secret store (for example `manage_master_user_password` on RDS, or ephemeral resources / write-only attributes where the tool supports them) so it doesn't land in state.
5. Environments are separated by **configuration and backend**, not by copy-pasted code (the same modules, with different variables and state).

**State management**
6. Remote state backend with **encryption at rest using a CMK**, versioning, and access restricted to the pipeline apply identity plus break-glass. No developer read access to production state by default.
7. One state per environment per component (limits blast radius). State locking enabled.
8. The state backend lives in a dedicated or management account, protected from the workload's runtime identity.

**Policy-as-code (preventive, at plan time)**
9. Static analysis on every pull request: Checkov / tfsec (Trivy) / KICS / cfn-lint + cfn-guard / PSRule for Azure. High-severity policy failures **block merge**.
10. Organisation policy evaluated against the **plan output** (OPA/Conftest, Sentinel, cfn-guard, or the Terraform Cloud/Spacelift policy engine) before apply. This catches issues that static scanning of source misses (computed values, module internals).
11. Policy exceptions are declared in code (inline skip with a justification and a ticket reference) and are reviewable. No global disabling.
12. Cloud-native preventive guardrails (SCP / RCP / Azure Policy deny / Org Policy constraints) back up policy-as-code, **because pipelines can be bypassed**.

**Plan and apply**
13. PR pipelines run `plan` with a **read-only identity**. Only the protected-branch pipeline can `apply`, with a **separate, write-capable identity**.
14. The apply uses the **exact saved plan artefact** that was reviewed and approved (plan file hashed and passed between stages). If there is no saved plan, the apply is rejected.
15. Production apply requires an environment-level approval by someone other than the change author (the pipeline's environment protection rules).
16. Plans from untrusted forks never run with cloud credentials. Provisioners and external data sources are restricted by policy.
17. The apply identity is scoped to the resource types and accounts the stack manages (a permission boundary or custom role), not organisation-wide admin. Platform stacks that need broad rights are Tier 1 and isolated.

**Drift (designed in; operated post-handover)**
18. Scheduled drift detection (`plan -detailed-exitcode`, CloudFormation drift detection, Azure deployment what-if) raises findings. Console write access to production is limited to break-glass.

### 5.1.3 Recommended controls
- Policy tests (unit tests for Rego / Sentinel) in the policy repository.
- Infracost-style change previews to catch unexpected resource creation.
- Tagging policy (owner, data classification, environment) enforced in policy-as-code. Classification tags drive other policies, such as requiring a CMK.

### 5.1.4 Evidence
- State backend configuration and bucket/container policy.
- Sample PR showing scanner and policy results, and the plan/apply job separation.
- Apply identity trust and permission policies.
- Module sources and lock files.
- List of policy exceptions with justifications.

---

## 5.2 Build and software supply chain

### 5.2.1 Threats

| ID | Threat (aligned to OWASP CI/CD Top 10) |
|---|---|
| BLD-T1 | **Poisoned pipeline execution**: untrusted PR code modifies the build and runs with the pipeline's secrets or identity |
| BLD-T2 | **Insufficient flow control**: code reaches prod without review or approval |
| BLD-T3 | **Dependency confusion / typosquatting / compromised upstream packages** |
| BLD-T4 | **Compromised third-party CI actions or plug-ins** (for example mutable tags repointed to malicious code) |
| BLD-T5 | **Over-privileged or long-lived pipeline credentials** that can be exfiltrated |
| BLD-T6 | **Shared, persistent runners** leaking secrets or artefacts between jobs, or being persistently compromised |
| BLD-T7 | **Artefact tampering** between build and deploy (registry write access, tag mutation) |
| BLD-T8 | **Insufficient logging** of pipeline activity, making tampering undetectable |
| BLD-T9 | Vulnerable base images or dependencies shipped to production |

### 5.2.2 Required controls

**Pipeline identity and secrets**
1. The pipeline authenticates to the cloud using **OIDC workload identity federation**, with **no static cloud keys**. The trust is conditioned on org/repo, branch/tag or environment claims (for example `sub: repo:org/app:environment:production`).
2. Separate identities per environment and per purpose (plan read-only; apply prod; push artefact). Non-prod pipelines cannot assume prod roles.
3. Pipeline secrets that remain (third-party tokens) are scoped to protected environments, never exposed to PR or fork builds, and masked in logs.

**Pipeline integrity**
4. Workflows triggered from untrusted contexts (forks, external PRs) run **without secrets and without cloud identity**. Privileged triggers such as `pull_request_target` are banned or tightly reviewed.
5. Third-party actions, orbs and plug-ins are **pinned to an immutable commit SHA or digest**, from an allow-list, and kept updated through automated PRs (Dependabot/Renovate).
6. Default pipeline token permissions set to **read-only** (for example `permissions: contents: read`), elevated per job.
7. Production deployments only from protected branches or tags, gated by environment protection rules (required reviewers, wait timers, and branch restrictions).

**Runners and build environment**
8. **Ephemeral, single-use runners** (fresh VM or container per job) for anything that touches production credentials or builds release artefacts.
9. Self-hosted runners sit in a dedicated, network-restricted account or segment. They are not shared between trust levels (public repos vs private; prod vs non-prod).
10. The build is hermetic or reproducible where practical. At minimum, the build environment is defined in code (runner image built by pipeline).

**Dependencies**
11. Dependencies are resolved through an **internal proxy or registry** (Artifactory / Nexus / CodeArtifact / Azure Artifacts / Artifact Registry) with upstream allow-listing and namespace protection against dependency confusion.
12. Lock files are committed, and installs use frozen or locked modes (`npm ci`, `pip --require-hashes`, `go.sum`).
13. **SCA** runs on every build with a blocking threshold (for example Critical with a known exploit, or on the CISA KEV list). Licence policy is applied.
14. Base images come from an approved, minimal, regularly rebuilt catalogue, and are pinned by digest.

**Artefacts**
15. An **SBOM** (SPDX or CycloneDX) is generated for every release artefact and stored alongside it.
16. Artefacts are **signed** (Sigstore cosign / Notation), and **build provenance** is generated (SLSA provenance / in-toto attestations). Target **SLSA Build L2** as the baseline and **L3** for Tier 1.
17. Registries have **immutable tags**, and push access is limited to the build identity. Deployment references artefacts **by digest**, not tag.
18. **Verification at deploy/admission.** The deploy stage or cluster admission controller verifies the signature and provenance (Binary Authorization, Kyverno verifyImages, Ratify, AWS Signer with Lambda code signing).
19. Container and artefact scanning runs at build, with a blocking threshold. Registry re-scanning after go-live is a handover item.

**Pipeline audit**
20. Pipeline run logs, approvals and deployment events are retained and centrally forwarded. Every production change is traceable to commit → build → artefact digest → approver → deploy.

### 5.2.3 Recommended controls
- OpenSSF Scorecard on critical repos and on key upstream dependencies.
- Two-person rule for changes to shared pipeline templates.
- SAST and secret scanning as blocking gates tuned for low false positives. DAST is run against pre-prod.

### 5.2.4 Evidence
- Pipeline definition files.
- OIDC trust policies for the pipeline roles.
- Runner configuration.
- Dependency proxy configuration.
- A sample SBOM, signature and provenance for a recent build, plus the admission or deploy verification policy.
- Environment protection settings.

---

## 5.3 Configuration

Configuration covers everything that changes system behaviour without a code change: application config, feature flags, OS and middleware settings, Kubernetes manifests and Helm values, managed-service parameters, and secrets.

### 5.3.1 Threats

| ID | Threat |
|---|---|
| CFG-T1 | Insecure defaults left in place (debug on, default credentials, permissive CORS, TLS off) |
| CFG-T2 | **Environment bleed**: non-prod config or credentials used in prod, or prod data/secrets in non-prod |
| CFG-T3 | Unreviewed runtime config changes (console edits, `kubectl edit`, feature flag toggles) that bypass review |
| CFG-T4 | Secrets exposed through config channels (env vars in images, ConfigMaps, logs, crash dumps) |
| CFG-T5 | Configuration drift from the approved baseline over time |
| CFG-T6 | Config store over-exposure: every workload can read every parameter |
| CFG-T7 | Feature flags or remote config used to enable unreviewed security-relevant behaviour |

### 5.3.2 Required controls

**Baselines**
1. Each component type has a **security configuration baseline**: CIS Benchmarks for the OS, Kubernetes, databases and cloud foundations; vendor hardening guides for managed services. Baselines are expressed **as code**: policy-as-code, image build scripts, Helm defaults, admission policies.
2. Golden images and base containers are built by pipeline with the baseline applied and tested (for example with CIS-CAT, InSpec or Goss), then versioned and signed.

**Configuration as code and promotion**
3. All configuration is version-controlled and changed via PR, using the same controls as §5.0. A GitOps model (Argo CD / Flux) is preferred for Kubernetes, with **the repo as the source of truth and automatic reconciliation of drift**.
4. **Environment separation.** Config is structured as a common base plus per-environment overlays (Kustomize overlays, Helm values per environment, separate parameter paths). Prod overlays can only be changed by approved reviewers.
5. **Promotion, not re-creation.** The same artefact (by digest) moves through environments, and only environment-specific config differs. Config changes to prod follow the same approval gate as code.

**Secrets in configuration**
6. Configuration holds **references** to secrets, not values. Secrets are injected at runtime from the secret store (CSI Secrets Store driver, External Secrets Operator, native integrations). Kubernetes Secrets are encrypted with KMS if used at all.
7. No secrets in container images, environment variables baked at build time, ConfigMaps, or IaC outputs. This is enforced by scanning images and manifests.

**Config stores**
8. Parameter and config stores (SSM Parameter Store, App Configuration, Secret Manager, Consul) use **hierarchical paths per application and environment**. IAM restricts each workload to its own path.
9. Security-relevant settings (auth enforcement, TLS, logging level, debug endpoints) are **not toggleable** by runtime feature flags. Where flags are needed, flag changes are audited and require approval in prod.

**Runtime change control and drift**
10. Human write access to production runtime config (console, `kubectl`, SSH) is removed or break-glass-only. Changes flow through the pipeline.
11. Configuration compliance is continuously evaluated *by design*: AWS Config rules / Azure Policy audit / GCP Security Health Analytics / Kubernetes admission plus background scans. Findings route to the owning team. Operating this is a handover item.

### 5.3.3 Recommended controls
- Configuration schema validation in CI (JSON Schema, CUE, `kubeconform`).
- Canary or staged rollout for config changes, with automated rollback.
- Periodic rebuild of long-lived infrastructure from code, to prove reproducibility and remove accumulated drift.

### 5.3.4 Evidence
- Baseline definitions and the tests that prove them.
- GitOps or config repo structure and its protections.
- Parameter-store path layout and the IAM policies that scope it.
- Secret injection mechanism.
- Record of break-glass access to prod config.
- Evaluation rules for config compliance.

---

## 5.4 Maturity model for the DLC

Use this to set targets and to show the risk owner where the system sits. Tier 1 systems must meet **Level 3** before go-live. Tier 2 must meet **Level 2**.

| Capability | Level 1: Initial | Level 2: Managed | Level 3: Defined | Level 4: Optimised |
|---|---|---|---|---|
| IaC coverage | Partial; some ClickOps | All prod infra in IaC | IaC with golden modules; console write removed | Periodic rebuild proves reproducibility |
| IaC policy | Ad-hoc scanning | Scanner in PR, non-blocking | Blocking static + plan-time policy + cloud guardrails | Policy tested; exceptions time-bound and reported |
| State | Local or unprotected | Remote, encrypted | CMK, per-env, least-privilege access | Secretless state (ephemeral/write-only) |
| Pipeline identity | Static keys | Scoped static keys, rotated | OIDC federation, per-env roles | OIDC with fine-grained claim conditions and permission boundaries |
| Runners | Shared persistent | Segregated persistent | Ephemeral for prod/release | Hardened, hermetic, isolated per trust level |
| Supply chain | No SCA | SCA + lock files | Internal proxy, pinned actions, SBOM | Signed + provenance (SLSA L3), verified at admission |
| Config | Manual | Versioned, manually applied | Config as code, pipeline-applied, secret refs | GitOps with auto drift reconciliation |
| Traceability | Partial | Deploy logs retained | Commit → artefact → deploy traceable | Attestation chain verifiable end to end |
