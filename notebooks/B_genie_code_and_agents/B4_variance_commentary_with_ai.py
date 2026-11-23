# Databricks notebook source
# MAGIC %md
# MAGIC # B4 — Let AI write the first draft of the variance commentary
# MAGIC
# MAGIC **About 20 minutes · AI Functions in SQL, with Genie Code · needs only the setup**
# MAGIC
# MAGIC ## The business problem
# MAGIC The numbers are done on working day 3. Then someone spends a day writing sentences like
# MAGIC *"IT costs were £440k adverse to budget, driven by…"* for every line in the pack. The reasons
# MAGIC are already in the ledger, in the journal descriptions. An AI function can read them and write
# MAGIC the first draft. You stay the editor.
# MAGIC
# MAGIC ## What you will build
# MAGIC A table **`my_variance_commentary`**: the five biggest cost variances for **September 2026**,
# MAGIC each with a one- or two-sentence explanation in a column called **`commentary`**.
# MAGIC
# MAGIC ## How AI functions work
# MAGIC They are ordinary SQL functions that call a language model for each row:
# MAGIC
# MAGIC ```sql
# MAGIC SELECT ai_gen('Explain in one sentence why a storm increases claims handling costs.');
# MAGIC ```
# MAGIC
# MAGIC Run the cell below to see one work. No model to deploy, no keys, no Python.

# COMMAND ----------

# MAGIC %run ../00_setup/02_check

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT ai_gen('In one sentence, explain to a finance director what an accrual is.') AS answer;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Steps
# MAGIC Open **Genie Code** and build this in stages. Suggested prompts:
# MAGIC
# MAGIC **1. The variances**
# MAGIC > From 2_actual_vs_budget, give me the five biggest absolute variances for Expense accounts in
# MAGIC > period 2026-09, by account, with actual, budget, variance and variance percent.
# MAGIC
# MAGIC **2. The evidence**
# MAGIC > For each of those accounts, add a column listing the distinct journal descriptions from
# MAGIC > 2_gl_journal for that account in 2026-09, joined into one text string.
# MAGIC
# MAGIC **3. The commentary**
# MAGIC > Add a commentary column using ai_gen. The prompt should give the account name, actual, budget,
# MAGIC > variance and the journal descriptions, and ask for at most two sentences in plain English for a
# MAGIC > finance director, saying whether the variance is adverse or favourable and the likely cause
# MAGIC > based only on the descriptions. Save the result as a table called my_variance_commentary.
# MAGIC
# MAGIC Then run the check below and **read the commentary critically**:
# MAGIC - Did it get adverse and favourable the right way round?
# MAGIC - Did it invent a reason that isn't in the descriptions?
# MAGIC - Would you sign it? What would you change in the prompt?
# MAGIC
# MAGIC ## If you have time
# MAGIC - Change the tone: *"write it as a bullet for a board pack"*, or ask for it in French.
# MAGIC - Use `ai_classify(description, ARRAY('one-off', 'recurring'))` to tag each journal description.
# MAGIC - Ask Genie Code to add this as a last step in the B1 pipeline, so the commentary is drafted
# MAGIC   every month before anyone opens a laptop.
# MAGIC
# MAGIC ## Worth discussing
# MAGIC Where does the human stay in this process? What would your auditors want to see?
# MAGIC
# MAGIC **Stuck?** `solutions/B_genie_code_and_agents/B4_solution`. If `ai_gen` is not available in your
# MAGIC notebook, paste the same SQL into the **SQL editor** and run it on the SQL warehouse.

# COMMAND ----------

check("B4")
