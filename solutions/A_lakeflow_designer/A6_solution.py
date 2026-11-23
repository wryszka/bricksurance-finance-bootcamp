# Databricks notebook source
# MAGIC %md
# MAGIC # A6 — Solution: a parameterised flow, scheduled
# MAGIC
# MAGIC ## The flow
# MAGIC | # | Operator | Settings |
# MAGIC |---|---|---|
# MAGIC | — | Parameter | `month` = `2026-10` |
# MAGIC | 1 | Source | `1_supplier_payments` |
# MAGIC | 2 | Filter | `status` Is equal to `Paid` **and** expression `date_format(payment_date, 'yyyy-MM') = :month` |
# MAGIC | 3 | Aggregate | SUM `amount_gbp` → `total_paid_gbp`, group by `supplier_name` |
# MAGIC | 4 | Output | table `my_monthly_supplier_spend`, Overwrite |
# MAGIC
# MAGIC Then **Schedule** → set `month` on the schedule → **Run now** → **View in Jobs**.
# MAGIC
# MAGIC ## The same logic as a notebook with a parameter
# MAGIC The widget below plays the role of the flow's parameter. A notebook like this can be scheduled
# MAGIC the same way (the **Schedule** button, top right).

# COMMAND ----------

# MAGIC %run ../../notebooks/00_setup/02_check

# COMMAND ----------

dbutils.widgets.text("month", "2026-10", "Month (yyyy-MM)")

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE my_monthly_supplier_spend AS
# MAGIC SELECT supplier_name, round(sum(amount_gbp), 2) AS total_paid_gbp
# MAGIC FROM `1_supplier_payments`
# MAGIC WHERE status = 'Paid' AND date_format(payment_date, 'yyyy-MM') = :month
# MAGIC GROUP BY supplier_name;
# MAGIC
# MAGIC SELECT * FROM my_monthly_supplier_spend ORDER BY total_paid_gbp DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ## For the engineers: the same flow in a bundle
# MAGIC A visual data prep file is deployed like a notebook. In a Declarative Automation Bundle:
# MAGIC
# MAGIC ```yaml
# MAGIC resources:
# MAGIC   jobs:
# MAGIC     monthly_supplier_spend:
# MAGIC       name: monthly_supplier_spend
# MAGIC       parameters:
# MAGIC         - name: month
# MAGIC           default: "2026-10"
# MAGIC       tasks:
# MAGIC         - task_key: run_flow
# MAGIC           notebook_task:
# MAGIC             notebook_path: ./A6 monthly supplier spend.designer.ipynb
# MAGIC ```
# MAGIC
# MAGIC `databricks bundle deploy` then `databricks bundle run monthly_supplier_spend`. Bundle targets
# MAGIC supply different parameter values for test and production.

# COMMAND ----------

check("A6")
