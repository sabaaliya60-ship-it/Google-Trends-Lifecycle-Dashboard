import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
from datetime import datetime

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="Google Trends Lifecycle Dashboard",
    page_icon="📈",
    layout="wide"
)

# -------------------------------------------------
# TITLE
# -------------------------------------------------

st.title("📈 Google Trends Topic Lifecycle Dashboard")

st.markdown("""
Analyze the complete lifecycle of any Google Trends topic.

This dashboard shows:
- 📈 Interest Timeline
- 🔥 Peak Analysis
- 📉 Drop Analysis
- 🔄 Recovery Analysis
- 🌍 Region Analysis
- 🔮 Future Trend Prediction
""")

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

@st.cache_data
def load_data():

    df = pd.read_csv(
        "data/processed/google_trends_clean.csv"
    )

    df["date"] = pd.to_datetime(df["date"])

    return df

df = load_data()

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

st.sidebar.header("Dashboard Filters")

# Topic

topic = st.sidebar.selectbox(
    "Select Topic",
    sorted(df["topic"].unique())
)

# Filter Topic

df = df[df["topic"] == topic]

# Region

region = st.sidebar.selectbox(

    "Select Region",

    ["All"] + sorted(df["region"].unique())

)

if region != "All":

    df = df[df["region"] == region]

# Date

start = st.sidebar.date_input(

    "Start Date",

    df["date"].min()

)

end = st.sidebar.date_input(

    "End Date",

    df["date"].max()

)

df = df[
    (df["date"] >= pd.to_datetime(start))
    &
    (df["date"] <= pd.to_datetime(end))
]

# Download

st.sidebar.download_button(

    label="📥 Download CSV",

    data=df.to_csv(index=False),

    file_name="filtered_google_trends.csv",

    mime="text/csv"

)

# -------------------------------------------------
# KPI SECTION
# -------------------------------------------------

st.subheader("📊 Key Performance Indicators")

k1, k2, k3, k4 = st.columns(4)

k1.metric(

    "Highest Interest",

    int(df["interest_score"].max())

)

k2.metric(

    "Average Interest",

    round(df["interest_score"].mean(),1)

)

k3.metric(

    "Peak Count",

    (df["Peak_Flag"]=="Peak").sum()

)

k4.metric(

    "Drop Count",

    (df["Drop_Flag"]=="Drop").sum()

)

k5,k6,k7,k8 = st.columns(4)

k5.metric(

    "Recovery Count",

    (df["Recovery_Flag"]=="Recovery").sum()

)

k6.metric(

    "Trend Start",

    df["date"].min().strftime("%d-%b-%Y")

)

k7.metric(

    "Latest Trend",

    df["date"].max().strftime("%d-%b-%Y")

)

k8.metric(

    "Trend Duration",

    f"{(df['date'].max()-df['date'].min()).days} Days"

)

st.divider()
# -------------------------------------------------
# CHART SECTION
# -------------------------------------------------

st.subheader("📈 Topic Lifecycle Analysis")

# -------------------------------
# Chart 1 : Interest Timeline
# -------------------------------

fig1 = px.line(
    df,
    x="date",
    y="interest_score",
    markers=True,
    title="Interest Score Timeline"
)

fig1.update_layout(
    xaxis_title="Date",
    yaxis_title="Interest Score"
)

# -------------------------------
# Chart 2 : Monthly Trend
# -------------------------------

df["Month"] = df["date"].dt.strftime("%b")

month = (
    df.groupby("Month")["interest_score"]
      .mean()
      .reset_index()
)

month_order = [
    "Jan","Feb","Mar","Apr","May","Jun",
    "Jul","Aug","Sep","Oct","Nov","Dec"
]

month["Month"] = pd.Categorical(
    month["Month"],
    categories=month_order,
    ordered=True
)

month = month.sort_values("Month")

fig2 = px.bar(
    month,
    x="Month",
    y="interest_score",
    color="interest_score",
    title="Average Monthly Interest"
)

fig2.update_layout(
    xaxis_title="Month",
    yaxis_title="Average Interest"
)

