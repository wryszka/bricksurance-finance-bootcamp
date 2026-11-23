# Databricks notebook source
# MAGIC %md
# MAGIC # B2 — Solution: a finished dashboard, created for you
# MAGIC
# MAGIC Run this notebook and a finished **Costs against budget** dashboard appears in your home folder,
# MAGIC pointing at *your* schema. Open it, click around, then open the draft to see how each chart is
# MAGIC defined. It is built from `costs_against_budget.lvdash.template.json` in this folder.
# MAGIC
# MAGIC ## The three things that happened
# MAGIC | What you see | Why (it is written in the journal descriptions) |
# MAGIC |---|---|
# MAGIC | **IT and Software** about 35% over budget every month from July | *Cloud migration - dual running costs*: paying for the old and the new platform at once |
# MAGIC | **Marketing** about 40% under budget January to May | *Spring campaign postponed* |
# MAGIC | **Claims Handling Costs** about 60% over in September only | *Storm Brigid surge - temporary claims handlers* |

# COMMAND ----------

# MAGIC %run ../../notebooks/00_setup/02_check

# COMMAND ----------

import json, os
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
template = open(os.path.join(os.getcwd(), "costs_against_budget.lvdash.template.json")).read()
serialized = template.replace("__SCHEMA__", FQ)            # point every dataset at your schema

warehouse = next(iter(w.warehouses.list()), None)
assert warehouse, "No SQL warehouse found. Create or start one under SQL Warehouses, then run again."
user = spark.sql("SELECT current_user()").first()[0]
body = {"display_name": "Costs against budget (solution)", "warehouse_id": warehouse.id,
        "parent_path": f"/Workspace/Users/{user}", "serialized_dashboard": serialized}

try:
    made = w.api_client.do("POST", "/api/2.0/lakeview/dashboards", body=body)
except Exception as e:
    if "already exists" not in str(e):
        raise
    body["display_name"] += " " + spark.sql("SELECT date_format(now(), 'HH:mm:ss')").first()[0]
    made = w.api_client.do("POST", "/api/2.0/lakeview/dashboards", body=body)

host = spark.conf.get("spark.databricks.workspaceUrl")
print("Open your dashboard:")
print(f"https://{host}/dashboardsv3/{made['dashboard_id']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## The SQL behind the three questions
# MAGIC If you prefer to see the answers as numbers.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT account_name, period,
# MAGIC        round(sum(actual_gbp))   AS actual_gbp,
# MAGIC        round(sum(budget_gbp))   AS budget_gbp,
# MAGIC        round(sum(variance_gbp)) AS variance_gbp,
# MAGIC        round(100 * sum(variance_gbp) / sum(budget_gbp), 1) AS variance_pct
# MAGIC FROM `2_actual_vs_budget`
# MAGIC WHERE account_code IN ('6100', '6300', '5100')
# MAGIC GROUP BY account_name, period
# MAGIC ORDER BY account_name, period;
