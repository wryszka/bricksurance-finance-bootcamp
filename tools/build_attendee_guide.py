"""Rebuild ATTENDEE_GUIDE.md from the exercise notebooks, so the guide and the notebooks never drift.

Usage:  python3 tools/build_attendee_guide.py
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


parts = [HEAD]
for folder, title, intro in TRACKS:
    parts.append(f"\n---\n\n# {title}\n\n" + open(os.path.join(ROOT, intro)).read().strip() + "\n")
    for nb in sorted(glob.glob(os.path.join(ROOT, "notebooks", folder, "*.py"))):
        parts.append("\n---\n\n" + markdown_of(nb) + f"\n\n*Notebook:* `notebooks/{folder}/{os.path.basename(nb)[:-3]}`\n")
parts.append("\n---\n\n" + TAIL)
open(os.path.join(ROOT, "ATTENDEE_GUIDE.md"), "w").write("".join(parts))
print("ATTENDEE_GUIDE.md rebuilt")
