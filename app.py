import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="AI Dashboard Generator", layout="wide")

# ---------- SIDEBAR ----------
st.sidebar.header("🏢 Upload Company Logo")
logo = st.sidebar.file_uploader("Upload logo (PNG/JPG)", type=["png", "jpg", "jpeg"])

# ---------- FILE UPLOAD ----------
uploaded_file = st.file_uploader("📂 Upload Dataset", type=["csv", "xlsx"])

if uploaded_file:

    # ---------- READ DATA ----------
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # ---------- HEADER WITH LOGO ----------
    if logo:
        col1, col2 = st.columns([1, 5])
        with col1:
            st.image(logo, width=120)
        with col2:
            st.title("📊 AI Dashboard Generator")
    else:
        st.title("📊 AI Dashboard Generator")

    st.markdown("---")

    # ---------- COLUMN TYPES ----------
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    # ---------- FILTER ----------
    st.sidebar.header("🔍 Filters")
    filter_col = st.sidebar.selectbox("Select Column to Filter", df.columns)

    if df[filter_col].dtype == 'object':
        selected_value = st.sidebar.selectbox("Select Value", df[filter_col].unique())
        df = df[df[filter_col] == selected_value]

    # ---------- KPI CARDS ----------
    st.subheader("📌 Key Metrics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Rows", df.shape[0])

    with col2:
        st.metric("Total Columns", df.shape[1])

    with col3:
        if len(numeric_cols) > 0:
            st.metric("Average Value", round(df[numeric_cols[0]].mean(), 2))

    st.markdown("---")

    # ---------- DATA PREVIEW ----------
    st.subheader("📄 Data Preview")
    st.dataframe(df)

    st.markdown("---")

    # ---------- CHARTS ----------
    st.subheader("📊 Visualizations")

    col1, col2 = st.columns(2)

    # ---------- NUMERIC CHART ----------
    if len(numeric_cols) > 0:
        with col1:
            num_col = st.selectbox("Select Numeric Column", numeric_cols)
            fig = px.histogram(df, x=num_col, title=f"Distribution of {num_col}")
            st.plotly_chart(fig, use_container_width=True)

    # ---------- CATEGORICAL CHART (FIXED ERROR) ----------
    if len(categorical_cols) > 0:
        with col2:
            cat_col = st.selectbox("Select Categorical Column", categorical_cols)

            cat_counts = df[cat_col].value_counts().reset_index()
            cat_counts.columns = [cat_col, "Count"]

            fig = px.bar(
                cat_counts,
                x=cat_col,
                y="Count",
                title=f"{cat_col} Count"
            )

            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ---------- AI INSIGHTS ----------
    st.subheader("🤖 AI Insights")

    api_key = st.text_input("Enter OpenAI API Key", type="password")

    if st.button("Generate Insights") and api_key:
        client = OpenAI(api_key=api_key)

        sample_data = df.head(20).to_string()

        prompt = f"""
        Analyze this dataset and provide:

        - Key trends
        - Important observations
        - Business recommendations

        Data:
        {sample_data}
        """

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        st.write(response.choices[0].message.content)
