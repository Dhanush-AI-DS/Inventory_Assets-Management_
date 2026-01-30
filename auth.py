import bcrypt
from sqlalchemy.orm import Session
from models import User, UserRole

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_user(db: Session, username: str, password: str, email: str, role: UserRole):
    hashed_pw = hash_password(password)
    user = User(username=username, password_hash=hashed_pw, email=email, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if user and verify_password(password, user.password_hash):
        return user
    return None

def seed_users(db: Session):
    # Check if admin exists
    admin = get_user_by_username(db, "admin")
    if not admin:
        create_user(db, "admin", "admin123", "admin@example.com", UserRole.ADMIN)
        print("Admin user created: admin/admin123")
    
    # Check if header exists (Approver)
    approver = get_user_by_username(db, "manager")
    if not approver:
        create_user(db, "manager", "manager123", "manager@example.com", UserRole.APPROVER)
        print("Approver user created: manager/manager123")

    # Check if user exists (Requester)
    requester = get_user_by_username(db, "user")
    if not requester:
        create_user(db, "user", "user123", "user@example.com", UserRole.REQUESTER)
        print("Requester user created: user/user123")
