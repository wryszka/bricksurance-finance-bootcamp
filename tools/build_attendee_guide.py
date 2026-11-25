"""Rebuild ATTENDEE_GUIDE.md from the exercise notebooks, so the guide and the notebooks never drift.

Usage:  python3 tools/build_attendee_guide.py

The appendix of full prompts at the end is built from the same files (see APPENDIX below).
"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEAD = open(os.path.join(ROOT, "tools", "guide_head.md")).read()
TAIL = open(os.path.join(ROOT, "tools", "guide_tail.md")).read()
TRACKS = [
    ("A_lakeflow_designer", "Track A — Lakeflow Designer", "tools/track_a_intro.md"),
    ("B_genie_code_and_agents", "Track B — Genie Code & agents", "tools/track_b_intro.md"),
    ("C_apps", "Track C — Apps", "tools/track_c_intro.md"),
]


def markdown_of(path):
    """All markdown cells of a notebook, joined, with headings pushed down one level."""
    cells, out = open(path).read().split("# COMMAND ----------"), []
    for cell in cells:
        lines = [l for l in cell.strip().splitlines() if l != "# Databricks notebook source"]
        if not lines or not lines[0].startswith("# MAGIC %md"):
            continue
        body = [re.sub(r"^# MAGIC ?", "", l) for l in lines[1:]]
        first = lines[0].replace("# MAGIC %md", "").strip()
        out.append("\n".join(([first] if first else []) + body).strip())
    text = "\n\n".join(out)
    text = re.sub(r"^(#+) ", lambda m: "#" * (len(m.group(1)) + 1) + " ", text, flags=re.M)
    text = text.replace("Run the two cells below.", "Run the last cells of the notebook.")
    text = re.sub(r"[Rr]un the (check )?cells? (at the bottom|below)", "run the check cell at the end of the notebook", text)
    return text


# Appendix: one full prompt per exercise, for the exercises a single prompt can build.
# The text is lifted from the notebooks and solutions (the n-th quoted prompt in the file), so it
# cannot drift from them. A list of numbers joins several staged prompts into one.
A, B, C = "A_lakeflow_designer", "B_genie_code_and_agents", "C_apps"
CANVAS = "the Genie Code prompt above an empty canvas (**New → Visual data prep**)"
APPENDIX = [
    # exercise notebook, [(label, file holding the prompt, which quoted prompts, text to put first)], where, note
    (f"{A}/A1_first_flow_spend_by_category", [("Prompt", f"solutions/{A}/A1_solution.py", [0], "")], CANVAS, ""),
    (f"{A}/A2_bank_reconciliation",
     [("Prompt", f"solutions/{A}/A2_solution.py", [0], ""),
      ("Prompt for the stretch (`my_bank_rec_breaks`)", f"solutions/{A}/A2_solution.py", [1], "")], CANVAS, ""),
    (f"{A}/A3_control_sheet_tie_back", [("Prompt", f"solutions/{A}/A3_solution.py", [0], "")], CANVAS, ""),
    (f"{A}/A4_describe_it_aged_debtors", [("Prompt", f"solutions/{A}/A4_solution.py", [0], "")], CANVAS, ""),
    (f"{A}/A5_migrate_a_legacy_workflow", [("Prompt", f"notebooks/{A}/A5_migrate_a_legacy_workflow.py", [0], "")], CANVAS,
     "Paste the whole of `legacy/desktop_etl_workflow/po_accruals_month_end.yxmd` into the prompt first, then this text."),
    (f"{A}/A6_take_a_flow_to_production", [("Prompt", f"notebooks/{A}/A6_take_a_flow_to_production.py", [0], "")], CANVAS,
     "This builds the flow (Part 1). Scheduling it (Part 2) is still a few clicks."),
    (f"{B}/B1_build_a_pipeline_by_asking",
     [("Prompt", f"notebooks/{B}/B1_build_a_pipeline_by_asking.py", [1, 2, 4],
       "The CSV files are in the gl folder of the raw volume in this notebook's schema.")],
     "the **Genie Code** panel in the B1 notebook, after running its first two cells",
     "This is the bronze, silver and gold prompts of the exercise in one go. The exercise asks you to "
     "look at the files first and to prove the silver table; one prompt skips both."),
    (f"{B}/B2_a_dashboard_in_ten_minutes", [("Prompt", f"notebooks/{B}/B2_a_dashboard_in_ten_minutes.py", [0], "")],
     "Genie Code inside a new dashboard (**New → Dashboard**)", ""),
    (f"{B}/B4_variance_commentary_with_ai", [("Prompt", f"notebooks/{B}/B4_variance_commentary_with_ai.py", [0, 1, 2], "")],
     "the **Genie Code** panel in the B4 notebook", "This is the three staged prompts of the exercise in one go."),
    (f"{C}/C1_build_an_app_by_asking", [("Prompt", f"notebooks/{C}/C1_build_an_app_by_asking.py", [0], "")],
     "**Genie Code**, full page",
     "This writes the app. Deploying it and granting it access to your table are the steps in Part 2 of the exercise."),
    (f"{C}/C2_rebuild_a_spreadsheet_as_an_app",
     [("Prompt for the table (`my_accruals_review`)", f"notebooks/{C}/C2_rebuild_a_spreadsheet_as_an_app.py", [1], ""),
      ("Prompt for the app", f"notebooks/{C}/C2_rebuild_a_spreadsheet_as_an_app.py", [3], "")],
     "**Genie Code**, full page",
     "For the table, paste the whole of `legacy/spreadsheet_euc/AccrualsTracker.bas` into the prompt first, then the text. "
     "The check at the end of the exercise tests the table, not the app."),
    (f"{C}/C3_genie_app_builder", [("Prompt", f"notebooks/{C}/C3_genie_app_builder.py", [1], "")],
     "**Apps → Build**, in your App Space", "Replace `[catalog.schema]` with your own schema."),
]


def quoted_prompts(path):
    """Every quoted block ('> ...') in a notebook's markdown, each as one line of text."""
    found, current = [], []
    for line in open(os.path.join(ROOT, path)).read().splitlines() + [""]:
        text = re.sub(r"^# MAGIC ?", "", line).strip() if line.startswith("# MAGIC") else ""
        if text.startswith(">"):
            current.append(text[1:].strip())
        elif current:
            found.append(" ".join(current))
            current = []
    return found