# -------------------------------
# Chart 3 : Lifecycle Stage
# -------------------------------

stage = (
    df.groupby("Lifecycle_Stage")
      .size()
      .reset_index(name="Count")
)

fig3 = px.pie(
    stage,
    names="Lifecycle_Stage",
    values="Count",
    hole=.45,
    title="Lifecycle Stage Distribution"
)

# -------------------------------
# Chart 4 : Peak Drop Recovery
# -------------------------------

flag = pd.DataFrame({

    "Type":[
        "Peak",
        "Drop",
        "Recovery"
    ],

    "Count":[

        (df["Peak_Flag"]=="Peak").sum(),

        (df["Drop_Flag"]=="Drop").sum(),

        (df["Recovery_Flag"]=="Recovery").sum()

    ]

})

fig4 = px.bar(

    flag,

    x="Type",

    y="Count",

    color="Type",

    title="Peak vs Drop vs Recovery"

)

# -------------------------------
# Chart 5 : Region
# -------------------------------

region = (

    df.groupby("region")["interest_score"]

    .mean()

    .reset_index()

)

fig5 = px.bar(

    region,

    x="region",

    y="interest_score",

    color="interest_score",

    title="Average Interest by Region"

)

# -------------------------------
# Dashboard Layout
# -------------------------------

c1,c2 = st.columns(2)

with c1:

    st.plotly_chart(fig1,use_container_width=True)

with c2:

    st.plotly_chart(fig2,use_container_width=True)

c3,c4 = st.columns(2)

with c3:

    st.plotly_chart(fig3,use_container_width=True)

with c4:

    st.plotly_chart(fig4,use_container_width=True)

st.plotly_chart(fig5,use_container_width=True)

st.divider()
# -------------------------------------------------
# FUTURE TREND PREDICTION
# -------------------------------------------------

st.subheader("🔮 Future Trend Prediction")

try:

    model = joblib.load("models/trend_model.pkl")

    last_day = (df["date"].max() - df["date"].min()).days

    future_days = list(range(last_day + 1, last_day + 31))

    future = pd.DataFrame({
        "Day_Number": future_days
    })

    prediction = model.predict(future)

    future_dates = pd.date_range(
        start=df["date"].max() + pd.Timedelta(days=1),
        periods=30
    )

    forecast = pd.DataFrame({
        "Date": future_dates,
        "Predicted_Interest": prediction
    })

    fig6 = px.line(
        forecast,
        x="Date",
        y="Predicted_Interest",
        markers=True,
        title="Next 30 Days Forecast"
    )

    st.plotly_chart(fig6, use_container_width=True)

except:

    st.warning("Prediction model not found.")

# -------------------------------------------------
# WEEKLY TREND
# -------------------------------------------------

st.subheader("📅 Weekly Trend")

week = (
    df.groupby("week_number")["interest_score"]
      .mean()
      .reset_index()
)

fig7 = px.bar(
    week,
    x="week_number",
    y="interest_score",
    color="interest_score",
    title="Average Weekly Interest"
)

st.plotly_chart(fig7, use_container_width=True)

# -------------------------------------------------
# SUMMARY
# -------------------------------------------------

st.subheader("📌 Dashboard Summary")

highest = df["interest_score"].max()
average = round(df["interest_score"].mean(), 2)
peaks = (df["Peak_Flag"] == "Peak").sum()
drops = (df["Drop_Flag"] == "Drop").sum()
recovery = (df["Recovery_Flag"] == "Recovery").sum()

st.info(f"""
Highest Interest : {highest}

Average Interest : {average}

Peak Count : {peaks}

Drop Count : {drops}

Recovery Count : {recovery}
""")

# -------------------------------------------------
# FOOTER
# -------------------------------------------------

st.markdown("---")

st.markdown(
"""
<center>

### 📈 Google Trends Topic Lifecycle Dashboard

Built with ❤️ using

Python • Streamlit • Plotly • Scikit-Learn

</center>
""",
unsafe_allow_html=True
)