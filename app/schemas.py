from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ==========================================
# 1. SCHEMAS ΑΠΟΘΗΚΗΣ (PRODUCTS)
# ==========================================
class ProductBase(BaseModel):
    name: str
    sku: str
    stock_quantity: int
    unit_price: float
    expiration_date: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

    class Config:
        from_attributes = True

# ==========================================
# 2. SCHEMAS ΟΙΚΟΝΟΜΙΚΩΝ (INVOICES)
# ==========================================
class InvoiceBase(BaseModel):
    customer_name: str
    total_amount: float
    status: str = "PAID"

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceResponse(InvoiceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ==========================================
# 3. SCHEMAS HR (LEAVE REQUESTS)
# ==========================================
class LeaveRequestBase(BaseModel):
    employee_name: str
    days_requested: int
    reason: Optional[str] = None

class LeaveRequestCreate(LeaveRequestBase):
    pass

class LeaveRequestResponse(LeaveRequestBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True