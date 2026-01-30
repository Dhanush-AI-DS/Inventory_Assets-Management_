import streamlit as st
import pandas as pd
from database import get_db
from models import AssetRequest, RequestStatus, ApprovalLog, InventoryItem, UserRole
from utils import send_email_notification
import datetime

st.set_page_config(page_title="Approver Portal", page_icon="🛡️", layout="wide")

def check_auth():
    if "user" not in st.session_state:
        st.warning("Please login first.")
        st.stop()
    user = st.session_state["user"]
    if user["role"] not in [UserRole.APPROVER.value, UserRole.ADMIN.value]:
        st.error("Unauthorized Access")
        st.stop()

check_auth()
user = st.session_state["user"]
st.title("Approver Portal")

db = next(get_db())

st.subheader("Pending Requests")
pending_requests = db.query(AssetRequest).filter(AssetRequest.status == RequestStatus.PENDING).all()

if not pending_requests:
    st.info("No pending requests.")
else:
    for req in pending_requests:
        with st.expander(f"Request #{req.id}: {req.item.manufacturer} {req.item.model} (Qty: {req.qty_requested})"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Requester:** {req.requester.username}")
                st.markdown(f"**Date:** {req.created_at}")
                st.markdown(f"**Purpose:** {req.purpose}")
            with col2:
                st.markdown(f"**Current Stock:** {req.item.qty}")
                
                # prevent approval if stock insufficient (double check)
                if req.item.qty < req.qty_requested:
                    st.error("⚠️ Insufficient Stock to Approve")
                    disable_approve = True
                else:
                    disable_approve = False

            container = st.container()
            with container:
                comments = st.text_input("Comments", key=f"comment_{req.id}")
                c1, c2 = st.columns([1, 1])
                
                if c1.button("✅ Approve", key=f"approve_{req.id}", disabled=disable_approve):
                    # Update Request
                    req.status = RequestStatus.APPROVED
                    # Update Inventory
                    req.item.qty -= req.qty_requested
                    
                    # Log
                    log = ApprovalLog(
                        request_id=req.id,
                        approver_id=user["id"],
                        decision="APPROVED",
                        comments=comments,
                        timestamp=datetime.datetime.utcnow()
                    )
                    db.add(log)
                    db.commit()
                    
                    st.success("Request Approved")
                    send_email_notification(req.requester.email or "user@example.com", "Request Approved", f"Your request for {req.item.model} has been approved.")
                    st.rerun()

                if c2.button("❌ Reject", key=f"reject_{req.id}"):
                    req.status = RequestStatus.REJECTED
                    
                    log = ApprovalLog(
                        request_id=req.id,
                        approver_id=user["id"],
                        decision="REJECTED",
                        comments=comments,
                        timestamp=datetime.datetime.utcnow()
                    )
                    db.add(log)
                    db.commit()
                    
                    st.error("Request Rejected")
                    send_email_notification(req.requester.email or "user@example.com", "Request Rejected", f"Your request for {req.item.model} has been rejected.")
                    st.rerun()

st.divider()
st.subheader("Approval History")
# Show logs where this user was the approver
history = db.query(ApprovalLog).filter(ApprovalLog.approver_id == user["id"]).order_by(ApprovalLog.timestamp.desc()).limit(50).all()

if history:
    hist_data = [{
        "Date": h.timestamp,
        "Request ID": h.request_id,
        "Decision": h.decision,
        "Comments": h.comments
    } for h in history]
    st.dataframe(pd.DataFrame(hist_data), use_container_width=True)

db.close()
