import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

st.set_page_config(page_title="AI Dashboard", layout="wide")

# ---------- FILE ----------
file = st.file_uploader("📂 Upload Dataset", type=["csv","xlsx"])

if file:

    df = pd.read_csv(file) if file.name.endswith("csv") else pd.read_excel(file)

    st.title("📊 AI Advanced Dashboard")

    # ---------- DATA UNDERSTANDING ----------
    st.subheader("🧠 Dataset Overview")

    st.write(f"Rows: {df.shape[0]} | Columns: {df.shape[1]}")

    st.dataframe(pd.DataFrame({
        "Column": df.columns,
        "Type": df.dtypes.astype(str),
        "Missing": df.isnull().sum()
    }))

    st.markdown("---")

    # ---------- DATA TYPES ----------
    numeric_cols = df.select_dtypes(include=['int64','float64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    # ---------- KPIs ----------
    st.subheader("📌 Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    if len(numeric_cols)>0:
        col = numeric_cols[0]

        col1.metric("Average", round(df[col].mean(),2))
        col2.metric("Maximum", df[col].max())
        col3.metric("Minimum", df[col].min())
        col4.metric("Total", df[col].sum())

    col5, col6, col7, col8 = st.columns(4)

    col5.metric("Rows", df.shape[0])
    col6.metric("Columns", df.shape[1])
    col7.metric("Missing Values", df.isnull().sum().sum())
    col8.metric("Unique Values", df.nunique().sum())

    st.markdown("---")

    # ---------- CHARTS ----------
    st.subheader("📊 Advanced Visual Dashboard")

    # 1 Histogram
    if len(numeric_cols)>0:
        st.plotly_chart(px.histogram(df, x=numeric_cols[0], title="Distribution"))

    # 2 Box
    if len(numeric_cols)>0:
        st.plotly_chart(px.box(df, y=numeric_cols[0], title="Spread"))

    # 3 Bar
    if len(categorical_cols)>0:
        cat = categorical_cols[0]
        counts = df[cat].value_counts().reset_index()
        counts.columns=[cat,"Count"]
        st.plotly_chart(px.bar(counts,x=cat,y="Count",title="Category Count"))

    # 4 Pie
    if len(categorical_cols)>0:
        st.plotly_chart(px.pie(df,names=categorical_cols[0],title="Category Share"))

    # 5 Scatter
    if len(numeric_cols)>1:
        st.plotly_chart(px.scatter(df,x=numeric_cols[0],y=numeric_cols[1],title="Correlation"))

    # 6 Line (if date exists)
    date_cols = df.select_dtypes(include=['datetime64']).columns
    if len(date_cols)>0 and len(numeric_cols)>0:
        st.plotly_chart(px.line(df,x=date_cols[0],y=numeric_cols[0],title="Trend Over Time"))

    st.markdown("---")

    # ---------- AUTO INSIGHTS ----------
    st.subheader("📈 KPI-Based Insights")

    if len(numeric_cols)>0:
        col = numeric_cols[0]
        st.write(f"• Average value is {df[col].mean():.2f}, indicating general trend.")
        st.write(f"• Maximum value {df[col].max()} shows peak performance.")
        st.write(f"• Minimum value {df[col].min()} indicates lowest performance.")

    if len(categorical_cols)>0:
        top = df[categorical_cols[0]].value_counts().idxmax()
        st.write(f"• Most common category is {top}.")

    st.markdown("---")

    # ---------- AI INSIGHTS ----------
    st.subheader("🤖 Detailed AI Insights")

    api_key = st.text_input("Enter OpenAI API Key", type="password")

    if st.button("Generate Full Insights") and api_key:

        client = OpenAI(api_key=api_key)

        sample = df.head(30).to_string()

        prompt = f"""
        Explain this dataset in detail.
        Then give:
        - Trends
        - Patterns
        - Key insights
        - Business recommendations

        Dataset:
        {sample}
        """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role":"user","content":prompt}]
        )

        st.write(response.choices[0].message.content)
