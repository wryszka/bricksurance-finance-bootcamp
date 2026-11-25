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

No clock to fight. The day runs in this order, and each part takes as long as it takes.

1. **Setup**, together.
2. **Demo: Lakeflow Designer** — what to use and where to find it.
3. **Your turn — Track A.** Start with A1, then choose.
4. Lunch.
5. **Demo: Genie Code & agents.**
6. **Your turn — Track B.** B1 or B2, then B3.
7. **Demo: Apps.**
8. **Your turn — Track C.** C1, or C2 if you live with spreadsheets.
9. Wrap-up: what to take home.

## How today works

- **You choose.** There are 13 exercises and nobody will finish them all. That is on purpose.
  Every exercise stands alone and needs only the setup, so skip anything that doesn't interest you.
- **Times are a guide, not a deadline.** Doing two exercises properly beats rushing through five.
- **Stuck for more than five minutes? Open the solution.** Same name, in the `solutions` folder.
  It has the steps, a prompt that works, and code you can run to catch up. That isn't cheating.
- **Short on time?** The appendix at the end of this guide has the full prompt for every exercise
  that one prompt can build.
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

✅ **You are ready when** the last cell lists 15 tables. Open **Catalog** in the left sidebar and
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

---

# Track A — Lakeflow Designer

**A short demo, then hands-on.** Lakeflow Designer is a canvas: tables on the left,
steps ("operators") joined by lines, your result on the right. Nothing to install and no code to
write, although every flow *is* code underneath, which is what makes it schedulable and auditable.

**Where to find it:** left sidebar → **New → Visual data prep**.

**Suggested route:** A1 first (everyone). Then pick one or two of A2–A6.

---

## A1 — Your first flow: where does the money go?

**About 25 minutes · Lakeflow Designer · needs only the setup**

### The business problem
The CFO asks: *"How much have we paid suppliers this year, by type of spend?"*
The payments extract has no spend category on it. The category lives in a separate lookup
maintained by Procurement. In a spreadsheet this is a VLOOKUP and a pivot table, redone by
hand every month. You are going to build it once.

### What you will build
A flow with five steps that writes a table called **`my_spend_by_category`**.

| Your tables | What is in them |
|---|---|
| `1_supplier_payments` | every payment to a supplier, January to October 2026 |
| `1_supplier_categories` | supplier → spend category |

> **New to the canvas?** In the left sidebar click **New → Visual data prep**. Add tables with
> **Browse all data** (or drag them from the **Catalog** pane). Add a step by hovering over an
> operator and clicking the **+** next to it. Click any operator to preview its rows.
> Previews use a sample; **Run all** processes everything and writes your table.

### Steps
1. **New → Visual data prep**. Click the name at the top and call it `A1 spend by category`.
2. Add both tables from **your** schema (the cell below prints its name).
3. **Filter** the payments: `status` **Is equal to** `Paid` → **Apply**. Reversed payments are not spend.
   Notice the Filter has two outputs, **Included** and **Excluded**. Click each one.
4. **Join**: connect the Filter's **Included** output and the categories table. Match
   `supplier_name` on both sides, **Join type** = **Inner join** → **Apply**.
5. **Aggregate**: under **Aggregate by** pick `amount_gbp`, `SUM`, and name it **`total_paid_gbp`**.
   **+ Add aggregation**: `payment_id`, `COUNT`, name it `payments`. Under **Group by** pick `category`.
6. **Sort** by `total_paid_gbp`, **DESC**.
7. **Output**: **Output type** = Table, **Table name** = `my_spend_by_category`, **Output location** =
   your catalog and schema, **Write mode** = Overwrite. Then click **Run all**.

### Check
Run the last cells of the notebook. Then answer for yourself: which category is the biggest, and is it
the one you expected for an insurer?

### If you have time
- Add a second **Group by** column (`company_code`). Which company spends most on Professional Fees?
- Click the **History** icon on the right. Every change you made is there, and you can compare versions.

**Stuck?** `solutions/A_lakeflow_designer/A1_solution` has the flow step by step, one prompt
that builds the whole thing, and the same logic as SQL.

*Notebook:* `notebooks/A_lakeflow_designer/A1_first_flow_spend_by_category`

---

## A2 — Bank reconciliation: does the ledger agree with the bank?

**About 30 minutes · Lakeflow Designer · needs only the setup**

### The business problem
It is month-end. Treasury must confirm that, for each of our 12 bank accounts, the cash
movements in the general ledger match what the bank says actually happened in October.
Most accounts will agree to the penny. A few will not, and those are the ones a person needs
to look at.

### What you will build
A flow that writes **`my_bank_rec`**: one row per bank account with the ledger total, the bank
total, the variance, and a status.

| Your tables | What is in them |
|---|---|
| `1_gl_cash` | cash entries in the ledger (receipts positive, payments negative) |
| `1_bank_statement` | the bank's statement lines for the same accounts |

> **New to the canvas?** In the left sidebar click **New → Visual data prep**. Add tables with
> **Browse all data** (or drag them from the **Catalog** pane). Add a step by hovering over an
> operator and clicking the **+** next to it. Click any operator to preview its rows.
> Previews use a sample; **Run all** processes everything and writes your table.

### Steps
1. **New → Visual data prep**, name it `A2 bank rec`. Add both tables.
2. On the ledger table add an **Aggregate**: SUM `amount_gbp` → **`gl_total_gbp`**, group by `bank_account`.
3. On the bank statement add another **Aggregate**: SUM `amount_gbp` → **`bank_total_gbp`**, group by `bank_account`.
4. **Join** the two aggregates on `bank_account` (Inner join).
   *Why aggregate first?* If you join line to line and then add up, rows can multiply and
   your totals inflate. Summarise each side, then compare.
5. Add a **Prepare** operator with two formulas:
   - `variance_gbp` = `round(gl_total_gbp - bank_total_gbp, 2)`
   - `status` = `CASE WHEN variance_gbp = 0 THEN 'Reconciled' ELSE 'Break' END`