def appendix():
    out = ["# Appendix — the full prompts\n",
           "For the exercises that one prompt can build, here is that prompt in full. Use it when you are "
           "short on time, or to compare with what you wrote yourself. Then run the check in the exercise "
           "as usual: a prompt that runs is not the same as a number that is right.\n",
           "Where a prompt says *my schema*, Genie Code usually works it out. If it picks the wrong one, "
           "add your schema's full name, for example `workspace.finance_<your name>`.\n",
           "**Not here:** B3. A Genie agent is something you set up and teach, not something one prompt builds.\n"]
    for nb, prompts, where, note in APPENDIX:
        title = next(l for l in open(os.path.join(ROOT, "notebooks", nb + ".py")).read().splitlines()
                     if l.startswith("# MAGIC # ")).replace("# MAGIC # ", "")
        out.append(f"## {title}\n")
        out.append(f"**Where to paste it:** {where}.\n")
        if note:
            out.append(note + "\n")
        for label, path, picks, first in prompts:
            quotes = quoted_prompts(path)
            text = " ".join(([first] if first else []) + [quotes[i] for i in picks])
            assert not text.startswith("**"), f"{path}: quoted block {picks} is a callout, not a prompt"
            out.append(f"**{label}**\n\n> {text}\n")
    return "\n".join(out)


parts = [HEAD]
for folder, title, intro in TRACKS:
    parts.append(f"\n---\n\n# {title}\n\n" + open(os.path.join(ROOT, intro)).read().strip() + "\n")
    for nb in sorted(glob.glob(os.path.join(ROOT, "notebooks", folder, "*.py"))):
        parts.append("\n---\n\n" + markdown_of(nb) + f"\n\n*Notebook:* `notebooks/{folder}/{os.path.basename(nb)[:-3]}`\n")
parts.append("\n---\n\n" + TAIL)
parts.append("\n---\n\n" + appendix())
open(os.path.join(ROOT, "ATTENDEE_GUIDE.md"), "w").write("".join(parts))
print("ATTENDEE_GUIDE.md rebuilt")
