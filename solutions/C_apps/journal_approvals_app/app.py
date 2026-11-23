"""Journal approvals - a small Databricks App over a governed table.

Reads and updates <schema>.3_journal_requests through a SQL warehouse.
All data is synthetic. Bricksurance is a fictional insurer.
"""
import os

import streamlit as st
from databricks import sql
from databricks.sdk.core import Config

SCHEMA = os.getenv("BOOTCAMP_SCHEMA", "workspace.finance_yourname")   # catalog.schema, set in app.yaml
TABLE = f"{SCHEMA}.`3_journal_requests`"
APPROVAL_LIMIT = 50_000
cfg = Config()                                                        # picks up the app's own identity


def run(query, params=None):
    """Run one statement on the SQL warehouse. Returns a DataFrame for SELECTs."""
    with sql.connect(server_hostname=cfg.host,
                     http_path=f"/sql/1.0/warehouses/{os.environ['DATABRICKS_WAREHOUSE_ID']}",
                     credentials_provider=lambda: cfg.authenticate) as conn, conn.cursor() as cur:
        cur.execute(query, params or {})
        return cur.fetchall_arrow().to_pandas() if cur.description else None


st.set_page_config(page_title="Journal approvals", layout="wide")
st.title("Journal approvals — October 2026 month-end")
st.caption("Synthetic data. Decisions are written straight back to the governed table, with your name on them.")

me = st.context.headers.get("X-Forwarded-Email", "app.user")

try:
    df = run(f"""SELECT request_id, requested_on, requested_by, company_code, account_code, cost_centre,
                        amount_gbp, reason, status, decided_by, decision_comment
                 FROM {TABLE} ORDER BY amount_gbp DESC""")
except Exception as e:
    st.error(f"Could not read {TABLE}. Has the app been granted access to your schema? "
             f"(Run the GRANT cell in the C1 notebook.)\n\n{e}")
    st.stop()

pending = df[df.status == "Pending"]
a, b, c = st.columns(3)
a.metric("Pending requests", len(pending))
b.metric("Pending value", f"£{pending.amount_gbp.sum():,.0f}")
c.metric(f"Need Financial Controller (≥ £{APPROVAL_LIMIT:,})", int((pending.amount_gbp >= APPROVAL_LIMIT).sum()))

show = st.radio("Show", ["Pending", "Approved", "Rejected", "All"], horizontal=True)
view = df if show == "All" else df[df.status == show]
st.dataframe(view, use_container_width=True, hide_index=True,
             column_config={"amount_gbp": st.column_config.NumberColumn("Amount (GBP)", format="£%.2f")})

st.subheader("Decide")
if pending.empty:
    st.success("Nothing left to decide.")
else:
    request_id = st.selectbox("Request", pending.request_id,
                              format_func=lambda r: f"{r} — £{pending.set_index('request_id').amount_gbp[r]:,.2f} — "
                                                    f"{pending.set_index('request_id').reason[r]}")
    amount = float(pending.set_index("request_id").amount_gbp[request_id])
    if amount >= APPROVAL_LIMIT:
        st.warning(f"£{amount:,.2f} is at or above the £{APPROVAL_LIMIT:,} limit: Financial Controller approval is required.")
    comment = st.text_input("Comment (required to reject)")
    approve, reject = st.columns(2)
    decision = "Approved" if approve.button("Approve", type="primary") else "Rejected" if reject.button("Reject") else None
    if decision == "Rejected" and not comment.strip():
        st.error("Please say why you are rejecting it.")
    elif decision:
        run(f"""UPDATE {TABLE} SET status = :status, decided_by = :who, decision_comment = :comment
                WHERE request_id = :id AND status = 'Pending'""",
            {"status": decision, "who": me, "comment": comment.strip() or None, "id": request_id})
        st.toast(f"{request_id} {decision.lower()} by {me}")
        st.rerun()
