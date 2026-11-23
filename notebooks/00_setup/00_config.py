# Databricks notebook source
# MAGIC %md
# MAGIC # 00 — Config
# MAGIC
# MAGIC **About this bootcamp:** all data is synthetic; Bricksurance is a fictional insurer.
# MAGIC
# MAGIC You never need to edit this notebook. Every exercise runs it for you and it works out
# MAGIC where your data lives:
# MAGIC
# MAGIC | Where you are | Catalog it picks |
# MAGIC |---|---|
# MAGIC | Databricks Free Edition | `workspace` |
# MAGIC | A company workspace | the workspace default catalog (override with the widget) |
# MAGIC
# MAGIC Everyone gets **their own schema** (`finance_<your name>`), so you cannot break your
# MAGIC neighbour's tables.

# COMMAND ----------

_user = spark.sql("SELECT current_user()").first()[0]
_user_slug = "".join(c if c.isalnum() else "_" for c in _user.split("@")[0].lower())

# Widgets are per notebook, so the default is detected rather than hard-coded.
_default_catalog = spark.sql("SELECT current_catalog()").first()[0]
if _default_catalog in ("spark_catalog", "hive_metastore", "system", "samples"):
    _visible = {r[0] for r in spark.sql("SHOW CATALOGS").collect()}
    _default_catalog = next((c for c in ("workspace", "main") if c in _visible), "workspace")

dbutils.widgets.text("catalog", _default_catalog, "Catalog")
dbutils.widgets.text("schema", f"finance_{_user_slug}", "Schema")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
FQ = f"{CATALOG}.{SCHEMA}"
RAW_VOLUME = f"/Volumes/{CATALOG}/{SCHEMA}/raw"

# The bootcamp is set at month-end close for October 2026.
PERIOD_END = "2026-10-31"

assert spark.sql(f"SHOW CATALOGS LIKE '{CATALOG}'").count() == 1, (
    f"Catalog '{CATALOG}' not found in this workspace - "
    "set the 'catalog' widget at the top of this notebook to one you can use")

# COMMAND ----------

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {FQ}")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {FQ}.raw")
spark.sql(f"USE {FQ}")

print(f"Your schema: {FQ}")
print(f"Raw files:   {RAW_VOLUME}")
