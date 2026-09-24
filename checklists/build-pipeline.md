# Build and Supply Chain Checklist

These are prompts for [§5.2](../docs/05-delivery-lifecycle.md). 🛑 = a hard stop from §2.3.

## Pipeline identity and secrets
- [ ] BLD-01 🛑 Cloud authentication via OIDC federation; no static cloud keys
- [ ] BLD-02 OIDC trust conditioned on org / repo and branch or environment (`sub` claim)
- [ ] BLD-03 Separate identities per environment and purpose (plan / apply / push); non-prod cannot assume prod
- [ ] BLD-04 Remaining secrets scoped to protected environments; never exposed to PR or fork builds
- [ ] BLD-05 Default pipeline token permissions read-only; elevated per job

## Pipeline integrity and flow control
- [ ] BLD-10 Untrusted-context workflows run with no secrets or cloud identity; privileged PR triggers banned or reviewed
- [ ] BLD-11 Third-party actions / plug-ins pinned by SHA or digest from an allow-list; update automation in place
- [ ] BLD-12 🛑 Prod deploys only from protected branches or tags with environment approval rules
- [ ] BLD-13 Pipeline definitions and shared templates under CODEOWNERS; shared templates pinned

## Runners
- [ ] BLD-20 Ephemeral single-use runners for prod-credentialed and release jobs
- [ ] BLD-21 Self-hosted runners isolated by trust level, in a restricted network segment
- [ ] BLD-22 Runner images built from code and kept up to date

## Dependencies
- [ ] BLD-30 Dependencies resolved via an internal proxy with upstream allow-listing
- [ ] BLD-31 Namespace protection against dependency confusion
- [ ] BLD-32 Lock files committed; frozen / hash-verified installs
- [ ] BLD-33 SCA blocking gate (for example Critical+exploitable / KEV); licence policy
- [ ] BLD-34 Base images from an approved catalogue, pinned by digest
- [ ] BLD-35 SAST and secret scanning in the pipeline

## Artefacts and provenance
- [ ] BLD-40 SBOM generated and stored for every release artefact
- [ ] BLD-41 Artefacts signed (cosign / Notation)
- [ ] BLD-42 Build provenance generated (SLSA L2 baseline; L3 for Tier 1)
- [ ] BLD-43 Registry tags immutable; push limited to the build identity
- [ ] BLD-44 Deploy references artefacts by digest
- [ ] BLD-45 Signature / provenance verified at deploy or admission
- [ ] BLD-46 Image / artefact vulnerability scan with a blocking threshold at build

## Traceability
- [ ] BLD-50 Pipeline logs, approvals and deploy events retained and forwarded centrally
- [ ] BLD-51 Every prod change traceable: commit → build → digest → approver → deploy
