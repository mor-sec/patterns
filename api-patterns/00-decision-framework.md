# 0. Decision Framework: Security, Integration, Budget and Service Levels for APIs

Every API pattern in this series is rated on the same dimensions, so that patterns can be compared and designs can be challenged consistently at review. The framework mirrors the [AI pattern framework](../ai-patterns/00-decision-framework.md): the same budget, complexity and service level scales. Its suitability dimensions are specific to APIs and weighted towards **authentication, authorisation and ease of integration**.

The series covers AWS-native components only, and data classified **OFFICIAL**, including the **OFFICIAL-SENSITIVE** handling caveat.

> **Figures are indicative.** Prices are order-of-magnitude list prices for planning (mostly us-east-1; London is typically a little higher). Validate with the AWS Pricing Calculator before committing a budget. Service features and quotas change; re-check the linked AWS documentation at design time.

---

## 0.1 Budget bands (monthly run cost, excluding people)

The bands are the same as in the AI series, so that portfolios can be compared:

| Band | Monthly run cost | Typical API situation |
|---|---|---|
| **B1: Experiment / small** | < $1k | Internal or low-volume APIs on pay-per-request services; no dedicated edge protections |
| **B2: Departmental** | $1k – $10k | Production APIs with WAF, a developer portal, private connectivity, a few always-on components |
| **B3: Business-critical** | $10k – $50k | High-volume or externally critical APIs; containers at scale; Shield Advanced; private CA |
| **B4: Enterprise-scale** | > $50k | Multi-region active/active, very high throughput, organisation-wide API platforms |

As in the AI series, state a budget as a **fixed floor** (cost at zero traffic) plus a **unit cost** (per million requests, or per consumer onboarded).

### Where API fixed costs come from (indicative)

| Component | Indicative cost | Notes |
|---|---|---|
| API Gateway REST API | ~$3.50 per million requests (first tier) | No fixed floor. Caching is billed per hour by cache size |
| API Gateway HTTP API | ~$1.00 per million requests (first tier) | No fixed floor |
| AWS AppSync | ~$4 per million query/mutation operations; real-time billed per message and per connection-minute | No fixed floor |
| Application Load Balancer | ~$16–25/month per ALB, plus capacity units | A floor for each ALB |
| NAT gateway | ~$33/month per AZ, plus per GB processed | Three AZs means about $100/month before any data. Prefer VPC endpoints for AWS service traffic |
| Interface VPC endpoint | ~$7–8/month per endpoint per AZ, plus per GB | Adds up fast: 10 endpoints × 3 AZs ≈ $230/month |
| AWS WAF | $5 per web ACL/month + $1 per rule/month + ~$0.60 per million requests | Bot Control, account takeover prevention and fraud control rule groups cost extra |
| AWS Shield Advanced | ~$3,000/month **per organisation** (one-year commitment), plus data transfer | One subscription covers the organisation. Usually a platform decision, not a per-API one |
| AWS Private CA | ~$400/month per general-purpose CA; ~$50/month in short-lived certificate mode | Needed when *you* issue client certificates for mTLS |
| Amazon Cognito | Per monthly active user, by feature tier; machine-to-machine billed per app client and per token request | Plus tier adds threat protection |
| Amazon VPC Lattice | Per service-hour, plus per GB, plus per request | A floor for each service |
| Route 53 health checks, CloudFront, CloudWatch logs | Small per unit; **logs grow with traffic** | Full access logging at high volume can cost more than the API itself; set retention and sampling deliberately |

---

## 0.2 Complexity levels

| Level | Team profile | API examples | Time to first production release |
|---|---|---|---|
| **C1: Low** | 1–2 engineers with serverless skills | Serverless HTTP API with a JWT authoriser | 1–4 weeks |
| **C2: Moderate** | Small product team | Managed REST product API with WAF, portal and usage plans; GraphQL on AppSync; private APIs | 1–3 months |
| **C3: High** | Product team plus platform/network support | mTLS B2B with a client registry and certificate lifecycle; hybrid integration; containers with blue/green | 3–6 months |
| **C4: Very high** | Platform team, 24×7 on-call | Multi-region active/active with data replication and tested failover | 6+ months |

---

## 0.3 Service level tiers