6. **Output** to table `my_bank_rec` → **Run all**.

### Check
run the check cell at the end of the notebook. How many accounts reconcile? Which ones are breaks?

### If you have time — find the lines behind each break
Knowing an account is £180 out is only half the job. Build a second output, **`my_bank_rec_breaks`**,
listing the individual lines that explain it. The idea: match ledger lines to bank lines on
`bank_account` **and** `reference` with a **Full outer** join, then keep only rows where one side is
missing or the amounts differ.

Try describing that to Genie Code in the prompt above the canvas instead of drawing it.
Then look at the three accounts: one is a timing difference, one is something the bank
charged us, and one is a typing error. Can you tell which is which?

**Stuck?** `solutions/A_lakeflow_designer/A2_solution`

*Notebook:* `notebooks/A_lakeflow_designer/A2_bank_reconciliation`

---

## A3 — The control sheet: do the parts add up to the whole?

**About 25 minutes · Lakeflow Designer · needs only the setup**

### The business problem
A control sheet splits a population into branches and proves that the branches add back up to
the original total, with zero variance. It is how Finance shows that no transaction fell
through a gap on its way through a process.

Here the population is supplier payments. The branches are **company** × **supplier type**
(Preferred, Non-preferred). And there is a gap waiting for you: three suppliers were onboarded
recently and nobody has added them to the category lookup.

### What you will build
A flow that writes **`my_control_sheet`**: one row per branch with its total, where the branch
totals add up to *everything* that was paid.

| Your tables | What is in them |
|---|---|
| `1_supplier_payments` | every payment (use only `status = 'Paid'`) |
| `1_supplier_categories` | supplier → category, and `is_preferred` |

> **New to the canvas?** In the left sidebar click **New → Visual data prep**. Add tables with
> **Browse all data** (or drag them from the **Catalog** pane). Add a step by hovering over an
> operator and clicking the **+** next to it. Click any operator to preview its rows.
> Previews use a sample; **Run all** processes everything and writes your table.

### Steps
1. **New → Visual data prep**, name it `A3 control sheet`. Add both tables.
2. **Filter** payments to `status` **Is equal to** `Paid`.
3. **Join** the Filter's **Included** output to the categories on `supplier_name`.
   **Start with an Inner join** — the obvious choice.
4. **Prepare**: add a formula column **`branch`**:
   ```
   concat(company_code, ' / ',
          CASE WHEN category IS NULL THEN 'Uncategorised'
               WHEN is_preferred THEN 'Preferred' ELSE 'Non-preferred' END)
   ```
5. **Aggregate**: SUM `amount_gbp` → **`branch_total_gbp`**, group by `branch`.
6. **Output** to table `my_control_sheet` → **Run all**.
7. Run the check below. **It will fail**, and tell you how much money has gone missing.
8. Go back to the Join. Click it and compare the row count going in with the row count coming
   out. Change **Join type** to **Left join**, **Run all** again, and re-run the check.

### What just happened
The inner join threw away every payment to a supplier that isn't in the lookup. No error, no
warning, just a smaller number. The control total caught it. That is why you tie out instead
of trusting the logic.

### If you have time
Build the tie-out *on the canvas* so the proof travels with the flow: from the Filter add a
second **Aggregate** with no Group by (the control total), bring it together with the sum of the
branches, and add a `variance` column that must be 0.00.

**Stuck?** `solutions/A_lakeflow_designer/A3_solution`

*Notebook:* `notebooks/A_lakeflow_designer/A3_control_sheet_tie_back`

---

## A4 — Describe it, don't draw it: aged debtors

**About 20 minutes · Lakeflow Designer with Genie Code · needs only the setup**

### The business problem
Credit Control wants the aged debtors report: how much do brokers owe us, and how old is the
debt? You know exactly what the report should say. So instead of placing operators one by
one, you are going to *describe* it and let Genie Code build the flow. Then you check its work,
because you are still the accountant.

### What you will build
A flow that writes **`my_aged_debtors`** with three columns:
`broker_name`, `age_bucket`, `outstanding_gbp`.

| Your table | What is in it |
|---|---|
| `1_ar_invoices` | invoices to brokers: `amount_gbp`, `amount_paid_gbp`, `due_date` |

The rules: outstanding = `amount_gbp` − `amount_paid_gbp` (ignore invoices that are fully paid).
Age = days between `due_date` and the period end, **31 October 2026**.
Buckets: `Not due`, `1-30`, `31-60`, `61-90`, `90+`.

### Steps
1. **New → Visual data prep**, name it `A4 aged debtors`.
2. In the **Genie Code prompt above the canvas**, describe what you want in your own words.
   Include the table name, the rules above and the output table name. Write it the way you
   would brief a new joiner.
3. Watch it add and connect operators. **Click every operator** and read its configuration.
   Does the age calculation use 31 October 2026, or today's date?
4. Something not right? Don't fix it by hand. Tell it: *"the oldest bucket should be called 90+"*
   or *"age must be measured to 2026-10-31, not today"*.
5. **Run all**, then run the check below.

### Check
The check tells you total debt, how much is over 90 days, and who the worst offender is.

### Things worth noticing
- You described a business rule, and got a flow a colleague can open, read and change.
- A vague prompt gives a vague flow. What did you have to add on your second attempt?
- Ask Genie Code: *"explain this flow to an auditor in five bullet points"*.

### If you have time
Ask for a second output: one row per broker with a column per bucket (a pivot), sorted by the
90+ amount. That is the layout Credit Control actually wants to see.

**Stuck?** `solutions/A_lakeflow_designer/A4_solution` has a prompt that works.

*Notebook:* `notebooks/A_lakeflow_designer/A4_describe_it_aged_debtors`

---

## A5 — Migrate a legacy workflow

**About 35 minutes · Lakeflow Designer with Genie Code · needs only the setup**

### The business problem
The month-end purchase order accrual runs today as a workflow in a desktop data-prep tool, on
one person's laptop, reading CSV files from a shared drive. You have been asked to move it.
The rule for a migration is simple: **the new process must produce the same number as the old
one**. Only then do you improve it.

