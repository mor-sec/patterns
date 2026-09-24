# IaC Checklist

These are prompts for [§5.0 and §5.1](../docs/05-delivery-lifecycle.md). 🛑 = a hard stop from §2.3.

## Source control (IaC repositories)
- [ ] IAC-01 🛑 Protected branches; independent review required; no admin bypass
- [ ] IAC-02 CODEOWNERS covers IaC, IAM, network, policy and pipeline paths
- [ ] IAC-03 Force-push and branch deletion disabled
- [ ] IAC-04 Secret push protection enabled
- [ ] IAC-05 Signed commits (required for Tier 1)

## Authoring
- [ ] IAC-10 🛑 All production infrastructure defined in IaC; ClickOps is not the normal path
- [ ] IAC-11 Golden / approved modules used; deviations recorded as ADRs
- [ ] IAC-12 Modules and providers pinned to exact versions; lock file with hashes committed
- [ ] IAC-13 Modules and providers sourced only from an approved registry or mirror
- [ ] IAC-14 No secrets in source, variables, `tfvars` or parameter files
- [ ] IAC-15 IaC-created secrets generated in the secret store, or kept out of state (ephemeral / write-only)
- [ ] IAC-16 Same modules across environments; differences only in variables and backend
- [ ] IAC-17 Mandatory tags (owner, environment, data classification) enforced

## State
- [ ] IAC-20 🛑 Remote state encrypted (CMK) with access control; versioned; locking enabled
- [ ] IAC-21 One state per environment per component
- [ ] IAC-22 Prod state readable and writable only by the apply identity and break-glass
- [ ] IAC-23 State backend in a protected account, not writable by workload runtime identities

## Policy-as-code
- [ ] IAC-30 Static IaC scanning on every PR; high-severity failures block merge
- [ ] IAC-31 Plan-time policy evaluation (OPA / Sentinel / cfn-guard) before apply
- [ ] IAC-32 Exceptions inline, justified, ticketed and reviewable; no global disables
- [ ] IAC-33 Cloud-native preventive guardrails back up pipeline policy
- [ ] IAC-34 Policies version-controlled and tested

## Plan and apply
- [ ] IAC-40 PR plan uses a read-only identity; apply identity is separate and only used from protected branches
- [ ] IAC-41 Apply consumes the exact reviewed plan artefact
- [ ] IAC-42 🛑 Production apply requires approval by someone other than the author
- [ ] IAC-43 Untrusted fork / PR plans run without cloud credentials
- [ ] IAC-44 Provisioners and external data sources restricted
- [ ] IAC-45 Apply identity scoped to the stack's resource types and accounts (permission boundary)

## Drift
- [ ] IAC-50 Human console write access to prod removed or break-glass-only
- [ ] IAC-51 Scheduled drift detection designed, with a findings route (listed as a handover item)
