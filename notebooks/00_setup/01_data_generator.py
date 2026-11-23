# Databricks notebook source
# MAGIC %md
# MAGIC # 01 — Data generator: the Bricksurance finance book
# MAGIC
# MAGIC Run this **once**. It builds everything every exercise needs, so you can do the
# MAGIC exercises in any order and skip the ones that don't interest you.
# MAGIC
# MAGIC It is month-end close for **October 2026** at Bricksurance (a fictional UK insurer).
# MAGIC
# MAGIC | Prefix | What it is | Used by |
# MAGIC |---|---|---|
# MAGIC | `0_` | reference data: companies, chart of accounts, cost centres | everything |
# MAGIC | `1_` | operational finance extracts: supplier payments, bank, debtors, purchase orders | Track A — Lakeflow Designer |
# MAGIC | `2_` | the general ledger: journal lines, budget, trial balance | Track B — Genie Code & Agents |
# MAGIC | `3_` | journal requests waiting for approval | Track C — Apps |
# MAGIC | volume `raw/gl/` | ten messy monthly GL extract files (CSV) | exercise B1 |
# MAGIC
# MAGIC Seeded and idempotent: rerun it any time to reset your data. No libraries to install.
# MAGIC Takes about two minutes.

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

import os
import numpy as np
import pandas as pd
from pyspark.sql import functions as F

rng = np.random.default_rng(42)
PERIODS = [f"2026-{m:02d}" for m in range(1, 11)]          # Jan-Oct actuals
ALL_PERIODS = [f"2026-{m:02d}" for m in range(1, 13)]      # full-year budget