### What you have
- The legacy workflow file: `legacy/desktop_etl_workflow/po_accruals_month_end.yxmd`
  (in this repo, next to the `notebooks` folder). It is XML; open it and have a look.
- A plain-words description of it: `legacy/desktop_etl_workflow/README.md`
- The same two extracts as governed tables: `1_purchase_orders` and `1_supplier_invoices`

### What you will build
A flow that writes **`my_accruals_summary`** with `company_code`, `cost_centre`, `po_count`
and `accrual_gbp` — matching the legacy output to the penny.

### Steps
1. Open the `.yxmd` file. Read the eleven tool annotations (the `<Name>` lines). Can you follow
   the logic without the original tool?
2. **New → Visual data prep**, name it `A5 po accruals`.
3. In the **Genie Code prompt above the canvas**, ask it to recreate the workflow. Copy the whole
   XML and paste it into the prompt, along with:
   > This is a legacy workflow exported as XML. Recreate it as a visual data prep. Instead of the
   > two CSV files use the tables 1_purchase_orders and 1_supplier_invoices in my schema. Keep one
   > operator per legacy tool where you can and keep the tool names as operator names. Write the
   > result to a table called my_accruals_summary instead of the spreadsheet.
4. Review it tool by tool against the XML. Things that often go wrong in a migration:
   - the legacy Join + Union pair means *"keep purchase orders with no invoice"* — that is a **Left join**
   - the date filters: on or before **31 October 2026**, on **both** inputs
   - cancelled purchase orders must be out
5. **Run all**, then run the check. If it does not match, the check tells you which rule is the
   likely culprit. Fix it by telling Genie Code what is wrong.

### Now improve it (pick one)
- **No more typing the date by hand.** Open **Parameters** in the left pane, create `period_end`
  with the value `2026-10-31`, and use `:period_end` in both filters.
- **Explain it.** Ask Genie Code to write a short description of the flow for the process
  documentation. Compare it with `legacy/desktop_etl_workflow/README.md`.
- **Add a guardrail.** The legacy process had no checks. Add one: fail (or flag) if any purchase
  order has a negative accrual, meaning it was invoiced for more than it was ordered.

### Worth discussing with your neighbour
What in *your* estate looks like this file? How would you prove parity for it, and who signs it off?

**Stuck?** `solutions/A_lakeflow_designer/A5_solution`

*Notebook:* `notebooks/A_lakeflow_designer/A5_migrate_a_legacy_workflow`

---

## A6 — Take a flow to production

**About 25 minutes · Lakeflow Designer + Jobs · needs only the setup**

### The business problem
A flow that only runs when you open it and press a button is still a manual process. This
exercise takes a small flow the rest of the way: a **parameter** instead of a typed-in month, a
**schedule**, a look at **what ran and when**, and the file that your data engineering team
would put under **version control**.

### What you will build
A small flow that writes **`my_monthly_supplier_spend`** (`supplier_name`, `total_paid_gbp`) for
**one month**, chosen by a parameter, and runs on a schedule.

### Part 1 — a flow with a parameter (10 min)
1. **New → Visual data prep**, name it `A6 monthly supplier spend`. Add `1_supplier_payments`.
2. Open **Parameters** in the left pane and create a parameter called **`month`** with the value `2026-10`.
3. Add a **Filter** with two conditions:
   - `status` **Is equal to** `Paid`
   - a condition expression that uses the parameter: `date_format(payment_date, 'yyyy-MM') = :month`
4. **Aggregate**: SUM `amount_gbp` → **`total_paid_gbp`**, group by `supplier_name`.
5. **Output** to table `my_monthly_supplier_spend`, Overwrite → **Run all**. Run the check below.
6. Change the parameter to `2026-09`, **Run all**, check again. Same flow, different month.

*Short on time?* Paste this into the Genie Code prompt above the canvas instead:
> Using 1_supplier_payments, keep Paid payments where the month of payment_date (yyyy-MM) equals a
> parameter called month, default 2026-10. Sum amount_gbp as total_paid_gbp by supplier_name and
> write to a table called my_monthly_supplier_spend.

### Part 2 — schedule it (5 min)
1. Click **Schedule** in the top menu and create a schedule (for example, the 1st of every month at 06:00).
2. In the schedule, set the `month` parameter value. Each schedule can carry its own values:
   that is how one flow serves test and production.
3. Open the schedule's menu and choose **Run now**, then **View in Jobs**. You are now looking
   at an ordinary Databricks job: run history, duration, who ran it, and alerts if it fails.

### Part 3 — what your engineers will ask for (10 min)
- **"Where is the code?"** In the editor's top-right menu choose **File → Export**. You get a file
  called `A6 monthly supplier spend.designer.ipynb`. That one file *is* the flow.
- **"Can it go in Git?"** Yes. Move the file into a Git folder and it is committed, reviewed and
  versioned like any other notebook.
- **"Can it be a step in a bigger job?"** Yes. In **Jobs & Pipelines** create a job, add a task and
  choose **Type → Visual data prep**. The task can sit after an ingestion step and before a report.
- **"What changed since last month?"** Click the **History** icon on the right and pick an older
  version: the canvas shows what was added, removed and changed.

### Worth discussing
Who owns this once it is scheduled: the analyst who built it, or data engineering? What has to
be true before a flow you built is allowed to feed a number in the accounts?

**Stuck?** `solutions/A_lakeflow_designer/A6_solution`

*Notebook:* `notebooks/A_lakeflow_designer/A6_take_a_flow_to_production`

---

# Track B — Genie Code & agents

**A short demo, then hands-on.** Genie Code is the AI that builds things with you:
notebooks, pipelines, dashboards. A Genie agent is the AI your *colleagues* talk to: they ask
questions in plain English and it answers from your governed tables.

**Where to find them:** the **Genie Code** panel inside any notebook or dashboard; **Genie** in the
left sidebar for agents; **New → Dashboard** for dashboards.

