# Databricks notebook source
# MAGIC %md
# MAGIC # A6 — Take a flow to production
# MAGIC
# MAGIC **About 25 minutes · Lakeflow Designer + Jobs · needs only the setup**
# MAGIC
# MAGIC ## The business problem
# MAGIC A flow that only runs when you open it and press a button is still a manual process. This
# MAGIC exercise takes a small flow the rest of the way: a **parameter** instead of a typed-in month, a
# MAGIC **schedule**, a look at **what ran and when**, and the file that your data engineering team
# MAGIC would put under **version control**.
# MAGIC
# MAGIC ## What you will build
# MAGIC A small flow that writes **`my_monthly_supplier_spend`** (`supplier_name`, `total_paid_gbp`) for
# MAGIC **one month**, chosen by a parameter, and runs on a schedule.
# MAGIC
# MAGIC ## Part 1 — a flow with a parameter (10 min)
# MAGIC 1. **New → Visual data prep**, name it `A6 monthly supplier spend`. Add `1_supplier_payments`.
# MAGIC 2. Open **Parameters** in the left pane and create a parameter called **`month`** with the value `2026-10`.
# MAGIC 3. Add a **Filter** with two conditions:
# MAGIC    - `status` **Is equal to** `Paid`
# MAGIC    - a condition expression that uses the parameter: `date_format(payment_date, 'yyyy-MM') = :month`
# MAGIC 4. **Aggregate**: SUM `amount_gbp` → **`total_paid_gbp`**, group by `supplier_name`.
# MAGIC 5. **Output** to table `my_monthly_supplier_spend`, Overwrite → **Run all**. Run the check below.
# MAGIC 6. Change the parameter to `2026-09`, **Run all**, check again. Same flow, different month.
# MAGIC
# MAGIC *Short on time?* Paste this into the Genie Code prompt above the canvas instead:
# MAGIC > Using 1_supplier_payments, keep Paid payments where the month of payment_date (yyyy-MM) equals a
# MAGIC > parameter called month, default 2026-10. Sum amount_gbp as total_paid_gbp by supplier_name and
# MAGIC > write to a table called my_monthly_supplier_spend.
# MAGIC
# MAGIC ## Part 2 — schedule it (5 min)
# MAGIC 1. Click **Schedule** in the top menu and create a schedule (for example, the 1st of every month at 06:00).
# MAGIC 2. In the schedule, set the `month` parameter value. Each schedule can carry its own values:
# MAGIC    that is how one flow serves test and production.
# MAGIC 3. Open the schedule's menu and choose **Run now**, then **View in Jobs**. You are now looking
# MAGIC    at an ordinary Databricks job: run history, duration, who ran it, and alerts if it fails.
# MAGIC
# MAGIC ## Part 3 — what your engineers will ask for (10 min)
# MAGIC - **"Where is the code?"** In the editor's top-right menu choose **File → Export**. You get a file
# MAGIC   called `A6 monthly supplier spend.designer.ipynb`. That one file *is* the flow.
# MAGIC - **"Can it go in Git?"** Yes. Move the file into a Git folder and it is committed, reviewed and
# MAGIC   versioned like any other notebook.
# MAGIC - **"Can it be a step in a bigger job?"** Yes. In **Jobs & Pipelines** create a job, add a task and
# MAGIC   choose **Type → Visual data prep**. The task can sit after an ingestion step and before a report.
# MAGIC - **"What changed since last month?"** Click the **History** icon on the right and pick an older
# MAGIC   version: the canvas shows what was added, removed and changed.
# MAGIC
# MAGIC ## Worth discussing
# MAGIC Who owns this once it is scheduled: the analyst who built it, or data engineering? What has to
# MAGIC be true before a flow you built is allowed to feed a number in the accounts?
# MAGIC
# MAGIC **Stuck?** `solutions/A_lakeflow_designer/A6_solution`

# COMMAND ----------

# MAGIC %run ../00_setup/02_check

# COMMAND ----------

check("A6")
