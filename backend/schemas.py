"""
Pydantic schemas for validation
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class TenantBase(BaseModel):
    name: str


class TenantCreate(TenantBase):
    pass


class Tenant(TenantBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LeadBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    status: str = "new"
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    tenant_id: int


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class Lead(LeadBase):
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmailGenerationRequest(BaseModel):
    lead_name: str
    company: Optional[str] = None
    tone: str = "professional"


class EmailGenerationResponse(BaseModel):
    subject: str
    body: str

