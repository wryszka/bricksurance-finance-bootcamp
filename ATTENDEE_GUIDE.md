# Bricksurance Finance Bootcamp — Attendee Guide

Welcome. Today you work in Finance at **Bricksurance**, a fictional UK insurer. It is month-end
close for **October 2026**, and you have the usual jobs to do: reconcile the bank, accrue for
what hasn't been invoiced, explain the variances, get the journals approved.

All the data is synthetic. Every problem in it is one you will recognise.

## How today works

- **You choose.** There are 13 exercises and nobody will finish them all. That is on purpose.
  Every exercise stands alone, so skip anything that doesn't interest you.
- **Each exercise is a notebook** with the business problem, the steps, and a last cell,
  `check("A1")`, that tells you whether you got the right answer and what to look at if not.
- **Stuck for more than five minutes? Open the solution.** Same name, in the `solutions` folder.
  It has the steps, a prompt that works, and code you can run to catch up. That isn't cheating;
  reading a working answer is a good way to learn.
- **Wave at a facilitator** whenever you like.

## Setup — do this once (about 5 minutes)

1. Sign in to your Databricks workspace.
2. In the left sidebar: **Workspace → Create → Git folder**, paste
   `https://github.com/wryszka/bricksurance-finance-bootcamp`, and create it.
   *(If the facilitator has already put the folder in the workspace, just open it.)*
3. Open `notebooks/00_setup/01_data_generator`.
4. Top right: **Connect → Serverless**.
5. Click **Run all**. It takes about two minutes.

✅ **You are ready when** the last cell lists 14 tables. Open **Catalog** in the left sidebar and
find your schema, `finance_<your name>`. Everything today lives there, and it is yours alone.

## Choose your exercises

**Track A — Lakeflow Designer** (visual data prep, no code)

| | Exercise | Pick this if… | Time |
|---|---|---|---|
| A1 | Your first flow: where does the money go? | you have never used Designer. **Start here.** | 25 min |
| A2 | Bank reconciliation | reconciliations are your daily bread | 30 min |
| A3 | The control sheet | you want to see how a join can quietly lose over a million pounds | 25 min |
| A4 | Describe it, don't draw it | you would rather describe a report than build it | 20 min |
| A5 | Migrate a legacy workflow | you have desktop data-prep workflows to move | 35 min |
| A6 | Take a flow to production | you want to know what happens after "it works on my screen" | 25 min |

**Track B — Genie Code & agents** (describe what you want; check what you get)

| | Exercise | Pick this if… | Time |
|---|---|---|---|
| B1 | Build a pipeline by asking | you clean the same files every month | 35 min |
| B2 | A dashboard in ten minutes | you build the month-end pack | 25 min |
| B3 | Your first Genie agent | people keep asking you for numbers. **Don't miss this one.** | 30 min |
| B4 | Variance commentary with AI | you write the commentary | 20 min |

**Track C — Apps**

| | Exercise | Pick this if… | Time |
|---|---|---|---|
| C1 | Build an app by asking | you approve things by email today | 35 min |
| C2 | Retire a spreadsheet | you own a macro you are slightly afraid of | 40 min |
| C3 | Genie App Builder | your workspace has it switched on (ask) | 20 min |

## Three habits that make the AI useful

1. **Brief it like a new colleague.** Name the table, the rule, and what you want to call the
   result. *"Aged debtors"* gets you a guess. *"Outstanding = amount minus paid, aged from the due
   date to 31 October 2026, in buckets of 30 days"* gets you the report.
2. **Don't fix its work by hand. Tell it what is wrong.** *"The oldest bucket should be 90+."*
   You learn how to brief it, and it keeps the whole thing consistent.
3. **Check it like an accountant.** Does it tie back to a total you trust? How many rows went in
   and came out? Every exercise has a check for exactly this reason.

## Finding your way around

| You want to… | Go to |
|---|---|
| see your tables | **Catalog** in the left sidebar → your catalog → `finance_<your name>` |
| build a visual flow | **New → Visual data prep** |
| ask the AI to build something | the **Genie Code** panel in a notebook, dashboard or flow |
| ask questions of your data | **Genie** in the left sidebar |
| see scheduled work | **Jobs & Pipelines** |
| see or create apps | **Compute → Apps** |

## If something goes wrong

| Problem | Fix |
|---|---|
| "Table not found" in a check | you haven't run your flow yet (**Run all**), or the table name differs from the exercise |
| A flow preview looks short | previews use a sample of rows; **Run all** uses everything |
| I broke my data | rerun `00_setup/01_data_generator` — it rebuilds everything in two minutes |
| The app says it can't read the table | run the grant cell in the C1 / C2 notebook with your app's name |
| Something isn't where the steps say | the product moves fast and labels change; ask a facilitator, or ask Genie Code *"where do I find…"* |

## Take it home

This repository is public and runs on the free edition of Databricks. Sign up, add the Git
folder, run the generator, and carry on with the exercises you didn't get to.