**Suggested route:** B1 *or* B2, then B3. B4 if you have time.

---

## B1 — Build a pipeline by asking

**About 35 minutes · Genie Code in a notebook · needs only the setup**

### The business problem
Every month the finance system drops a general ledger extract as a CSV file. Somebody opens
it, fixes the dates, strips the brackets off the negative numbers, deletes the test journals,
and builds a trial balance. Ten files are waiting for you. You are going to build the process
that does this properly, by telling Genie Code what you need.

The point of this exercise is not the code. It is learning how to **brief an AI like a
colleague, and check its work like an accountant**.

### What you will build
Three tables, ending in **`my_trial_balance`** (`period`, `company_code`, `account_code`, `net_gbp`).

| Layer | Table | What it is |
|---|---|---|
| Bronze | `my_bronze_gl` | the files exactly as they arrived, plus which file each row came from |
| Silver | `my_silver_gl` | cleaned: real dates, real numbers, no duplicates, no test journals |
| Gold | `my_trial_balance` | net movement per period, company and account |

Run the next two cells first. They print where your files are.

### Steps
Open **Genie Code** (the side panel in this notebook) and work through these prompts one at a
time. Read what it writes before you run it. Swap in your own path and schema where needed —
or just say *"in this notebook's schema"*; it can see the cells above.

**1. Look before you load (5 min)**
> Look at the CSV files in my raw/gl volume folder. Tell me what columns they have and anything
> that would cause trouble if I loaded them into a table as they are. Don't write any tables yet.

Did it spot the UK dates, the amounts in brackets, the duplicates and the test journals? If it
missed one, tell it. You know this data better than it does.

**2. Bronze (5 min)**
> Load all the files into a table called my_bronze_gl. Keep every column as text, exactly as it
> arrived, and add the source file name and a load timestamp.

**3. Silver (10 min)**
> Create my_silver_gl from my_bronze_gl: remove exact duplicate lines, remove test journals
> (posted_by is TESTUSER), convert posting_date from day/month/year to a date, and convert amount
> to a number called amount_gbp where brackets mean negative, for example (1,234.50) is -1234.50.
> Add a period column in yyyy-MM format.

**4. Prove it (5 min)** — the step most people skip
> Check my_silver_gl: does every journal_id sum to zero? How many rows did we drop and why?

**5. Gold (5 min)**
> Create my_trial_balance: net amount_gbp as net_gbp by period, company_code and account_code,
> with the account name from 0_accounts.

Then run the check cell at the end of the notebook.

### If you have time
- **Schedule it.** Use **Schedule** (top right of the notebook) so it runs on the 1st of each month.
- **Ask for the grown-up version.** *"Turn this into a Lakeflow declarative pipeline with data
  quality expectations for the rules we just wrote."* Open what it creates and look at the
  expectations: your cleaning rules have become monitored controls.
- **Ask it to document itself.** *"Add a short markdown explanation above each step, written for
  someone in Finance, not an engineer."*

**Stuck?** `solutions/B_genie_code_and_agents/B1_solution`

*Notebook:* `notebooks/B_genie_code_and_agents/B1_build_a_pipeline_by_asking`

---

## B2 — A dashboard in ten minutes

**About 25 minutes · AI/BI Dashboards with Genie Code · needs only the setup**

### The business problem
The month-end pack has a page called *"Costs against budget"*. Today it is a spreadsheet
pasted into a slide. By the time anyone reads it, it is out of date and nobody can click on
anything. You are going to replace that page with a live dashboard — and then use it to find
out what actually happened this year.

### Your table
`2_actual_vs_budget` — actual and budget by month, company, cost centre and account.
`variance_gbp` is actual minus budget, so for costs **a positive variance is an overspend**.

### Steps
1. In the left sidebar click **New → Dashboard**. Name it `Costs against budget`.
2. Open Genie Code in the dashboard and describe the page you want. For example:
   > Build a costs-against-budget dashboard from the table 2_actual_vs_budget in my schema, for
   > Expense accounts only, excluding Claims Paid. I want: three headline numbers (actual, budget,
   > variance, in GBP), a monthly line chart of actual against budget, a bar chart of variance by
   > account, and a table of the ten biggest overspends by account and month. Add filters for
   > company and cost centre.
3. Look at what it built. Change things by asking: *"make the variance chart horizontal and sort
   it largest first"*, *"show amounts in millions"*, *"colour overspends red"*.
4. Click a bar in the variance chart. The other charts follow. That is the part a slide can't do.
5. **Publish** (top right) and open the published view. That link is what you would send the CFO.

### Now use it — three things happened this year
Your dashboard should let you answer these in a few clicks. Find them:

1. One cost line has been **running over budget every month since July**. Which, and by roughly how much a month?
2. One cost line was **well under budget from January to May**, then came back to plan. Which?
3. One cost line had a **single very bad month**. Which line, which month?

*(The answers, and why they happened, are in the solution. In exercise B4 you get the AI to write the commentary.)*

### If you have time
- Add a page for **revenue** (Gross Written Premium against budget).
- In the dashboard settings, switch on the **Genie** button so readers can ask follow-up questions.
- Set a **schedule** to email the dashboard as a PDF on working day 2.

**Stuck?** Run `solutions/B_genie_code_and_agents/B2_solution` — it creates a finished dashboard
in your workspace that you can open, take apart and copy from.

*Notebook:* `notebooks/B_genie_code_and_agents/B2_a_dashboard_in_ten_minutes`

---

## B3 — Your first Genie agent

**About 30 minutes · Genie · needs only the setup**

### The business problem
Finance Business Partners spend the first week of every month answering the same kind of
question: *"How much did we spend on X?"*, *"Are we over budget on Y?"*, *"Why?"*. A Genie agent
answers those in plain English, straight from the governed tables, and shows its working.

It will not be right out of the box. It doesn't know that revenue is stored as a negative
number, or what *you* mean by "overspend" or "expense ratio". **Teaching it those things is the
job** — and it is a Finance job, not an IT one.

