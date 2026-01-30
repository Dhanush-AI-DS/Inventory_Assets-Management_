from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    REQUESTER = "REQUESTER"
    APPROVER = "APPROVER"
    ADMIN = "ADMIN"

class RequestStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    email = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.REQUESTER)
    
    requests = relationship("AssetRequest", back_populates="requester")
    approvals = relationship("ApprovalLog", back_populates="approver")

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True)
    type = Column(String)
    manufacturer = Column(String)
    model = Column(String)
    description = Column(String)
    sum_description = Column(String)
    qty = Column(Integer, default=0)
    head_configuration = Column(String, nullable=True)
    dept = Column(String)
    status = Column(String)
    area = Column(String)
    location = Column(String)
    site = Column(String)
    
    requests = relationship("AssetRequest", back_populates="item")

class AssetRequest(Base):
    __tablename__ = "asset_requests"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer, ForeignKey("inventory_items.id"))
    qty_requested = Column(Integer, nullable=False)
    purpose = Column(Text)
    status = Column(Enum(RequestStatus), default=RequestStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    requester = relationship("User", back_populates="requests")
    item = relationship("InventoryItem", back_populates="requests")
    approvals = relationship("ApprovalLog", back_populates="request")

class ApprovalLog(Base):
    __tablename__ = "approval_logs"
    
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey("asset_requests.id"))
    approver_id = Column(Integer, ForeignKey("users.id"))
    decision = Column(String) # APPROVED or REJECTED
    comments = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    request = relationship("AssetRequest", back_populates="approvals")
    approver = relationship("User", back_populates="approvals")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    action = Column(String)
    actor = Column(String) # Username
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(Text) # JSON string
