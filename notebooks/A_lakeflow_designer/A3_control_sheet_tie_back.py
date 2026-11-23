# Databricks notebook source
# MAGIC %md
# MAGIC # A3 — The control sheet: do the parts add up to the whole?
# MAGIC
# MAGIC **About 25 minutes · Lakeflow Designer · needs only the setup**
# MAGIC
# MAGIC ## The business problem
# MAGIC A control sheet splits a population into branches and proves that the branches add back up to
# MAGIC the original total, with zero variance. It is how Finance shows that no transaction fell
# MAGIC through a gap on its way through a process.
# MAGIC
# MAGIC Here the population is supplier payments. The branches are **company** × **supplier type**
# MAGIC (Preferred, Non-preferred). And there is a gap waiting for you: three suppliers were onboarded
# MAGIC recently and nobody has added them to the category lookup.
# MAGIC
# MAGIC ## What you will build
# MAGIC A flow that writes **`my_control_sheet`**: one row per branch with its total, where the branch
# MAGIC totals add up to *everything* that was paid.
# MAGIC
# MAGIC | Your tables | What is in them |
# MAGIC |---|---|
# MAGIC | `1_supplier_payments` | every payment (use only `status = 'Paid'`) |
# MAGIC | `1_supplier_categories` | supplier → category, and `is_preferred` |
# MAGIC
# MAGIC > **New to the canvas?** In the left sidebar click **New → Visual data prep**. Add tables with
# MAGIC > **Browse all data** (or drag them from the **Catalog** pane). Add a step by hovering over an
# MAGIC > operator and clicking the **+** next to it. Click any operator to preview its rows.
# MAGIC > Previews use a sample; **Run all** processes everything and writes your table.
# MAGIC
# MAGIC ## Steps
# MAGIC 1. **New → Visual data prep**, name it `A3 control sheet`. Add both tables.
# MAGIC 2. **Filter** payments to `status` **Is equal to** `Paid`.
# MAGIC 3. **Join** the Filter's **Included** output to the categories on `supplier_name`.
# MAGIC    **Start with an Inner join** — the obvious choice.
# MAGIC 4. **Prepare**: add a formula column **`branch`**:
# MAGIC    ```
# MAGIC    concat(company_code, ' / ',
# MAGIC           CASE WHEN category IS NULL THEN 'Uncategorised'
# MAGIC                WHEN is_preferred THEN 'Preferred' ELSE 'Non-preferred' END)
# MAGIC    ```
# MAGIC 5. **Aggregate**: SUM `amount_gbp` → **`branch_total_gbp`**, group by `branch`.
# MAGIC 6. **Output** to table `my_control_sheet` → **Run all**.
# MAGIC 7. Run the check below. **It will fail**, and tell you how much money has gone missing.
# MAGIC 8. Go back to the Join. Click it and compare the row count going in with the row count coming
# MAGIC    out. Change **Join type** to **Left join**, **Run all** again, and re-run the check.
# MAGIC
# MAGIC ## What just happened
# MAGIC The inner join threw away every payment to a supplier that isn't in the lookup. No error, no
# MAGIC warning, just a smaller number. The control total caught it. That is why you tie out instead
# MAGIC of trusting the logic.
# MAGIC
# MAGIC ## If you have time
# MAGIC Build the tie-out *on the canvas* so the proof travels with the flow: from the Filter add a
# MAGIC second **Aggregate** with no Group by (the control total), bring it together with the sum of the
# MAGIC branches, and add a `variance` column that must be 0.00.
# MAGIC
# MAGIC **Stuck?** `solutions/A_lakeflow_designer/A3_solution`

# COMMAND ----------

# MAGIC %run ../00_setup/02_check

# COMMAND ----------

check("A3")
