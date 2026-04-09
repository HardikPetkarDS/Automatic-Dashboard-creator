import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="AI Dashboard", layout="wide")

# ---------- LOAD ----------
st.sidebar.header("🏢 Upload Logo")
logo = st.sidebar.file_uploader("Upload Logo", type=["png","jpg"])

file = st.file_uploader("Upload Dataset", type=["csv","xlsx"])

if file:

    df = pd.read_csv(file) if file.name.endswith("csv") else pd.read_excel(file)

    numeric_cols = df.select_dtypes(include=['int64','float64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    # ---------- HEADER ----------
    if logo:
        c1,c2 = st.columns([1,5])
        c1.image(logo,width=100)
        c2.title("📊 AI Smart Dashboard")
    else:
        st.title("📊 AI Smart Dashboard")

    st.markdown("---")

    # ---------- AUTO KPI DETECTION ----------
    st.subheader("🎯 Business KPIs")

    kpis = {}

    for col in numeric_cols:
        if "revenue" in col.lower() or "sales" in col.lower():
            kpis["Revenue"] = df[col].sum()
        elif "profit" in col.lower():
            kpis["Profit"] = df[col].sum()
        elif "cost" in col.lower():
            kpis["Cost"] = df[col].sum()

    col1,col2,col3 = st.columns(3)

    i=0
    for key,val in kpis.items():
        if i==0: col1.metric(key, round(val,2))
        elif i==1: col2.metric(key, round(val,2))
        elif i==2: col3.metric(key, round(val,2))
        i+=1

    st.markdown("---")

    # ---------- AUTO CHART RECOMMENDATION ----------
    st.subheader("📊 Auto Charts")

    if len(numeric_cols)>0:
        st.plotly_chart(px.histogram(df, x=numeric_cols[0], title="Distribution"))

    if len(categorical_cols)>0:
        cat = categorical_cols[0]
        counts = df[cat].value_counts().reset_index()
        counts.columns=[cat,"Count"]
        st.plotly_chart(px.bar(counts,x=cat,y="Count",title="Category Count"))

    if len(numeric_cols)>1:
        st.plotly_chart(px.scatter(df,x=numeric_cols[0],y=numeric_cols[1],title="Correlation"))

    if len(categorical_cols)>0:
        st.plotly_chart(px.pie(df,names=categorical_cols[0],title="Share"))

    st.markdown("---")

    # ---------- AUTO INSIGHTS ----------
    st.subheader("📈 Smart Insights")

    insights_text = ""

    if len(numeric_cols)>0:
        col = numeric_cols[0]
        insights_text += f"Average {col}: {df[col].mean():.2f}\n"
        insights_text += f"Max {col}: {df[col].max()}\n"

    if len(categorical_cols)>0:
        top = df[categorical_cols[0]].value_counts().idxmax()
        insights_text += f"Top category: {top}\n"

    st.text(insights_text)

    st.markdown("---")

    # ---------- CHAT WITH DATA ----------
    st.subheader("💬 Chat with your Data")

    api_key = st.text_input("Enter OpenAI API Key", type="password")

    user_q = st.text_input("Ask anything about your data")

    if st.button("Ask AI") and api_key:
        client = OpenAI(api_key=api_key)

        sample = df.head(20).to_string()

        prompt = f"""
        Dataset:
        {sample}

        Question:
        {user_q}
        """

        res = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role":"user","content":prompt}]
        )

        st.write(res.choices[0].message.content)

    st.markdown("---")

    # ---------- PDF EXPORT ----------
    st.subheader("📄 Export Report")

    if st.button("Generate PDF"):
        doc = SimpleDocTemplate("report.pdf")
        styles = getSampleStyleSheet()

        content = []
        content.append(Paragraph("AI Dashboard Report", styles['Title']))
        content.append(Paragraph(insights_text, styles['Normal']))

        doc.build(content)

        with open("report.pdf", "rb") as f:
            st.download_button("Download Report", f, "report.pdf")