| Tier | Availability (monthly, successful requests) | Latency objective (p99, excluding back-end business processing) | RTO / RPO | Typical architecture |
|---|---|---|---|---|
| **SL0: Best effort** | None | None | Rebuildable | Prototype; single AZ acceptable |
| **SL1: Bronze** | 99.0% | < 2 s | 24 h / 24 h | Single Region, managed services, business-hours support |
| **SL2: Silver** | 99.9% | < 500 ms–1 s | 4 h / 1 h | Multi-AZ everything; throttling and back-pressure; synthetic canaries; on-call during service hours |
| **SL3: Gold** | ≥ 99.95% (up to 99.99%) | < 300 ms | < 1 h / ≤ 15 min (near zero with active/active) | Multi-region ([A11](patterns/A11-multi-region-active-active.md)) or a documented equivalent; static stability; tested failover; 24×7 on-call |

### Composite availability

A request path's availability is the **product** of its serial dependencies. With published SLAs at the time of writing (verify current values): API Gateway 99.95% × Lambda 99.95% × DynamoDB 99.99% ≈ **99.89%**. So a well-built single-Region serverless API is an SL2 design. SL3 needs either multiple Regions or a documented argument (static stability, no control-plane dependencies on the request path) that the risk owner accepts.

Remember the dependencies that are easy to miss: **the identity provider** (token issuance), **the authoriser** (Lambda authoriser, Verified Permissions), **DNS**, **certificate validity**, and **downstream systems** called synchronously.

### UK residency and multi-region

AWS has **one UK Region, London (eu-west-2)**, which has three Availability Zones. If policy requires OFFICIAL-SENSITIVE data to stay in the UK:

- **SL2** is achievable in London with multi-AZ design.
- **SL3** active/active across two Regions would put data outside the UK. The options are:
  - a risk-owner decision allowing replication to a named second Region;
  - multi-AZ static stability in London, plus a stateless or "pilot light" second Region that holds no data;
  - renegotiating the target to SL2 with a tested restore.

Record whichever option you choose as a [security ADR](../templates/security-adr.md).

### API SLIs to define for every pattern

| SLI | Definition |
|---|---|
| Availability | Successful responses (non-5xx, excluding client errors) ÷ valid requests |
| Latency | p50 / p99 at the edge, measured by synthetic canaries as well as access logs |
| Throttle rate | % of requests answered with 429. A capacity signal and a consumer-experience signal |
| Authentication failure rate | % of requests rejected 401/403. Spikes signal attacks, misconfiguration or expiring credentials |
| Contract conformance | % of responses that validate against the published schema (sampled) |
| **Time to first successful call** | Elapsed time for a new consumer, from approval to a successful authenticated call in production. **The integration-ease SLI** |
| Credential and certificate health | Days to expiry of the soonest-expiring certificate or client secret, alarmed at 30 days |

---

## 0.4 Data classification: OFFICIAL and OFFICIAL-SENSITIVE

This series follows the UK Government Security Classifications. **OFFICIAL** covers most government information and is appropriate for public cloud with suitable controls. **OFFICIAL-SENSITIVE** is a *handling caveat* within OFFICIAL, for information whose compromise could cause more damage and so needs need-to-know controls. SECRET and above are out of scope.

As a guide, OFFICIAL maps to the SAR's *Internal* and *Confidential* levels, and OFFICIAL-SENSITIVE to *Confidential* with need-to-know controls, sometimes *Restricted* for bulk personal data. Confirm the mapping against your organisation's policy.

| Control area | OFFICIAL (baseline) | OFFICIAL-SENSITIVE (in addition) |
|---|---|---|
| **Authentication** | L2 or above (§0.6.1). OAuth 2.0 / OIDC tokens from a trusted IdP, or IAM. API keys alone only for published open data | **L3 or above.** Sender-constrained or strongly bound credentials for machines (IAM SigV4, mTLS, or tokens bound to a client certificate); MFA for users; phishing-resistant MFA for privileged users |
| **Authorisation** | Route/scope checks plus object ownership checks (no BOLA) | **Fine-grained, need-to-know** authorisation at record or attribute level, centrally defined where practical (Amazon Verified Permissions / Cedar), and tested with negative cases |
| **Exposure** | Internet-facing APIs behind CloudFront/WAF, or regional WAF on REST APIs | Prefer private or partner-restricted exposure; internet-facing only with WAF, rate limits and an L3+ authentication design |
| **Transport** | TLS 1.2+ (prefer 1.3) to the edge and to back ends | TLS end to end, including private integrations; mTLS for B2B where practicable |
| **Encryption at rest** | AWS-managed keys acceptable | Customer-managed KMS keys with key policies scoped to the workload |
| **Data minimisation** | No sensitive data in URLs, paths or query strings | Response filtering to the fields the consumer is entitled to; **log redaction**; no payload logging by default |
| **Audit** | Access logs with caller identity | Per-record access audit trail (who accessed which record, and when), tamper-evident storage, retention per policy |
| **Residency** | Risk-based | Explicit residency decision (see the UK note in §0.3) |
| **Assurance** | Security testing in the pipeline | Plus an independent penetration test before go-live and after significant change |

