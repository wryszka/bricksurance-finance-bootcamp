# Databricks notebook source
# MAGIC %md
# MAGIC # B3 — Solution: the Genie agent, its instructions, and the right answers
# MAGIC
# MAGIC ## Set-up
# MAGIC **Genie → New** → tables `2_actual_vs_budget`, `2_gl_journal`, `2_budget`, `0_accounts`,
# MAGIC `0_cost_centres`, `0_companies` → name `Finance month-end`.
# MAGIC
# MAGIC ## Instructions to paste in
# MAGIC ```
# MAGIC - All amounts are in GBP (pounds sterling). The data covers January to October 2026; "year to date" means all of it.
# MAGIC - For actual versus budget questions always use the table 2_actual_vs_budget. In that table actual_gbp and budget_gbp are positive numbers for both revenue and costs.
# MAGIC - variance_gbp = actual minus budget. For Expense accounts a positive variance is an overspend (adverse). For Revenue accounts a positive variance is favourable.
# MAGIC - "Revenue" or "premium" means Gross Written Premium (account 4000) unless the user says otherwise.
# MAGIC - "Operating costs" or "expenses" means Expense accounts excluding Claims Paid (account 5000).
# MAGIC - Expense ratio = operating costs divided by Gross Written Premium, shown as a percentage.
# MAGIC - The table 2_gl_journal is double-entry: debits are positive and credits are negative, so revenue appears as a negative number there. Only use it for journal-level detail such as descriptions, and flip the sign of revenue before showing it.
# MAGIC - When asked why a variance happened, look at the description column of 2_gl_journal for that account and period.
# MAGIC - Company names: C100 is Commercial, C200 is Personal Lines, C300 is Services.
# MAGIC ```
# MAGIC
# MAGIC ## Sample questions to add
# MAGIC - What is our expense ratio year to date, by company?
# MAGIC - Where are we overspending against budget this year?
# MAGIC - Why were claims handling costs so high in September?
# MAGIC - Show actual versus budget for IT and Software by month.
# MAGIC
# MAGIC ## What went wrong before the instructions, and why
# MAGIC | Question | Typical first answer | Cause |
# MAGIC |---|---|---|
# MAGIC | Revenue in September | a negative number | it read `2_gl_journal`, where credits are negative |
# MAGIC | Where are we overspending | a list of favourable variances, or revenue lines | nobody told it which sign is bad for a cost |
# MAGIC | Expense ratio | a guess (often total costs including claims ÷ premium) | the definition lives in people's heads |
# MAGIC | Why were claims handling costs high | "I don't have that information" | it didn't know the reason is in the journal descriptions |
# MAGIC
# MAGIC ## The right answers, as SQL

# COMMAND ----------

# MAGIC %run ../../notebooks/00_setup/02_check

# COMMAND ----------

check("B3")

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Revenue in September: positive, from the reporting table
# MAGIC SELECT round(sum(actual_gbp)) AS gwp_september
# MAGIC FROM `2_actual_vs_budget` WHERE account_code = '4000' AND period = '2026-09';

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Where are we overspending? Costs only, positive variance = bad
# MAGIC SELECT account_name, round(sum(variance_gbp)) AS overspend_gbp,
# MAGIC        round(100 * sum(variance_gbp) / sum(budget_gbp), 1) AS pct_over_budget
# MAGIC FROM `2_actual_vs_budget`
# MAGIC WHERE account_type = 'Expense' AND account_code <> '5000'
# MAGIC GROUP BY account_name ORDER BY overspend_gbp DESC;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Expense ratio by company = operating costs / gross written premium
# MAGIC SELECT company_name,
# MAGIC        round(100 * sum(CASE WHEN account_type = 'Expense' AND account_code <> '5000' THEN actual_gbp END)
# MAGIC                  / sum(CASE WHEN account_code = '4000' THEN actual_gbp END), 1) AS expense_ratio_pct
# MAGIC FROM `2_actual_vs_budget`
# MAGIC WHERE company_code <> 'C300'          -- the services company writes no premium
# MAGIC GROUP BY company_name;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Why were claims handling costs high in September? The journals say so.
# MAGIC SELECT description, count(*) AS journals, round(sum(amount_gbp)) AS amount_gbp
# MAGIC FROM `2_gl_journal`
# MAGIC WHERE account_code = '5100' AND period = '2026-09'
# MAGIC GROUP BY description ORDER BY amount_gbp DESC;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Stretch — a trusted answer
# MAGIC A SQL function is a definition Finance has approved. Add it to the agent and Genie will use it,
# MAGIC and label the answer as trusted, whenever someone asks for the variance report.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE FUNCTION variance_report(report_period STRING COMMENT 'Period as yyyy-MM, for example 2026-09')
# MAGIC RETURNS TABLE (account_name STRING, actual_gbp DOUBLE, budget_gbp DOUBLE, variance_gbp DOUBLE, variance_pct DOUBLE, flag STRING)
# MAGIC COMMENT 'Approved month-end variance report for operating costs: actual versus budget by account for one period, flagging overspends above 10 percent.'
# MAGIC RETURN
# MAGIC   SELECT account_name,
# MAGIC          round(sum(actual_gbp)), round(sum(budget_gbp)), round(sum(variance_gbp)),
# MAGIC          round(100 * sum(variance_gbp) / sum(budget_gbp), 1),
# MAGIC          CASE WHEN sum(variance_gbp) / sum(budget_gbp) > 0.10 THEN 'Investigate' ELSE 'OK' END
# MAGIC   FROM `2_actual_vs_budget`
# MAGIC   WHERE account_type = 'Expense' AND account_code <> '5000' AND period = report_period
# MAGIC   GROUP BY account_name;
# MAGIC
# MAGIC SELECT * FROM variance_report('2026-09') ORDER BY variance_gbp DESC;
