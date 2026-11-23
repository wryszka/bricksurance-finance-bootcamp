# Databricks notebook source
# MAGIC %md
# MAGIC # A2 — Solution: bank reconciliation
# MAGIC
# MAGIC ## The flow
# MAGIC | # | Operator | Settings |
# MAGIC |---|---|---|
# MAGIC | 1 | Source | `1_gl_cash` |
# MAGIC | 2 | Aggregate | SUM `amount_gbp` → `gl_total_gbp`, group by `bank_account` |
# MAGIC | 3 | Source | `1_bank_statement` |
# MAGIC | 4 | Aggregate | SUM `amount_gbp` → `bank_total_gbp`, group by `bank_account` |
# MAGIC | 5 | Join | the two aggregates on `bank_account`, Inner join |
# MAGIC | 6 | Prepare | `variance_gbp` = `round(gl_total_gbp - bank_total_gbp, 2)`; `status` = `CASE WHEN variance_gbp = 0 THEN 'Reconciled' ELSE 'Break' END` |
# MAGIC | 7 | Output | table `my_bank_rec` |
# MAGIC
# MAGIC ## One prompt that builds it
# MAGIC > Using 1_gl_cash and 1_bank_statement in my schema: total amount_gbp per bank_account on each side
# MAGIC > (gl_total_gbp and bank_total_gbp), join the two totals on bank_account, add variance_gbp = ledger
# MAGIC > minus bank rounded to 2 decimals and a status column that says Reconciled when the variance is zero
# MAGIC > and Break otherwise. Write to a table called my_bank_rec.
# MAGIC
# MAGIC ## Prompt for the stretch
# MAGIC > Add a second branch: full outer join 1_gl_cash to 1_bank_statement on bank_account and reference.
# MAGIC > Keep rows where the ledger amount is missing, the bank amount is missing, or the two amounts differ.
# MAGIC > Add a reason column: 'In ledger, not at bank', 'At bank, not in ledger' or 'Amount differs'.
# MAGIC > Write to a table called my_bank_rec_breaks.
# MAGIC
# MAGIC ## The same logic as SQL

# COMMAND ----------

# MAGIC %run ../../notebooks/00_setup/02_check

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE my_bank_rec AS
# MAGIC WITH gl   AS (SELECT bank_account, sum(amount_gbp) AS gl_total_gbp   FROM `1_gl_cash`        GROUP BY bank_account),
# MAGIC      bank AS (SELECT bank_account, sum(amount_gbp) AS bank_total_gbp FROM `1_bank_statement` GROUP BY bank_account)
# MAGIC SELECT bank_account,
# MAGIC        round(gl_total_gbp, 2)                    AS gl_total_gbp,
# MAGIC        round(bank_total_gbp, 2)                  AS bank_total_gbp,
# MAGIC        round(gl_total_gbp - bank_total_gbp, 2)   AS variance_gbp,
# MAGIC        CASE WHEN round(gl_total_gbp - bank_total_gbp, 2) = 0 THEN 'Reconciled' ELSE 'Break' END AS status
# MAGIC FROM gl JOIN bank USING (bank_account);
# MAGIC
# MAGIC SELECT * FROM my_bank_rec ORDER BY bank_account;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Stretch: the lines behind each break
# MAGIC CREATE OR REPLACE TABLE my_bank_rec_breaks AS
# MAGIC SELECT coalesce(g.bank_account, b.bank_account) AS bank_account,
# MAGIC        coalesce(g.reference, b.reference)       AS reference,
# MAGIC        g.posting_date, b.value_date,
# MAGIC        g.amount_gbp AS gl_amount_gbp,
# MAGIC        b.amount_gbp AS bank_amount_gbp,
# MAGIC        CASE WHEN b.amount_gbp IS NULL THEN 'In ledger, not at bank'
# MAGIC             WHEN g.amount_gbp IS NULL THEN 'At bank, not in ledger'
# MAGIC             ELSE 'Amount differs' END           AS reason
# MAGIC FROM `1_gl_cash` g
# MAGIC FULL OUTER JOIN `1_bank_statement` b
# MAGIC   ON g.bank_account = b.bank_account AND g.reference = b.reference
# MAGIC WHERE g.amount_gbp IS NULL OR b.amount_gbp IS NULL OR g.amount_gbp <> b.amount_gbp;
# MAGIC
# MAGIC SELECT * FROM my_bank_rec_breaks ORDER BY bank_account, reference;

# COMMAND ----------

# MAGIC %md
# MAGIC ## What the three breaks are
# MAGIC - **BA-03 — timing.** Six payments posted in the ledger on 29–31 October that had not cleared the bank by month-end. Nothing to fix; they are outstanding items.
# MAGIC - **BA-07 — bank charges.** Four `CHG-` lines on the statement that nobody has posted to the ledger. A journal is needed.
# MAGIC - **BA-11 — keying errors.** Two lines where the digits were transposed in the ledger (1,450 for 1,540 and 8,360.25 for 8,630.25). The ledger needs correcting.

# COMMAND ----------

check("A2")
