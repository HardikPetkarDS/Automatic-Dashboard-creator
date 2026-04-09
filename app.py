import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

st.set_page_config(page_title="AI Dashboard", layout="wide")

# ---------- FILE ----------
file = st.file_uploader("Upload Dataset", type=["csv","xlsx"])

if file:

    df = pd.read_csv(file) if file.name.endswith("csv") else pd.read_excel(file)

    st.title("📊 AI Data Analysis Dashboard")

    # ---------- DATA OVERVIEW ----------
    st.subheader("🧠 Dataset Understanding")

    st.write("### 📌 Shape of Data")
    st.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

    st.write("### 📌 Column Information")
    st.dataframe(pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str),
        "Missing Values": df.isnull().sum()
    }))

    st.write("### 📌 Summary Statistics")
    st.dataframe(df.describe())

    st.markdown("---")

    # ---------- VISUALS ----------
    numeric_cols = df.select_dtypes(include=['int64','float64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    st.subheader("📊 Visual Insights")

    if len(numeric_cols)>0:
        st.plotly_chart(px.histogram(df, x=numeric_cols[0], title="Distribution"))

    if len(categorical_cols)>0:
        cat = categorical_cols[0]
        counts = df[cat].value_counts().reset_index()
        counts.columns=[cat,"Count"]
        st.plotly_chart(px.bar(counts,x=cat,y="Count",title="Category Count"))

    st.markdown("---")

    # ---------- BASIC INSIGHTS ----------
    st.subheader("📈 Analytical Insights")

    insights = []

    if len(numeric_cols)>0:
        col = numeric_cols[0]
        insights.append(f"Average {col} is {df[col].mean():.2f}")
        insights.append(f"Maximum {col} is {df[col].max()}")
        insights.append(f"Minimum {col} is {df[col].min()}")

    if len(categorical_cols)>0:
        top = df[categorical_cols[0]].value_counts().idxmax()
        insights.append(f"Most frequent {categorical_cols[0]} is {top}")

    for i in insights:
        st.write("•", i)

    st.markdown("---")

    # ---------- AI DETAILED INSIGHTS ----------
    st.subheader("🤖 AI Detailed Insights")

    api_key = st.text_input("Enter OpenAI API Key", type="password")

    if st.button("Generate Detailed Insights") and api_key:

        client = OpenAI(api_key=api_key)

        sample = df.head(30).to_string()

        prompt = f"""
        You are a professional data analyst.

        Step 1: Explain what this dataset is about in simple terms.

        Step 2: Identify key trends and patterns.

        Step 3: Highlight important insights.

        Step 4: Provide business recommendations.

        Dataset:
        {sample}
        """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role":"user","content":prompt}]
        )

        st.write(response.choices[0].message.content)
