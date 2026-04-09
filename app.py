import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

st.set_page_config(page_title="AI Dashboard", layout="wide")

# ---------- SIDEBAR ----------
st.sidebar.header("🏢 Upload Company Logo")
logo = st.sidebar.file_uploader("Upload logo", type=["png", "jpg", "jpeg"])

uploaded_file = st.file_uploader("📂 Upload Dataset", type=["csv", "xlsx"])

if uploaded_file:

    # ---------- LOAD DATA ----------
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # ---------- HEADER ----------
    if logo:
        col1, col2 = st.columns([1,5])
        with col1:
            st.image(logo, width=100)
        with col2:
            st.title("📊 AI Business Dashboard")
    else:
        st.title("📊 AI Business Dashboard")

    st.markdown("---")

    # ---------- DATA TYPES ----------
    numeric_cols = df.select_dtypes(include=['int64','float64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    # ---------- FILTER ----------
    st.sidebar.header("🔍 Filters")
    filter_col = st.sidebar.selectbox("Filter Column", df.columns)

    if df[filter_col].dtype == 'object':
        val = st.sidebar.selectbox("Value", df[filter_col].unique())
        df = df[df[filter_col] == val]

    # ---------- KPIs ----------
    st.subheader("📌 Key Metrics")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Rows", df.shape[0])

    with col2:
        st.metric("Columns", df.shape[1])

    with col3:
        if len(numeric_cols)>0:
            st.metric("Avg", round(df[numeric_cols[0]].mean(),2))

    with col4:
        if len(numeric_cols)>0:
            st.metric("Max", df[numeric_cols[0]].max())

    with col5:
        if len(numeric_cols)>0:
            st.metric("Min", df[numeric_cols[0]].min())

    st.markdown("---")

    # ---------- CHARTS ----------
    st.subheader("📊 Insights Dashboard")

    col1, col2 = st.columns(2)

    # 1 Histogram
    if len(numeric_cols)>0:
        fig = px.histogram(df, x=numeric_cols[0], title="Distribution")
        col1.plotly_chart(fig, use_container_width=True)

    # 2 Bar chart
    if len(categorical_cols)>0:
        cat = categorical_cols[0]
        counts = df[cat].value_counts().reset_index()
        counts.columns=[cat,"Count"]

        fig = px.bar(counts, x=cat, y="Count", title="Category Count")
        col2.plotly_chart(fig, use_container_width=True)

    # 3 Pie Chart
    if len(categorical_cols)>0:
        fig = px.pie(df, names=categorical_cols[0], title="Category Share")
        st.plotly_chart(fig, use_container_width=True)

    # 4 Box Plot
    if len(numeric_cols)>0:
        fig = px.box(df, y=numeric_cols[0], title="Spread Analysis")
        st.plotly_chart(fig, use_container_width=True)

    # 5 Scatter Plot
    if len(numeric_cols)>1:
        fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], title="Correlation")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ---------- KPI BASED INSIGHTS ----------
    st.subheader("📈 Auto Insights")

    if len(numeric_cols)>0:
        col = numeric_cols[0]
        st.write(f"• Average {col}: {round(df[col].mean(),2)}")
        st.write(f"• Highest {col}: {df[col].max()}")
        st.write(f"• Lowest {col}: {df[col].min()}")

    if len(categorical_cols)>0:
        top_cat = df[categorical_cols[0]].value_counts().idxmax()
        st.write(f"• Most frequent {categorical_cols[0]}: {top_cat}")

    st.markdown("---")

    # ---------- AI INSIGHTS ----------
    st.subheader("🤖 AI Insights")

    api_key = st.text_input("Enter OpenAI API Key", type="password")

    if st.button("Generate AI Insights") and api_key:
        client = OpenAI(api_key=api_key)

        sample = df.head(20).to_string()

        prompt = f"""
        Analyze this dataset and provide:
        - Trends
        - Risks
        - Business recommendations

        {sample}
        """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role":"user","content":prompt}]
        )

        st.write(response.choices[0].message.content)
