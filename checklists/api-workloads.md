# API Workload Checklist

These are prompts for APIs built on the [API architecture patterns](../api-patterns/README.md). Use them alongside the [cloud architecture checklist](cloud-architecture.md). Items marked *(foundation)* are satisfied by inheritance when the API uses a reviewed [shared foundation](../api-patterns/01-shared-foundations.md).

## Pattern fit, budget and service levels
- [ ] API-01 Pattern(s) selected and recorded in an [API pattern selection record](../templates/api-pattern-selection.md), with lighter patterns considered and rejected for stated reasons
- [ ] API-02 Classification agreed (OFFICIAL / OFFICIAL-SENSITIVE) and the matching control baseline from [§0.4](../api-patterns/00-decision-framework.md#04-data-classification-official-and-official-sensitive) applied
- [ ] API-03 Budget stated as a fixed floor (incl. per-AZ endpoints, WAF, CA, organisation services) plus unit cost, at today's volume and at 10×
- [ ] API-04 Service level tier agreed, with SLIs for availability, p99 latency, throttle rate, auth failure rate and time to first successful call
- [ ] API-05 Composite availability calculated, including the identity provider, authoriser, DNS and synchronous downstreams; degraded mode defined for SL2+
- [ ] API-06 For SL3 with OFFICIAL-SENSITIVE data: residency decision recorded as a security ADR
- [ ] API-07 For Tier 1–2 or contested choices: [scoring sheet](../templates/api-pattern-scoring-sheet.md) completed and attached

## Authentication
- [ ] API-10 Required authentication assurance level (L1–L4) stated per consumer type, and met natively by the design
- [ ] API-11 API keys used only for metering/throttling, never as the sole authentication (except published open data)
- [ ] API-12 One credential (OAuth client, IAM role, certificate) per consumer system; none shared
- [ ] API-13 Token validation checks signature, issuer, audience, expiry, type and scopes; algorithm allow-list
- [ ] API-14 Access tokens short-lived; refresh tokens never sent to APIs; tokens never in browser storage, URLs or logs
- [ ] API-15 OFFICIAL-SENSITIVE: machine credentials strongly bound (SigV4, mTLS, or token bound to the certificate); users have MFA; privileged users have phishing-resistant MFA
- [ ] API-16 Credential and certificate lifecycle: rotation automated or scheduled; expiry alarmed at 30 days (60/30/7 for partner certificates); revocation tested

## Authorisation
- [ ] API-20 Deny-by-default function-level authorisation on every route/operation
- [ ] API-21 Object-level (ownership / need-to-know) checks on every request that touches a record; negative tests with other callers' identifiers
- [ ] API-22 Property-level controls: request allow-listing (no mass assignment) and response shaping; GraphQL field-level rules where applicable
- [ ] API-23 Lambda authoriser cache keys include every decision input; returned policies are no broader than the request
- [ ] API-24 Fine-grained policies (Verified Permissions/Cedar or equivalent) versioned, reviewed and tested like code
- [ ] API-25 Asynchronous processors re-check authorisation before acting

## Edge, network and exposure
- [ ] API-30 Internet-facing APIs behind CloudFront and/or WAF with managed rules, rate-based rules and size limits *(foundation)*
- [ ] API-31 Default `execute-api` endpoint disabled where custom domains are used; no route bypasses WAF or mTLS
- [ ] API-32 Origins accept traffic only from the intended front door (private integration, VPC origin, secret header)
- [ ] API-33 Private APIs: resource policy restricts `aws:SourceVpce` and `aws:PrincipalOrgID`; endpoint policies scoped
- [ ] API-34 CORS restricted to known origins; never wildcard with credentials
- [ ] API-35 TLS 1.2 minimum (1.3 preferred) at the edge and to back ends; hybrid links (Direct Connect) encrypted
- [ ] API-36 Egress from back ends controlled; no fetching of user-supplied URLs without an allow-list (SSRF)

## Data protection
- [ ] API-40 No sensitive data in paths, query strings or headers that are logged
- [ ] API-41 Customer-managed KMS keys for OFFICIAL-SENSITIVE data stores, queues, caches and logs
- [ ] API-42 Logs record metadata, not payloads; redaction where payload logging is unavoidable
- [ ] API-43 Events and webhooks carry minimal data ("thin events") for OFFICIAL-SENSITIVE content; payloads signed

## Resilience and performance
- [ ] API-50 Multi-AZ for every component; capacity sized for AZ loss (static stability)
- [ ] API-51 Layered throttling (stage/method, per-consumer usage plans, WAF rate rules, back-end concurrency); 429 with `Retry-After`
- [ ] API-52 Idempotency keys for non-idempotent writes; consumer retry guidance published
- [ ] API-53 Long-running work is asynchronous (A08), not held open against gateway timeouts
- [ ] API-54 GraphQL depth/complexity limits, pagination caps and payload size limits (unrestricted resource consumption)
- [ ] API-55 Load test at 2× expected peak and failover/AZ-loss game day completed before go-live

## Integration and lifecycle
- [ ] API-60 OpenAPI or GraphQL contract reviewed, linted in CI and published to the catalogue/portal
- [ ] API-61 Versioning and deprecation policy applied (base paths, `Deprecation`/`Sunset` headers, notice period)
- [ ] API-62 Consumer onboarding documented (portal, sandbox, credentials); time to first successful call measured with a pilot consumer
- [ ] API-63 Every API and stage in the inventory with an owner; unused versions and stages decommissioned

## Logging and audit
- [ ] API-70 Structured access logs with request ID and caller identity (principal / client ID / certificate subject) *(foundation)*
- [ ] API-71 OFFICIAL-SENSITIVE: per-record access audit trail, tamper-evident and retained per policy
- [ ] API-72 Alarms for 5xx, p99 latency, 429 and 401/403 anomalies, authoriser errors and credential expiry routed to the handover pack
- [ ] API-73 Synthetic canaries exercise authenticated critical journeys from outside the VPC
