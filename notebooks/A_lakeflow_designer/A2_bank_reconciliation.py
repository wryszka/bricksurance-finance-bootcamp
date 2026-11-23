# Databricks notebook source
# MAGIC %md
# MAGIC # A2 — Bank reconciliation: does the ledger agree with the bank?
# MAGIC
# MAGIC **About 30 minutes · Lakeflow Designer · needs only the setup**
# MAGIC
# MAGIC ## The business problem
# MAGIC It is month-end. Treasury must confirm that, for each of our 12 bank accounts, the cash
# MAGIC movements in the general ledger match what the bank says actually happened in October.
# MAGIC Most accounts will agree to the penny. A few will not, and those are the ones a person needs
# MAGIC to look at.
# MAGIC
# MAGIC ## What you will build
# MAGIC A flow that writes **`my_bank_rec`**: one row per bank account with the ledger total, the bank
# MAGIC total, the variance, and a status.
# MAGIC
# MAGIC | Your tables | What is in them |
# MAGIC |---|---|
# MAGIC | `1_gl_cash` | cash entries in the ledger (receipts positive, payments negative) |
# MAGIC | `1_bank_statement` | the bank's statement lines for the same accounts |
# MAGIC
# MAGIC > **New to the canvas?** In the left sidebar click **New → Visual data prep**. Add tables with
# MAGIC > **Browse all data** (or drag them from the **Catalog** pane). Add a step by hovering over an
# MAGIC > operator and clicking the **+** next to it. Click any operator to preview its rows.
# MAGIC > Previews use a sample; **Run all** processes everything and writes your table.
# MAGIC
# MAGIC ## Steps
# MAGIC 1. **New → Visual data prep**, name it `A2 bank rec`. Add both tables.
# MAGIC 2. On the ledger table add an **Aggregate**: SUM `amount_gbp` → **`gl_total_gbp`**, group by `bank_account`.
# MAGIC 3. On the bank statement add another **Aggregate**: SUM `amount_gbp` → **`bank_total_gbp`**, group by `bank_account`.
# MAGIC 4. **Join** the two aggregates on `bank_account` (Inner join).
# MAGIC    *Why aggregate first?* If you join line to line and then add up, rows can multiply and
# MAGIC    your totals inflate. Summarise each side, then compare.
# MAGIC 5. Add a **Prepare** operator with two formulas:
# MAGIC    - `variance_gbp` = `round(gl_total_gbp - bank_total_gbp, 2)`
# MAGIC    - `status` = `CASE WHEN variance_gbp = 0 THEN 'Reconciled' ELSE 'Break' END`
# MAGIC 6. **Output** to table `my_bank_rec` → **Run all**.
# MAGIC
# MAGIC ## Check
# MAGIC Run the cells below. How many accounts reconcile? Which ones are breaks?
# MAGIC
# MAGIC ## If you have time — find the lines behind each break
# MAGIC Knowing an account is £180 out is only half the job. Build a second output, **`my_bank_rec_breaks`**,
# MAGIC listing the individual lines that explain it. The idea: match ledger lines to bank lines on
# MAGIC `bank_account` **and** `reference` with a **Full outer** join, then keep only rows where one side is
# MAGIC missing or the amounts differ.
# MAGIC
# MAGIC Try describing that to Genie Code in the prompt above the canvas instead of drawing it.
# MAGIC Then look at the three accounts: one is a timing difference, one is something the bank
# MAGIC charged us, and one is a typing error. Can you tell which is which?
# MAGIC
# MAGIC **Stuck?** `solutions/A_lakeflow_designer/A2_solution`

# COMMAND ----------

# MAGIC %run ../00_setup/02_check

# COMMAND ----------

check("A2")
