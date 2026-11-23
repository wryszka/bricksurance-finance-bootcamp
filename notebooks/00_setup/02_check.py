# Databricks notebook source
# MAGIC %md
# MAGIC # 02 — Check my work
# MAGIC
# MAGIC You don't need to open this. Every exercise ends with a cell like `check("A1")` that
# MAGIC compares **your** output table with the right answer, worked out live from the source
# MAGIC data, and tells you what to look at if they differ.

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

def _q(sql):
    return spark.sql(sql.replace("{S}", FQ))


def _one(sql):
    v = _q(sql).first()[0]
    return float(v) if v is not None else 0.0


def _mine(name, needed):
    """Return the attendee's table, or None (with a friendly message) if it isn't ready."""
    if not spark.catalog.tableExists(f"{FQ}.{name}"):
        print(f"⏳ No table `{name}` in {FQ} yet. Build it, run the flow (Run all), then run this cell again.")
        return None
    df = spark.table(f"{FQ}.{name}")
    missing = [c for c in needed if c not in df.columns]
    if missing:
        print(f"🔎 Found `{name}` but it has no column {missing}. It has: {df.columns}")
        print("   Rename your output columns to match the exercise, then run again.")
        return None
    return df


def _same(a, b, tol=0.05):
    return abs(a - b) <= tol


def _gbp(v):
    return f"£{v:,.2f}"


def _ok(msg):
    print(f"✅ {msg}")


def _no(msg):
    print(f"❌ {msg}")


# ---------------------------------------------------------------- Track A

def _check_a1():
    df = _mine("my_spend_by_category", ["category", "total_paid_gbp"])
    if df is None:
        return
    mine = float(df.agg({"total_paid_gbp": "sum"}).first()[0] or 0)
    paid = _one("SELECT sum(amount_gbp) FROM {S}.`1_supplier_payments` WHERE status = 'Paid'")
    everything = _one("SELECT sum(amount_gbp) FROM {S}.`1_supplier_payments`")
    matched = _one("""SELECT sum(p.amount_gbp) FROM {S}.`1_supplier_payments` p
                      JOIN {S}.`1_supplier_categories` c USING (supplier_name) WHERE p.status = 'Paid'""")
    if _same(mine, matched):
        _ok(f"Spot on: {df.count()} categories, {_gbp(mine)} in total.")
        print(f"   One thing to notice: the finance system says {_gbp(paid)} was paid. "
              f"Your flow is {_gbp(paid - matched)} short. Nothing is wrong with your flow - "
              "but where did that money go? Exercise A3 is about exactly that.")
    elif _same(mine, paid):
        _ok(f"Spot on, and you kept every payment: {_gbp(mine)} across {df.count()} rows "
            "(including the suppliers with no category).")
    elif _same(mine, everything) or mine > paid:
        _no(f"Your total is {_gbp(mine)}, which is too high. Did you filter out the Reversed payments?")
    else:
        _no(f"Your total is {_gbp(mine)}; expected {_gbp(matched)} (or {_gbp(paid)} if you kept uncategorised suppliers).")


def _check_a2():
    df = _mine("my_bank_rec", ["bank_account", "variance_gbp"])
    if df is None:
        return
    truth = {r[0]: float(r[1]) for r in _q("""
        WITH g AS (SELECT bank_account, sum(amount_gbp) v FROM {S}.`1_gl_cash` GROUP BY 1),
             b AS (SELECT bank_account, sum(amount_gbp) v FROM {S}.`1_bank_statement` GROUP BY 1)
        SELECT bank_account, round(g.v - b.v, 2) FROM g JOIN b USING (bank_account)""").collect()}
    mine = {r["bank_account"]: float(r["variance_gbp"] or 0) for r in df.collect()}
    if len(mine) != len(truth):
        _no(f"Expected one row per bank account ({len(truth)}), found {len(mine)}. "
            "Aggregate each side by bank_account BEFORE you join, otherwise rows multiply.")
        return
    wrong = [a for a in truth if not (_same(mine.get(a, 1e12), truth[a]) or _same(mine.get(a, 1e12), -truth[a]))]
    breaks = sorted(a for a, v in truth.items() if abs(v) > 0.005)
    if wrong:
        _no(f"Variance is off for {wrong[:4]}. Variance = ledger total minus bank total, per account.")
        return
    _ok(f"{len(truth) - len(breaks)} of {len(truth)} accounts reconcile to the penny. The breaks are {', '.join(breaks)}.")
    if spark.catalog.tableExists(f"{FQ}.my_bank_rec_breaks"):
        n = spark.table(f"{FQ}.my_bank_rec_breaks").count()
        want = _q("""SELECT count(*) FROM {S}.`1_gl_cash` g FULL OUTER JOIN {S}.`1_bank_statement` b
                     ON g.bank_account = b.bank_account AND g.reference = b.reference
                     WHERE g.amount_gbp IS NULL OR b.amount_gbp IS NULL OR g.amount_gbp <> b.amount_gbp""").first()[0]
        (_ok if n == want else _no)(f"Stretch: your break list has {n} lines; the real answer is {want}.")
    else:
        print("   Stretch: build `my_bank_rec_breaks` to find the individual lines behind each break.")


