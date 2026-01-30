from database import init_db, SessionLocal
from auth import seed_users
from utils import ingest_inventory_excel
import os

def main():
    print("Initializing Database...")
    init_db()
    
    db = SessionLocal()
    try:
        print("Seeding Users...")
        seed_users(db)
        
        excel_path = "Inventory_dataset.xlsx"
        if os.path.exists(excel_path):
            print(f"Ingesting Initial Inventory from {excel_path}...")
            success, msg = ingest_inventory_excel(db, excel_path)
            print(msg)
        else:
            print("No initial inventory file found.")
            
    finally:
        db.close()
    print("Initialization Complete.")

if __name__ == "__main__":
    main()
