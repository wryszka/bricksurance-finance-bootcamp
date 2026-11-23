# Finding your way around

| You want to… | Go to |
|---|---|
| see your tables | **Catalog** in the left sidebar → your catalog → `finance_<your name>` |
| build a visual flow | **New → Visual data prep** |
| ask the AI to build something | the **Genie Code** panel in a notebook, dashboard or flow |
| ask questions of your data | **Genie** in the left sidebar |
| see scheduled work | **Jobs & Pipelines** |
| see or create apps | **Compute → Apps** |

# If something goes wrong

| Problem | Fix |
|---|---|
| "Table not found" in a check | you haven't run your flow yet (**Run all**), or the table name differs from the exercise |
| A flow preview looks short | previews use a sample of rows; **Run all** uses everything |
| I broke my data | rerun `00_setup/01_data_generator` — it rebuilds everything in two minutes |
| The app says it can't read the table | run the grant cell in the C1 / C2 notebook with your app's name |
| Something isn't where the steps say | the product moves fast and labels change; ask a facilitator, or ask Genie Code *"where do I find…"* |

# Take it home

This repository is public and runs on the free edition of Databricks. Sign up, add the Git
folder, run the generator, and carry on with the exercises you didn't get to.

*About this bootcamp: all data is synthetic and Bricksurance is a fictional insurer. The legacy
workflow and spreadsheet macro were written for these exercises and are not any real
organisation's process.*