def _check_a3():
    df = _mine("my_control_sheet", ["branch", "branch_total_gbp"])
    if df is None:
        return
    mine = float(df.agg({"branch_total_gbp": "sum"}).first()[0] or 0)
    paid = _one("SELECT sum(amount_gbp) FROM {S}.`1_supplier_payments` WHERE status = 'Paid'")
    matched = _one("""SELECT sum(p.amount_gbp) FROM {S}.`1_supplier_payments` p
                      JOIN {S}.`1_supplier_categories` c USING (supplier_name) WHERE p.status = 'Paid'""")
    if _same(mine, paid) or _same(mine, 2 * paid):          # 2x when a grand-total row is included
        _ok(f"The branches tie back to the whole: {_gbp(paid)}, variance 0.00. That is a control you can sign.")
    elif _same(mine, matched) or _same(mine, 2 * matched):
        _no(f"Your branches add up to {_gbp(matched)} but {_gbp(paid)} was paid: {_gbp(paid - matched)} has vanished.")
        print("   An inner join silently drops payments to suppliers missing from the lookup. "
              "Switch the join to a LEFT join and give those rows their own branch.")
    else:
        _no(f"Your branches add up to {_gbp(mine)}; the control total is {_gbp(paid)}. Check the Reversed filter and the join.")


def _check_a4():
    df = _mine("my_aged_debtors", ["broker_name", "age_bucket", "outstanding_gbp"])
    if df is None:
        return
    total = _one("SELECT sum(amount_gbp - amount_paid_gbp) FROM {S}.`1_ar_invoices` WHERE amount_gbp > amount_paid_gbp")
    over90 = _one(f"""SELECT sum(amount_gbp - amount_paid_gbp) FROM {{S}}.`1_ar_invoices`
                      WHERE amount_gbp > amount_paid_gbp AND datediff('{PERIOD_END}', due_date) > 90""")
    mine = float(df.agg({"outstanding_gbp": "sum"}).first()[0] or 0)
    mine90 = float(df.filter("age_bucket LIKE '%90+%' OR lower(age_bucket) LIKE '%over 90%'")
                   .agg({"outstanding_gbp": "sum"}).first()[0] or 0)
    if not _same(mine, total):
        _no(f"Total outstanding is {_gbp(mine)}; expected {_gbp(total)}. Outstanding = amount_gbp - amount_paid_gbp, "
            "and fully paid invoices should not appear.")
    elif not _same(mine90, over90):
        _no(f"Total is right, but the 90+ bucket is {_gbp(mine90)}; expected {_gbp(over90)}. "
            f"Age = days between due_date and {PERIOD_END} (not today). Call the oldest bucket '90+'.")
    else:
        _ok(f"Total debt {_gbp(total)}, of which {_gbp(over90)} is more than 90 days overdue.")
        worst = df.filter("age_bucket LIKE '%90+%'").orderBy(df.outstanding_gbp.desc()).first()
        print(f"   Worst offender in 90+: {worst['broker_name']} ({_gbp(float(worst['outstanding_gbp']))}).")


