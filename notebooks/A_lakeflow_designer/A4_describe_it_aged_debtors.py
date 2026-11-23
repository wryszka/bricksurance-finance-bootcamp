# Databricks notebook source
# MAGIC %md
# MAGIC # A4 — Describe it, don't draw it: aged debtors
# MAGIC
# MAGIC **About 20 minutes · Lakeflow Designer with Genie Code · needs only the setup**
# MAGIC
# MAGIC ## The business problem
# MAGIC Credit Control wants the aged debtors report: how much do brokers owe us, and how old is the
# MAGIC debt? You know exactly what the report should say. So instead of placing operators one by
# MAGIC one, you are going to *describe* it and let Genie Code build the flow. Then you check its work,
# MAGIC because you are still the accountant.
# MAGIC
# MAGIC ## What you will build
# MAGIC A flow that writes **`my_aged_debtors`** with three columns:
# MAGIC `broker_name`, `age_bucket`, `outstanding_gbp`.
# MAGIC
# MAGIC | Your table | What is in it |
# MAGIC |---|---|
# MAGIC | `1_ar_invoices` | invoices to brokers: `amount_gbp`, `amount_paid_gbp`, `due_date` |
# MAGIC
# MAGIC The rules: outstanding = `amount_gbp` − `amount_paid_gbp` (ignore invoices that are fully paid).
# MAGIC Age = days between `due_date` and the period end, **31 October 2026**.
# MAGIC Buckets: `Not due`, `1-30`, `31-60`, `61-90`, `90+`.
# MAGIC
# MAGIC ## Steps
# MAGIC 1. **New → Visual data prep**, name it `A4 aged debtors`.
# MAGIC 2. In the **Genie Code prompt above the canvas**, describe what you want in your own words.
# MAGIC    Include the table name, the rules above and the output table name. Write it the way you
# MAGIC    would brief a new joiner.
# MAGIC 3. Watch it add and connect operators. **Click every operator** and read its configuration.
# MAGIC    Does the age calculation use 31 October 2026, or today's date?
# MAGIC 4. Something not right? Don't fix it by hand. Tell it: *"the oldest bucket should be called 90+"*
# MAGIC    or *"age must be measured to 2026-10-31, not today"*.
# MAGIC 5. **Run all**, then run the check below.
# MAGIC
# MAGIC ## Check
# MAGIC The check tells you total debt, how much is over 90 days, and who the worst offender is.
# MAGIC
# MAGIC ## Things worth noticing
# MAGIC - You described a business rule, and got a flow a colleague can open, read and change.
# MAGIC - A vague prompt gives a vague flow. What did you have to add on your second attempt?
# MAGIC - Ask Genie Code: *"explain this flow to an auditor in five bullet points"*.
# MAGIC
# MAGIC ## If you have time
# MAGIC Ask for a second output: one row per broker with a column per bucket (a pivot), sorted by the
# MAGIC 90+ amount. That is the layout Credit Control actually wants to see.
# MAGIC
# MAGIC **Stuck?** `solutions/A_lakeflow_designer/A4_solution` has a prompt that works.

# COMMAND ----------

# MAGIC %run ../00_setup/02_check

# COMMAND ----------

check("A4")
