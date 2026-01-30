import streamlit as st
import pandas as pd
from database import get_db
from models import InventoryItem, AssetRequest, RequestStatus
from utils import send_email_notification
import time

st.set_page_config(page_title="Requester Portal", page_icon="📝", layout="wide")

def check_auth():
    if "user" not in st.session_state:
        st.warning("Please login first.")
        st.stop()

check_auth()
user = st.session_state["user"]

st.title("Requester Portal")

tab1, tab2 = st.tabs(["📢 Make a Request", "📜 My Requests"])

db = next(get_db())

with tab1:
    st.subheader("Available Inventory")
    
    # Fetch inventory
    items = db.query(InventoryItem).filter(InventoryItem.qty > 0).all()
    
    if not items:
        st.info("No items currently available in inventory.")
    else:
        # Create a dataframe for display
        data = [{
            "ID": i.id,
            "Type": i.type,
            "Manufacturer": i.manufacturer,
            "Model": i.model,
            "Description": i.description,
            "Available Qty": i.qty,
            "Location": i.location
        } for i in items]
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
        st.divider()
        st.subheader("Submit Request")
        
        with st.form("request_form"):
            # Select Item
            item_options = {f"{i.id} - {i.manufacturer} {i.model} ({i.description})": i.id for i in items}
            selected_label = st.selectbox("Select Item", options=list(item_options.keys()))
            selected_item_id = item_options[selected_label]
            
            qty_needed = st.number_input("Quantity Needed", min_value=1, value=1, step=1)
            purpose = st.text_area("Purpose / Justification")
            approver_email = st.text_input("Approver Email", help="Enter the email address of the person who should approve this request.")
            
            submitted = st.form_submit_button("Submit Request")
            
            if submitted:
                # Validation
                if not approver_email:
                    st.error("Please provide an approver email.")
                elif not "@" in approver_email: # Basic validation
                    st.error("Please provide a valid email address.")
                else:
                    item = db.query(InventoryItem).get(selected_item_id)
                    if qty_needed > item.qty:
                        st.error(f"Error: Requested quantity ({qty_needed}) exceeds available stock ({item.qty}).")
                    else:
                        new_request = AssetRequest(
                            user_id=user["id"],
                            item_id=selected_item_id,
                            qty_requested=qty_needed,
                            purpose=purpose,
                            status=RequestStatus.PENDING
                        )
                        db.add(new_request)
                        db.commit()
                        
                        st.success("Request submitted successfully!")
                        
                        # Notify Approvers
                        from utils import generate_email_body
                        
                        email_body = generate_email_body(
                            requester_name=user['username'],
                            item_details=f"{item.manufacturer} {item.model} ({item.description})",
                            qty_requested=qty_needed,
                            purpose=purpose
                        )
                        
                        send_email_notification(
                            approver_email,
                            "New Asset Request",
                            email_body,
                            is_html=True
                        )
                        time.sleep(1)
                        st.rerun()

with tab2:
    st.subheader("My Request History")
    my_requests = db.query(AssetRequest).filter(AssetRequest.user_id == user["id"]).order_by(AssetRequest.created_at.desc()).all()
    
    if my_requests:
        req_data = [{
            "ID": r.id,
            "Item": f"{r.item.manufacturer} {r.item.model}",
            "Qty": r.qty_requested,
            "Status": r.status.value,
            "Date": r.created_at
        } for r in my_requests]
        
        st.dataframe(pd.DataFrame(req_data), use_container_width=True)
    else:
        st.info("No requests found.")

db.close()
