# Databricks notebook source
# MAGIC %md
# MAGIC # A1 — Solution: spend by category
# MAGIC
# MAGIC ## The flow
# MAGIC | # | Operator | Settings |
# MAGIC |---|---|---|
# MAGIC | 1 | Source | `1_supplier_payments` |
# MAGIC | 2 | Source | `1_supplier_categories` |
# MAGIC | 3 | Filter | `status` Is equal to `Paid` |
# MAGIC | 4 | Join | Filter **Included** + categories, on `supplier_name`, Inner join |
# MAGIC | 5 | Aggregate | SUM `amount_gbp` → `total_paid_gbp`, COUNT `payment_id` → `payments`, group by `category` |
# MAGIC | 6 | Sort | `total_paid_gbp` DESC |
# MAGIC | 7 | Output | table `my_spend_by_category`, Overwrite |
# MAGIC
# MAGIC ## One prompt that builds it
# MAGIC Paste into the Genie Code prompt above an empty canvas (swap in your catalog and schema):
# MAGIC
# MAGIC > Using 1_supplier_payments and 1_supplier_categories in my schema, keep only payments with status
# MAGIC > Paid, join to the categories on supplier_name, and show total amount_gbp as total_paid_gbp and the
# MAGIC > number of payments by category, highest first. Write the result to a table called my_spend_by_category.
# MAGIC
# MAGIC ## The same logic as SQL
# MAGIC Running the cell below creates the table, so you can carry on even if your flow isn't finished.

# COMMAND ----------

# MAGIC %run ../../notebooks/00_setup/02_check

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE my_spend_by_category AS
# MAGIC SELECT c.category,
# MAGIC        round(sum(p.amount_gbp), 2) AS total_paid_gbp,
# MAGIC        count(p.payment_id)         AS payments
# MAGIC FROM `1_supplier_payments` p
# MAGIC JOIN `1_supplier_categories` c USING (supplier_name)
# MAGIC WHERE p.status = 'Paid'
# MAGIC GROUP BY c.category
# MAGIC ORDER BY total_paid_gbp DESC;
# MAGIC
# MAGIC SELECT * FROM my_spend_by_category ORDER BY total_paid_gbp DESC;

# COMMAND ----------

check("A1")
