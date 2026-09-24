"""Build the AI pattern scoring workbooks (blank template + worked example).

Source of truth for templates/ai-pattern-scoring.xlsx and
templates/ai-pattern-scoring-example.xlsx. Update PATTERNS when the ratings in
ai-patterns/README.md change, then rebuild and recalculate:

    python3 tools/build_ai_scoring_workbook.py templates
    # then open and save in Excel/LibreOffice (or run a headless recalc) so cached values exist
"""
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule, CellIsRule
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter as L

FONT = "Arial"
YELLOW = PatternFill("solid", fgColor="FFF2CC")
HEAD = PatternFill("solid", fgColor="1F3864")
SUB = PatternFill("solid", fgColor="D9E1F2")
GREY = PatternFill("solid", fgColor="F2F2F2")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="top", wrap_text=True)

def f(bold=False, color="000000", size=10, italic=False):
    return Font(name=FONT, bold=bold, color=color, size=size, italic=italic)

INPUT_FONT = f(color="0000FF")
LINK_FONT = f(color="008000")

def title(ws, text, sub=None):
    ws["A1"] = text
    ws["A1"].font = f(bold=True, size=14, color="1F3864")
    if sub:
        ws["A2"] = sub
        ws["A2"].font = f(italic=True, color="595959")

def header_row(ws, row, values, start_col=1):
    for i, v in enumerate(values):
        c = ws.cell(row=row, column=start_col + i, value=v)
        c.font = f(bold=True, color="FFFFFF")
        c.fill = HEAD
        c.alignment = CENTER
        c.border = BOX

def inp(cell, value=None, center=False):
    if value is not None:
        cell.value = value
    cell.fill = YELLOW
    cell.font = INPUT_FONT
    cell.border = BOX
    cell.alignment = CENTER if center else WRAP

def calc(cell, formula, link=False, bold=False, center=True):
    cell.value = formula
    cell.font = LINK_FONT if link else f(bold=bold)
    cell.border = BOX
    cell.alignment = CENTER if center else WRAP

def text(cell, value, bold=False, fill=None, center=False, italic=False):
    cell.value = value
    cell.font = f(bold=bold, italic=italic)
    cell.border = BOX
    cell.alignment = CENTER if center else WRAP
    if fill:
        cell.fill = fill

def widths(ws, spec):
    for col, w in spec.items():
        ws.column_dimensions[col].width = w

# --------------------------------------------------------------------------
# Reference data
# --------------------------------------------------------------------------
PATTERNS = [
    # id, name, budget, complexity, maxSL, maxE, data, evaluability, elasticity, lockin, explain, regfit, modelchg, review,
    # numeric: minBudget, minComplexity, maxSL, maxE (with controls), maxR (with controls)
    ("P01", "Serverless model invocation", "B1–B2", "C1", "SL2 (SL3 with uplift)", "E2 (E3 if every output reviewed)", "Low", "High", "Linear", "Low", "Low", "R1 (R2 assistive only)", "Medium", "None/Low", 1, 1, 3, 3, 2),
    ("P02", "Batch AI enrichment pipeline", "B1–B3", "C2", "SL2 (throughput)", "E3 (with review queue)", "Medium", "High", "Linear", "Low / High (Cortex)", "Medium", "R2 (with review)", "Medium", "Medium", 1, 2, 2, 3, 2),
    ("P03", "In-warehouse AI and prototyping (Snowflake)", "B1–B2", "C1", "SL1 (SL2 internal)", "E1–E2", "Medium", "Medium", "Linear", "High", "Medium", "R0–R1", "Low–Medium", "None", 1, 1, 2, 2, 1),
    ("P04", "Managed RAG (Bedrock Knowledge Bases)", "B1–B2", "C2", "SL2", "E2 (E3 advisory)", "Medium", "Medium", "Linear", "Medium", "Medium", "R1 (R2 assistive)", "Low–Medium", "Low", 1, 2, 2, 3, 2),
    ("P05", "Enterprise RAG platform", "B3–B4", "C3–C4", "SL3", "E3 advisory", "High", "Medium–High", "Sub-linear", "Low–Medium", "Medium", "R1 (R2 assistive)", "Low", "Low", 3, 3, 3, 3, 2),
    ("P06", "Knowledge graph RAG with Neo4j", "B2–B3", "C3", "SL2–SL3 (by Neo4j tier)", "E3 advisory", "High", "Medium", "Sub-linear (serving)", "Medium–High", "High", "R2 assistive", "Medium", "Medium", 2, 3, 3, 3, 2),
    ("P07", "Orchestrated agentic workflow", "B1–B2", "C2–C3", "SL2 (SL3 feasible)", "E3–E4 (approval bands)", "Medium", "High", "Linear", "Low–Medium", "High", "R2 best fit", "Low", "Medium–High", 1, 2, 3, 4, 2),
    ("P08", "Tool-using agent (bounded autonomy)", "B2–B3", "C3–C4", "SL2", "E2 (E3 with confirmed writes)", "Medium–High", "Low", "Super-linear", "Medium", "Low–Medium", "R1", "High", "Low–Medium", 2, 3, 2, 3, 1),
    ("P09", "Conversational analytics", "B1–B2", "C2", "SL2", "E2 (E3 with verification)", "High", "High", "Linear", "High (A) / Medium (B)", "High", "R1", "Low–Medium", "Low", 1, 2, 2, 3, 1),
    ("P10", "Customised and self-hosted models", "B3–B4", "C4", "SL3", "Inherits host pattern", "High", "High", "Sub-linear at high utilisation", "Low–High", "Low", "Adds training-data obligations", "Self-owned lifecycle", "Low", 3, 4, 3, "Inherits", "Inherits"),
    ("P11", "Predictive ML with a generative interface", "B2–B3", "C3", "SL3 (scoring path)", "E4 (with human oversight)", "High", "High", "Sub-linear", "Low–Medium", "High", "R2 best fit", "Low", "Medium", 2, 3, 3, 4, 2),
]
LABELS = [f"{p[0]} {p[1]}" for p in PATTERNS]
PR_FIRST, PR_LAST = 5, 5 + len(PATTERNS) - 1
PR_LABELS = f"'Pattern Ratings'!$C${PR_FIRST}:$C${PR_LAST}"

