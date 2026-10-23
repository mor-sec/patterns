Task: identify threats using STRIDE per element, and MITRE ATLAS for AI elements.

You are given the system model, the STRIDE categories that apply to each element and flow, and candidate threats from the threat library.
- Consider every element and every boundary-crossing flow. Use only the STRIDE categories listed as applicable for that element.
- Prefer adapting a library threat (set library_ref) over inventing one; invent one only when the design has a threat the library does not cover.
- For AI elements, include the relevant ATLAS technique IDs from the library entries.
- Write each threat statement specifically for this design: name the component, the actor and the weakness.
- Give evidence: what in the design makes this threat credible (or the absence of a control the design should mention).
- Use IDs T-01, T-02... in order. One threat may carry several STRIDE categories.
If reviewer notes are present, address them first.
