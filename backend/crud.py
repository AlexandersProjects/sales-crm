"""
CRUD operations
"""
from typing import List, Optional
from sqlalchemy.orm import Session
import models
import schemas


def get_tenant(db: Session, tenant_id: int) -> Optional[models.Tenant]:
    return db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()


def get_tenants(db: Session, skip: int = 0, limit: int = 100) -> List[models.Tenant]:
    return db.query(models.Tenant).offset(skip).limit(limit).all()


def create_tenant(db: Session, tenant: schemas.TenantCreate) -> models.Tenant:
    db_tenant = models.Tenant(name=tenant.name)
    db.add(db_tenant)
    db.commit()
    db.refresh(db_tenant)
    return db_tenant


def get_lead(db: Session, lead_id: int) -> Optional[models.Lead]:
    return db.query(models.Lead).filter(models.Lead.id == lead_id).first()


def get_leads(db: Session, skip: int = 0, limit: int = 100, tenant_id: Optional[int] = None) -> List[models.Lead]:
    query = db.query(models.Lead)
    if tenant_id:
        query = query.filter(models.Lead.tenant_id == tenant_id)
    return query.offset(skip).limit(limit).all()


def create_lead(db: Session, lead: schemas.LeadCreate) -> models.Lead:
    db_lead = models.Lead(**lead.model_dump())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


def update_lead(db: Session, lead_id: int, lead_update: schemas.LeadUpdate) -> Optional[models.Lead]:
    db_lead = get_lead(db, lead_id)
    if not db_lead:
        return None
    for field, value in lead_update.model_dump(exclude_unset=True).items():
        setattr(db_lead, field, value)
    db.commit()
    db.refresh(db_lead)
    return db_lead


def delete_lead(db: Session, lead_id: int) -> bool:
    db_lead = get_lead(db, lead_id)
    if not db_lead:
        return False
    db.delete(db_lead)
    db.commit()
    return True