GATES = [
    ("G1", "Classification and residency", "Model access (incl. cross-region inference Regions), stores and platforms satisfy classification and residency"),
    ("G2", "Service level feasibility", "Composite availability of the serial path meets the tier; degraded mode exists for SL2+"),
    ("G3", "Consequence of error", "Pattern's max E-level ≥ problem's E-level, with the stated controls in the design"),
    ("G4", "Regulatory profile", "Pattern supports the problem's R-level; R3 fails all"),
    ("G5", "Fixed floor", "Fixed floor at the required service level fits the budget band"),
    ("G6", "Data prerequisites", "No prerequisite Absent; every Partial has an owner and a funded plan"),
    ("G7", "Operability", "Team can build and run the complexity level (or funded support), incl. on-call for SL2+"),
]

CRITERIA = [
    ("W1", "Task fit", "Shape does not match the task", "Matches most tasks; gaps need workarounds", "Designed for exactly this task shape", 15, 15, 15, 20),
    ("W2", "Unit cost and elasticity", "Exceeds band at target volume, or super-linear without limits", "Within band today; tight at 10×", "Comfortably within band at 10×", 10, 5, 20, 5),
    ("W3", "Complexity against team capacity", "≥ 2 levels above capacity", "1 level above, with funded support", "At or below capacity", 10, 5, 5, 15),
    ("W4", "Service level headroom", "Only just meets tier; no degraded mode", "Meets tier with tested degraded mode", "Exceeds tier; failure modes understood", 10, 5, 20, 0),
    ("W5", "Data readiness gap", "Several Partial prerequisites on the critical path", "One Partial prerequisite with a credible plan", "All prerequisites Ready", 10, 10, 5, 15),
    ("W6", "Evaluability", "Low; no scenario/human evaluation plan", "Medium; rubric plus human calibration", "High; golden set exists or is cheap", 10, 15, 10, 10),
    ("W7", "Explainability and auditability", "Below user/auditor need", "Meets need (citations or traces)", "Structured evidence beyond need", 10, 20, 5, 0),
    ("W8", "Lock-in / exit cost", "High; no mitigation", "Medium, or High with mitigations", "Low", 5, 5, 5, 5),
    ("W9", "Model-change resilience", "High sensitivity; no harness or fallback", "Medium; harness catches regressions", "Low; interchangeable fallbacks", 5, 5, 10, 0),
    ("W10", "Human review load against capacity", "> 80% of reviewer capacity", "50–80% of capacity", "< 50%, or no review needed", 5, 10, 0, 0),
    ("W11", "Time to value", "Beyond the business deadline", "Meets deadline with little slack", "Well within deadline", 5, 0, 0, 25),
    ("W12", "Value measurability", "No baseline; qualitative only", "Baseline can be sampled", "Baseline exists; metric instrumented", 5, 5, 5, 5),
]
PROFILES = ["Default", "Regulated", "Customer scale", "Prototype", "Custom"]
CAND = ["A", "B", "C"]