_ACCRUAL_SQL = """
    WITH inv AS (SELECT po_id, sum(invoice_amount_gbp) AS invoiced FROM {S}.`1_supplier_invoices` {inv_filter} GROUP BY po_id)
    SELECT sum(p.po_amount_gbp - coalesce(i.invoiced, 0))
    FROM {S}.`1_purchase_orders` p LEFT JOIN inv i USING (po_id)
    WHERE {po_filter} AND p.po_amount_gbp - coalesce(i.invoiced, 0) > 0.005"""


def _accrual(po_filter, inv_filter):
    return _one(_ACCRUAL_SQL.replace("{po_filter}", po_filter).replace("{inv_filter}", inv_filter))


def _check_a5(table="my_accruals_summary"):
    df = _mine(table, ["company_code", "cost_centre", "accrual_gbp"])
    if df is None:
        return
    good_po = f"p.po_status <> 'Cancelled' AND p.goods_received_date <= '{PERIOD_END}'"
    good_inv = f"WHERE invoice_date <= '{PERIOD_END}'"
    truth = _accrual(good_po, good_inv)
    mine = float(df.agg({"accrual_gbp": "sum"}).first()[0] or 0)
    if _same(mine, truth, 1.0):
        _ok(f"Parity with the legacy process: accrual of {_gbp(truth)} across {df.count()} company / cost-centre lines.")
        return
    _no(f"Your accrual is {_gbp(mine)}; the legacy process gives {_gbp(truth)}.")
    suspects = {
        "cancelled purchase orders are still in": _accrual(f"p.goods_received_date <= '{PERIOD_END}'", good_inv),
        "invoices dated after the period end are being netted off": _accrual(good_po, ""),
        "purchase orders with no goods received (or received in November) are in": _accrual("p.po_status <> 'Cancelled'", good_inv),
    }
    for reason, value in suspects.items():
        if _same(mine, value, 1.0):
            print(f"   Likely cause: {reason}.")
            return
    print("   Check the four rules in the legacy workflow one at a time, previewing the row count after each step.")


def _check_a6():
    df = _mine("my_monthly_supplier_spend", ["supplier_name", "total_paid_gbp"])
    if df is None:
        return
    mine = float(df.agg({"total_paid_gbp": "sum"}).first()[0] or 0)
    months = {r[0]: float(r[1]) for r in _q("""SELECT date_format(payment_date, 'yyyy-MM'), sum(amount_gbp)
                                               FROM {S}.`1_supplier_payments` WHERE status = 'Paid' GROUP BY 1""").collect()}
    hit = [m for m, v in months.items() if _same(mine, v)]
    if hit:
        _ok(f"Your table holds supplier spend for {hit[0]} ({_gbp(mine)}). Change the parameter, run again, and this line changes.")
        print("   Now look in Jobs & Pipelines: is there a schedule with your name on it?")
    else:
        _no(f"Total is {_gbp(mine)}, which doesn't match any single month. Is the month parameter used in the Filter?")


# ---------------------------------------------------------------- Track B

def _check_b1():
    df = _mine("my_trial_balance", ["period", "company_code", "account_code", "net_gbp"])
    if df is None:
        return
    df.createOrReplaceTempView("_mine_tb")
    net = _one("SELECT sum(net_gbp) FROM _mine_tb")
    diff = _q("""SELECT count(*) AS n, coalesce(max(abs(coalesce(m.net_gbp, 0) - coalesce(t.net_gbp, 0))), 0) AS worst
                 FROM (SELECT period, company_code, account_code, sum(net_gbp) net_gbp FROM _mine_tb GROUP BY ALL) m
                 FULL OUTER JOIN {S}.`2_trial_balance` t USING (period, company_code, account_code)
                 WHERE abs(coalesce(m.net_gbp, 0) - coalesce(t.net_gbp, 0)) > 0.05""").first()
    if diff["n"] == 0:
        _ok(f"Your trial balance matches the finance system on every line and nets to {_gbp(net)}. It balances.")
        return
    _no(f"{diff['n']} lines differ from the finance system (worst by {_gbp(float(diff['worst']))}).")
    it = _one("SELECT sum(net_gbp) FROM _mine_tb WHERE account_code = '6100' AND company_code = 'C100'")
    it_true = _one("SELECT sum(net_gbp) FROM {S}.`2_trial_balance` WHERE account_code = '6100' AND company_code = 'C100'")
    if it - it_true > 900_000:
        print("   IT and Software is millions too high: the TEST journals (posted_by = 'TESTUSER') are still in.")
    elif abs(net) > 1 or it > it_true:
        print("   Totals are a little too high: the files contain exact duplicate rows. Remove duplicates before you sum.")
    else:
        print("   Check the amount conversion: '(1,234.50)' means minus 1234.50, and dates are day/month/year.")


