# Databricks notebook source
# MAGIC %md
# MAGIC # A3 — Solution: the control sheet
# MAGIC
# MAGIC ## The flow
# MAGIC | # | Operator | Settings |
# MAGIC |---|---|---|
# MAGIC | 1 | Source | `1_supplier_payments` |
# MAGIC | 2 | Source | `1_supplier_categories` |
# MAGIC | 3 | Filter | `status` Is equal to `Paid` |
# MAGIC | 4 | Join | Filter **Included** + categories on `supplier_name`, **Left join** |
# MAGIC | 5 | Prepare | `branch` = company + ' / ' + Preferred / Non-preferred / Uncategorised |
# MAGIC | 6 | Aggregate | SUM `amount_gbp` → `branch_total_gbp`, group by `branch` |
# MAGIC | 7 | Output | table `my_control_sheet` |
# MAGIC
# MAGIC ## One prompt that builds it
# MAGIC > Using 1_supplier_payments (status Paid only) left joined to 1_supplier_categories on supplier_name,
# MAGIC > add a branch column = company_code + ' / ' + ('Uncategorised' when category is null, 'Preferred'
# MAGIC > when is_preferred is true, otherwise 'Non-preferred'). Sum amount_gbp as branch_total_gbp by branch
# MAGIC > and write to a table called my_control_sheet.
# MAGIC
# MAGIC ## The same logic as SQL

# COMMAND ----------

# MAGIC %run ../../notebooks/00_setup/02_check

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE my_control_sheet AS
# MAGIC SELECT concat(p.company_code, ' / ',
# MAGIC               CASE WHEN c.category IS NULL THEN 'Uncategorised'
# MAGIC                    WHEN c.is_preferred THEN 'Preferred' ELSE 'Non-preferred' END) AS branch,
# MAGIC        round(sum(p.amount_gbp), 2) AS branch_total_gbp
# MAGIC FROM `1_supplier_payments` p
# MAGIC LEFT JOIN `1_supplier_categories` c USING (supplier_name)     -- LEFT: keep payments with no category
# MAGIC WHERE p.status = 'Paid'
# MAGIC GROUP BY ALL;
# MAGIC
# MAGIC SELECT * FROM my_control_sheet ORDER BY branch;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- The tie-out: branches versus the whole. variance must be 0.00
# MAGIC SELECT (SELECT round(sum(branch_total_gbp), 2) FROM my_control_sheet)                       AS sum_of_branches,
# MAGIC        (SELECT round(sum(amount_gbp), 2) FROM `1_supplier_payments` WHERE status = 'Paid') AS control_total,
# MAGIC        (SELECT round(sum(branch_total_gbp), 2) FROM my_control_sheet)
# MAGIC      - (SELECT round(sum(amount_gbp), 2) FROM `1_supplier_payments` WHERE status = 'Paid') AS variance;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Who is missing from the lookup? This is the list to send to Procurement.
# MAGIC SELECT p.supplier_name, count(*) AS payments, round(sum(p.amount_gbp), 2) AS total_paid_gbp
# MAGIC FROM `1_supplier_payments` p
# MAGIC LEFT ANTI JOIN `1_supplier_categories` c USING (supplier_name)
# MAGIC WHERE p.status = 'Paid'
# MAGIC GROUP BY p.supplier_name;

# COMMAND ----------

check("A3")
