# Databricks notebook source
# MAGIC %md
# MAGIC # B2 — A dashboard in ten minutes
# MAGIC
# MAGIC **About 25 minutes · AI/BI Dashboards with Genie Code · needs only the setup**
# MAGIC
# MAGIC ## The business problem
# MAGIC The month-end pack has a page called *"Costs against budget"*. Today it is a spreadsheet
# MAGIC pasted into a slide. By the time anyone reads it, it is out of date and nobody can click on
# MAGIC anything. You are going to replace that page with a live dashboard — and then use it to find
# MAGIC out what actually happened this year.
# MAGIC
# MAGIC ## Your table
# MAGIC `2_actual_vs_budget` — actual and budget by month, company, cost centre and account.
# MAGIC `variance_gbp` is actual minus budget, so for costs **a positive variance is an overspend**.
# MAGIC
# MAGIC ## Steps
# MAGIC 1. In the left sidebar click **New → Dashboard**. Name it `Costs against budget`.
# MAGIC 2. Open Genie Code in the dashboard and describe the page you want. For example:
# MAGIC    > Build a costs-against-budget dashboard from the table 2_actual_vs_budget in my schema, for
# MAGIC    > Expense accounts only, excluding Claims Paid. I want: three headline numbers (actual, budget,
# MAGIC    > variance, in GBP), a monthly line chart of actual against budget, a bar chart of variance by
# MAGIC    > account, and a table of the ten biggest overspends by account and month. Add filters for
# MAGIC    > company and cost centre.
# MAGIC 3. Look at what it built. Change things by asking: *"make the variance chart horizontal and sort
# MAGIC    it largest first"*, *"show amounts in millions"*, *"colour overspends red"*.
# MAGIC 4. Click a bar in the variance chart. The other charts follow. That is the part a slide can't do.
# MAGIC 5. **Publish** (top right) and open the published view. That link is what you would send the CFO.
# MAGIC
# MAGIC ## Now use it — three things happened this year
# MAGIC Your dashboard should let you answer these in a few clicks. Find them:
# MAGIC
# MAGIC 1. One cost line has been **running over budget every month since July**. Which, and by roughly how much a month?
# MAGIC 2. One cost line was **well under budget from January to May**, then came back to plan. Which?
# MAGIC 3. One cost line had a **single very bad month**. Which line, which month?
# MAGIC
# MAGIC *(The answers, and why they happened, are in the solution. In exercise B4 you get the AI to write the commentary.)*
# MAGIC
# MAGIC ## If you have time
# MAGIC - Add a page for **revenue** (Gross Written Premium against budget).
# MAGIC - In the dashboard settings, switch on the **Genie** button so readers can ask follow-up questions.
# MAGIC - Set a **schedule** to email the dashboard as a PDF on working day 2.
# MAGIC
# MAGIC **Stuck?** Run `solutions/B_genie_code_and_agents/B2_solution` — it creates a finished dashboard
# MAGIC in your workspace that you can open, take apart and copy from.