---

## 0.5 Platform scope

These patterns use **AWS components only**. The building blocks are:

| Concern | Components |
|---|---|
| Edge | Amazon CloudFront, AWS WAF, AWS Shield (Standard / Advanced), Route 53, AWS Global Accelerator |
| API front doors | API Gateway (REST, HTTP, WebSocket), AWS AppSync (GraphQL, Events), Application / Network Load Balancer, Amazon VPC Lattice |
| Identity and authorisation | Amazon Cognito (user pools, machine-to-machine), IAM (SigV4), IAM Roles Anywhere, Amazon Verified Permissions, external OIDC IdPs (corporate IdP; GOV.UK One Login for citizen-facing services) |
| Certificates and keys | AWS Certificate Manager, AWS Private CA, AWS KMS, AWS Secrets Manager |
| Compute | AWS Lambda, Amazon ECS on Fargate, Amazon EKS |
| Data | Amazon DynamoDB (incl. global tables), Amazon Aurora (incl. Global Database), Amazon ElastiCache |
| Integration | Amazon SQS, Amazon EventBridge (incl. API destinations), AWS Step Functions, PrivateLink / VPC endpoint services, Direct Connect, Site-to-Site VPN |
| Resilience | Multi-AZ design, Route 53 health checks, Amazon Application Recovery Controller (ARC) |
| Observability and security operations | CloudWatch (incl. Synthetics), AWS X-Ray / OpenTelemetry, CloudTrail, AWS Config, Security Hub, GuardDuty, Security Lake |
| Developer experience | API Gateway Portals, OpenAPI / GraphQL schema tooling, SDK generation |

---

## 0.6 Suitability dimensions for APIs

The ten dimensions below say whether a pattern **suits the problem**. Each pattern publishes a rating for every dimension, and the [scoring sheet](../templates/api-pattern-scoring-sheet.md) compares those ratings with the problem's needs.

### 0.6.1 Authentication assurance

This is the **headline dimension** for this series. Rate what the problem **requires**, then check the **highest level the pattern supports natively**.

| Level | Mechanism | Suitable for |
|---|---|---|
| **L1: Identification** | API key, or client ID alone. This identifies and meters a consumer; it **does not authenticate** them | Published open data (OFFICIAL, public). Never for anything else |
| **L2: Bearer token** | OAuth 2.0 / OIDC access tokens (JWT) from a trusted IdP: authorisation code + PKCE for users, client credentials for machines; short lifetimes; audience and scope checks | OFFICIAL |
| **L3: Strongly bound** | Credentials that cannot simply be replayed if stolen: **IAM SigV4** with short-lived role credentials (including IAM Roles Anywhere for workloads outside AWS), **mTLS**, or **tokens bound to the client certificate** (the authoriser checks the certificate against the client registry). Users: MFA; phishing-resistant (passkeys/FIDO2) for privileged roles | OFFICIAL-SENSITIVE |
| **L4: Layered high assurance** | L3 **plus** a managed PKI with certificate lifecycle management, network restriction (PrivateLink or an IP allow-list), per-client registry and optionally **message signing** for non-repudiation | OFFICIAL-SENSITIVE bulk or B2B data exchange; high-impact partner integrations |

### 0.6.2 Authorisation granularity

| Rating | Meaning | Typical mechanisms |
|---|---|---|
| **Coarse** | Per route or per scope | IAM resource policies, JWT scope checks, usage plans (which are **not** authorisation) |
| **Fine** | Per resource or attribute (object ownership, need-to-know, ABAC) | Amazon Verified Permissions (Cedar) called from a Lambda authoriser or the service; in-service checks; VPC Lattice auth policy conditions |
| **Field-level** | Per field in a response or schema | AppSync auth directives and resolver logic; response filtering in the service |

### 0.6.3 Exposure