def save(pdf, name, comment, dates=()):
    """Write a pandas frame as a managed table with proper DATE columns and a comment."""
    sdf = spark.createDataFrame(pdf)
    for c in dates:
        sdf = sdf.withColumn(c, F.to_date(c))
    (sdf.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{FQ}.`{name}`"))
    spark.sql(f"COMMENT ON TABLE {FQ}.`{name}` IS '{comment}'")
    print(f"  {name:28s} {len(pdf):>7,} rows")


def random_dates(start, end, n):
    days = (pd.Timestamp(end) - pd.Timestamp(start)).days
    return (pd.Timestamp(start) + pd.to_timedelta(rng.integers(0, days + 1, n), unit="D")).strftime("%Y-%m-%d")

# COMMAND ----------

# MAGIC %md ## 0 — Reference data

# COMMAND ----------

companies = pd.DataFrame(
    [("C100", "Bricksurance Commercial Ltd", 1.00),
     ("C200", "Bricksurance Personal Lines Ltd", 0.70),
     ("C300", "Bricksurance Services Ltd", 0.15)],
    columns=["company_code", "company_name", "scale"])

accounts = pd.DataFrame(
    [("1000", "Cash at Bank", "Asset", "Balance Sheet"),
     ("1100", "Premium Debtors", "Asset", "Balance Sheet"),
     ("2000", "Trade Creditors", "Liability", "Balance Sheet"),
     ("2100", "Accruals", "Liability", "Balance Sheet"),
     ("4000", "Gross Written Premium", "Revenue", "Profit and Loss"),
     ("4100", "Reinsurance Premium Ceded", "Revenue", "Profit and Loss"),
     ("4200", "Investment Income", "Revenue", "Profit and Loss"),
     ("5000", "Claims Paid", "Expense", "Profit and Loss"),
     ("5100", "Claims Handling Costs", "Expense", "Profit and Loss"),
     ("6000", "Staff Costs", "Expense", "Profit and Loss"),
     ("6100", "IT and Software", "Expense", "Profit and Loss"),
     ("6200", "Professional Fees", "Expense", "Profit and Loss"),
     ("6300", "Marketing", "Expense", "Profit and Loss"),
     ("6400", "Facilities", "Expense", "Profit and Loss"),
     ("6500", "Travel and Entertainment", "Expense", "Profit and Loss")],
    columns=["account_code", "account_name", "account_type", "statement"])

cost_centres = pd.DataFrame(
    [("CC100", "Claims Operations"), ("CC200", "Underwriting"), ("CC300", "Finance"),
     ("CC400", "IT"), ("CC500", "Marketing"), ("CC600", "HR and Facilities")],
    columns=["cost_centre", "cost_centre_name"])

print("Reference data")
save(companies.drop(columns="scale"), "0_companies", "Legal entities of Bricksurance (fictional).")
save(accounts, "0_accounts",
     "Chart of accounts. account_type is Asset, Liability, Revenue or Expense. "
     "statement is Balance Sheet or Profit and Loss.")
save(cost_centres, "0_cost_centres", "Cost centres (departments) that own expenses.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1 — Operational finance extracts (Track A)
# MAGIC ### Supplier payments + the category lookup

# COMMAND ----------

# (category, cost centre, typical payment size, suppliers)
supplier_groups = [
    ("Claims Repair Network", "CC100", 4200, ["Alder Motor Repairs", "Birchfield Bodyshop", "Calder Glass", "Dovecote Recovery",
                                              "Elmstead Accident Repair", "Fenbrook Garage Group", "Greyfriars Coachworks",
                                              "Harrowgate Vehicle Hire", "Ivybridge Plumbing & Drying", "Juniper Building Repairs"]),
    ("IT and Software", "CC400", 9500, ["Kestrel Cloud Hosting", "Larkspur Software", "Marlow Data Services", "Northlight Telecoms",
                                        "Orchard Cyber Security", "Pennine IT Contractors", "Quayside Licensing", "Rowan Devices"]),
    ("Professional Fees", "CC300", 12500, ["Saxon Legal LLP", "Thornbury Audit", "Underhill Actuarial", "Verity Tax Advisers",
                                           "Westbrook Consulting", "Yarrow Recruitment", "Zennor Surveyors"]),
    ("Facilities", "CC600", 3100, ["Abbey Cleaning", "Beacon Energy", "Castlegate Security", "Dunmore Catering",
                                   "Eastfield Office Supplies", "Foxglove Property Mgmt"]),
    ("Marketing", "CC500", 7800, ["Gable Media", "Hawthorn Creative", "Inkwell Print", "Jetstream Digital", "Kingfisher Events"]),
    ("Travel", "CC200", 650, ["Lowland Rail", "Meridian Hotels", "Nimbus Travel Desk", "Oakhill Car Hire"]),
]
suppliers = pd.DataFrame(
    [(s, cat, cc, size, i < 2) for cat, cc, size, names in supplier_groups for i, s in enumerate(names)],
    columns=["supplier_name", "category", "cost_centre", "_size", "_top"])
suppliers["is_preferred"] = rng.random(len(suppliers)) < 0.6

# Three recently onboarded suppliers have NOT been added to the category lookup yet.
UNCATEGORISED = ["Juniper Building Repairs", "Rowan Devices", "Kingfisher Events"]
lookup = suppliers[~suppliers.supplier_name.isin(UNCATEGORISED)][["supplier_name", "category", "is_preferred"]]

N_PAY = 4000
w = np.where(suppliers._top, 3.0, 1.0)
idx = rng.choice(len(suppliers), N_PAY, p=w / w.sum())
pay = suppliers.iloc[idx].reset_index(drop=True)
payments = pd.DataFrame({
    "payment_id": [f"PAY-{i:06d}" for i in range(1, N_PAY + 1)],
    "payment_date": random_dates("2026-01-02", PERIOD_END, N_PAY),
    "company_code": rng.choice(["C100", "C200", "C300"], N_PAY, p=[0.55, 0.35, 0.10]),
    "supplier_name": pay.supplier_name,
    "cost_centre": pay.cost_centre,
    "amount_gbp": np.round(pay._size.values * rng.lognormal(0, 0.6, N_PAY), 2),
    "payment_method": rng.choice(["BACS", "CHAPS", "Card"], N_PAY, p=[0.80, 0.12, 0.08]),
    "status": rng.choice(["Paid", "Reversed"], N_PAY, p=[0.97, 0.03]),
}).sort_values("payment_date").reset_index(drop=True)

print("Supplier payments")
save(payments, "1_supplier_payments",
     "Payments made to suppliers, January to October 2026. status is Paid or Reversed; "
     "reversed payments must be excluded from spend. No category on this table - see 1_supplier_categories.",
     dates=["payment_date"])
save(lookup, "1_supplier_categories",
     "Lookup: supplier_name to spend category, and whether the supplier is on the preferred list. "
     "Newly onboarded suppliers may be missing.")

# COMMAND ----------

# MAGIC %md ### Bank reconciliation — ledger cash vs bank statement (October)

# COMMAND ----------

bank_accounts = [f"BA-{i:02d}" for i in range(1, 13)]
gl_rows, bank_rows, n = [], [], 0
for ba in bank_accounts:
    for _ in range(int(rng.integers(180, 260))):
        n += 1
        receipt = rng.random() < 0.45
        amount = round(float(rng.lognormal(8.2 if receipt else 7.6, 0.9)) * (1 if receipt else -1), 2)
        day = int(rng.integers(1, 29))
        ref = f"{'RCP' if receipt else 'PMT'}-{n:06d}"
        gl_rows.append((f"GL-{n:06d}", ba, f"2026-10-{day:02d}", ref,
                        "Broker receipt" if receipt else "Supplier payment run", amount))
        bank_rows.append((f"BS-{n:06d}", ba, f"2026-10-{min(day + int(rng.integers(0, 3)), 31):02d}", ref, amount))

# Planted breaks - only three accounts fail to reconcile.
# BA-03: six payments posted in the ledger on the last days of October, not yet on the bank (timing).
for k in range(6):
    n += 1
    gl_rows.append((f"GL-{n:06d}", "BA-03", f"2026-10-{29 + k % 3:02d}", f"PMT-{n:06d}",
                    "Supplier payment run", -round(float(rng.lognormal(7.9, 0.5)), 2)))
# BA-07: four bank charges on the statement that nobody has posted to the ledger.
for k in range(4):
    n += 1
    bank_rows.append((f"BS-{n:06d}", "BA-07", f"2026-10-{7 * (k + 1):02d}", f"CHG-{n:06d}", -round(35 + 20 * k + 0.5, 2)))
# BA-11: two keying errors - same reference, digits transposed in the ledger.
for ref_i, (good, bad) in zip([40, 95], [(-1540.00, -1450.00), (8630.25, 8360.25)]):
    j = [i for i, r in enumerate(gl_rows) if r[1] == "BA-11"][ref_i]
    g = gl_rows[j]
    gl_rows[j] = (g[0], g[1], g[2], g[3], g[4], bad)
    b = next(i for i, r in enumerate(bank_rows) if r[3] == g[3])
    bank_rows[b] = bank_rows[b][:4] + (good,)

gl_cash = pd.DataFrame(gl_rows, columns=["entry_id", "bank_account", "posting_date", "reference", "description", "amount_gbp"])
bank_stmt = pd.DataFrame(bank_rows, columns=["statement_line_id", "bank_account", "value_date", "reference", "amount_gbp"])

print("Bank reconciliation")
save(gl_cash, "1_gl_cash",
     "Cash entries in the general ledger for October 2026, one row per receipt or payment. "
     "Receipts are positive, payments negative. reference matches the bank statement reference.",
     dates=["posting_date"])
save(bank_stmt, "1_bank_statement",
     "Bank statement lines for October 2026 for the same 12 bank accounts. "
     "Receipts are positive, payments negative.", dates=["value_date"])

# COMMAND ----------

# MAGIC %md ### Debtors — broker invoices and what has been paid

# COMMAND ----------

brokers = [f"{a} {b}" for a, b in zip(
    ["Ashdown", "Bramley", "Carrick", "Denholm", "Eastgate", "Farleigh", "Glenmore", "Hartwell", "Ingleby", "Jesmond",
     "Kelso", "Lynton", "Marden", "Netherby", "Oxley", "Penrose", "Quarry", "Ravens", "Selwyn", "Tavistock",
     "Upton", "Vale", "Wexcombe", "Yeoman", "Zetland"],
    ["Brokers", "Risk Partners", "Insurance Services", "Broking Group", "Risk Solutions"] * 5)]
slow_payers = set(brokers[::6])                      # a handful of brokers pay late
N_INV = 1500
inv_broker = rng.choice(brokers, N_INV)
inv_date = pd.to_datetime(random_dates("2026-03-01", "2026-10-25", N_INV))
due = inv_date + pd.Timedelta(days=30)
age = (pd.Timestamp(PERIOD_END) - due).days
amount = np.round(rng.lognormal(9.3, 0.8, N_INV), 2)
p_paid = np.clip(0.25 + age / 90, 0.05, 0.97) - np.where(pd.Series(inv_broker).isin(slow_payers), 0.35, 0.0)
u = rng.random(N_INV)
paid = np.where(u < p_paid, amount, np.where(u < p_paid + 0.08, np.round(amount * 0.5, 2), 0.0))
invoices = pd.DataFrame({
    "invoice_id": [f"INV-{i:06d}" for i in range(1, N_INV + 1)],
    "broker_name": inv_broker,
    "company_code": rng.choice(["C100", "C200"], N_INV, p=[0.6, 0.4]),
    "invoice_date": inv_date.strftime("%Y-%m-%d"),
    "due_date": due.strftime("%Y-%m-%d"),
    "amount_gbp": amount,
    "amount_paid_gbp": paid,
})

print("Debtors")
save(invoices, "1_ar_invoices",
     "Premium invoices raised to brokers. Outstanding = amount_gbp minus amount_paid_gbp. "
     "An invoice is overdue when due_date is before the period end (2026-10-31).",
     dates=["invoice_date", "due_date"])

# COMMAND ----------

# MAGIC %md ### Purchase orders and supplier invoices — the month-end accrual

# COMMAND ----------

N_PO = 1200
po_sup = suppliers.iloc[rng.choice(len(suppliers), N_PO)].reset_index(drop=True)
po_date = pd.to_datetime(random_dates("2026-06-01", "2026-10-28", N_PO))
received = rng.random(N_PO) < 0.8
grn = po_date + pd.to_timedelta(rng.integers(2, 25, N_PO), unit="D")      # some land in November
pos = pd.DataFrame({
    "po_id": [f"PO-{i:05d}" for i in range(1, N_PO + 1)],
    "supplier_name": po_sup.supplier_name,
    "company_code": rng.choice(["C100", "C200", "C300"], N_PO, p=[0.55, 0.35, 0.10]),
    "cost_centre": po_sup.cost_centre,
    "po_date": po_date.strftime("%Y-%m-%d"),
    "goods_received_date": np.where(received, grn.strftime("%Y-%m-%d"), None),
    "po_amount_gbp": np.round(po_sup._size.values * rng.lognormal(0.4, 0.7, N_PO), 2),
    "po_status": rng.choice(["Open", "Closed", "Cancelled"], N_PO, p=[0.70, 0.25, 0.05]),
})
inv_rows, k = [], 0
for po in pos[received].itertuples():
    u = rng.random()
    shares = [1.0] if u < 0.45 else [0.6] if u < 0.65 else [0.5, 0.5] if u < 0.75 else []
    for s in shares:
        k += 1
        d = pd.Timestamp(po.goods_received_date) + pd.Timedelta(days=int(rng.integers(1, 30)))
        inv_rows.append((f"SI-{k:05d}", po.po_id, d.strftime("%Y-%m-%d"), round(po.po_amount_gbp * s, 2)))
sup_inv = pd.DataFrame(inv_rows, columns=["supplier_invoice_id", "po_id", "invoice_date", "invoice_amount_gbp"])

print("Purchase orders")
save(pos, "1_purchase_orders",
     "Purchase orders raised June to October 2026. goods_received_date is empty when nothing has been "
     "delivered yet. po_status is Open, Closed or Cancelled.", dates=["po_date", "goods_received_date"])
save(sup_inv, "1_supplier_invoices",
     "Invoices received from suppliers against purchase orders. A purchase order can have zero, one or "
     "several invoices. Some are dated after the period end.", dates=["invoice_date"])

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2 — The general ledger (Track B)
# MAGIC
# MAGIC Journals are double-entry: **debits are positive, credits are negative**, and every
# MAGIC journal sums to zero. That means revenue sits in the ledger as a *negative* number —
# MAGIC remember that when you get to Genie.
# MAGIC
# MAGIC Three real things happen in the numbers (you'll find them later):
# MAGIC a cloud migration, a postponed marketing campaign, and a storm.

# COMMAND ----------

# (account, cost centre, annual budget for C100 in GBP, balancing account, services company has it?)
pnl_cells = [
    ("4000", "CC200", 240_000_000, "1100", False), ("4100", "CC200", 36_000_000, "2000", False),
    ("4200", "CC300", 9_000_000, "1000", False),
    ("5000", "CC100", 150_000_000, "1000", False), ("5100", "CC100", 12_000_000, "2000", False),
    ("6000", "CC100", 9_000_000, "1000", True), ("6000", "CC200", 7_000_000, "1000", True),
    ("6000", "CC300", 4_000_000, "1000", True), ("6000", "CC400", 5_000_000, "1000", True),
    ("6000", "CC500", 2_500_000, "1000", True), ("6000", "CC600", 2_500_000, "1000", True),
    ("6100", "CC400", 9_000_000, "2000", True), ("6200", "CC300", 2_600_000, "2000", True),
    ("6200", "CC200", 1_400_000, "2000", True), ("6300", "CC500", 6_000_000, "2000", True),
    ("6400", "CC600", 3_500_000, "2000", True), ("6500", "CC200", 600_000, "2000", True),
    ("6500", "CC500", 350_000, "2000", True), ("6500", "CC300", 250_000, "2000", True),
]
CREDIT_NATURE = {"4000", "4200"}          # income: credit the P&L account
default_text = {
    "4000": "Premium bordereau", "4100": "Reinsurance treaty instalment", "4200": "Bond coupon / interest",
    "5000": "Claims payment run", "5100": "Loss adjuster and handling fees", "6000": "Payroll",
    "6100": "Software licences and hosting", "6200": "Advisory and audit fees", "6300": "Advertising and campaigns",
    "6400": "Rent, rates and utilities", "6500": "Staff travel",
}


def story(account, month):
    """The three planted events: returns (multiplier, description override)."""
    if account == "6100" and month >= 7:
        return 1.35, "Cloud migration - dual running costs"
    if account == "6300" and month <= 5:
        return 0.60, "Spring campaign postponed - reduced spend"
    if account == "5100" and month == 9:
        return 1.60, "Storm Brigid surge - temporary claims handlers"
    if account == "5000" and month in (9, 10):
        return 1.25, "Storm Brigid claims payments"
    return 1.0, None


budget_rows, lines, jn = [], [], 0
for co in companies.itertuples():
    for account, cc, annual, balancing, in_services in pnl_cells:
        if co.company_code == "C300" and not in_services:
            continue
        monthly = annual * co.scale / 12
        for p in ALL_PERIODS:
            budget_rows.append((p, co.company_code, cc, account, round(monthly, 2)))
        for p in PERIODS:
            month = int(p[-2:])
            mult, text = story(account, month)
            total = monthly * mult * rng.normal(1.0, 0.03)
            for share in rng.dirichlet(np.ones(int(rng.integers(8, 26)))):
                jn += 1
                amt = round(total * share, 2)
                signed = -amt if account in CREDIT_NATURE else amt
                jid, day = f"JNL-{jn:07d}", int(rng.integers(1, 29))
                desc = text or default_text[account]
                lines.append((jid, 1, f"{p}-{day:02d}", p, co.company_code, account, cc, signed, desc))
                lines.append((jid, 2, f"{p}-{day:02d}", p, co.company_code, balancing, None, -signed, desc))

gl = pd.DataFrame(lines, columns=["journal_id", "line_no", "posting_date", "period", "company_code",
                                  "account_code", "cost_centre", "amount_gbp", "description"])
gl["posted_by"] = rng.choice(["a.okafor", "j.patel", "m.hughes", "s.lindqvist", "batch.interface"], len(gl),
                             p=[0.15, 0.15, 0.15, 0.15, 0.40])
budget = pd.DataFrame(budget_rows, columns=["period", "company_code", "cost_centre", "account_code", "budget_gbp"])

print("General ledger")
save(gl, "2_gl_journal",
     "Clean general ledger journal lines, January to October 2026. Double entry: debits are positive, "
     "credits are negative, every journal_id sums to zero. Revenue accounts therefore hold negative amounts. "
     "cost_centre is empty on balance sheet lines.", dates=["posting_date"])
save(budget, "2_budget",
     "Full-year 2026 budget by period, company, cost centre and account. Always positive: revenue budget "
     "is income expected, expense budget is cost expected.")

# COMMAND ----------

# MAGIC %md ### Reporting tables on top of the ledger

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE TABLE {FQ}.`2_trial_balance`
COMMENT 'Trial balance by period, company and account. net_gbp = debits minus credits and sums to zero per company and period.'
AS SELECT g.period, g.company_code, g.account_code, a.account_name, a.account_type, a.statement,
          round(sum(CASE WHEN g.amount_gbp > 0 THEN g.amount_gbp ELSE 0 END), 2)  AS debit_gbp,
          round(sum(CASE WHEN g.amount_gbp < 0 THEN -g.amount_gbp ELSE 0 END), 2) AS credit_gbp,
          round(sum(g.amount_gbp), 2)                                             AS net_gbp
FROM {FQ}.`2_gl_journal` g JOIN {FQ}.`0_accounts` a USING (account_code)
GROUP BY ALL
""")

spark.sql(f"""
CREATE OR REPLACE TABLE {FQ}.`2_actual_vs_budget`
COMMENT 'Profit and loss actual versus budget by period, company, cost centre and account, January to October 2026. actual_gbp and budget_gbp are both shown as positive numbers (income earned, cost incurred). variance_gbp = actual minus budget: for Expense accounts positive is an overspend (adverse), for Revenue accounts positive is favourable.'
AS WITH actual AS (
  SELECT g.period, g.company_code, g.cost_centre, g.account_code,
         sum(CASE WHEN g.account_code IN ('4000', '4200') THEN -g.amount_gbp ELSE g.amount_gbp END) AS actual_gbp
  FROM {FQ}.`2_gl_journal` g JOIN {FQ}.`0_accounts` a USING (account_code)
  WHERE a.statement = 'Profit and Loss'
  GROUP BY ALL)
SELECT b.period, b.company_code, c.company_name, b.cost_centre, cc.cost_centre_name,
       b.account_code, a.account_name, a.account_type,
       round(coalesce(x.actual_gbp, 0), 2)                AS actual_gbp,
       round(b.budget_gbp, 2)                             AS budget_gbp,
       round(coalesce(x.actual_gbp, 0) - b.budget_gbp, 2) AS variance_gbp
FROM {FQ}.`2_budget` b
JOIN {FQ}.`0_accounts` a USING (account_code)
JOIN {FQ}.`0_companies` c USING (company_code)
JOIN {FQ}.`0_cost_centres` cc USING (cost_centre)
LEFT JOIN actual x USING (period, company_code, cost_centre, account_code)
WHERE b.period <= '2026-10'
""")
for t in ("2_trial_balance", "2_actual_vs_budget"):
    print(f"  {t:28s} {spark.table(f'{FQ}.`{t}`').count():>7,} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ### The raw monthly extract files (for exercise B1)
# MAGIC
# MAGIC The same ledger, as the source system really sends it — one CSV per month, with the
# MAGIC usual problems: UK dates, amounts as text with brackets for negatives, a few
# MAGIC duplicated rows, and test journals that should never reach a report.

# COMMAND ----------

def as_text(v):
    return f"({abs(v):,.2f})" if v < 0 else f"{v:,.2f}"


gl_dir = f"{RAW_VOLUME}/gl"
os.makedirs(gl_dir, exist_ok=True)
for f in os.listdir(gl_dir):
    os.remove(f"{gl_dir}/{f}")

n_dupes = n_test = 0
for p in PERIODS:
    m = gl[gl.period == p]
    raw = pd.DataFrame({
        "journal_id": m.journal_id, "line_no": m.line_no,
        "posting_date": pd.to_datetime(m.posting_date).dt.strftime("%d/%m/%Y"),
        "company_code": m.company_code, "account_code": m.account_code,
        "cost_centre": m.cost_centre.fillna(""), "amount": m.amount_gbp.map(as_text),
        "currency": "GBP", "description": m.description, "posted_by": m.posted_by,
    })
    dupes = raw.sample(frac=0.01, random_state=int(p[-2:]))
    tests = pd.DataFrame([(f"TEST-{p[-2:]}{i}", ln, f"15/{p[-2:]}/2026", "C100", acc, "", as_text(amt), "GBP",
                           "TEST - please ignore", "TESTUSER")
                          for i in range(3) for ln, acc, amt in [(1, "6100", 999999.99), (2, "2000", -999999.99)]],
                         columns=raw.columns)
    out = pd.concat([raw, dupes, tests]).sample(frac=1, random_state=7)
    out.to_csv(f"{gl_dir}/gl_journal_{p.replace('-', '_')}.csv", index=False)
    n_dupes += len(dupes); n_test += len(tests)
print(f"Raw GL files: {len(PERIODS)} files in {gl_dir}  ({n_dupes:,} duplicate rows and {n_test} test lines planted)")

# COMMAND ----------

# MAGIC %md ## 3 — Journal requests waiting for approval (Track C)

# COMMAND ----------

reasons = ["Reclass to correct cost centre", "Month-end accrual", "Prepayment release", "Correction of miscoding",
           "Intercompany recharge", "Bonus provision true-up", "Software licence accrual", "Legal fee accrual"]
N_REQ = 60
req_amount = np.round(rng.lognormal(9.5, 1.1, N_REQ), 2)
status = rng.choice(["Pending", "Approved", "Rejected"], N_REQ, p=[0.5, 0.4, 0.1])
requests = pd.DataFrame({
    "request_id": [f"REQ-{i:04d}" for i in range(1, N_REQ + 1)],
    "requested_on": random_dates("2026-10-20", PERIOD_END, N_REQ),
    "requested_by": rng.choice(["a.okafor", "j.patel", "m.hughes", "s.lindqvist"], N_REQ),
    "company_code": rng.choice(["C100", "C200", "C300"], N_REQ, p=[0.5, 0.35, 0.15]),
    "account_code": rng.choice(["5100", "6000", "6100", "6200", "6300", "6400", "6500"], N_REQ),
    "cost_centre": rng.choice(cost_centres.cost_centre, N_REQ),
    "amount_gbp": req_amount,
    "reason": rng.choice(reasons, N_REQ),
    "status": status,
    "decided_by": np.where(status == "Pending", None, "f.controller"),
    "decision_comment": np.where(status == "Rejected", "Insufficient supporting evidence", None),
}).sort_values("requested_on").reset_index(drop=True)

print("Journal requests")
save(requests, "3_journal_requests",
     "Manual journal requests raised at October month-end. status is Pending, Approved or Rejected. "
     "Policy: anything of 50,000 GBP or more needs Financial Controller approval.", dates=["requested_on"])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Done
# MAGIC
# MAGIC Open **Catalog** in the left-hand menu and find your schema — you should see 14 tables
# MAGIC and a `raw` volume with ten files under `gl/`. Now pick any exercise.

# COMMAND ----------

display(spark.sql(f"SHOW TABLES IN {FQ}").select("tableName").orderBy("tableName"))
