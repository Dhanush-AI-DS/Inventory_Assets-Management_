import streamlit as st
from database import get_db
from auth import authenticate_user
import time

st.set_page_config(page_title="Inventory Assets Management", page_icon="📦", layout="wide")

def login_page():
    st.title("📦 Inventory Assets Management")
    st.header("Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            db = next(get_db())
            user = authenticate_user(db, username, password)
            if user:
                st.session_state["user"] = {"id": user.id, "username": user.username, "role": user.role.value}
                st.success(f"Welcome {user.username}!")
                st.rerun()
            else:
                st.error("Invalid credentials")

def main():
    if "user" not in st.session_state:
        login_page()
    else:
        user = st.session_state["user"]
        st.sidebar.title(f"User: {user['username']}")
        st.sidebar.text(f"Role: {user['role']}")
        
        if st.sidebar.button("Logout"):
            del st.session_state["user"]
            st.rerun()
        
        st.title("Dashboard")
        st.write(f"Hello **{user['username']}**! You are logged in as **{user['role']}**.")
        st.info("Please select a page from the sidebar to continue.")

        # Role based access hints (actual enforcement in pages)
        if user["role"] == "REQUESTER":
            st.write("Go to **Requester Portal** to view inventory and make requests.")
        elif user["role"] == "APPROVER":
            st.write("Go to **Approver Portal** to manage pending requests.")
        elif user["role"] == "ADMIN":
            st.write("Go to **Admin Console** to manage system data.")

if __name__ == "__main__":
    main()
