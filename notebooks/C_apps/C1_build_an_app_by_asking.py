# Databricks notebook source
# MAGIC %md
# MAGIC # C1 — Build an app by asking: journal approvals
# MAGIC
# MAGIC **About 35 minutes · Genie Code + Databricks Apps · needs only the setup**
# MAGIC
# MAGIC ## The business problem
# MAGIC At month-end, manual journal requests are approved by email. Somebody keeps a spreadsheet of
# MAGIC who said yes to what. Auditors love asking for it. You are going to replace the email chain
# MAGIC with a small app: a list of pending requests, an Approve and a Reject button, and every
# MAGIC decision written back to a governed table with a name and a comment on it.
# MAGIC
# MAGIC You will not write the code. You will describe the app.
# MAGIC
# MAGIC ## Your table
# MAGIC `3_journal_requests` — about 60 requests; `status` is Pending, Approved or Rejected.
# MAGIC Policy: anything of **£50,000 or more** needs the Financial Controller.
# MAGIC
# MAGIC ## Part 1 — describe the app (15 min)
# MAGIC Open **Genie Code** (full page works best for this) and brief it. For example:
# MAGIC
# MAGIC > Build a Streamlit app for Databricks Apps called journal approvals, in a new folder in my home
# MAGIC > directory. It reads the table 3_journal_requests in my schema through a SQL warehouse. Show three
# MAGIC > headline numbers: pending requests, pending value in GBP, and how many pending requests are
# MAGIC > £50,000 or more. Show the requests in a table with a filter on status. Let me pick a pending
# MAGIC > request, type a comment, and click Approve or Reject. Rejecting needs a comment. Write the
# MAGIC > decision back to the table: status, decided_by (the signed-in user's email) and decision_comment.
# MAGIC > Warn me when the amount is £50,000 or more. Include app.yaml and requirements.txt.
# MAGIC
# MAGIC Read what it produced. You should be able to follow it: one function that runs SQL, one
# MAGIC `SELECT`, one `UPDATE`. Ask it to explain anything you can't follow.
# MAGIC
# MAGIC ## Part 2 — deploy it (10 min)
# MAGIC Ask Genie Code to deploy the app for you, or do it by hand:
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
# MAGIC ## Part 3 — use it (5 min)
# MAGIC Approve one request, reject another with a comment, then run the check at the bottom.
# MAGIC Then open `3_journal_requests` in **Catalog** and look at the table's **History** tab: every
# MAGIC decision is a versioned change. That is your audit trail, and you didn't build it.
# MAGIC
# MAGIC ## Make it yours (pick one)
# MAGIC Change the app by asking, then redeploy:
# MAGIC - *"Only let people approve requests under £50,000 unless they tick a box confirming they are the Financial Controller."*
# MAGIC - *"Add a chart of pending value by cost centre."*
# MAGIC - *"Add a button that downloads the approved requests as a CSV for the journal upload."*
# MAGIC
# MAGIC ## Worth discussing
# MAGIC Which spreadsheet in your team is really an app that nobody has built yet?
# MAGIC
# MAGIC **Stuck?** A finished version is in `solutions/C_apps/journal_approvals_app/`. Edit
# MAGIC `BOOTCAMP_SCHEMA` in its `app.yaml`, then deploy that folder. `solutions/C_apps/C1_solution`
# MAGIC walks through it.

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

check("C1")
