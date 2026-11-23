# Databricks notebook source
# MAGIC %md
# MAGIC # B1 — Build a pipeline by asking
# MAGIC
# MAGIC **About 35 minutes · Genie Code in a notebook · needs only the setup**
# MAGIC
# MAGIC ## The business problem
# MAGIC Every month the finance system drops a general ledger extract as a CSV file. Somebody opens
# MAGIC it, fixes the dates, strips the brackets off the negative numbers, deletes the test journals,
# MAGIC and builds a trial balance. Ten files are waiting for you. You are going to build the process
# MAGIC that does this properly, by telling Genie Code what you need.
# MAGIC
# MAGIC The point of this exercise is not the code. It is learning how to **brief an AI like a
# MAGIC colleague, and check its work like an accountant**.
# MAGIC
# MAGIC ## What you will build
# MAGIC Three tables, ending in **`my_trial_balance`** (`period`, `company_code`, `account_code`, `net_gbp`).
# MAGIC
# MAGIC | Layer | Table | What it is |
# MAGIC |---|---|---|
# MAGIC | Bronze | `my_bronze_gl` | the files exactly as they arrived, plus which file each row came from |
# MAGIC | Silver | `my_silver_gl` | cleaned: real dates, real numbers, no duplicates, no test journals |
# MAGIC | Gold | `my_trial_balance` | net movement per period, company and account |
# MAGIC
# MAGIC Run the next two cells first. They print where your files are.

# COMMAND ----------

# MAGIC %run ../00_setup/02_check

# COMMAND ----------

files = dbutils.fs.ls(f"{RAW_VOLUME}/gl/")
print(f"Your files: {RAW_VOLUME}/gl/   ({len(files)} files)\n")
print(dbutils.fs.head(files[0].path, 600))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Steps
# MAGIC Open **Genie Code** (the side panel in this notebook) and work through these prompts one at a
# MAGIC time. Read what it writes before you run it. Swap in your own path and schema where needed —
# MAGIC or just say *"in this notebook's schema"*; it can see the cells above.
# MAGIC
# MAGIC **1. Look before you load (5 min)**
# MAGIC > Look at the CSV files in my raw/gl volume folder. Tell me what columns they have and anything
# MAGIC > that would cause trouble if I loaded them into a table as they are. Don't write any tables yet.
# MAGIC
# MAGIC Did it spot the UK dates, the amounts in brackets, the duplicates and the test journals? If it
# MAGIC missed one, tell it. You know this data better than it does.
# MAGIC
# MAGIC **2. Bronze (5 min)**
# MAGIC > Load all the files into a table called my_bronze_gl. Keep every column as text, exactly as it
# MAGIC > arrived, and add the source file name and a load timestamp.
# MAGIC
# MAGIC **3. Silver (10 min)**
# MAGIC > Create my_silver_gl from my_bronze_gl: remove exact duplicate lines, remove test journals
# MAGIC > (posted_by is TESTUSER), convert posting_date from day/month/year to a date, and convert amount
# MAGIC > to a number called amount_gbp where brackets mean negative, for example (1,234.50) is -1234.50.
# MAGIC > Add a period column in yyyy-MM format.
# MAGIC
# MAGIC **4. Prove it (5 min)** — the step most people skip
# MAGIC > Check my_silver_gl: does every journal_id sum to zero? How many rows did we drop and why?
# MAGIC
# MAGIC **5. Gold (5 min)**
# MAGIC > Create my_trial_balance: net amount_gbp as net_gbp by period, company_code and account_code,
# MAGIC > with the account name from 0_accounts.
# MAGIC
# MAGIC Then run the check cell at the bottom.
# MAGIC
# MAGIC ## If you have time
# MAGIC - **Schedule it.** Use **Schedule** (top right of the notebook) so it runs on the 1st of each month.
# MAGIC - **Ask for the grown-up version.** *"Turn this into a Lakeflow declarative pipeline with data
# MAGIC   quality expectations for the rules we just wrote."* Open what it creates and look at the
# MAGIC   expectations: your cleaning rules have become monitored controls.
# MAGIC - **Ask it to document itself.** *"Add a short markdown explanation above each step, written for
# MAGIC   someone in Finance, not an engineer."*
# MAGIC
# MAGIC **Stuck?** `solutions/B_genie_code_and_agents/B1_solution`

# COMMAND ----------

check("B1")
