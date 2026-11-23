# Databricks notebook source
# MAGIC %md
# MAGIC # A4 — Solution: aged debtors
# MAGIC
# MAGIC ## A prompt that works
# MAGIC > Using 1_ar_invoices in my schema, build an aged debtors report as at 2026-10-31. Outstanding is
# MAGIC > amount_gbp minus amount_paid_gbp; ignore invoices with nothing outstanding. Age each invoice by the
# MAGIC > number of days from due_date to 2026-10-31 and put it in a bucket called 'Not due' (0 days or
# MAGIC > fewer), '1-30', '31-60', '61-90' or '90+'. Sum outstanding as outstanding_gbp by broker_name and
# MAGIC > age_bucket. Write the result to a table called my_aged_debtors.
# MAGIC
# MAGIC ## The flow it should produce
# MAGIC | # | Operator | Settings |
# MAGIC |---|---|---|
# MAGIC | 1 | Source | `1_ar_invoices` |
# MAGIC | 2 | Prepare | `outstanding` = `amount_gbp - amount_paid_gbp`; `days_overdue` = `datediff(DATE'2026-10-31', due_date)`; `age_bucket` = the CASE below |
# MAGIC | 3 | Filter | `outstanding` greater than 0 |
# MAGIC | 4 | Aggregate | SUM `outstanding` → `outstanding_gbp`, group by `broker_name`, `age_bucket` |
# MAGIC | 5 | Output | table `my_aged_debtors` |
# MAGIC
# MAGIC ## The same logic as SQL

# COMMAND ----------

# MAGIC %run ../../notebooks/00_setup/02_check

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE my_aged_debtors AS
# MAGIC SELECT broker_name,
# MAGIC        CASE WHEN datediff(DATE'2026-10-31', due_date) <= 0  THEN 'Not due'
# MAGIC             WHEN datediff(DATE'2026-10-31', due_date) <= 30 THEN '1-30'
# MAGIC             WHEN datediff(DATE'2026-10-31', due_date) <= 60 THEN '31-60'
# MAGIC             WHEN datediff(DATE'2026-10-31', due_date) <= 90 THEN '61-90'
# MAGIC             ELSE '90+' END                              AS age_bucket,
# MAGIC        round(sum(amount_gbp - amount_paid_gbp), 2)       AS outstanding_gbp
# MAGIC FROM `1_ar_invoices`
# MAGIC WHERE amount_gbp - amount_paid_gbp > 0
# MAGIC GROUP BY ALL;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- The layout Credit Control wants: one row per broker, a column per bucket
# MAGIC SELECT * FROM my_aged_debtors
# MAGIC PIVOT (sum(outstanding_gbp) FOR age_bucket IN ('Not due', '1-30', '31-60', '61-90', '90+'))
# MAGIC ORDER BY `90+` DESC NULLS LAST;

# COMMAND ----------

check("A4")
