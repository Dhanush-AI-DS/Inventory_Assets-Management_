import streamlit as st
import pandas as pd
from database import get_db
from models import AuditLog, UserRole
from utils import ingest_inventory_excel

st.set_page_config(page_title="Admin Console", page_icon="⚙️", layout="wide")

def check_auth():
    if "user" not in st.session_state:
        st.warning("Please login first.")
        st.stop()
    user = st.session_state["user"]
    if user["role"] != UserRole.ADMIN.value:
        st.error("Unauthorized Access")
        st.stop()

check_auth()
user = st.session_state["user"]
st.title("Admin Console")

tab1, tab2 = st.tabs(["📤 Upload Inventory", "📜 Audit Logs"])

db = next(get_db())

with tab1:
    st.subheader("Update Inventory Data")
    st.write("Upload an Excel file to bulk update inventory. Matches on 'Model'.")
    
    uploaded_file = st.file_uploader("Choose Excel File", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        if st.button("Process File"):
            with st.spinner("Ingesting data..."):
                success, msg = ingest_inventory_excel(db, uploaded_file, user_id=user["id"])
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

with tab2:
    st.subheader("System Access & Action Logs")
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()
    
    if logs:
        log_data = [{
            "ID": l.id,
            "Timestamp": l.timestamp,
            "Action": l.action,
            "Actor": l.actor,
            "Details": l.details
        } for l in logs]
        
        st.dataframe(pd.DataFrame(log_data), use_container_width=True)
    else:
        st.info("No audit logs found.")

db.close()
