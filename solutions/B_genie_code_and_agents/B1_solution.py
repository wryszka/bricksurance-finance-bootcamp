# Databricks notebook source
# MAGIC %md
# MAGIC # B1 — Solution: raw GL files → trial balance
# MAGIC
# MAGIC The same pipeline Genie Code should arrive at, written out. Run it top to bottom.

# COMMAND ----------

# MAGIC %run ../../notebooks/00_setup/02_check

# COMMAND ----------

# MAGIC %md
# MAGIC ## Bronze — exactly as it arrived

# COMMAND ----------

from pyspark.sql import functions as F

bronze = (spark.read.option("header", True).csv(f"{RAW_VOLUME}/gl/")      # every column stays text
          .withColumn("_source_file", F.col("_metadata.file_name"))
          .withColumn("_loaded_at", F.current_timestamp()))
bronze.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable("my_bronze_gl")
print(f"bronze: {spark.table('my_bronze_gl').count():,} rows from {bronze.select('_source_file').distinct().count()} files")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Silver — the four fixes
# MAGIC 1. test journals out
# MAGIC 2. exact duplicates out
# MAGIC 3. `15/03/2026` → a real date
# MAGIC 4. `(1,234.50)` → `-1234.50`

# COMMAND ----------

silver = (
    spark.table("my_bronze_gl")
    .filter("posted_by <> 'TESTUSER'")
    .dropDuplicates(["journal_id", "line_no"])
    .withColumn("posting_date", F.to_date("posting_date", "dd/MM/yyyy"))
    .withColumn("amount_gbp", F.expr("""
        CASE WHEN amount LIKE '(%' THEN -1 ELSE 1 END
        * cast(regexp_replace(amount, '[(),]', '') AS double)"""))
    .withColumn("period", F.date_format("posting_date", "yyyy-MM"))
    .select("journal_id", F.col("line_no").cast("int").alias("line_no"), "posting_date", "period",
            "company_code", "account_code", "cost_centre", "amount_gbp", "description", "posted_by", "_source_file")
)
silver.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable("my_silver_gl")

b, s = spark.table("my_bronze_gl").count(), spark.table("my_silver_gl").count()
print(f"bronze {b:,} -> silver {s:,}  ({b - s:,} rows removed: duplicates and test journals)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prove it — every journal must balance

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT count(*) AS journals,
# MAGIC        sum(CASE WHEN abs(net) > 0.005 THEN 1 ELSE 0 END) AS journals_out_of_balance,
# MAGIC        round(sum(net), 2) AS ledger_net
# MAGIC FROM (SELECT journal_id, sum(amount_gbp) AS net FROM my_silver_gl GROUP BY journal_id);

# COMMAND ----------

# MAGIC %md
# MAGIC ## Gold — the trial balance

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE my_trial_balance AS
# MAGIC SELECT g.period, g.company_code, g.account_code, a.account_name, a.account_type,
# MAGIC        round(sum(CASE WHEN g.amount_gbp > 0 THEN g.amount_gbp ELSE 0 END), 2)  AS debit_gbp,
# MAGIC        round(sum(CASE WHEN g.amount_gbp < 0 THEN -g.amount_gbp ELSE 0 END), 2) AS credit_gbp,
# MAGIC        round(sum(g.amount_gbp), 2)                                             AS net_gbp
# MAGIC FROM my_silver_gl g JOIN `0_accounts` a USING (account_code)
# MAGIC GROUP BY ALL;
# MAGIC
# MAGIC SELECT * FROM my_trial_balance WHERE period = '2026-10' AND company_code = 'C100' ORDER BY account_code;

# COMMAND ----------

check("B1")