def _check_b3():
    print("Answer key for your Genie agent - ask it, then compare:\n")
    rows = _q("""
      SELECT 'Gross written premium, January to October' AS question,
             format_number(sum(actual_gbp), 0) AS answer FROM {S}.`2_actual_vs_budget` WHERE account_code = '4000'
      UNION ALL SELECT 'Total expenses, January to October',
             format_number(sum(actual_gbp), 0) FROM {S}.`2_actual_vs_budget` WHERE account_type = 'Expense'
      UNION ALL SELECT 'Biggest overspend against budget in a single month',
             (SELECT concat(account_name, ', ', period, ': ', format_number(sum(variance_gbp), 0), ' over')
              FROM {S}.`2_actual_vs_budget` WHERE account_type = 'Expense' AND account_code <> '5000'
              GROUP BY account_name, period ORDER BY sum(variance_gbp) DESC LIMIT 1)
      UNION ALL SELECT 'Marketing spend versus budget, January to May',
             (SELECT concat(format_number(sum(actual_gbp), 0), ' against ', format_number(sum(budget_gbp), 0))
              FROM {S}.`2_actual_vs_budget` WHERE account_code = '6300' AND period <= '2026-05')
      UNION ALL SELECT 'IT and Software overspend, July to October',
             (SELECT format_number(sum(variance_gbp), 0)
              FROM {S}.`2_actual_vs_budget` WHERE account_code = '6100' AND period >= '2026-07')""").collect()
    for r in rows:
        answer = r["answer"] if r["answer"][0].isalpha() else "£" + r["answer"].replace(" against ", " against £")
        print(f"  {r['question']:52s} {answer}")


def _check_b4():
    df = _mine("my_variance_commentary", ["commentary"])
    if df is None:
        return
    n, filled = df.count(), df.filter("commentary IS NOT NULL AND length(commentary) > 20").count()
    if n >= 3 and filled == n:
        _ok(f"{n} variances, every one with commentary. Read them: would you send them to the CFO as they are?")
    else:
        _no(f"{filled} of {n} rows have commentary. Aim for the top 5 variances, each with a short explanation.")


# ---------------------------------------------------------------- Track C

def _check_c1():
    df = _mine("3_journal_requests", ["status", "decided_by"])
    if df is None:
        return
    mine = df.filter("decided_by IS NOT NULL AND decided_by <> 'f.controller'").count()
    pending = df.filter("status = 'Pending'").count()
    if mine:
        _ok(f"{mine} request(s) decided through your app, written straight back to the governed table. "
            f"{pending} still pending.")
    else:
        print("⏳ No decisions from your app yet. Approve or reject a request in the app, then run this again.")
        print("   (If the app shows a permissions error, run the GRANT cell in this notebook first.)")


def _check_c2():
    if spark.catalog.tableExists(f"{FQ}.my_accruals_review"):
        _check_a5("my_accruals_review")
    else:
        print("⏳ No table `my_accruals_review` yet. Ask Genie Code to rebuild the macro's logic as a table first.")


_CHECKS = {"A1": _check_a1, "A2": _check_a2, "A3": _check_a3, "A4": _check_a4, "A5": _check_a5, "A6": _check_a6,
           "B1": _check_b1, "B3": _check_b3, "B4": _check_b4, "C1": _check_c1, "C2": _check_c2}


def check(exercise):
    """Compare your output for an exercise with the right answer."""
    fn = _CHECKS.get(exercise.upper())
    if fn is None:
        print(f"No automatic check for {exercise}. Available: {', '.join(sorted(_CHECKS))}")
        return
    fn()
