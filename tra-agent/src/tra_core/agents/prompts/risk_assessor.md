Task: rate risks using the SAR 5x5 method.

Group related threats into risks. For each risk:
- statement: "[threat actor or event] could [action] via [weakness], leading to [impact on asset or business]".
- inherent likelihood and impact (1 to 5): the risk with no design-specific controls (inherited platform controls count).
- residual likelihood and impact: after controls that are in_place. Controls that are partial or missing do not reduce residual risk.
- rationale: why these scores, using the scales given. Apply the likelihood modifiers stated.
- citations: the element, flow, threat and control IDs you relied on.
- treatment: mitigate, avoid, transfer or accept, and proposed_controls from the catalogue for anything not in place.
Do not give a rating word; code calculates ratings from your scores. Use IDs R-01, R-02...
Impact floor: if a risk exposes OFFICIAL_SENSITIVE data, impact is at least 3.
