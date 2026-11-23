# Databricks notebook source
# MAGIC %md
# MAGIC # A1 — Your first flow: where does the money go?
# MAGIC
# MAGIC **About 25 minutes · Lakeflow Designer · needs only the setup**
# MAGIC
# MAGIC ## The business problem
# MAGIC The CFO asks: *"How much have we paid suppliers this year, by type of spend?"*
# MAGIC The payments extract has no spend category on it. The category lives in a separate lookup
# MAGIC maintained by Procurement. In a spreadsheet this is a VLOOKUP and a pivot table, redone by
# MAGIC hand every month. You are going to build it once.
# MAGIC
# MAGIC ## What you will build
# MAGIC A flow with five steps that writes a table called **`my_spend_by_category`**.
# MAGIC
# MAGIC | Your tables | What is in them |
# MAGIC |---|---|
# MAGIC | `1_supplier_payments` | every payment to a supplier, January to October 2026 |
# MAGIC | `1_supplier_categories` | supplier → spend category |
# MAGIC
# MAGIC > **New to the canvas?** In the left sidebar click **New → Visual data prep**. Add tables with
# MAGIC > **Browse all data** (or drag them from the **Catalog** pane). Add a step by hovering over an
# MAGIC > operator and clicking the **+** next to it. Click any operator to preview its rows.
# MAGIC > Previews use a sample; **Run all** processes everything and writes your table.
# MAGIC
# MAGIC ## Steps
# MAGIC 1. **New → Visual data prep**. Click the name at the top and call it `A1 spend by category`.
# MAGIC 2. Add both tables from **your** schema (the cell below prints its name).
# MAGIC 3. **Filter** the payments: `status` **Is equal to** `Paid` → **Apply**. Reversed payments are not spend.
# MAGIC    Notice the Filter has two outputs, **Included** and **Excluded**. Click each one.
# MAGIC 4. **Join**: connect the Filter's **Included** output and the categories table. Match
# MAGIC    `supplier_name` on both sides, **Join type** = **Inner join** → **Apply**.
# MAGIC 5. **Aggregate**: under **Aggregate by** pick `amount_gbp`, `SUM`, and name it **`total_paid_gbp`**.
# MAGIC    **+ Add aggregation**: `payment_id`, `COUNT`, name it `payments`. Under **Group by** pick `category`.
# MAGIC 6. **Sort** by `total_paid_gbp`, **DESC**.
# MAGIC 7. **Output**: **Output type** = Table, **Table name** = `my_spend_by_category`, **Output location** =
# MAGIC    your catalog and schema, **Write mode** = Overwrite. Then click **Run all**.
# MAGIC
# MAGIC ## Check
# MAGIC Run the two cells below. Then answer for yourself: which category is the biggest, and is it
# MAGIC the one you expected for an insurer?
# MAGIC
# MAGIC ## If you have time
# MAGIC - Add a second **Group by** column (`company_code`). Which company spends most on Professional Fees?
# MAGIC - Click the **History** icon on the right. Every change you made is there, and you can compare versions.
# MAGIC
# MAGIC **Stuck?** `solutions/A_lakeflow_designer/A1_solution` has the flow step by step, one prompt
# MAGIC that builds the whole thing, and the same logic as SQL.

# COMMAND ----------

# MAGIC %run ../00_setup/02_check

# COMMAND ----------

check("A1")
