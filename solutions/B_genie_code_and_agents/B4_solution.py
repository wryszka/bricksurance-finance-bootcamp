# Databricks notebook source
# MAGIC %md
# MAGIC # B4 — Solution: variance commentary drafted by an AI function
# MAGIC
# MAGIC One statement: find the variances, gather the evidence, ask for the commentary.

# COMMAND ----------

# MAGIC %run ../../notebooks/00_setup/02_check

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE TABLE my_variance_commentary AS
# MAGIC WITH by_account AS (
# MAGIC   SELECT account_code, account_name,
# MAGIC          round(sum(actual_gbp))   AS actual_gbp,
# MAGIC          round(sum(budget_gbp))   AS budget_gbp,
# MAGIC          round(sum(actual_gbp) - sum(budget_gbp)) AS variance_gbp,
# MAGIC          round(100 * (sum(actual_gbp) - sum(budget_gbp)) / sum(budget_gbp), 1) AS variance_pct
# MAGIC   FROM `2_actual_vs_budget`
# MAGIC   WHERE account_type = 'Expense' AND period = '2026-09'
# MAGIC   GROUP BY account_code, account_name),
# MAGIC variances AS (
# MAGIC   SELECT * FROM by_account ORDER BY abs(variance_gbp) DESC LIMIT 5),
# MAGIC evidence AS (
# MAGIC   SELECT account_code, array_join(collect_set(description), '; ') AS journal_descriptions
# MAGIC   FROM `2_gl_journal`
# MAGIC   WHERE period = '2026-09'
# MAGIC   GROUP BY account_code)
# MAGIC SELECT v.*, e.journal_descriptions,
# MAGIC        ai_gen(concat(
# MAGIC          'You are drafting month-end variance commentary for a finance director at an insurer. ',
# MAGIC          'Write at most two plain-English sentences. Say whether the variance is adverse (cost above budget) ',
# MAGIC          'or favourable (cost below budget), give the amount in GBP, and give the likely cause using ONLY ',
# MAGIC          'the journal descriptions provided. If the descriptions do not explain it, say so. ',
# MAGIC          'Account: ', v.account_name,
# MAGIC          '. Actual: ', v.actual_gbp, '. Budget: ', v.budget_gbp,
# MAGIC          '. Variance (actual minus budget): ', v.variance_gbp, ' (', v.variance_pct, '%). ',
# MAGIC          'Journal descriptions this month: ', e.journal_descriptions)) AS commentary
# MAGIC FROM variances v JOIN evidence e USING (account_code);

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT account_name, variance_gbp, variance_pct, commentary FROM my_variance_commentary ORDER BY abs(variance_gbp) DESC;

# COMMAND ----------

check("B4")