### Part 1 — create it (5 min)
1. In the left sidebar open **Genie** and create a new one (the button is **New**).
2. Add these tables from your schema: `2_actual_vs_budget`, `2_gl_journal`, `2_budget`,
   `0_accounts`, `0_cost_centres`, `0_companies`.
3. Name it `Finance month-end`.

### Part 2 — just ask (5 min)
Ask these and, each time, open the SQL it wrote (**Show code**). Is the answer right?
run the check cell at the end of the notebook of this notebook to see the correct figures.

- *What was our gross written premium from January to October?*
- *What were total expenses year to date?*
- *Which cost centre spent the most on staff?*

### Part 3 — break it (5 min)
Now ask the kind of thing a real stakeholder asks:

- *What was our revenue in September?* — did you get a **negative** number? Why?
- *Where are we overspending?* — did it understand that a positive variance on a cost is bad?
- *What is our expense ratio?* — it has to guess what that means. Did it guess your definition?
- *Why were claims handling costs so high in September?*

### Part 4 — teach it (10 min)
Open the agent's **Instructions** and write down what a new joiner in Finance would need to be
told. Start with these, then add your own:

```
- All amounts are in GBP (pounds sterling). The data covers January to October 2026; "year to date" means all of it.
- For actual versus budget questions always use the table 2_actual_vs_budget. In that table actual_gbp and budget_gbp are positive numbers for both revenue and costs.
- variance_gbp = actual minus budget. For Expense accounts a positive variance is an overspend (adverse). For Revenue accounts a positive variance is favourable.
- "Revenue" or "premium" means Gross Written Premium (account 4000) unless the user says otherwise.
- "Operating costs" or "expenses" means Expense accounts excluding Claims Paid (account 5000).
- Expense ratio = operating costs divided by Gross Written Premium, shown as a percentage.
- The table 2_gl_journal is double-entry: debits are positive and credits are negative, so revenue appears as a negative number there. Only use it for journal-level detail such as descriptions, and flip the sign of revenue before showing it.
- When asked why a variance happened, look at the description column of 2_gl_journal for that account and period.
- Company names: C100 is Commercial, C200 is Personal Lines, C300 is Services.
```

Ask the Part 3 questions again. **That difference is the whole job.** Then:
- Add two or three **sample questions** so colleagues know what it is good at.
- When it gets an answer right, mark the answer as correct so it can be reused.

### Part 5 — put it in front of someone (5 min)
Click **Share**. Who would you give this to on Monday? They need access to the agent *and*
to the tables: Unity Catalog decides what data each person can see, so the same agent is safe to
share widely.

### If you have time — give it a trusted answer
Some questions must always be answered the same way. Run the last cell of the **solution**
notebook to create a SQL function `variance_report(period)`, then add it to the agent under
its SQL functions / trusted answers. Ask *"show me the variance report for 2026-09"*: the answer
is now marked as coming from a definition Finance approved.

### Worth discussing
Which three definitions in *your* team does everybody "just know" and nobody has written down?

**Stuck?** `solutions/B_genie_code_and_agents/B3_solution`

*Notebook:* `notebooks/B_genie_code_and_agents/B3_your_first_genie_agent`

---

## B4 — Let AI write the first draft of the variance commentary

**About 20 minutes · AI Functions in SQL, with Genie Code · needs only the setup**

### The business problem
The numbers are done on working day 3. Then someone spends a day writing sentences like
*"IT costs were £440k adverse to budget, driven by…"* for every line in the pack. The reasons
are already in the ledger, in the journal descriptions. An AI function can read them and write
the first draft. You stay the editor.

### What you will build
A table **`my_variance_commentary`**: the five biggest cost variances for **September 2026**,
each with a one- or two-sentence explanation in a column called **`commentary`**.

### How AI functions work
They are ordinary SQL functions that call a language model for each row:

```sql
SELECT ai_gen('Explain in one sentence why a storm increases claims handling costs.');
```

run the check cell at the end of the notebook to see one work. No model to deploy, no keys, no Python.

### Steps
Open **Genie Code** and build this in stages. Suggested prompts:

**1. The variances**
> From 2_actual_vs_budget, give me the five biggest absolute variances for Expense accounts in
> period 2026-09, by account, with actual, budget, variance and variance percent.

**2. The evidence**
> For each of those accounts, add a column listing the distinct journal descriptions from
> 2_gl_journal for that account in 2026-09, joined into one text string.

**3. The commentary**
> Add a commentary column using ai_gen. The prompt should give the account name, actual, budget,
> variance and the journal descriptions, and ask for at most two sentences in plain English for a
> finance director, saying whether the variance is adverse or favourable and the likely cause
> based only on the descriptions. Save the result as a table called my_variance_commentary.

Then run the check below and **read the commentary critically**:
- Did it get adverse and favourable the right way round?
- Did it invent a reason that isn't in the descriptions?
- Would you sign it? What would you change in the prompt?

### If you have time
- Change the tone: *"write it as a bullet for a board pack"*, or ask for it in French.
- Use `ai_classify(description, ARRAY('one-off', 'recurring'))` to tag each journal description.
- Ask Genie Code to add this as a last step in the B1 pipeline, so the commentary is drafted
  every month before anyone opens a laptop.

### Worth discussing
Where does the human stay in this process? What would your auditors want to see?

**Stuck?** `solutions/B_genie_code_and_agents/B4_solution`. If `ai_gen` is not available in your
notebook, paste the same SQL into the **SQL editor** and run it on the SQL warehouse.

*Notebook:* `notebooks/B_genie_code_and_agents/B4_variance_commentary_with_ai`

---

# Track C — Apps

**A short demo, then hands-on.** A Databricks App is a small web application that runs
inside your workspace, next to your data, with the same permissions and audit trail. You describe
it; Genie Code writes it.

**Where to find them:** left sidebar → **Compute → Apps**.

**Suggested route:** pick one. C1 if you approve things by email; C2 if you own a
spreadsheet with a macro in it.

---

## C1 — Build an app by asking: journal approvals

