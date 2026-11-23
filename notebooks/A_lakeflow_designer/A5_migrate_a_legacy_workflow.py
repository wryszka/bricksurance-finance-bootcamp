# Databricks notebook source
# MAGIC %md
# MAGIC # A5 — Migrate a legacy workflow
# MAGIC
# MAGIC **About 35 minutes · Lakeflow Designer with Genie Code · needs only the setup**
# MAGIC
# MAGIC ## The business problem
# MAGIC The month-end purchase order accrual runs today as a workflow in a desktop data-prep tool, on
# MAGIC one person's laptop, reading CSV files from a shared drive. You have been asked to move it.
# MAGIC The rule for a migration is simple: **the new process must produce the same number as the old
# MAGIC one**. Only then do you improve it.
# MAGIC
# MAGIC ## What you have
# MAGIC - The legacy workflow file: `legacy/desktop_etl_workflow/po_accruals_month_end.yxmd`
# MAGIC   (in this repo, next to the `notebooks` folder). It is XML; open it and have a look.
# MAGIC - A plain-words description of it: `legacy/desktop_etl_workflow/README.md`
# MAGIC - The same two extracts as governed tables: `1_purchase_orders` and `1_supplier_invoices`
# MAGIC
# MAGIC ## What you will build
# MAGIC A flow that writes **`my_accruals_summary`** with `company_code`, `cost_centre`, `po_count`
# MAGIC and `accrual_gbp` — matching the legacy output to the penny.
# MAGIC
# MAGIC ## Steps
# MAGIC 1. Open the `.yxmd` file. Read the eleven tool annotations (the `<Name>` lines). Can you follow
# MAGIC    the logic without the original tool?
# MAGIC 2. **New → Visual data prep**, name it `A5 po accruals`.
# MAGIC 3. In the **Genie Code prompt above the canvas**, ask it to recreate the workflow. Copy the whole
# MAGIC    XML and paste it into the prompt, along with:
# MAGIC    > This is a legacy workflow exported as XML. Recreate it as a visual data prep. Instead of the
# MAGIC    > two CSV files use the tables 1_purchase_orders and 1_supplier_invoices in my schema. Keep one
# MAGIC    > operator per legacy tool where you can and keep the tool names as operator names. Write the
# MAGIC    > result to a table called my_accruals_summary instead of the spreadsheet.
# MAGIC 4. Review it tool by tool against the XML. Things that often go wrong in a migration:
# MAGIC    - the legacy Join + Union pair means *"keep purchase orders with no invoice"* — that is a **Left join**
# MAGIC    - the date filters: on or before **31 October 2026**, on **both** inputs
# MAGIC    - cancelled purchase orders must be out
# MAGIC 5. **Run all**, then run the check. If it does not match, the check tells you which rule is the
# MAGIC    likely culprit. Fix it by telling Genie Code what is wrong.
# MAGIC
# MAGIC ## Now improve it (pick one)
# MAGIC - **No more typing the date by hand.** Open **Parameters** in the left pane, create `period_end`
# MAGIC   with the value `2026-10-31`, and use `:period_end` in both filters.
# MAGIC - **Explain it.** Ask Genie Code to write a short description of the flow for the process
# MAGIC   documentation. Compare it with `legacy/desktop_etl_workflow/README.md`.
# MAGIC - **Add a guardrail.** The legacy process had no checks. Add one: fail (or flag) if any purchase
# MAGIC   order has a negative accrual, meaning it was invoiced for more than it was ordered.
# MAGIC
# MAGIC ## Worth discussing with your neighbour
# MAGIC What in *your* estate looks like this file? How would you prove parity for it, and who signs it off?
# MAGIC
# MAGIC **Stuck?** `solutions/A_lakeflow_designer/A5_solution`

# COMMAND ----------

# MAGIC %run ../00_setup/02_check

# COMMAND ----------

check("A5")
