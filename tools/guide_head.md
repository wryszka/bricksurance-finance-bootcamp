# Bricksurance Finance Bootcamp — Attendee Guide

Welcome. Today you work in Finance at **Bricksurance**, a fictional UK insurer. It is month-end
close for **October 2026**, and you have the usual jobs to do: reconcile the bank, accrue for
what hasn't been invoiced, explain the variances, get the journals approved.

All the data is synthetic. Every problem in it is one you will recognise.

**How this guide works:** every exercise starts with *the business problem*, says *what you will
build*, then gives *step-by-step* directions, with example prompts you can paste into Genie Code.
The same steps are inside each exercise notebook, so you can follow either. Every exercise ends
with a **check** that tells you whether you got the right answer.

---

## What we are doing today — at a glance

| Part | The business problems | What you learn | Databricks tools |
|---|---|---|---|
| **A. Lakeflow Designer** | Where does the money go? Does the ledger agree with the bank? Do the parts add up? | Build data preparation visually; let AI build it from a description; migrate a legacy workflow; schedule it | Lakeflow Designer, Genie Code, Jobs |
| **B. Genie Code & agents** | The same files cleaned by hand every month; the month-end pack; "can you pull me the numbers?" | Brief an AI to build a pipeline and a dashboard; teach an agent your definitions; draft commentary with AI | Genie Code, AI/BI Dashboards, Genie, AI Functions |
| **C. Apps** | Approvals by email; a macro everyone is afraid of | Describe an app and deploy it; take a spreadsheet apart and rebuild it properly | Genie Code, Databricks Apps, Genie App Builder |

Running underneath everything: **Unity Catalog** (your own schema, permissions, history of every
table) and **serverless compute** (nothing to size, start or manage).

## The day

| Time | What happens |
|---|---|
| 10:00 | **Setup** together (10 minutes) |
| 10:10 | **Demo: Lakeflow Designer** — what to use and where to find it (15 minutes) |
| 10:25 | **Your turn — Track A.** Start with A1, then choose |
| 12:00 | Lunch |
| 12:30 | **Demo: Genie Code & agents** (15 minutes) |
| 12:45 | **Your turn — Track B.** B1 or B2, then B3 |
| 14:00 | **Demo: Apps** (15 minutes) |
| 14:15 | **Your turn — Track C.** C1, or C2 if you live with spreadsheets |
| 14:55 | Wrap-up: what to take home |
| 15:00 | Close |

## How today works

- **You choose.** There are 13 exercises and nobody will finish them all. That is on purpose.
  Every exercise stands alone and needs only the setup, so skip anything that doesn't interest you.
- **Times are a guide, not a deadline.** Doing two exercises properly beats rushing through five.
- **Stuck for more than five minutes? Open the solution.** Same name, in the `solutions` folder.
  It has the steps, a prompt that works, and code you can run to catch up. That isn't cheating.
- **Wave at a facilitator** whenever you like.

## Choose your exercises

| | Exercise | Pick this if… | Time |
|---|---|---|---|
| A1 | Your first flow: where does the money go? | you have never used Designer. **Start here.** | 25 min |
| A2 | Bank reconciliation | reconciliations are your daily bread | 30 min |
| A3 | The control sheet | you want to see how a join can quietly lose over a million pounds | 25 min |
| A4 | Describe it, don't draw it | you would rather describe a report than build it | 20 min |
| A5 | Migrate a legacy workflow | you have desktop data-prep workflows to move | 35 min |
| A6 | Take a flow to production | you want to know what happens after "it works on my screen" | 25 min |
| B1 | Build a pipeline by asking | you clean the same files every month | 35 min |
| B2 | A dashboard in ten minutes | you build the month-end pack | 25 min |
| B3 | Your first Genie agent | people keep asking you for numbers. **Don't miss this one.** | 30 min |
| B4 | Variance commentary with AI | you write the commentary | 20 min |
| C1 | Build an app by asking | you approve things by email today | 35 min |
| C2 | Retire a spreadsheet | you own a macro you are slightly afraid of | 40 min |
| C3 | Genie App Builder | your workspace has it switched on (ask a facilitator) | 20 min |

---

## Start here — setup (about 5 minutes, do once)

1. Sign in to your Databricks workspace (the address is on the screen).
2. In the left sidebar: **Workspace → Create → Git folder**, paste
   `https://github.com/wryszka/bricksurance-finance-bootcamp`, and create it.
   *(If the facilitator has already put the folder in the workspace, just open it.)*
3. Open `notebooks/00_setup/01_data_generator`.
4. Top right: **Connect → Serverless**.
5. Click **Run all**. It takes about two minutes.

✅ **You are ready when** the last cell lists 14 tables. Open **Catalog** in the left sidebar and
find your schema, `finance_<your name>`. Everything today lives there, and it is yours alone:
you cannot break anybody else's data, and they cannot break yours.

**Your data**

| Tables | What they are | Used in |
|---|---|---|
| `0_companies`, `0_accounts`, `0_cost_centres` | reference data | everywhere |
| `1_supplier_payments`, `1_supplier_categories` | payments to suppliers, and the spend-category lookup | A1, A3, A6 |
| `1_gl_cash`, `1_bank_statement` | ledger cash entries and bank statement lines for October | A2 |
| `1_ar_invoices` | invoices to brokers and what has been paid | A4 |
| `1_purchase_orders`, `1_supplier_invoices` | purchase orders and the invoices received against them | A5, C2 |
| `2_gl_journal`, `2_budget`, `2_trial_balance`, `2_actual_vs_budget` | the general ledger, the budget, and reporting tables | B2, B3, B4 |
| files in the `raw` volume, folder `gl` | ten messy monthly ledger extracts | B1 |
| `3_journal_requests` | journal requests waiting for approval | C1 |

Anything **you** build is named `my_…`, so it is easy to find.

## Three habits that make the AI useful

1. **Brief it like a new colleague.** Name the table, the rule, and what you want to call the
   result. *"Aged debtors"* gets you a guess. *"Outstanding = amount minus paid, aged from the due
   date to 31 October 2026, in buckets of 30 days"* gets you the report.
2. **Don't fix its work by hand. Tell it what is wrong.** *"The oldest bucket should be 90+."*
   You learn how to brief it, and it keeps the whole thing consistent.
3. **Check it like an accountant.** Does it tie back to a total you trust? How many rows went in
   and came out? Every exercise has a check for exactly this reason.
