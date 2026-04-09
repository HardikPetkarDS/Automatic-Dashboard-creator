import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="AI Dashboard Generator", layout="wide")

# ---------- TITLE ----------
st.title("📊 AI Dashboard Generator")

# ---------- LOGO UPLOAD ----------
st.sidebar.header("🏢 Upload Company Logo")
logo = st.sidebar.file_uploader("Upload logo (PNG/JPG)", type=["png", "jpg", "jpeg"])

if logo:
    st.image(logo, width=150)

# ---------- FILE UPLOAD ----------
uploaded_file = st.file_uploader("📂 Upload Dataset", type=["csv", "xlsx"])

if uploaded_file:
    # ---------- READ DATA ----------
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # ---------- DATA PREVIEW ----------
    st.subheader("📄 Data Preview")
    st.dataframe(df)

    # ---------- COLUMN DETECTION ----------
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    # ---------- DASHBOARD ----------
    st.subheader("📊 Dashboard")

    col1, col2 = st.columns(2)

    # ---------- NUMERIC CHART ----------
    if len(numeric_cols) > 0:
        with col1:
            num_col = st.selectbox("Select Numeric Column", numeric_cols)
            fig = px.histogram(df, x=num_col, title=f"Distribution of {num_col}")
            st.plotly_chart(fig, use_container_width=True)

    # ---------- CATEGORICAL CHART ----------
    if len(categorical_cols) > 0:
        with col2:
            cat_col = st.selectbox("Select Categorical Column", categorical_cols)
            fig = px.bar(
                df[cat_col].value_counts().reset_index(),
                x='index',
                y=cat_col,
                title=f"{cat_col} Count"
            )
            st.plotly_chart(fig, use_container_width=True)

    # ---------- AI INSIGHTS ----------
    st.subheader("🤖 AI Insights")

    api_key = st.text_input("Enter OpenAI API Key", type="password")

    if st.button("Generate Insights") and api_key:
        client = OpenAI(api_key=api_key)

        sample_data = df.head(20).to_string()

        prompt = f"""
        Analyze this dataset and give business insights:

        {sample_data}

        Provide:
        - Key trends
        - Important observations
        - Business recommendations
        """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        st.write(response.choices[0].message.content)
