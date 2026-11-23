# Bricksurance Finance Bootcamp

Hands-on Databricks exercises for finance data teams: **Lakeflow Designer**, **Genie Code and
Genie agents**, and **Databricks Apps**. One synthetic month-end close, thirteen short exercises,
every one with a solved version.

> **About this bootcamp**
> All data is synthetic and generated on the fly. Bricksurance is a fictional insurer. Supplier,
> broker and people names are made up. The two "legacy" files (a desktop data-prep workflow and a
> spreadsheet macro) were written for this bootcamp and are not any real organisation's process.

## How it works

- **Pick what interests you.** Every exercise is independent: it needs only the 5-minute setup,
  never another exercise. There is deliberately more here than fits in the time.
- **Each exercise is one notebook**: the business problem, what to build, steps, and a
  `check(...)` cell that compares your result with the right answer and tells you what to look at
  if it differs.
- **Stuck? Every exercise has a solution** in `solutions/`: the steps, a prompt that works, and
  runnable SQL or Python that produces the answer so you can carry on.
- **Runs anywhere**, including **Databricks Free Edition**: plain notebooks, serverless compute,
  nothing to install, no external data.

Start with **[ATTENDEE_GUIDE.md](ATTENDEE_GUIDE.md)** — every exercise, step by step. It is generated from the
exercise notebooks (`python3 tools/build_attendee_guide.py`), so the two never drift.

## The exercises

It is month-end close for October 2026.

| | Exercise | You will | Time |
|---|---|---|---|
| **A** | **Lakeflow Designer** — visual data prep | | |
| A1 | Your first flow: where does the money go? | join, filter, aggregate supplier payments by category | 25 min |
| A2 | Bank reconciliation | reconcile 12 bank accounts, find the three that break and why | 30 min |
| A3 | The control sheet | prove the parts add up to the whole, and catch a join that loses money | 25 min |
| A4 | Describe it, don't draw it | build an aged debtors report from one prompt, then check it | 20 min |
| A5 | Migrate a legacy workflow | rebuild a desktop data-prep workflow and prove parity | 35 min |
| A6 | Take a flow to production | parameters, schedules, jobs, version history, Git | 25 min |
| **B** | **Genie Code & agents** | | |
| B1 | Build a pipeline by asking | messy monthly GL files → clean ledger → trial balance | 35 min |
| B2 | A dashboard in ten minutes | costs against budget, and three things hiding in it | 25 min |
| B3 | Your first Genie agent | ask, break it, teach it your definitions, share it | 30 min |
| B4 | Variance commentary with AI | AI functions write the first draft from the journals | 20 min |
| **C** | **Apps** | | |
| C1 | Build an app by asking | a journal approvals app with write-back and an audit trail | 35 min |
| C2 | Retire a spreadsheet | take a VBA macro apart, find its bug, rebuild it as a table and an app | 40 min |
| C3 | Genie App Builder | the same app with no code and no deploy step (where enabled) | 20 min |

## Suggested agenda (5 hours)

No slides-first introduction: each part opens with a 15-minute live demo of what to use and
where to find it, then everyone builds.

| Time | Session |
|---|---|
| 10:00 | Setup together (10 min) |
| 10:10 | **Demo: Lakeflow Designer** (15 min) |
| 10:25 | **Track A — Lakeflow Designer.** A1, then choose from A2–A6 |
| 12:00 | Lunch |
| 12:30 | **Demo: Genie Code & agents** (15 min) |
| 12:45 | **Track B — Genie Code & agents.** B1 or B2, then B3 |
| 14:00 | **Demo: Apps** (15 min) |
| 14:15 | **Track C — Apps.** C1, or C2 if you live with spreadsheets |
| 14:55 | Wrap-up |
| 15:00 | Close |

## Setup (once, about 5 minutes)

1. In your workspace: **Workspace → Create → Git folder** → `https://github.com/wryszka/bricksurance-finance-bootcamp`
2. Open `notebooks/00_setup/01_data_generator`, connect to **Serverless**, and **Run all**.

That creates your own schema, `finance_<your name>`, with 14 tables and ten raw files.

## The data

| Prefix | Tables | Used by |
|---|---|---|
| `0_` | `0_companies`, `0_accounts`, `0_cost_centres` | everything |
| `1_` | `1_supplier_payments`, `1_supplier_categories`, `1_gl_cash`, `1_bank_statement`, `1_ar_invoices`, `1_purchase_orders`, `1_supplier_invoices` | Track A, C2 |
| `2_` | `2_gl_journal`, `2_budget`, `2_trial_balance`, `2_actual_vs_budget` | Track B |
| `3_` | `3_journal_requests` | Track C |
| volume `raw/gl/` | ten monthly GL extract CSVs, deliberately messy | B1 |
| `my_…` | everything **you** build | the checks |

The data has things to find: three bank accounts that don't reconcile (a timing difference,
unposted bank charges, a keying error), three suppliers missing from a lookup, brokers who pay
late, a cloud migration, a postponed campaign, a storm, and a spreadsheet that has been
under-reporting an accrual.

## Repo layout

```
notebooks/
  00_setup/                  00_config, 01_data_generator, 02_check
  A_lakeflow_designer/       A1–A6
  B_genie_code_and_agents/   B1–B4
  C_apps/                    C1–C3
solutions/                   one solved notebook per exercise, plus two finished apps
                             and a dashboard template
legacy/
  desktop_etl_workflow/      the workflow file migrated in A5
  spreadsheet_euc/           the VBA macro retired in C2
```

## Running it on Databricks Free Edition

Everything in tracks A and B, and C1/C2, is built for Free Edition (serverless only, catalog
`workspace`, detected automatically). Things to know:

- Lakeflow Designer is **New → Visual data prep**. Genie Code must be enabled for the AI prompts.
- Free Edition allows a small number of apps and stops them after 24 hours; delete old ones.
- Free Edition has a daily compute allowance. One person working through a track is fine.
- **C3 (Genie App Builder)** is a Beta feature that an admin must switch on; treat it as optional.
- If `ai_gen` is not available in a notebook (B4), run the same SQL in the SQL editor.

## For facilitators

- Run every solution yourself once in the target workspace before the day; UI labels move.
- `solutions/` notebooks write the same `my_…` tables the exercises expect, so anyone who falls
  behind can run a solution and carry on.
- To reset an attendee: rerun `01_data_generator`.
- After your dry run, export your own finished flows (**File → Export**, `.designer.ipynb`) and
  hand them out if you want importable solutions for Track A.
