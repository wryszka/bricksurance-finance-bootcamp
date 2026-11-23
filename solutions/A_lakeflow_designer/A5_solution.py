# Databricks notebook source
# MAGIC %md
# MAGIC # A5 — Solution: migrating the PO accruals workflow
# MAGIC
# MAGIC ## Legacy tool → Designer operator
# MAGIC | Legacy tool | What it does | Designer operator |
# MAGIC |---|---|---|
# MAGIC | 1, 2 Input | read two CSV extracts from a shared drive | **Source** × 2: `1_purchase_orders`, `1_supplier_invoices` |
# MAGIC | 3 Filter | not cancelled, goods received on or before period end | **Filter** |
# MAGIC | 4 Filter | invoices dated on or before period end | **Filter** |
# MAGIC | 5 Summarize | invoiced per purchase order | **Aggregate**: SUM `invoice_amount_gbp` → `invoiced_gbp`, group by `po_id` |
# MAGIC | 6 Join + 7 Union | match, and keep purchase orders with no invoice | **Join**, type **Left join** (one operator instead of two) |
# MAGIC | 8 Formula | accrual = ordered − invoiced | **Prepare**: `accrual_gbp` = `po_amount_gbp - coalesce(invoiced_gbp, 0)` |
# MAGIC | 9 Filter | accrual greater than zero | **Filter** |
# MAGIC | 10 Summarize | by company and cost centre | **Aggregate**: COUNT `po_id` → `po_count`, SUM `accrual_gbp`, group by `company_code`, `cost_centre` |
# MAGIC | 11 Output | spreadsheet on a shared drive | **Output**: table `my_accruals_summary` |
# MAGIC
# MAGIC ## The same logic as SQL

# COMMAND ----------

# MAGIC %run ../../notebooks/00_setup/02_check

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE my_accruals_summary AS
# MAGIC WITH live_pos AS (                                   -- tool 3
# MAGIC   SELECT * FROM `1_purchase_orders`
# MAGIC   WHERE po_status <> 'Cancelled' AND goods_received_date <= DATE'2026-10-31'),
# MAGIC invoiced AS (                                        -- tools 4 and 5
# MAGIC   SELECT po_id, sum(invoice_amount_gbp) AS invoiced_gbp
# MAGIC   FROM `1_supplier_invoices`
# MAGIC   WHERE invoice_date <= DATE'2026-10-31'
# MAGIC   GROUP BY po_id),
# MAGIC accrual AS (                                         -- tools 6, 7 and 8
# MAGIC   SELECT p.*, p.po_amount_gbp - coalesce(i.invoiced_gbp, 0) AS accrual_gbp
# MAGIC   FROM live_pos p LEFT JOIN invoiced i USING (po_id))
# MAGIC SELECT company_code, cost_centre,                    -- tools 9 and 10
# MAGIC        count(po_id)                AS po_count,
# MAGIC        round(sum(accrual_gbp), 2)  AS accrual_gbp
# MAGIC FROM accrual
# MAGIC WHERE accrual_gbp > 0.005
# MAGIC GROUP BY company_code, cost_centre;
# MAGIC
# MAGIC SELECT * FROM my_accruals_summary ORDER BY company_code, cost_centre;

# COMMAND ----------

# MAGIC %md
# MAGIC ## The guardrail the legacy process never had
# MAGIC Purchase orders invoiced for more than was ordered. In the old workflow these were silently
# MAGIC dropped by the "accrual > 0" filter.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT p.po_id, p.supplier_name, p.po_amount_gbp, sum(i.invoice_amount_gbp) AS invoiced_gbp
# MAGIC FROM `1_purchase_orders` p JOIN `1_supplier_invoices` i USING (po_id)
# MAGIC WHERE i.invoice_date <= DATE'2026-10-31'
# MAGIC GROUP BY ALL
# MAGIC HAVING sum(i.invoice_amount_gbp) > p.po_amount_gbp + 0.005;

# COMMAND ----------

check("A5")
