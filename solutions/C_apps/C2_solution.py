# Databricks notebook source
# MAGIC %md
# MAGIC # C2 — Solution: from macro to governed table to app
# MAGIC
# MAGIC ## What the macro does
# MAGIC 1. Loops over the pasted purchase orders, rows 2 to **1000**.
# MAGIC 2. Skips cancelled purchase orders and those with no goods received by the period end.
# MAGIC 3. For each one, loops over the pasted invoices (again rows 2 to 1000) and adds up those dated on or before the period end.
# MAGIC 4. Accrual = ordered − invoiced; writes a row if it is positive.
# MAGIC 5. Refreshes a pivot by company and cost centre and highlights lines of £250,000 or more.
# MAGIC
# MAGIC ## The three things that should worry you
# MAGIC | Risk | Where | Why it matters |
# MAGIC |---|---|---|
# MAGIC | **Silent row limit** | `Const LAST_ROW = 1000` | There are 1,200 purchase orders. The last 201 are never read. The accrual is understated and nothing tells you. |
# MAGIC | **Errors are swallowed** | `On Error Resume Next` | A bad date makes the comparison fail quietly; the purchase order is skipped or mis-handled with no message. |
# MAGIC | **Hard-coded period end** | `Const PERIOD_END = #10/31/2026#` | Edited by hand in the code every month. Forget once and you accrue the wrong period. |
# MAGIC
# MAGIC Also: data pasted in by hand, no record of which extract was used, approval by email, journal keyed manually.
# MAGIC
# MAGIC ## The logic, rebuilt

# COMMAND ----------

# MAGIC %run ../../notebooks/00_setup/02_check

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE my_accruals_review AS
# MAGIC WITH invoiced AS (
# MAGIC   SELECT po_id, sum(invoice_amount_gbp) AS invoiced_gbp
# MAGIC   FROM `1_supplier_invoices`
# MAGIC   WHERE invoice_date <= DATE'2026-10-31'
# MAGIC   GROUP BY po_id)
# MAGIC SELECT p.company_code, p.cost_centre,
# MAGIC        count(p.po_id)                                                AS po_count,
# MAGIC        round(sum(p.po_amount_gbp - coalesce(i.invoiced_gbp, 0)), 2)   AS accrual_gbp
# MAGIC FROM `1_purchase_orders` p LEFT JOIN invoiced i USING (po_id)
# MAGIC WHERE p.po_status <> 'Cancelled'
# MAGIC   AND p.goods_received_date <= DATE'2026-10-31'
# MAGIC   AND p.po_amount_gbp - coalesce(i.invoiced_gbp, 0) > 0.005
# MAGIC GROUP BY p.company_code, p.cost_centre;
# MAGIC
# MAGIC SELECT * FROM my_accruals_review ORDER BY accrual_gbp DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ## What the spreadsheet has been reporting
# MAGIC The same rules, but only the first 999 purchase orders, as the macro's loop does.

# COMMAND ----------

# MAGIC %sql
# MAGIC WITH invoiced AS (
# MAGIC   SELECT po_id, sum(invoice_amount_gbp) AS invoiced_gbp
# MAGIC   FROM `1_supplier_invoices` WHERE invoice_date <= DATE'2026-10-31' GROUP BY po_id),
# MAGIC accrual AS (
# MAGIC   SELECT p.po_id, p.po_amount_gbp - coalesce(i.invoiced_gbp, 0) AS accrual_gbp,
# MAGIC          row_number() OVER (ORDER BY p.po_id) AS sheet_row
# MAGIC   FROM `1_purchase_orders` p LEFT JOIN invoiced i USING (po_id))
# MAGIC SELECT round(sum(a.accrual_gbp), 2)                                              AS correct_accrual_gbp,
# MAGIC        round(sum(CASE WHEN a.sheet_row <= 999 THEN a.accrual_gbp END), 2)         AS spreadsheet_accrual_gbp,
# MAGIC        round(sum(CASE WHEN a.sheet_row > 999 THEN a.accrual_gbp END), 2)          AS understated_by_gbp
# MAGIC FROM accrual a JOIN `1_purchase_orders` p USING (po_id)
# MAGIC WHERE p.po_status <> 'Cancelled' AND p.goods_received_date <= DATE'2026-10-31' AND a.accrual_gbp > 0.005;

# COMMAND ----------

# MAGIC %md
# MAGIC ## The app
# MAGIC A finished version is in **`accruals_review_app`** next to this notebook. The cell below writes
# MAGIC your schema into its `app.yaml`. Then: **Compute → Apps → Create app → Create a custom app** →
# MAGIC add a **SQL warehouse** resource (key `sql-warehouse`) → **Deploy** that folder → put the app's
# MAGIC name in the `app_name` box and run the grant cell.

# COMMAND ----------

import os, re

path = os.path.join(os.getcwd(), "accruals_review_app", "app.yaml")
text = open(path).read()
text = re.sub(r'(name: BOOTCAMP_SCHEMA\s+value: )"[^"]*"', rf'\1"{FQ}"', text)
open(path, "w").write(text)
print(text)

# COMMAND ----------

dbutils.widgets.text("app_name", "", "Your app's name")
APP = dbutils.widgets.get("app_name").strip()

print(f"Your schema (put this in app.yaml as BOOTCAMP_SCHEMA):  {FQ}\n")
if not APP:
    print("When your app exists, type its name in the 'app_name' box at the top and run this cell again.")
else:
    from databricks.sdk import WorkspaceClient
    sp = WorkspaceClient().apps.get(APP).service_principal_client_id
    for stmt in (f"GRANT USE CATALOG ON CATALOG `{CATALOG}` TO `{sp}`",
                 f"GRANT USE SCHEMA ON SCHEMA {FQ} TO `{sp}`",
                 f"GRANT SELECT, MODIFY ON SCHEMA {FQ} TO `{sp}`"):
        spark.sql(stmt)
    print(f"Done. The app '{APP}' can now read and update the tables in {FQ}.")

# COMMAND ----------

check("C2")
