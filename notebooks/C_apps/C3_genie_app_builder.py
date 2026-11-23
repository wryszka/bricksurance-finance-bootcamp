# Databricks notebook source
# MAGIC %md
# MAGIC # C3 — The same app, with Genie App Builder
# MAGIC
# MAGIC **About 20 minutes · Genie App Builder · needs it switched on in your workspace**
# MAGIC
# MAGIC > **Check first.** Genie App Builder is in Beta. It needs a workspace admin to have switched on
# MAGIC > *Governed agentic app-building* and given you an **App Space**. Open **Apps** in the left
# MAGIC > sidebar: if you see a **Build** tab, you have it. If not, do C1 or C2 instead — nothing else in
# MAGIC > this bootcamp depends on this exercise.
# MAGIC
# MAGIC ## The idea
# MAGIC In C1 you briefed Genie Code, got code, and deployed it yourself. Genie App Builder goes one
# MAGIC step further for business users: you describe the app, it builds it and shows you a **live
# MAGIC preview**, you refine it by talking to it, and you deploy with one click. No folder, no
# MAGIC `app.yaml`, no deploy step.
# MAGIC
# MAGIC ## Steps
# MAGIC 1. **Apps → Build**. Choose your App Space. Give the app a name, e.g. `journal approvals`.
# MAGIC 2. Describe the app. Use the same brief as C1, in your own words:
# MAGIC    > An app for approving month-end journal requests. It reads the table 3_journal_requests in my
# MAGIC    > schema [catalog.schema]. Show pending requests with their amount, reason and who asked. Let me
# MAGIC    > approve or reject one with a comment, and save the decision to the table with my name. Flag
# MAGIC    > anything of £50,000 or more as needing the Financial Controller.
# MAGIC 3. If asked, click **Sign in** to open the preview.
# MAGIC 4. Refine it by asking: *"put the big numbers at the top"*, *"add a filter for company"*,
# MAGIC    *"make rejecting require a comment"*.
# MAGIC 5. Deploy it, then **Share** it with your neighbour (`CAN USE`).
# MAGIC
# MAGIC ## Compare the two routes
# MAGIC | | C1: Genie Code + custom app | C3: Genie App Builder |
# MAGIC |---|---|---|
# MAGIC | Who it suits | someone comfortable reading code | anyone who can describe what they want |
# MAGIC | What you get | files you own, in a folder or in Git | a managed app inside an App Space |
# MAGIC | Control | everything | what the App Space allows |
# MAGIC | Always-on / scaled out | possible | no: it scales to zero when idle |
# MAGIC | Data it can reach | whatever you grant the app | only what the App Space shares |
# MAGIC
# MAGIC ## Worth discussing
# MAGIC Which of these would your team be allowed to use tomorrow? Who would own the App Space and
# MAGIC decide what data goes in it?

# COMMAND ----------

# MAGIC %run ../00_setup/02_check

# COMMAND ----------

print(f"Your schema: {FQ}")