**About 35 minutes · Genie Code + Databricks Apps · needs only the setup**

### The business problem
At month-end, manual journal requests are approved by email. Somebody keeps a spreadsheet of
who said yes to what. Auditors love asking for it. You are going to replace the email chain
with a small app: a list of pending requests, an Approve and a Reject button, and every
decision written back to a governed table with a name and a comment on it.

You will not write the code. You will describe the app.

### Your table
`3_journal_requests` — about 60 requests; `status` is Pending, Approved or Rejected.
Policy: anything of **£50,000 or more** needs the Financial Controller.

### Part 1 — describe the app (15 min)
Open **Genie Code** (full page works best for this) and brief it. For example:

> Build a Streamlit app for Databricks Apps called journal approvals, in a new folder in my home
> directory. It reads the table 3_journal_requests in my schema through a SQL warehouse. Show three
> headline numbers: pending requests, pending value in GBP, and how many pending requests are
> £50,000 or more. Show the requests in a table with a filter on status. Let me pick a pending
> request, type a comment, and click Approve or Reject. Rejecting needs a comment. Write the
> decision back to the table: status, decided_by (the signed-in user's email) and decision_comment.
> Warn me when the amount is £50,000 or more. Include app.yaml and requirements.txt.

Read what it produced. You should be able to follow it: one function that runs SQL, one
`SELECT`, one `UPDATE`. Ask it to explain anything you can't follow.

### Part 2 — deploy it (10 min)
Ask Genie Code to deploy the app for you, or do it by hand:

#### Deploying a custom app (the same for any app)
1. Left sidebar → **Compute → Apps → Create app → Create a custom app**. Give it a short name, e.g. `journal-approvals`.
2. Under **App resources** add a **SQL warehouse** and leave the resource key as `sql-warehouse`.
3. **Deploy**, and choose the folder that holds `app.py`, `app.yaml` and `requirements.txt`.
4. Give the app permission to use your tables: type the app's name into the `app_name` box at the
   top of this notebook and run the check cell at the end of the notebook. An app has its own identity; it sees nothing until
   you grant it access. That is the governance working, not a bug.
5. Open the app's URL.

### Part 3 — use it (5 min)
Approve one request, reject another with a comment, then run the check at the bottom.
Then open `3_journal_requests` in **Catalog** and look at the table's **History** tab: every
decision is a versioned change. That is your audit trail, and you didn't build it.

### Make it yours (pick one)
Change the app by asking, then redeploy:
- *"Only let people approve requests under £50,000 unless they tick a box confirming they are the Financial Controller."*
- *"Add a chart of pending value by cost centre."*
- *"Add a button that downloads the approved requests as a CSV for the journal upload."*

### Worth discussing
Which spreadsheet in your team is really an app that nobody has built yet?

**Stuck?** A finished version is in `solutions/C_apps/journal_approvals_app/`. Edit
`BOOTCAMP_SCHEMA` in its `app.yaml`, then deploy that folder. `solutions/C_apps/C1_solution`
walks through it.

*Notebook:* `notebooks/C_apps/C1_build_an_app_by_asking`

---

## C2 — Retire a spreadsheet: from macro to app

**About 40 minutes · Genie Code + Databricks Apps · needs only the setup**

### The business problem
*"Accruals Tracker v7 FINAL (2).xlsm"* calculates the month-end purchase order accrual. It was
written years ago by someone who has since moved on. It works — everyone thinks. It is on the
EUC register and Internal Audit want it gone. You are going to take it apart, find out what it
really does, and rebuild it as something governed.

### What you have
- The macro: `legacy/spreadsheet_euc/AccrualsTracker.bas` (in this repo, next to `notebooks`)
- How it is used today: `legacy/spreadsheet_euc/README.md`
- The data it needs, as governed tables: `1_purchase_orders`, `1_supplier_invoices`

### Part 1 — understand it (10 min)
Open the `.bas` file, then open **Genie Code** and ask (paste the macro in, or point it at the file):

> Read this VBA macro. Explain in plain English what it does, step by step, for someone in Finance.
> Then list every risk you can see: anything hard-coded, anything that could silently give a wrong
> number, and anything that depends on a person doing something by hand.

There are **at least three** things in there that should worry you. Did it find them? Did you?

### Part 2 — rebuild the logic (10 min)
> Rebuild the macro's calculation as SQL on my tables 1_purchase_orders and 1_supplier_invoices.
> Create a table called my_accruals_review with company_code, cost_centre, po_count and accrual_gbp.
> Use a period end of 2026-10-31. Do not copy the macro's row limit.

Run the check at the bottom. It compares your table with the correct accrual.

Now the interesting question: **the spreadsheet would have reported a different number.** Ask:
> How much lower would the accrual be if only the first 999 purchase orders (by po_id) were
> processed, as the macro does?

That difference is an error that has been going into the accounts.

### Part 3 — give it a front end (15 min)
> Build a Streamlit app for Databricks Apps that shows my_accruals_review joined to 0_cost_centres:
> headline numbers for total accrual and number of purchase orders, a company filter, a table that
> marks lines of £250,000 or more for review, and a bar chart of accrual by cost centre.

Deploy it:

#### Deploying a custom app (the same for any app)
1. Left sidebar → **Compute → Apps → Create app → Create a custom app**. Give it a short name, e.g. `journal-approvals`.
2. Under **App resources** add a **SQL warehouse** and leave the resource key as `sql-warehouse`.
3. **Deploy**, and choose the folder that holds `app.py`, `app.yaml` and `requirements.txt`.
4. Give the app permission to use your tables: type the app's name into the `app_name` box at the
   top of this notebook and run the check cell at the end of the notebook. An app has its own identity; it sees nothing until
   you grant it access. That is the governance working, not a bug.
5. Open the app's URL.

### What you have replaced
| The spreadsheet | What you built |
|---|---|
| data pasted in by hand | governed tables, refreshed by a pipeline |
| a date edited in the code each month | a parameter |
| a silent 1,000-row limit | no limit |
| `On Error Resume Next` | errors that stop the process and tell someone |
| emailed around for approval | an app, with access controlled per person |
| no history | every version of every table |

### Worth discussing
How many files like this are on your EUC register? Which one would you do first, and what
would you need to see before you trusted the replacement?

**Stuck?** `solutions/C_apps/C2_solution` and the finished app in `solutions/C_apps/accruals_review_app/`.

*Notebook:* `notebooks/C_apps/C2_rebuild_a_spreadsheet_as_an_app`

---

## C3 — The same app, with Genie App Builder

**About 20 minutes · Genie App Builder · needs it switched on in your workspace**

> **Check first.** Genie App Builder is in Beta. It needs a workspace admin to have switched on
> *Governed agentic app-building* and given you an **App Space**. Open **Apps** in the left
> sidebar: if you see a **Build** tab, you have it. If not, do C1 or C2 instead — nothing else in
> this bootcamp depends on this exercise.

### The idea
In C1 you briefed Genie Code, got code, and deployed it yourself. Genie App Builder goes one
step further for business users: you describe the app, it builds it and shows you a **live
preview**, you refine it by talking to it, and you deploy with one click. No folder, no
`app.yaml`, no deploy step.

### Steps
1. **Apps → Build**. Choose your App Space. Give the app a name, e.g. `journal approvals`.
2. Describe the app. Use the same brief as C1, in your own words:
   > An app for approving month-end journal requests. It reads the table 3_journal_requests in my
   > schema [catalog.schema]. Show pending requests with their amount, reason and who asked. Let me
   > approve or reject one with a comment, and save the decision to the table with my name. Flag
   > anything of £50,000 or more as needing the Financial Controller.
3. If asked, click **Sign in** to open the preview.
4. Refine it by asking: *"put the big numbers at the top"*, *"add a filter for company"*,
   *"make rejecting require a comment"*.
5. Deploy it, then **Share** it with your neighbour (`CAN USE`).

### Compare the two routes
| | C1: Genie Code + custom app | C3: Genie App Builder |
|---|---|---|
| Who it suits | someone comfortable reading code | anyone who can describe what they want |
| What you get | files you own, in a folder or in Git | a managed app inside an App Space |
| Control | everything | what the App Space allows |
| Always-on / scaled out | possible | no: it scales to zero when idle |
| Data it can reach | whatever you grant the app | only what the App Space shares |

### Worth discussing
Which of these would your team be allowed to use tomorrow? Who would own the App Space and
decide what data goes in it?

*Notebook:* `notebooks/C_apps/C3_genie_app_builder`

---

# Finding your way around

| You want to… | Go to |
|---|---|
| see your tables | **Catalog** in the left sidebar → your catalog → `finance_<your name>` |
| build a visual flow | **New → Visual data prep** |
| ask the AI to build something | the **Genie Code** panel in a notebook, dashboard or flow |
| ask questions of your data | **Genie** in the left sidebar |
| see scheduled work | **Jobs & Pipelines** |
| see or create apps | **Compute → Apps** |

# If something goes wrong

| Problem | Fix |
|---|---|
| "Table not found" in a check | you haven't run your flow yet (**Run all**), or the table name differs from the exercise |
| A flow preview looks short | previews use a sample of rows; **Run all** uses everything |
| I broke my data | rerun `00_setup/01_data_generator` — it rebuilds everything in two minutes |
| The app says it can't read the table | run the grant cell in the C1 / C2 notebook with your app's name |
| Something isn't where the steps say | the product moves fast and labels change; ask a facilitator, or ask Genie Code *"where do I find…"* |

# Take it home

This repository is public and runs on the free edition of Databricks. Sign up, add the Git
folder, run the generator, and carry on with the exercises you didn't get to.

*About this bootcamp: all data is synthetic and Bricksurance is a fictional insurer. The legacy
workflow and spreadsheet macro were written for these exercises and are not any real
organisation's process.*

---

# Appendix — the full prompts

For the exercises that one prompt can build, here is that prompt in full. Use it when you are short on time, or to compare with what you wrote yourself. Then run the check in the exercise as usual: a prompt that runs is not the same as a number that is right.

Where a prompt says *my schema*, Genie Code usually works it out. If it picks the wrong one, add your schema's full name, for example `workspace.finance_<your name>`.

**Not here:** B3. A Genie agent is something you set up and teach, not something one prompt builds.

## A1 — Your first flow: where does the money go?

**Where to paste it:** the Genie Code prompt above an empty canvas (**New → Visual data prep**).

**Prompt**

> Using 1_supplier_payments and 1_supplier_categories in my schema, keep only payments with status Paid, join to the categories on supplier_name, and show total amount_gbp as total_paid_gbp and the number of payments by category, highest first. Write the result to a table called my_spend_by_category.

## A2 — Bank reconciliation: does the ledger agree with the bank?

**Where to paste it:** the Genie Code prompt above an empty canvas (**New → Visual data prep**).

**Prompt**

> Using 1_gl_cash and 1_bank_statement in my schema: total amount_gbp per bank_account on each side (gl_total_gbp and bank_total_gbp), join the two totals on bank_account, add variance_gbp = ledger minus bank rounded to 2 decimals and a status column that says Reconciled when the variance is zero and Break otherwise. Write to a table called my_bank_rec.

**Prompt for the stretch (`my_bank_rec_breaks`)**

> Add a second branch: full outer join 1_gl_cash to 1_bank_statement on bank_account and reference. Keep rows where the ledger amount is missing, the bank amount is missing, or the two amounts differ. Add a reason column: 'In ledger, not at bank', 'At bank, not in ledger' or 'Amount differs'. Write to a table called my_bank_rec_breaks.

## A3 — The control sheet: do the parts add up to the whole?

**Where to paste it:** the Genie Code prompt above an empty canvas (**New → Visual data prep**).

**Prompt**

> Using 1_supplier_payments (status Paid only) left joined to 1_supplier_categories on supplier_name, add a branch column = company_code + ' / ' + ('Uncategorised' when category is null, 'Preferred' when is_preferred is true, otherwise 'Non-preferred'). Sum amount_gbp as branch_total_gbp by branch and write to a table called my_control_sheet.

## A4 — Describe it, don't draw it: aged debtors

**Where to paste it:** the Genie Code prompt above an empty canvas (**New → Visual data prep**).

**Prompt**

> Using 1_ar_invoices in my schema, build an aged debtors report as at 2026-10-31. Outstanding is amount_gbp minus amount_paid_gbp; ignore invoices with nothing outstanding. Age each invoice by the number of days from due_date to 2026-10-31 and put it in a bucket called 'Not due' (0 days or fewer), '1-30', '31-60', '61-90' or '90+'. Sum outstanding as outstanding_gbp by broker_name and age_bucket. Write the result to a table called my_aged_debtors.

## A5 — Migrate a legacy workflow

**Where to paste it:** the Genie Code prompt above an empty canvas (**New → Visual data prep**).

Paste the whole of `legacy/desktop_etl_workflow/po_accruals_month_end.yxmd` into the prompt first, then this text.

**Prompt**

> This is a legacy workflow exported as XML. Recreate it as a visual data prep. Instead of the two CSV files use the tables 1_purchase_orders and 1_supplier_invoices in my schema. Keep one operator per legacy tool where you can and keep the tool names as operator names. Write the result to a table called my_accruals_summary instead of the spreadsheet.

## A6 — Take a flow to production

**Where to paste it:** the Genie Code prompt above an empty canvas (**New → Visual data prep**).

This builds the flow (Part 1). Scheduling it (Part 2) is still a few clicks.

**Prompt**

> Using 1_supplier_payments, keep Paid payments where the month of payment_date (yyyy-MM) equals a parameter called month, default 2026-10. Sum amount_gbp as total_paid_gbp by supplier_name and write to a table called my_monthly_supplier_spend.

## B1 — Build a pipeline by asking

**Where to paste it:** the **Genie Code** panel in the B1 notebook, after running its first two cells.

This is the bronze, silver and gold prompts of the exercise in one go. The exercise asks you to look at the files first and to prove the silver table; one prompt skips both.

**Prompt**

> The CSV files are in the gl folder of the raw volume in this notebook's schema. Load all the files into a table called my_bronze_gl. Keep every column as text, exactly as it arrived, and add the source file name and a load timestamp. Create my_silver_gl from my_bronze_gl: remove exact duplicate lines, remove test journals (posted_by is TESTUSER), convert posting_date from day/month/year to a date, and convert amount to a number called amount_gbp where brackets mean negative, for example (1,234.50) is -1234.50. Add a period column in yyyy-MM format. Create my_trial_balance: net amount_gbp as net_gbp by period, company_code and account_code, with the account name from 0_accounts.

## B2 — A dashboard in ten minutes

**Where to paste it:** Genie Code inside a new dashboard (**New → Dashboard**).

**Prompt**

> Build a costs-against-budget dashboard from the table 2_actual_vs_budget in my schema, for Expense accounts only, excluding Claims Paid. I want: three headline numbers (actual, budget, variance, in GBP), a monthly line chart of actual against budget, a bar chart of variance by account, and a table of the ten biggest overspends by account and month. Add filters for company and cost centre.

## B4 — Let AI write the first draft of the variance commentary

**Where to paste it:** the **Genie Code** panel in the B4 notebook.

This is the three staged prompts of the exercise in one go.

**Prompt**

> From 2_actual_vs_budget, give me the five biggest absolute variances for Expense accounts in period 2026-09, by account, with actual, budget, variance and variance percent. For each of those accounts, add a column listing the distinct journal descriptions from 2_gl_journal for that account in 2026-09, joined into one text string. Add a commentary column using ai_gen. The prompt should give the account name, actual, budget, variance and the journal descriptions, and ask for at most two sentences in plain English for a finance director, saying whether the variance is adverse or favourable and the likely cause based only on the descriptions. Save the result as a table called my_variance_commentary.

## C1 — Build an app by asking: journal approvals

**Where to paste it:** **Genie Code**, full page.

This writes the app. Deploying it and granting it access to your table are the steps in Part 2 of the exercise.

**Prompt**

> Build a Streamlit app for Databricks Apps called journal approvals, in a new folder in my home directory. It reads the table 3_journal_requests in my schema through a SQL warehouse. Show three headline numbers: pending requests, pending value in GBP, and how many pending requests are £50,000 or more. Show the requests in a table with a filter on status. Let me pick a pending request, type a comment, and click Approve or Reject. Rejecting needs a comment. Write the decision back to the table: status, decided_by (the signed-in user's email) and decision_comment. Warn me when the amount is £50,000 or more. Include app.yaml and requirements.txt.

## C2 — Retire a spreadsheet: from macro to app

**Where to paste it:** **Genie Code**, full page.

For the table, paste the whole of `legacy/spreadsheet_euc/AccrualsTracker.bas` into the prompt first, then the text. The check at the end of the exercise tests the table, not the app.

**Prompt for the table (`my_accruals_review`)**

> Rebuild the macro's calculation as SQL on my tables 1_purchase_orders and 1_supplier_invoices. Create a table called my_accruals_review with company_code, cost_centre, po_count and accrual_gbp. Use a period end of 2026-10-31. Do not copy the macro's row limit.

**Prompt for the app**

> Build a Streamlit app for Databricks Apps that shows my_accruals_review joined to 0_cost_centres: headline numbers for total accrual and number of purchase orders, a company filter, a table that marks lines of £250,000 or more for review, and a bar chart of accrual by cost centre.

## C3 — The same app, with Genie App Builder

**Where to paste it:** **Apps → Build**, in your App Space.

Replace `[catalog.schema]` with your own schema.

**Prompt**

> An app for approving month-end journal requests. It reads the table 3_journal_requests in my schema [catalog.schema]. Show pending requests with their amount, reason and who asked. Let me approve or reject one with a comment, and save the decision to the table with my name. Flag anything of £50,000 or more as needing the Financial Controller.
