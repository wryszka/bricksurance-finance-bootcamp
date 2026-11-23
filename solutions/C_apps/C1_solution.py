# Databricks notebook source
# MAGIC %md
# MAGIC # C1 — Solution: the journal approvals app
# MAGIC
# MAGIC A finished app is in the folder **`journal_approvals_app`** next to this notebook:
# MAGIC
# MAGIC | File | What it is |
# MAGIC |---|---|
# MAGIC | `app.py` | the whole app: about 70 lines of Streamlit. One `run()` function, one `SELECT`, one `UPDATE` |
# MAGIC | `app.yaml` | how to start it, which SQL warehouse to use, and **which schema to read** |
# MAGIC | `requirements.txt` | the libraries it needs |
# MAGIC
# MAGIC ## Deploy it
# MAGIC 1. Run the cells below. The first prints your schema; this notebook then writes it into
# MAGIC    `journal_approvals_app/app.yaml` for you.
# MAGIC 2. Left sidebar → **Compute → Apps → Create app → Create a custom app**. Name it `journal-approvals`.
# MAGIC 3. Under **App resources** add a **SQL warehouse**, resource key `sql-warehouse`.
# MAGIC 4. **Deploy** → choose the `journal_approvals_app` folder.
# MAGIC 5. Type `journal-approvals` into the `app_name` box at the top of this notebook and run the grant cell.
# MAGIC 6. Open the app.

# COMMAND ----------

# MAGIC %run ../../notebooks/00_setup/02_check

# COMMAND ----------

import os, re

path = os.path.join(os.getcwd(), "journal_approvals_app", "app.yaml")
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

# MAGIC %md
# MAGIC ## How the app talks to your data
# MAGIC - The app runs as **its own identity** (a service principal). `Config()` in `app.py` picks that
# MAGIC   identity up automatically; there are no passwords or tokens in the code.
# MAGIC - It reaches the table through the **SQL warehouse** you attached as a resource.
# MAGIC - It can only see what you **granted** it. Revoke the grant and the app goes blind.
# MAGIC - The signed-in user's email arrives in a request header, which is how `decided_by` is filled in.

# COMMAND ----------

check("C1")
