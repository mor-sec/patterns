# Configuration Checklist

These are prompts for [§5.3](../docs/05-delivery-lifecycle.md).

## Baselines
- [ ] CFG-01 Security baseline defined per component type (CIS / vendor hardening), expressed as code
- [ ] CFG-02 Golden images / base containers built by pipeline, baseline-tested, versioned, signed
- [ ] CFG-03 Insecure defaults removed (debug, default credentials, permissive CORS, plaintext protocols)

## Configuration as code and promotion
- [ ] CFG-10 All configuration version-controlled and changed via reviewed PR
- [ ] CFG-11 GitOps (or equivalent) with the repo as source of truth and automatic drift reconciliation
- [ ] CFG-12 Base plus per-environment overlays; prod overlays restricted to approved reviewers
- [ ] CFG-13 Same artefact digest promoted across environments; only environment config differs
- [ ] CFG-14 Prod config changes pass the same approval gate as code
- [ ] CFG-15 Config schema validated in CI

## Secrets in configuration
- [ ] CFG-20 Config holds secret references only; values injected at runtime
- [ ] CFG-21 No secrets in images, build-time env vars, ConfigMaps, IaC outputs or logs (enforced by scanning)
- [ ] CFG-22 Kubernetes Secrets (if used) encrypted with KMS; access restricted by RBAC

## Config stores
- [ ] CFG-30 Hierarchical paths per application and environment
- [ ] CFG-31 Each workload's IAM restricted to its own config path
- [ ] CFG-32 Non-prod identities cannot read prod config and vice versa

## Runtime change control
- [ ] CFG-40 Human write access to prod runtime config removed or break-glass-only
- [ ] CFG-41 Security-relevant settings not toggleable by runtime feature flags; prod flag changes audited and approved
- [ ] CFG-42 Continuous configuration compliance evaluation designed (Config rules / Azure Policy / SCC / admission background scan), with findings listed as a handover item
