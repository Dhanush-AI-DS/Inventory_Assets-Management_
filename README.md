# 📦 Inventory Assets Management

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B)

A streamlined, role-based application for managing organizational assets. This system facilitates efficient inventory tracking, request management, and approval workflows.

---

## 🚀 Key Features

### 👤 User Roles & Portals

- **Requester Portal**:
  - Browse available inventory in real-time.
  - Submit asset requests with justification.
  - Track personal request history and status.
  - **Dynamic Notifications**: Automatically notifies approvers via email with detailed HTML templates.
- **Approver Dashboard** :
  - Review pending requests.
  - Approve or reject with comments.
- **Admin Console**:
  - **Bulk Upload**: Ingest inventory data via Excel (`.xlsx`).
  - **Audit Logs**: Track all system activities for security and compliance.

### 🛠 System Capabilities

- **Authentication**: Secure login with role-based access control (RBAC).
- **Email Integration**: Automated HTML emails sent via Gmail SMTP.
- **Data persistence**: Lightweight SQLite database for easy deployment.

---

## 🏗️ Architecture

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: Python
- **Database**: SQLite (SQLAlchemy ORM)
- **Utilities**: Pandas for data processing, smtplib for emails.

### 📂 Directory Structure

```plaintext
Inventory_Assets Management/

├── app.py                 # Main entry point (Login & Routing)
├── pages/                 # Role-specific portals
│   ├── 1_Requester_Portal.py
│   ├── 2_Approver_Dashboard.py
│   ├── 3_Admin_Console.py
├── data/
│   └── inventory.db       # SQLite Database
├── database.py            # DB Connection & Session
├── models.py              # SQLAlchemy Data Models
├── utils.py               # Helper functions (Email, Excel Ingest)
├── .env                   # Environment Variables
└── requirements.txt       # Dependencies
```

---

## ⚙️ Setup & Installation

### 1. Prerequisities

- Python 3.8 or higher installed.

### 2. Installation

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd Inventory_Assets Management
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the root directory with your credentials:

```env
DATABASE_URL=sqlite:///./data/inventory.db
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

> **Note**: For Gmail, use an [App Password](https://myaccount.google.com/apppasswords), not your login password.

### 4. Run the Application

Start the Streamlit server:

```bash
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

---

## Login Credintials
<img width="604" height="228" alt="image" src="https://github.com/user-attachments/assets/0d9a592e-2aa9-40ba-87c9-e1fd1938b3a1" />

---

## 🧪 Usage Guide

1. **Login**: Use your assigned credentials.
2. **Requester**: Go to "Requester Portal", select an item, enter quantity, and click submit.
3. **Admin**: Use "Admin Console" to upload new inventory lists via Excel.

---

## 📄 License

This project is for internal use. All rights reserved.
