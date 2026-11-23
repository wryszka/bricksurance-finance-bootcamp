# Databricks notebook source
# MAGIC %md
# MAGIC # C2 — Retire a spreadsheet: from macro to app
# MAGIC
# MAGIC **About 40 minutes · Genie Code + Databricks Apps · needs only the setup**
# MAGIC
# MAGIC ## The business problem
# MAGIC *"Accruals Tracker v7 FINAL (2).xlsm"* calculates the month-end purchase order accrual. It was
# MAGIC written years ago by someone who has since moved on. It works — everyone thinks. It is on the
# MAGIC EUC register and Internal Audit want it gone. You are going to take it apart, find out what it
# MAGIC really does, and rebuild it as something governed.
# MAGIC
# MAGIC ## What you have
# MAGIC - The macro: `legacy/spreadsheet_euc/AccrualsTracker.bas` (in this repo, next to `notebooks`)
# MAGIC - How it is used today: `legacy/spreadsheet_euc/README.md`
# MAGIC - The data it needs, as governed tables: `1_purchase_orders`, `1_supplier_invoices`
# MAGIC
# MAGIC ## Part 1 — understand it (10 min)
# MAGIC Open the `.bas` file, then open **Genie Code** and ask (paste the macro in, or point it at the file):
# MAGIC
# MAGIC > Read this VBA macro. Explain in plain English what it does, step by step, for someone in Finance.
# MAGIC > Then list every risk you can see: anything hard-coded, anything that could silently give a wrong
# MAGIC > number, and anything that depends on a person doing something by hand.
# MAGIC
# MAGIC There are **at least three** things in there that should worry you. Did it find them? Did you?
# MAGIC
# MAGIC ## Part 2 — rebuild the logic (10 min)
# MAGIC > Rebuild the macro's calculation as SQL on my tables 1_purchase_orders and 1_supplier_invoices.
# MAGIC > Create a table called my_accruals_review with company_code, cost_centre, po_count and accrual_gbp.
# MAGIC > Use a period end of 2026-10-31. Do not copy the macro's row limit.
# MAGIC
# MAGIC Run the check at the bottom. It compares your table with the correct accrual.
# MAGIC
# MAGIC Now the interesting question: **the spreadsheet would have reported a different number.** Ask:
# MAGIC > How much lower would the accrual be if only the first 999 purchase orders (by po_id) were
# MAGIC > processed, as the macro does?
# MAGIC
# MAGIC That difference is an error that has been going into the accounts.
# MAGIC
# MAGIC ## Part 3 — give it a front end (15 min)
# MAGIC > Build a Streamlit app for Databricks Apps that shows my_accruals_review joined to 0_cost_centres:
# MAGIC > headline numbers for total accrual and number of purchase orders, a company filter, a table that
# MAGIC > marks lines of £250,000 or more for review, and a bar chart of accrual by cost centre.
# MAGIC
# MAGIC Deploy it:
# MAGIC
# MAGIC ### Deploying a custom app (the same for any app)
# MAGIC 1. Left sidebar → **Compute → Apps → Create app → Create a custom app**. Give it a short name, e.g. `journal-approvals`.
# MAGIC 2. Under **App resources** add a **SQL warehouse** and leave the resource key as `sql-warehouse`.
# MAGIC 3. **Deploy**, and choose the folder that holds `app.py`, `app.yaml` and `requirements.txt`.
# MAGIC 4. Give the app permission to use your tables: type the app's name into the `app_name` box at the
# MAGIC    top of this notebook and run the cell below. An app has its own identity; it sees nothing until
# MAGIC    you grant it access. That is the governance working, not a bug.
# MAGIC 5. Open the app's URL.
# MAGIC
# MAGIC ## What you have replaced
# MAGIC | The spreadsheet | What you built |
# MAGIC |---|---|
# MAGIC | data pasted in by hand | governed tables, refreshed by a pipeline |
# MAGIC | a date edited in the code each month | a parameter |
# MAGIC | a silent 1,000-row limit | no limit |
# MAGIC | `On Error Resume Next` | errors that stop the process and tell someone |
# MAGIC | emailed around for approval | an app, with access controlled per person |
# MAGIC | no history | every version of every table |
# MAGIC
# MAGIC ## Worth discussing
# MAGIC How many files like this are on your EUC register? Which one would you do first, and what
# MAGIC would you need to see before you trusted the replacement?
# MAGIC
# MAGIC **Stuck?** `solutions/C_apps/C2_solution` and the finished app in `solutions/C_apps/accruals_review_app/`.

# COMMAND ----------

# MAGIC %run ../00_setup/02_check

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
