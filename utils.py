import pandas as pd
from sqlalchemy.orm import Session
from models import InventoryItem, AuditLog
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
from datetime import datetime
import streamlit as st

def ingest_inventory_excel(db: Session, file, user_id=None):
    try:
        df = pd.read_excel(file)
        # Expected columns mapping
        column_map = {
            "Type": "type", "Manufacturer": "manufacturer", "Model ": "model",
            "Description": "description", "Sum-Description": "sum_description",
            "QTY": "qty", "Head Configuration": "head_configuration",
            "Dept": "dept", "Status": "status", "Area": "area",
            "Location": "location", "Site": "site"
        }
        
        added_count = 0
        updated_count = 0
        
        for _, row in df.iterrows():
            # Check for existing item (composite key could be Manufacturer + Model + Serial, but we lack Serial)
            # Assuming Manufacturer + Model is unique-ish for this logic, or just adding all.
            # Plan says "Insert or update". Let's assume Model is key.
            
            model_val = str(row.get("Model ", "")).strip()
            if not model_val or model_val == "nan":
                continue
                
            existing_item = db.query(InventoryItem).filter(InventoryItem.model == model_val).first()
            
            item_data = {
                "type": row.get("Type"),
                "manufacturer": row.get("Manufacturer"),
                "model": model_val,
                "description": row.get("Description"),
                "sum_description": row.get("Sum-Description"),
                "qty": int(row.get("QTY", 0)) if pd.notna(row.get("QTY")) else 0,
                "head_configuration": str(row.get("Head Configuration")) if pd.notna(row.get("Head Configuration")) else None,
                "dept": row.get("Dept"),
                "status": row.get("Status"),
                "area": row.get("Area"),
                "location": row.get("Location"),
                "site": row.get("Site")
            }
            
            if existing_item:
                for key, value in item_data.items():
                    setattr(existing_item, key, value)
                updated_count += 1
            else:
                new_item = InventoryItem(**item_data)
                db.add(new_item)
                added_count += 1
        
        # Log action
        log = AuditLog(
            action="INVENTORY_UPLOAD",
            actor=str(user_id) if user_id else "SYSTEM",
            details=json.dumps({"added": added_count, "updated": updated_count})
        )
        db.add(log)
        db.commit()
        return True, f"Success: Added {added_count}, Updated {updated_count} items."
        
    except Exception as e:
        db.rollback()
        return False, f"Error: {str(e)}"

def generate_email_body(requester_name, item_details, qty_requested, purpose):
    """
    Generates an HTML email body for an asset request.
    """
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ width: 80%; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9; }}
            .header {{ background-color: #4CAF50; color: white; padding: 10px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ padding: 20px; }}
            .footer {{ margin-top: 20px; font-size: 0.8em; text-align: center; color: #777; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Asset Request Notification</h2>
            </div>
            <div class="content">
                <p>Dear Approver,</p>
                <p>A new asset request has been submitted by <strong>{requester_name}</strong>. Please review the details below:</p>
                
                <table>
                    <tr>
                        <th>Request Date</th>
                        <td>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                    </tr>
                    <tr>
                        <th>Requester</th>
                        <td>{requester_name}</td>
                    </tr>
                    <tr>
                        <th>Item Requested</th>
                        <td>{item_details}</td>
                    </tr>
                    <tr>
                        <th>Quantity Needed</th>
                        <td>{qty_requested}</td>
                    </tr>
                    <tr>
                        <th>Purpose / Justification</th>
                        <td>{purpose}</td>
                    </tr>
                </table>
                
                <p>Please log in to the Inventory Management System to approve or reject this request.</p>
            </div>
            <div class="footer">
                <p>This is an automated message from the Inventory Assets Management System.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def send_email_notification(to_email: str, subject: str, body: str, is_html: bool = False):
    # Helper to get config from secrets or env
    def get_config(key, default=None):
        if key in st.secrets:
            return st.secrets[key]
        return os.getenv(key, default)

    smtp_server = get_config("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(get_config("SMTP_PORT", 587))
    sender_email = get_config("SMTP_EMAIL")
    sender_password = get_config("SMTP_PASSWORD")
    
    if not sender_email or sender_email == "dummy@example.com":
        print(f"[MOCK EMAIL] To: {to_email} | Subject: {subject} | Body: (HTML Content omitted in logs)" if is_html else f"[MOCK EMAIL] To: {to_email} | Subject: {subject} | Body: {body}")
        if is_html:
             # Print a snippet for verification
             print(f"[MOCK EMAIL PREVIEW] {body[:200]}...")
        return True

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg_type = 'html' if is_html else 'plain'
        msg.attach(MIMEText(body, msg_type))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