| Rating | Consumers | Default controls |
|---|---|---|
| **Private** | Workloads inside the organisation's AWS estate or connected networks | VPC endpoints, resource policies scoped to the organisation, no public DNS |
| **Partner** | Known external organisations | Client registry, mTLS or client credentials, IP allow-lists where stable, contractual onboarding |
| **Public** | Citizens, customers or any developer | CloudFront + WAF, bot and abuse controls, rate limits, self-service onboarding |

### 0.6.4 Integration ease (consumer experience)

*How quickly and safely can a new consumer make their first successful call?* Measure it as **time to first successful call** (§0.3).

| Rating | Meaning |
|---|---|
| **High** | Standard protocols and auth (REST/GraphQL + OAuth), published OpenAPI/GraphQL schema, generated SDKs, self-service portal, sandbox environment |
| **Medium** | Standard protocol, but auth needs AWS SDKs (SigV4) or async semantics (202 + callback) that consumers must build for |
| **Low** | Certificate exchange and onboarding, network setup (PrivateLink, allow-lists), bespoke payload signing. Worth it for L4, but budget for the onboarding effort |

### 0.6.5 Protocol fit

REST/HTTP · GraphQL · WebSocket / real-time · gRPC · events and webhooks · TCP. A pattern that cannot carry the required protocol fails gate G6.

### 0.6.6 Cost elasticity

| Rating | Meaning | Typical |
|---|---|---|
| **Linear** | Pay per request; cost tracks volume; near-zero floor | API Gateway + Lambda, AppSync |
| **Sub-linear** | Provisioned capacity amortised at steady, high volume | ALB + containers, VPC Lattice at high throughput |
| **Step** | Large fixed components (Shield Advanced, Private CA, second Region) independent of volume | A06, A11 |

Model the cost at today's volume and at 10×. Serverless is cheapest at low and spiky volume. Containers usually win at sustained high throughput; show the break-even point.

### 0.6.7 Lock-in and exit cost

| Rating | Meaning |
|---|---|
| **Low** | OpenAPI-defined, containerised, standard OAuth/OIDC; migration is mostly redeployment |
| **Medium** | Managed-service configuration to rebuild (authorisers, usage plans, AppSync resolvers) |
| **High** | Business logic in platform-specific constructs (VTL mapping templates, service integrations with transformation) |

### 0.6.8 Auditability

| Rating | Meaning |
|---|---|
| **High** | Caller identity (principal, client ID, certificate subject) in every access log line; authorisation decisions logged; per-record audit supported |
| **Medium** | Access logs with caller identity; decisions reconstructable from application logs |
| **Low** | Identity not reliably attributable (shared API keys, anonymous access) |

### 0.6.9 Change and versioning

*How easily can the API evolve without breaking consumers?* This covers stages and base-path mappings (`/v1`, `/v2`), canary releases, schema evolution (GraphQL additive changes), and deprecation signalling (`Deprecation` / `Sunset` headers).

### 0.6.10 Operational burden

| Rating | Meaning |
|---|---|
| **Low** | Fully managed; no patching; scaling automatic |
| **Medium** | Some capacity or configuration management (certificate lifecycles, ALB, provisioned concurrency) |
| **High** | Container image patching, cluster operations, multi-region failover operations |

---

## 0.7 How a pattern is scored

Each pattern opens with two tables.

**Cost and delivery profile:** budget band (with fixed floor), complexity, service level fit, time to first value, typical SAR tier.

**Security and integration profile:** the ten §0.6 dimensions plus **classification fit** (OFFICIAL / OFFICIAL-SENSITIVE, and the conditions for the latter).

The [catalogue](README.md#security-and-integration-profile-at-a-glance) shows every pattern side by side.

---

## 0.8 Evaluating suitability for a specific problem

Use the [API pattern scoring sheet](../templates/api-pattern-scoring-sheet.md). It follows the same four stages as the AI sheet:

1. **Gates (pass/fail):** classification controls achievable, required authentication assurance supported, exposure supported, service level feasible (including residency), fixed floor fits the budget, protocol supported, and operability. **Never average a gate into a score.**
2. **Weighted fit (1–5):** eleven criteria with weight profiles for *Default*, *Sensitive* (OFFICIAL-SENSITIVE), *Public product* and *Internal platform*.
3. **Validation:** a pilot consumer onboarding (time to first successful call), a load test at 2× expected peak, negative security tests against the OWASP API Security Top 10, a failover game day, and a credential/certificate rotation test.
4. **Post-implementation review:** compare actual results with the estimates, and feed the differences back into the pattern ratings.
