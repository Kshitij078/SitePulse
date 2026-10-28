import pandas as pd
import plotly.express as px
import streamlit as st

from app.database.connection import Base, SessionLocal, engine
from app.database.models import Incident, MonitoredWebsite, WebsiteCheck


Base.metadata.create_all(bind=engine)

st.set_page_config(
    page_title="SitePulse | Website Health Monitor",
    layout="wide",
)

st.title("SitePulse")
st.caption("Website Health Monitoring Dashboard")

with SessionLocal() as session:
    records = (
        session.query(WebsiteCheck)
        .order_by(WebsiteCheck.checked_at.desc())
        .limit(2000)
        .all()
    )

    incidents = (
        session.query(Incident)
        .order_by(Incident.started_at.desc())
        .limit(100)
        .all()
    )

data = [
    {
        "URL": record.url,
        "Status": "UP" if record.is_up else "DOWN",
        "HTTP Code": record.status_code,
        "Response Time (ms)": record.response_time_ms,
        "Checked At": record.checked_at,
        "Error": record.error,
    }
    for record in records
]

if not data:
    st.info(
        "No monitoring data yet. Start the monitor to collect website checks."
    )
    st.stop()

df = pd.DataFrame(data)
df["Checked At"] = pd.to_datetime(df["Checked At"], errors="coerce")

websites = sorted(df["URL"].dropna().unique().tolist())

selected_websites = st.multiselect(
    "Filter websites",
    options=websites,
    default=websites,
)

filtered = df[df["URL"].isin(selected_websites)].copy()

if filtered.empty:
    st.warning("No records found for the selected websites.")
    st.stop()

latest = (
    filtered.sort_values("Checked At")
    .groupby("URL", as_index=False)
    .tail(1)
)

total_websites = latest["URL"].nunique()
up_websites = int((latest["Status"] == "UP").sum())
down_websites = int((latest["Status"] == "DOWN").sum())

valid_response_times = filtered["Response Time (ms)"].dropna()
average_response = (
    round(valid_response_times.mean(), 2)
    if not valid_response_times.empty
    else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Websites Monitored", total_websites)
col2.metric("Websites Up", up_websites)
col3.metric("Websites Down", down_websites)
col4.metric("Avg Response Time", f"{average_response} ms")

st.divider()

st.subheader("Current Website Status")

status_columns = [
    "URL",
    "Status",
    "HTTP Code",
    "Response Time (ms)",
    "Checked At",
    "Error",
]

st.dataframe(
    latest[status_columns].sort_values("URL"),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Website Reliability")

reliability = (
    filtered.groupby("URL")
    .agg(
        Total_Checks=("Status", "count"),
        Successful_Checks=(
            "Status",
            lambda values: (values == "UP").sum(),
        ),
    )
    .reset_index()
)

reliability["Uptime (%)"] = (
    reliability["Successful_Checks"]
    / reliability["Total_Checks"]
    * 100
).round(2)

st.dataframe(
    reliability,
    use_container_width=True,
    hide_index=True,
)


st.subheader("Manage Websites")

with st.form("add_website_form", clear_on_submit=True):
    new_url = st.text_input(
        "Website URL",
        placeholder="https://example.com",
    )
    submitted = st.form_submit_button("Add Website")

    if submitted:
        url = new_url.strip()

        if not url:
            st.error("Enter a website URL.")
        else:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            from urllib.parse import urlparse

            parsed = urlparse(url)

            if parsed.scheme not in ("http", "https") or not parsed.hostname:
                st.error("Enter a valid HTTP or HTTPS URL.")
            else:
                with SessionLocal() as session:
                    existing = (
                        session.query(MonitoredWebsite)
                        .filter(MonitoredWebsite.url == url)
                        .first()
                    )

                    if existing:
                        if not existing.is_active:
                            existing.is_active = True
                            session.commit()
                            st.success("Website reactivated.")
                        else:
                            st.info("This website is already being monitored.")
                    else:
                        session.add(MonitoredWebsite(url=url))
                        session.commit()
                        st.success("Website added successfully.")

                st.rerun()

with SessionLocal() as session:
    managed_websites = (
        session.query(MonitoredWebsite)
        .order_by(MonitoredWebsite.created_at.desc())
        .all()
    )

if managed_websites:
    for website in managed_websites:
        col_url, col_status, col_action = st.columns([5, 2, 2])

        col_url.write(website.url)
        col_status.write("Active" if website.is_active else "Paused")

        if website.is_active:
            if col_action.button("Pause", key=f"pause_{website.id}"):
                with SessionLocal() as session:
                    item = session.get(MonitoredWebsite, website.id)
                    if item:
                        item.is_active = False
                        session.commit()
                st.rerun()
        else:
            if col_action.button("Resume", key=f"resume_{website.id}"):
                with SessionLocal() as session:
                    item = session.get(MonitoredWebsite, website.id)
                    if item:
                        item.is_active = True
                        session.commit()
                st.rerun()
else:
    st.info("No websites added yet. Add your first website above.")


st.caption(
    "Uptime is calculated from recorded checks in the available history, "
    "not from continuous time measurements."
)

st.subheader("Response Time History")

chart_data = filtered.dropna(subset=["Response Time (ms)", "Checked At"])

if not chart_data.empty:
    chart = px.line(
        chart_data.sort_values("Checked At"),
        x="Checked At",
        y="Response Time (ms)",
        color="URL",
        markers=True,
        title="Website Response Times",
    )

    chart.update_layout(
        xaxis_title="Check Time",
        yaxis_title="Response Time (ms)",
        legend_title="Website",
    )

    st.plotly_chart(chart, use_container_width=True)
else:
    st.info("No response-time data available yet.")

st.subheader("Check History")

st.dataframe(
    filtered.sort_values("Checked At", ascending=False),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Incident History")

selected_incidents = [
    incident
    for incident in incidents
    if incident.url in selected_websites
]

incident_data = [
    {
        "Website": incident.url,
        "Started At": incident.started_at,
        "Resolved At": incident.resolved_at,
        "Status": (
            "Resolved"
            if incident.resolved_at
            else "Ongoing"
        ),
        "Error": incident.error,
    }
    for incident in selected_incidents
]

if incident_data:
    st.dataframe(
        pd.DataFrame(incident_data),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No incidents recorded for the selected websites.")

st.caption("SitePulse | Website Health Monitoring")