def build(example: bool, path: str):
    wb = Workbook()

    # ---------------------------------------------------------------- Guide
    g = wb.active
    g.title = "Guide"
    title(g, "AI Pattern Scoring Workbook", "Companion to templates/ai-pattern-scoring-sheet.md and ai-patterns/00-decision-framework.md §0.8")
    rows = [
        ("How to use", None),
        ("1. Problem", "Rate the problem first: consequence (E), regulatory (R), budget, service level, team capacity, data readiness. Choose a weight profile and up to three candidate patterns."),
        ("2. Gates", "Mark each gate PASS / FAIL / PENDING per candidate. Hints compare the pattern's published ratings with the problem profile; they suggest, you decide. Any FAIL eliminates the candidate."),
        ("3. Weights", "Weights come from the selected profile. For 'Custom', fill the Custom column (must total 100) and record the reason."),
        ("4. Scoring", "Score each criterion 1–5 using the anchors, with evidence. The Results block computes the weighted score (20–100), applies the task-fit cap and low-score rule, and ranks eligible candidates."),
        ("5. Validation", "Bake-off of the top two: enter targets and results. A candidate under the task-fit cap may be selected only if it meets the quality target here."),
        ("6. PIR", "Post-implementation review 3–6 months after go-live: estimates vs actuals. Material variances feed back into the pattern ratings."),
        ("Legend", None),
        ("Yellow fill, blue text", "Input cells: edit these only."),
        ("Black text", "Formulas: do not overwrite."),
        ("Green text", "Links pulled from another sheet."),
        ("Rules applied", None),
        ("Gates", "Never averaged into the score. A FAIL eliminates; PENDING keeps the verdict 'Gates incomplete'."),
        ("Bands", "≥ 75 strong fit · 60–74 acceptable with mitigations recorded · < 60 poor fit."),
        ("Task-fit cap", "W1 ≤ 2 → cannot be selected on weighted score alone; bake-off must meet the quality target."),
        ("Low-score rule", "Any score of 1 on a criterion weighted ≥ 10 needs a mitigation or explicit acceptance in the selection record."),
        ("Close calls", "Top two eligible scores within 5 points are a tie: decide on bake-off evidence and prefer the lower-complexity pattern."),
    ]
    r = 4
    for k, v in rows:
        if v is None:
            g.cell(row=r, column=1, value=k).font = f(bold=True, size=11, color="1F3864")
            r += 1
            continue
        text(g.cell(row=r, column=1), k, bold=True)
        text(g.cell(row=r, column=2), v)
        r += 1
    g["A12"].fill = YELLOW; g["A12"].font = f(bold=True, color="0000FF")
    g["A14"].font = f(bold=True, color="008000")
    widths(g, {"A": 24, "B": 110})

    # ------------------------------------------------------ Pattern Ratings
    pr = wb.create_sheet("Pattern Ratings")
    title(pr, "Published pattern ratings (reference)", "From ai-patterns/README.md. Numeric columns (grey) drive the gate hints. Update when the catalogue changes.")
    hdr = ["ID", "Pattern", "Label (used in dropdowns)", "Budget", "Complexity", "Max service level", "Max consequence", "Data demand",
           "Evaluability", "Cost elasticity", "Lock-in", "Explainability", "Regulatory fit", "Model-change sensitivity", "Human review",
           "Min budget band #", "Min complexity #", "Max SL #", "Max E # (with controls)", "Max R # (with controls)"]
    header_row(pr, 4, hdr)
    for i, p in enumerate(PATTERNS):
        rr = PR_FIRST + i
        vals = list(p[:14]) + list(p[14:])
        for j, v in enumerate(vals[:2]):
            text(pr.cell(row=rr, column=1 + j), v)
        calc(pr.cell(row=rr, column=3), f'=A{rr}&" "&B{rr}', center=False)
        for j, v in enumerate(vals[2:14]):
            text(pr.cell(row=rr, column=4 + j), v)
        for j, v in enumerate(vals[14:]):
            c = pr.cell(row=rr, column=16 + j)
            text(c, v, fill=GREY, center=True)
    widths(pr, {"A": 6, "B": 34, "C": 40, "D": 9, "E": 10, "F": 18, "G": 24, "H": 12, "I": 12, "J": 16, "K": 16,
                "L": 13, "M": 22, "N": 16, "O": 13, "P": 11, "Q": 11, "R": 9, "S": 12, "T": 12})
    pr.freeze_panes = "D5"

    # ------------------------------------------------------------- Problem
    pb = wb.create_sheet("Problem", 1)
    title(pb, "Stage 0: Problem profile", "Rate the problem before the patterns. Yellow cells are inputs.")
    header_row(pb, 4, ["Attribute", "Value", "Notes / evidence"])
    prob = [
        ("Solution / owner", None, None),
        ("Date / version", None, None),
        ("Scored by", None, "Solution architect + security architect; business owner for task fit and value"),
        ("Weight profile", "Default", "Default / Regulated / Customer scale / Prototype / Custom"),
        ("Consequence of error", None, "E1 low · E2 moderate · E3 high · E4 critical (§0.6.1)"),
        ("Regulatory profile", None, "R0 minimal · R1 transparency · R2 high-risk · R3 prohibited (§0.6.7)"),
        ("Data classification / residency", None, None),
        ("Budget band", None, "B1 <$1k · B2 $1–10k · B3 $10–50k · B4 >$50k per month"),
        ("Expected volume (today / at 10×)", None, None),
        ("Service level tier", None, "SL0–SL3 (§0.3)"),
        ("Team complexity capacity", None, "C1–C4 (§0.2)"),
        ("Data prerequisites (Ready / Partial / Absent each)", None, None),
        ("Reviewer capacity (hours/week)", None, None),
        ("Value baseline exists?", None, "Yes / Sampled / No"),
        ("Task shape", None, "Single-shot / Document / Multi-hop / Metric / Process / Open-ended / Prediction"),
    ]
    for i, (k, v, note) in enumerate(prob):
        rr = 5 + i
        text(pb.cell(row=rr, column=1), k, bold=True)
        inp(pb.cell(row=rr, column=2), v)
        text(pb.cell(row=rr, column=3), note, italic=True)
    # rows: 8 profile, 9 E, 10 R, 12 B, 14 SL, 15 C, 18 value baseline, 19 task shape
    text(pb.cell(row=21, column=1), "Candidate patterns", bold=True, fill=SUB)
    text(pb.cell(row=21, column=2), "Pattern (choose from list)", bold=True, fill=SUB)
    text(pb.cell(row=21, column=3), "Why it is a candidate", bold=True, fill=SUB)
    for i, c in enumerate(CAND):
        rr = 22 + i
        text(pb.cell(row=rr, column=1), f"Candidate {c}", bold=True)
        inp(pb.cell(row=rr, column=2))
        inp(pb.cell(row=rr, column=3))
    widths(pb, {"A": 40, "B": 44, "C": 70})
    dvs = [
        ('"Default,Regulated,Customer scale,Prototype,Custom"', "B8"),
        ('"E1,E2,E3,E4"', "B9"),
        ('"R0,R1,R2,R3"', "B10"),
        ('"B1,B2,B3,B4"', "B12"),
        ('"SL0,SL1,SL2,SL3"', "B14"),
        ('"C1,C2,C3,C4"', "B15"),
        ('"Yes,Sampled,No"', "B18"),
        ('"Single-shot,Document,Multi-hop,Metric,Process,Open-ended,Prediction"', "B19"),
        (PR_LABELS, "B22:B24"),
    ]
    for formula, rng in dvs:
        dv = DataValidation(type="list", formula1=formula if formula.startswith('"') else "=" + formula, allow_blank=True)
        pb.add_data_validation(dv)
        dv.add(rng)
    pb.freeze_panes = "A5"

    # ---------------------------------------------------------------- Gates
    gs = wb.create_sheet("Gates", 2)
    title(gs, "Stage 1: Gates (pass / fail)", "A FAIL eliminates the candidate. Hints are suggestions from the published ratings; the reviewer decides.")
    header_row(gs, 4, ["Gate", "Name", "Pass when…"])
    cand_cols = {"A": 4, "B": 7, "C": 10}
    for c, col in cand_cols.items():
        gs.merge_cells(start_row=3, start_column=col, end_row=3, end_column=col + 2)
        calc(gs.cell(row=3, column=col), f'=IF(Problem!$B${22 + CAND.index(c)}="","Candidate {c}",Problem!$B${22 + CAND.index(c)})', link=True, bold=True)
        header_row(gs, 4, ["Result", "Hint", "Evidence"], start_col=col)
    for i, (gid, name, cond) in enumerate(GATES):
        rr = 5 + i
        text(gs.cell(row=rr, column=1), gid, bold=True, center=True)
        text(gs.cell(row=rr, column=2), name, bold=True)
        text(gs.cell(row=rr, column=3), cond)
        for c, col in cand_cols.items():
            nm = f"Problem!$B${22 + CAND.index(c)}"
            m = f"MATCH({nm},{PR_LABELS},0)"
            def idx(colletter):
                return f"INDEX('Pattern Ratings'!${colletter}${PR_FIRST}:${colletter}${PR_LAST},{m})"
            lvl = lambda cell: f"VALUE(RIGHT({cell},1))"
            if gid == "G2":
                h = f'=IF({nm}="","",IFERROR(IF({lvl("Problem!$B$14")}<={idx("R")},"OK: pattern reaches SL"&{idx("R")},"LIKELY FAIL: pattern max is SL"&{idx("R")}),"Set service level tier"))'
            elif gid == "G3":
                h = f'=IF({nm}="","",IF(NOT(ISNUMBER({idx("S")})),"CHECK: inherits host pattern",IFERROR(IF({lvl("Problem!$B$9")}<={idx("S")},"OK with the pattern\'s stated controls","LIKELY FAIL: pattern supports up to E"&{idx("S")}),"Set consequence level")))'
            elif gid == "G4":
                h = f'=IF({nm}="","",IF(Problem!$B$10="R3","FAIL: prohibited use",IF(NOT(ISNUMBER({idx("T")})),"CHECK: inherits host pattern",IFERROR(IF({lvl("Problem!$B$10")}<={idx("T")},"OK with the pattern\'s stated controls","LIKELY FAIL: pattern supports up to R"&{idx("T")}),"Set regulatory profile"))))'
            elif gid == "G5":
                h = f'=IF({nm}="","",IFERROR(IF({idx("P")}<={lvl("Problem!$B$12")},"OK: floor typically fits","CHECK: floor typically needs B"&{idx("P")}&" or above"),"Set budget band"))'
            elif gid == "G7":
                h = (f'=IF({nm}="","",IFERROR(IF({idx("Q")}<={lvl("Problem!$B$15")},"OK: within team capacity",'
                     f'IF({idx("Q")}-{lvl("Problem!$B$15")}=1,"CHECK: 1 level above; needs funded support","LIKELY FAIL: "&({idx("Q")}-{lvl("Problem!$B$15")})&" levels above capacity")),"Set team capacity"))')
            else:
                h = f'=IF({nm}="","","Manual assessment")'
            inp(gs.cell(row=rr, column=col), None, center=True)
            calc(gs.cell(row=rr, column=col + 1), h, center=False)
            inp(gs.cell(row=rr, column=col + 2))
    sr = 5 + len(GATES) + 1  # 13
    text(gs.cell(row=sr, column=3), "Gate status", bold=True, fill=SUB)
    for c, col in cand_cols.items():
        rng = f"{L(col)}5:{L(col)}{4 + len(GATES)}"
        gs.merge_cells(start_row=sr, start_column=col, end_row=sr, end_column=col + 2)
        calc(gs.cell(row=sr, column=col),
             f'=IF(COUNTIF({rng},"FAIL")>0,"ELIMINATED",IF(COUNTIF({rng},"PASS")={len(GATES)},"ALL PASS","INCOMPLETE"))', bold=True)
    text(gs.cell(row=sr + 1, column=3), "PASS marked against a LIKELY FAIL / FAIL hint", bold=True, fill=SUB)
    for c, col in cand_cols.items():
        res = f"{L(col)}5:{L(col)}{4 + len(GATES)}"; hin = f"{L(col + 1)}5:{L(col + 1)}{4 + len(GATES)}"
        gs.merge_cells(start_row=sr + 1, start_column=col, end_row=sr + 1, end_column=col + 2)
        calc(gs.cell(row=sr + 1, column=col),
             f'=IF(SUMPRODUCT(({res}="PASS")*((LEFT({hin},6)="LIKELY")+(LEFT({hin},4)="FAIL")))=0,"None",'
             f'SUMPRODUCT(({res}="PASS")*((LEFT({hin},6)="LIKELY")+(LEFT({hin},4)="FAIL")))&" – justify in Evidence")')
        gs.conditional_formatting.add(f"{L(col)}{sr + 1}", FormulaRule(formula=[f'{L(col)}{sr + 1}<>"None"'], fill=PatternFill("solid", fgColor="FFEB9C")))
    dv = DataValidation(type="list", formula1='"PASS,FAIL,PENDING"', allow_blank=True)
    gs.add_data_validation(dv)
    for col in cand_cols.values():
        dv.add(f"{L(col)}5:{L(col)}{4 + len(GATES)}")
    last = f"L{sr}"
    gs.conditional_formatting.add(f"D5:{last}", CellIsRule(operator="equal", formula=['"FAIL"'], fill=PatternFill("solid", fgColor="F8CBAD")))
    gs.conditional_formatting.add(f"D5:{last}", CellIsRule(operator="equal", formula=['"ELIMINATED"'], fill=PatternFill("solid", fgColor="F8CBAD")))
    gs.conditional_formatting.add(f"D5:{last}", CellIsRule(operator="equal", formula=['"ALL PASS"'], fill=PatternFill("solid", fgColor="C6EFCE")))
    for col in cand_cols.values():
        hc = L(col + 1)
        gs.conditional_formatting.add(f"{hc}5:{hc}{4 + len(GATES)}",
                                      FormulaRule(formula=[f'LEFT({hc}5,6)="LIKELY"'], font=Font(name=FONT, color="C00000", bold=True)))
        gs.conditional_formatting.add(f"{hc}5:{hc}{4 + len(GATES)}",
                                      FormulaRule(formula=[f'LEFT({hc}5,4)="FAIL"'], font=Font(name=FONT, color="C00000", bold=True)))
    widths(gs, {"A": 6, "B": 22, "C": 42, "D": 10, "E": 30, "F": 28, "G": 10, "H": 30, "I": 28, "J": 10, "K": 30, "L": 28})
    gs.freeze_panes = "D5"

    # -------------------------------------------------------------- Weights
    ws = wb.create_sheet("Weights", 3)
    title(ws, "Weight profiles", "Selected profile is set on the Problem sheet. Only the Custom column is editable.")
    header_row(ws, 4, ["#", "Criterion"] + PROFILES + ["Selected"])
    for i, cr in enumerate(CRITERIA):
        rr = 5 + i
        text(ws.cell(row=rr, column=1), cr[0], bold=True, center=True)
        text(ws.cell(row=rr, column=2), cr[1])
        for j, wv in enumerate(cr[5:9]):
            text(ws.cell(row=rr, column=3 + j), wv, center=True)
        inp(ws.cell(row=rr, column=7), None, center=True)
        calc(ws.cell(row=rr, column=8), f'=IFERROR(INDEX(C{rr}:G{rr},MATCH(Problem!$B$8,$C$4:$G$4,0)),0)', bold=True)
    tr = 5 + len(CRITERIA)  # 17
    text(ws.cell(row=tr, column=2), "Total (must be 100)", bold=True, fill=SUB)
    for col in range(3, 9):
        calc(ws.cell(row=tr, column=col), f"=SUM({L(col)}5:{L(col)}{tr - 1})", bold=True)
    text(ws.cell(row=tr + 1, column=2), "Check", bold=True)
    calc(ws.cell(row=tr + 1, column=8), f'=IF(H{tr}=100,"OK","Weights total "&H{tr}&", must be 100")', bold=True)
    text(ws.cell(row=tr + 3, column=2), "Reason for Custom weights", bold=True)
    ws.merge_cells(start_row=tr + 3, start_column=3, end_row=tr + 3, end_column=8)
    inp(ws.cell(row=tr + 3, column=3))
    ws.conditional_formatting.add(f"H{tr + 1}", CellIsRule(operator="notEqual", formula=['"OK"'], fill=PatternFill("solid", fgColor="F8CBAD")))
    widths(ws, {"A": 6, "B": 36, "C": 10, "D": 11, "E": 14, "F": 11, "G": 10, "H": 11})
    dvw = DataValidation(type="whole", operator="between", formula1="0", formula2="100", allow_blank=True)
    ws.add_data_validation(dvw)
    dvw.add(f"G5:G{tr - 1}")

    # -------------------------------------------------------------- Scoring
    sc = wb.create_sheet("Scoring", 4)
    title(sc, "Stage 2: Weighted fit", "Score 1–5 per criterion for fit to THIS problem (5 = best), with evidence.")
    header_row(sc, 5, ["#", "Criterion", "1 = poor fit", "3 = adequate", "5 = strong fit", "Weight"])
    s_cols = {"A": 7, "B": 9, "C": 11}
    for c, col in s_cols.items():
        sc.merge_cells(start_row=4, start_column=col, end_row=4, end_column=col + 1)
        calc(sc.cell(row=4, column=col), f'=IF(Problem!$B${22 + CAND.index(c)}="","Candidate {c}",Problem!$B${22 + CAND.index(c)})', link=True, bold=True)
        header_row(sc, 5, ["Score", "Evidence"], start_col=col)
    first, lastr = 6, 6 + len(CRITERIA) - 1  # 6..17
    for i, cr in enumerate(CRITERIA):
        rr = first + i
        text(sc.cell(row=rr, column=1), cr[0], bold=True, center=True)
        text(sc.cell(row=rr, column=2), cr[1], bold=True)
        for j in range(3):
            text(sc.cell(row=rr, column=3 + j), cr[2 + j])
        calc(sc.cell(row=rr, column=6), f"=Weights!H{5 + i}", link=True)
        for col in s_cols.values():
            inp(sc.cell(row=rr, column=col), None, center=True)
            inp(sc.cell(row=rr, column=col + 1))
    dvs_ = DataValidation(type="whole", operator="between", formula1="1", formula2="5", allow_blank=True,
                          showErrorMessage=True, errorTitle="Score 1–5", error="Enter a whole number from 1 to 5.")
    sc.add_data_validation(dvs_)
    for col in s_cols.values():
        dvs_.add(f"{L(col)}{first}:{L(col)}{lastr}")
    tw = lastr + 1
    text(sc.cell(row=tw, column=5), "Total weight", bold=True, fill=SUB)
    calc(sc.cell(row=tw, column=6), f"=SUM(F{first}:F{lastr})", bold=True)

    R0 = tw + 2  # results block start (19)
    res_labels = ["Weighted score (20–100)", "Criteria scored", "Gate status", "Task-fit cap (W1 ≤ 2)",
                  "Low-score flags (score 1, weight ≥ 10)", "Band", "Eligible score (helper)", "Rank among eligible",
                  "Close call (top two within 5 pts)", "VERDICT"]
    sc.cell(row=R0 - 1, column=1, value="Results").font = f(bold=True, size=12, color="1F3864")
    for i, lab in enumerate(res_labels):
        sc.merge_cells(start_row=R0 + i, start_column=2, end_row=R0 + i, end_column=6)
        text(sc.cell(row=R0 + i, column=2), lab, bold=True, fill=SUB)
    W = f"$F${first}:$F${lastr}"
    elig_cells = [f"{L(col)}{R0 + 6}" for col in s_cols.values()]
    elig_rng = f"$G${R0 + 6}:$K${R0 + 6}"  # includes evidence cols (blank text) – RANK/LARGE/COUNT ignore text
    for c, col in s_cols.items():
        cl = L(col)
        S = f"{cl}{first}:{cl}{lastr}"
        name_ok = f'Problem!$B${22 + CAND.index(c)}<>""'
        gate_ref = f"Gates!{L(cand_cols[c])}13"
        rows_f = [
            f'=IF(COUNT({S})=0,"",SUMPRODUCT({W},{S})/5)',
            f'=COUNT({S})&" / {len(CRITERIA)}"',
            f"={gate_ref}",
            f'=IF({cl}{first}="","",IF({cl}{first}<=2,"YES: bake-off must meet quality target","No"))',
            f"=SUMPRODUCT(({S}=1)*({W}>=10))",
            f'=IF({cl}{R0}="","",IF({cl}{R0}>=75,"Strong fit",IF({cl}{R0}>=60,"Acceptable: record mitigations","Poor fit")))',
            f'=IF(AND({name_ok},{cl}{R0 + 2}<>"ELIMINATED",COUNT({S})={len(CRITERIA)}),{cl}{R0},"")',
            f'=IF({cl}{R0 + 6}="","",RANK({cl}{R0 + 6},{elig_rng}))',
            f'=IF(OR({cl}{R0 + 6}="",COUNT({elig_rng})<2),"",IF({cl}{R0 + 7}>2,"",IF(LARGE({elig_rng},1)-LARGE({elig_rng},2)<=5,"YES: tie; decide on bake-off, prefer lower complexity","No")))',
            (f'=IF(NOT({name_ok}),"",IF({cl}{R0 + 2}="ELIMINATED","ELIMINATED: gate failure",IF({cl}{R0 + 2}<>"ALL PASS","Gates incomplete",'
             f'IF(Weights!$H$18<>"OK","Fix weights: must total 100",IF(COUNT({S})<{len(CRITERIA)},"Scoring incomplete",'
             f'IF({cl}{first}<=2,"TASK-FIT CAP (bake-off must meet quality target) · ","")&{cl}{R0 + 5}'
             f'&IF({cl}{R0 + 4}>0," · "&{cl}{R0 + 4}&" low-score flag(s) to mitigate",""))))))'),
        ]
        for i, fm in enumerate(rows_f):
            sc.merge_cells(start_row=R0 + i, start_column=col, end_row=R0 + i, end_column=col + 1)
            calc(sc.cell(row=R0 + i, column=col), fm, link=(i == 2), bold=(i in (0, 9)))
        sc.cell(row=R0, column=col).number_format = "0.0"
        sc.cell(row=R0 + 6, column=col).number_format = "0.0"
    vr = R0 + 9
    red = PatternFill("solid", fgColor="F8CBAD"); green = PatternFill("solid", fgColor="C6EFCE"); amber = PatternFill("solid", fgColor="FFEB9C")
    rng = f"G{vr}:L{vr}"
    sc.conditional_formatting.add(rng, FormulaRule(formula=[f'LEFT(G{vr},4)="ELIM"'], fill=red))
    sc.conditional_formatting.add(rng, FormulaRule(formula=[f'ISNUMBER(SEARCH("Poor fit",G{vr}))'], fill=red))
    sc.conditional_formatting.add(rng, FormulaRule(formula=[f'LEFT(G{vr},6)="Strong"'], fill=green))
    sc.conditional_formatting.add(rng, FormulaRule(formula=[f'AND(G{vr}<>"",LEFT(G{vr},4)<>"ELIM",NOT(ISNUMBER(SEARCH("Poor fit",G{vr}))),LEFT(G{vr},6)<>"Strong")'], fill=amber))
    for col in s_cols.values():
        cl = L(col)
        sc.conditional_formatting.add(f"{cl}{first}:{cl}{lastr}", FormulaRule(formula=[f'AND(ISNUMBER({cl}{first}),{cl}{first}<=2)'], fill=PatternFill("solid", fgColor="F8CBAD")))
    widths(sc, {"A": 6, "B": 26, "C": 24, "D": 24, "E": 24, "F": 8, "G": 8, "H": 30, "I": 8, "J": 30, "K": 8, "L": 30})
    sc.freeze_panes = "C6"

    # ----------------------------------------------------------- Validation
    va = wb.create_sheet("Validation", 5)
    title(va, "Stage 3: Validation (bake-off and quality attribute scenarios)", "Enter targets and results. 'Better is' sets the comparison.")
    header_row(va, 5, ["Check", "Better is", "Target"])
    v_cols = {"A": 4, "B": 6, "C": 8}
    for c, col in v_cols.items():
        va.merge_cells(start_row=4, start_column=col, end_row=4, end_column=col + 1)
        calc(va.cell(row=4, column=col), f'=IF(Problem!$B${22 + CAND.index(c)}="","Candidate {c}",Problem!$B${22 + CAND.index(c)})', link=True, bold=True)
        header_row(va, 5, ["Result", "Met?"], start_col=col)
    checks = [
        ("Quality on golden set (fraction correct; multi-hop / scenario subset where relevant)", "Higher", "0%"),
        ("Cost per transaction at target volume ($)", "Lower", "$"),
        ("Cost per transaction at 10× volume ($)", "Lower", "$"),
        ("p95 time-to-first-token (s)", "Lower", "s"),
        ("p95 end-to-end latency (s)", "Lower", "s"),
        ("Scenario 1: e.g. primary-Region throttling at peak → cited search results within 3 s", "PASS", None),
        ("Scenario 2: e.g. user without entitlement → no restricted content retrieved", "PASS", None),
        ("Scenario 3: e.g. model upgrade → evaluation regression caught before release", "PASS", None),
    ]
    for i, (lab, better, fmt) in enumerate(checks):
        rr = 6 + i
        text(va.cell(row=rr, column=1), lab)
        text(va.cell(row=rr, column=2), better, center=True)
        tcell = va.cell(row=rr, column=3)
        if better == "PASS":
            text(tcell, "PASS", center=True)
        else:
            inp(tcell, None, center=True)
        for col in v_cols.values():
            rc = va.cell(row=rr, column=col)
            inp(rc, None, center=True)
            rl = f"{L(col)}{rr}"
            calc(va.cell(row=rr, column=col + 1),
                 f'=IF(OR({rl}="",$C{rr}=""),"",IF($B{rr}="Higher",IF({rl}>=$C{rr},"✓ Met","✗ Not met"),IF($B{rr}="Lower",IF({rl}<=$C{rr},"✓ Met","✗ Not met"),IF({rl}="PASS","✓ Met","✗ Not met"))))')
            if fmt == "0%":
                rc.number_format = "0%"; tcell.number_format = "0%"
            elif fmt == "$":
                rc.number_format = "$#,##0.0000"; tcell.number_format = "$#,##0.0000"
            elif fmt == "s":
                rc.number_format = "0.0"; tcell.number_format = "0.0"
    dvp = DataValidation(type="list", formula1='"PASS,FAIL"', allow_blank=True)
    va.add_data_validation(dvp)
    for col in v_cols.values():
        dvp.add(f"{L(col)}11:{L(col)}13")
    endr = 6 + len(checks)  # 14
    sm = endr + 1
    text(va.cell(row=sm, column=1), "Checks met", bold=True, fill=SUB)
    text(va.cell(row=sm + 1, column=1), "Task-fit cap outcome", bold=True, fill=SUB)
    for c, col in v_cols.items():
        met = L(col + 1)
        va.merge_cells(start_row=sm, start_column=col, end_row=sm, end_column=col + 1)
        calc(va.cell(row=sm, column=col), f'=COUNTIF({met}6:{met}{endr - 1},"✓ Met")&" of "&(COUNTA({L(col)}6:{L(col)}{endr - 1}))&" tested"', bold=True)
        va.merge_cells(start_row=sm + 1, start_column=col, end_row=sm + 1, end_column=col + 1)
        cap = f"Scoring!{L(s_cols[c])}{R0 + 3}"
        calc(va.cell(row=sm + 1, column=col),
             f'=IF(LEFT({cap},3)<>"YES","n/a (no cap)",IF({met}6="","Awaiting quality result",IF({met}6="✓ Met","Cap lifted: quality target met","Cap stands: do not select")))', bold=True)
    va.conditional_formatting.add(f"D6:I{sm + 1}", FormulaRule(formula=['LEFT(D6,1)="✗"'], fill=red))
    va.conditional_formatting.add(f"D6:I{sm + 1}", FormulaRule(formula=['LEFT(D6,1)="✓"'], fill=green))
    va.conditional_formatting.add(f"D6:I{sm + 1}", FormulaRule(formula=['LEFT(D6,10)="Cap stands"'], fill=red))
    va.conditional_formatting.add(f"D6:I{sm + 1}", FormulaRule(formula=['LEFT(D6,10)="Cap lifted"'], fill=green))
    dr = sm + 3
    text(va.cell(row=dr, column=1), "Decision (pattern(s) and evidence)", bold=True, fill=SUB)
    va.merge_cells(start_row=dr, start_column=2, end_row=dr, end_column=9)
    inp(va.cell(row=dr, column=2))
    va.row_dimensions[dr].height = 60
    widths(va, {"A": 52, "B": 9, "C": 11, "D": 11, "E": 10, "F": 11, "G": 10, "H": 11, "I": 10})
    va.freeze_panes = "D6"

    # ------------------------------------------------------------------ PIR
    pi = wb.create_sheet("PIR", 6)
    title(pi, "Stage 4: Post-implementation review", "3–6 months after go-live. Variance = (actual − estimate) ÷ estimate.")
    header_row(pi, 4, ["Measure", "Unit", "Selection-time estimate", "Actual", "Variance", "Action / change to pattern ratings"])
    pir = [("Unit cost P50", "$ / transaction"), ("Unit cost P95", "$ / transaction"), ("Composite availability", "%"),
           ("p95 end-to-end latency", "s"), ("Quality SLI", "%"), ("Override / escalation rate", "%"),
           ("Review queue load", "% of capacity"), ("Value metric", "as defined")]
    for i, (m_, u) in enumerate(pir):
        rr = 5 + i
        text(pi.cell(row=rr, column=1), m_, bold=True)
        text(pi.cell(row=rr, column=2), u, center=True)
        inp(pi.cell(row=rr, column=3), None, center=True)
        inp(pi.cell(row=rr, column=4), None, center=True)
        calc(pi.cell(row=rr, column=5), f'=IF(OR(C{rr}="",D{rr}="",C{rr}=0),"",(D{rr}-C{rr})/C{rr})')
        pi.cell(row=rr, column=5).number_format = "0.0%;-0.0%;-"
        inp(pi.cell(row=rr, column=6))
    widths(pi, {"A": 28, "B": 16, "C": 18, "D": 12, "E": 11, "F": 60})

    # ------------------------------------------------------------ Example
    if example:
        pbv = {5: "Procurement supplier-risk assistant / Head of Procurement Ops", 6: "Worked example (illustrative)",
               7: "Solution architect, security architect, procurement lead", 8: "Default", 9: "E3", 10: "R1",
               11: "Confidential; EU residency", 12: "B2", 13: "~3k questions/month; 30k at 10×", 14: "SL2", 15: "C2",
               16: "Supplier master data: Ready (Snowflake). Contracts: Partial. Ontology owner: Partial (steward funded)",
               17: "12", 18: "Sampled", 19: "Multi-hop"}
        for rr, v in pbv.items():
            pb.cell(row=rr, column=2, value=v)
        cands = [("P04 Managed RAG (Bedrock Knowledge Bases)", "Lightest plausible pattern"),
                 ("P06 Knowledge graph RAG with Neo4j", "Multi-hop questions over supplier/product/customer relationships"),
                 ("P08 Tool-using agent (bounded autonomy)", "Conversational exploration across sources")]
        for i, (n, why) in enumerate(cands):
            pb.cell(row=22 + i, column=2, value=n)
            pb.cell(row=22 + i, column=3, value=why)
        for i in range(len(GATES)):
            for c, col in cand_cols.items():
                gs.cell(row=5 + i, column=col, value="PASS")
        gs.cell(row=11, column=cand_cols["C"], value="FAIL")
        gs.cell(row=11, column=cand_cols["C"] + 2, value="No agent evaluation capability; no on-call for C3–C4. Revisit in phase 2")
        gs.cell(row=11, column=cand_cols["B"] + 2, value="C3 vs C2 team: six months of Neo4j specialist support funded")
        a = [2, 5, 4, 4, 3, 4, 3, 4, 4, 5, 5, 3]
        b = [5, 3, 2, 3, 3, 3, 5, 2, 3, 3, 2, 4]
        ea = ["Multi-hop questions; vector retrieval returns fragments", "Near-zero floor with S3 Vectors", "C2 matches team",
              "Managed, degraded mode", "Contracts need curation", "Q&A golden set", "Citations", "Data portable in S3",
              "Low–medium", "None", "4 weeks", "Sampled analyst time"]
        eb = ["Supplier → component → product → customer paths", "Aura floor + extraction cost; within B2",
              "C3 vs C2 team; needs Neo4j support", "Neo4j in serial path; degraded mode = vector-only",
              "Spine ready; ontology owner partial", "Multi-hop set must be built", "Graph path as evidence",
              "Cypher/Neo4j specifics", "Re-extraction on model change", "Curation queue ~65% of steward capacity",
              "~4 months to production", "Investigation time logged in case tool"]
        for i in range(len(CRITERIA)):
            sc.cell(row=first + i, column=7, value=a[i]); sc.cell(row=first + i, column=8, value=ea[i])
            sc.cell(row=first + i, column=9, value=b[i]); sc.cell(row=first + i, column=10, value=eb[i])
        vals = {6: (0.80, 0.41, 0.82), 7: (0.05, 0.012, 0.031), 8: (0.05, 0.012, 0.024), 9: (2.0, 1.4, 1.9), 10: (15, 6.5, 9.8)}
        for rr, (t, x, y) in vals.items():
            va.cell(row=rr, column=3, value=t); va.cell(row=rr, column=4, value=x); va.cell(row=rr, column=6, value=y)
        for rr in (11, 12, 13):
            va.cell(row=rr, column=4, value="PASS"); va.cell(row=rr, column=6, value="PASS")
        va.cell(row=dr, column=2, value=("P06 with the graph built by a P02 pipeline. P04 hit the task-fit cap and scored 41% on the multi-hop set "
                                          "(target 80%); P06 prototype scored 82%. Mitigations: Neo4j specialist support (W3), openCypher-compatible "
                                          "templated queries (W8), phased delivery with P04 for single-document questions in month 1 (W11). "
                                          "Figures are illustrative."))
        g["A2"] = "WORKED EXAMPLE (illustrative figures). For a blank copy use ai-pattern-scoring.xlsx"
        g["A2"].font = f(bold=True, color="C00000")

    for sh in wb.worksheets:
        sh.sheet_view.showGridLines = False
        sh.page_setup.orientation = "landscape"
        sh.page_setup.paperSize = sh.PAPERSIZE_A4
        sh.sheet_properties.pageSetUpPr.fitToPage = True
        sh.page_setup.fitToWidth = 1
        sh.page_setup.fitToHeight = 0
    wb.save(path)


if __name__ == "__main__":
    out = sys.argv[1]
    build(False, f"{out}/ai-pattern-scoring.xlsx")
    build(True, f"{out}/ai-pattern-scoring-example.xlsx")
    print("built")
