# Databricks notebook source
# MAGIC %md
# MAGIC # B3 — Your first Genie agent
# MAGIC
# MAGIC **About 30 minutes · Genie · needs only the setup**
# MAGIC
# MAGIC ## The business problem
# MAGIC Finance Business Partners spend the first week of every month answering the same kind of
# MAGIC question: *"How much did we spend on X?"*, *"Are we over budget on Y?"*, *"Why?"*. A Genie agent
# MAGIC answers those in plain English, straight from the governed tables, and shows its working.
# MAGIC
# MAGIC It will not be right out of the box. It doesn't know that revenue is stored as a negative
# MAGIC number, or what *you* mean by "overspend" or "expense ratio". **Teaching it those things is the
# MAGIC job** — and it is a Finance job, not an IT one.
# MAGIC
# MAGIC ## Part 1 — create it (5 min)
# MAGIC 1. In the left sidebar open **Genie** and create a new one (the button is **New**).
# MAGIC 2. Add these tables from your schema: `2_actual_vs_budget`, `2_gl_journal`, `2_budget`,
# MAGIC    `0_accounts`, `0_cost_centres`, `0_companies`.
# MAGIC 3. Name it `Finance month-end`.
# MAGIC
# MAGIC ## Part 2 — just ask (5 min)
# MAGIC Ask these and, each time, open the SQL it wrote (**Show code**). Is the answer right?
# MAGIC Run the cell at the bottom of this notebook to see the correct figures.
# MAGIC
# MAGIC - *What was our gross written premium from January to October?*
# MAGIC - *What were total expenses year to date?*
# MAGIC - *Which cost centre spent the most on staff?*
# MAGIC
# MAGIC ## Part 3 — break it (5 min)
# MAGIC Now ask the kind of thing a real stakeholder asks:
# MAGIC
# MAGIC - *What was our revenue in September?* — did you get a **negative** number? Why?
# MAGIC - *Where are we overspending?* — did it understand that a positive variance on a cost is bad?
# MAGIC - *What is our expense ratio?* — it has to guess what that means. Did it guess your definition?
# MAGIC - *Why were claims handling costs so high in September?*
# MAGIC
# MAGIC ## Part 4 — teach it (10 min)
# MAGIC Open the agent's **Instructions** and write down what a new joiner in Finance would need to be
# MAGIC told. Start with these, then add your own:
# MAGIC
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
# MAGIC Ask the Part 3 questions again. **That difference is the whole job.** Then:
# MAGIC - Add two or three **sample questions** so colleagues know what it is good at.
# MAGIC - When it gets an answer right, mark the answer as correct so it can be reused.
# MAGIC
# MAGIC ## Part 5 — put it in front of someone (5 min)
# MAGIC Click **Share**. Who would you give this to on Monday? They need access to the agent *and*
# MAGIC to the tables: Unity Catalog decides what data each person can see, so the same agent is safe to
# MAGIC share widely.
# MAGIC
# MAGIC ## If you have time — give it a trusted answer
# MAGIC Some questions must always be answered the same way. Run the last cell of the **solution**
# MAGIC notebook to create a SQL function `variance_report(period)`, then add it to the agent under
# MAGIC its SQL functions / trusted answers. Ask *"show me the variance report for 2026-09"*: the answer
# MAGIC is now marked as coming from a definition Finance approved.
# MAGIC
# MAGIC ## Worth discussing
# MAGIC Which three definitions in *your* team does everybody "just know" and nobody has written down?
# MAGIC
# MAGIC **Stuck?** `solutions/B_genie_code_and_agents/B3_solution`

# COMMAND ----------

# MAGIC %run ../00_setup/02_check

# COMMAND ----------

check("B3")
