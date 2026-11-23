"""Accruals review - the spreadsheet tracker rebuilt as a small Databricks App.

Reads <schema>.my_accruals_review (built in exercise C2) through a SQL warehouse.
All data is synthetic. Bricksurance is a fictional insurer.
"""
import os

import streamlit as st
from databricks import sql
from databricks.sdk.core import Config

SCHEMA = os.getenv("BOOTCAMP_SCHEMA", "workspace.finance_yourname")   # catalog.schema, set in app.yaml
REVIEW_LIMIT = 250_000
cfg = Config()


def run(query):
    with sql.connect(server_hostname=cfg.host,
                     http_path=f"/sql/1.0/warehouses/{os.environ['DATABRICKS_WAREHOUSE_ID']}",
                     credentials_provider=lambda: cfg.authenticate) as conn, conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall_arrow().to_pandas()


st.set_page_config(page_title="Accruals review", layout="wide")
st.title("Purchase order accruals — October 2026")
st.caption("Goods and services received but not yet invoiced. Synthetic data.")

try:
    df = run(f"""SELECT a.company_code, a.cost_centre, c.cost_centre_name, a.po_count, a.accrual_gbp
                 FROM {SCHEMA}.my_accruals_review a
                 JOIN {SCHEMA}.`0_cost_centres` c USING (cost_centre)
                 ORDER BY a.accrual_gbp DESC""")
except Exception as e:
    st.error(f"Could not read {SCHEMA}.my_accruals_review. Build it in exercise C2 and grant the app access.\n\n{e}")
    st.stop()

company = st.multiselect("Company", sorted(df.company_code.unique()), default=sorted(df.company_code.unique()))
view = df[df.company_code.isin(company)]

a, b, c = st.columns(3)
a.metric("Total accrual", f"£{view.accrual_gbp.sum():,.0f}")
b.metric("Purchase orders", int(view.po_count.sum()))
c.metric(f"Lines to review (≥ £{REVIEW_LIMIT:,})", int((view.accrual_gbp >= REVIEW_LIMIT).sum()))

left, right = st.columns([3, 2])
left.dataframe(view.assign(review=view.accrual_gbp.ge(REVIEW_LIMIT).map({True: "Review", False: ""})),
               use_container_width=True, hide_index=True,
               column_config={"accrual_gbp": st.column_config.NumberColumn("Accrual (GBP)", format="£%.2f")})
right.bar_chart(view.groupby("cost_centre_name").accrual_gbp.sum())
