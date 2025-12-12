import streamlit as st
import pandas as pd
from src.models import SessionLocal, Company, FinancialMetric
from sqlalchemy import asc
import altair as alt

st.set_page_config(layout="wide", page_title="Financial Metrics Dashboard")

session = SessionLocal()
companies = session.query(Company).all()
tickers = [c.ticker for c in companies]
sel = st.sidebar.selectbox("Select company", ["--"] + tickers)

if sel and sel != "--":
    company = session.query(Company).filter_by(ticker=sel).first()
    st.title(f"{company.ticker} — Financial Metrics")
    metrics = session.query(FinancialMetric).filter_by(company_id=company.id).order_by(asc(FinancialMetric.fiscal_date)).all()
    if not metrics:
        st.info("No metrics found. Run loader & metrics scripts first.")
    else:
        df = pd.DataFrame([{
            "fiscal_date": m.fiscal_date,
            "metric_name": m.metric_name,
            "metric_value": float(m.metric_value) if m.metric_value is not None else None
        } for m in metrics])

        pivot = df.pivot(index="fiscal_date", columns="metric_name", values="metric_value").reset_index()
        st.subheader("Metrics table")
        st.dataframe(pivot)

        metric_choices = list(df["metric_name"].unique())
        chosen = st.multiselect("Choose metrics to chart", metric_choices, default=metric_choices[:3])

        for m in chosen:
            chart_df = pivot[["fiscal_date", m]].dropna()
            if chart_df.empty:
                st.write(f"No data for {m}")
                continue
            c = alt.Chart(chart_df).mark_line(point=True).encode(
                x=alt.X("fiscal_date:T", title="Fiscal Date"),
                y=alt.Y(f"{m}:Q", title=m)
            ).properties(height=250, width=700, title=m)
            st.altair_chart(c, use_container_width=True)

session.close()
