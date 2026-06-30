import streamlit as st
from streamlit_gsheets import GSheetsConnection
from fpdf import FPDF
import pandas as pd
import urllib.parse
from datetime import datetime

# --- CONFIG & CONNECTION ---
st.set_page_config(page_title="Factory Batch Tracker", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCTIONS ---
def generate_pdf(batch_id, process, operator, tasks, remarks):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Daily Process Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.cell(200, 10, txt=f"Batch ID: {batch_id}", ln=True)
    pdf.cell(200, 10, txt=f"Process: {process}", ln=True)
    pdf.cell(200, 10, txt=f"Operator: {operator}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Tasks Completed:", ln=True)
    pdf.set_font("Arial", size=12)
    for t in tasks:
        pdf.cell(200, 10, txt=f"- {t}", ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt=f"Remarks: {remarks}")
    return pdf.output(dest='S').encode('latin-1')

def generate_whatsapp_link(batch_id, process, tasks, remarks):
    task_list = "\n- ".join(tasks)
    text = f"*FACTORY REPORT*\n\n*Batch:* {batch_id}\n*Process:* {process}\n*Status:* Completed ✅\n*Tasks:*\n- {task_list}\n*Notes:* {remarks}"
    encoded_text = urllib.parse.quote(text)
    return f"https://wa.me/?text={encoded_text}"

# --- UI ---
st.title("🏭 Batch Workflow & Reporting")

# 1. Batch & Process Selection
col1, col2 = st.columns(2)
with col1:
    batch_id = st.text_input("Enter/Scan Batch ID", placeholder="e.g. BATCH-2023-001")
with col2:
    process = st.selectbox("Current Process", ["Molding", "Assembly", "CNC Machining", "QC", "Packaging"])

operator = st.text_input("Operator Name")

# 2. Dynamic Task List (Modify based on process)
st.subheader(f"Tasks for {process}")
tasks_to_show = ["Check machine oil", "Initial safety check", "Calibrate sensors", "Record temperature"] # Example
selected_tasks = []
for t in tasks_to_show:
    if st.checkbox(t):
        selected_tasks.append(t)

remarks = st.text_area("Maintenance Remarks / Observations")

# 3. Submission & Export
if st.button("Submit & Generate Report"):
    if not batch_id or not operator:
        st.error("Please fill in Batch ID and Operator Name")
    else:
        # Save to Google Sheets logic here
        # conn.update(...) 

        st.success(f"Batch {batch_id} updated successfully!")
        
        # Create Two Columns for Sharing
        share_col1, share_col2 = st.columns(2)
        
        with share_col1:
            # PDF Generation
            pdf_data = generate_pdf(batch_id, process, operator, selected_tasks, remarks)
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_data,
                file_name=f"Report_{batch_id}.pdf",
                mime="application/pdf"
            )
            
        with share_col2:
            # WhatsApp Generation
            wa_link = generate_whatsapp_link(batch_id, process, selected_tasks, remarks)
            st.markdown(f'''
                <a href="{wa_link}" target="_blank">
                    <button style="background-color: #25D366; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">
                        Share via WhatsApp
                    </button>
                </a>
            ''', unsafe_allow_html=True)
