from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from app.database import Base

# 1. Πίνακας Αποθήκης (Inventory)
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    sku = Column(String, unique=True, index=True, nullable=False)
    stock_quantity = Column(Integer, default=0)
    unit_price = Column(Float, nullable=False)
    expiration_date = Column(String, nullable=True) # Ημερομηνία λήξης (π.χ. YYYY-MM-DD)

# 2. Πίνακας Οικονομικών / Τιμολογίων (Invoices)
class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="PAID") # PAID, PENDING, CANCELLED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# 3. Πίνακας HR / Αδειών (Leave Requests)
class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_name = Column(String, nullable=False)
    days_requested = Column(Integer, nullable=False)
    reason = Column(String, nullable=True)
    status = Column(String, default="PENDING") # PENDING, APPROVED, REJECTED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))