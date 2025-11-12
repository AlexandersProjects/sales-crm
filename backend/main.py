"""
FastAPI Sales CRM - Minimal MVP
"""
import os
import json
from typing import List, Optional
from pathlib import Path
import tomllib
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import openai

import crud
import models
import schemas
from database import engine, get_db

# Read version from pyproject.toml
def get_version() -> str:
    """Read version from pyproject.toml"""
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
            return pyproject_data["tool"]["poetry"]["version"]
    except Exception:
        return "0.1.0"  # Fallback version

VERSION = get_version()

# Create tables
models.Base.metadata.create_all(bind=engine)

# Initialize app
app = FastAPI(title="Sales CRM API", version=VERSION)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY


@app.get("/")
async def root():
    return {"message": "Sales CRM API", "version": VERSION, "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "healthy", "version": VERSION}


# Tenants
@app.post("/api/tenants", response_model=schemas.Tenant, status_code=201)
async def create_tenant(tenant: schemas.TenantCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_tenant(db, tenant)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/tenants", response_model=List[schemas.Tenant])
async def list_tenants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_tenants(db, skip=skip, limit=limit)


@app.get("/api/tenants/{tenant_id}", response_model=schemas.Tenant)
async def get_tenant(tenant_id: int, db: Session = Depends(get_db)):
    tenant = crud.get_tenant(db, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


# Leads
@app.post("/api/leads", response_model=schemas.Lead, status_code=201)
async def create_lead(lead: schemas.LeadCreate, db: Session = Depends(get_db)):
    if not crud.get_tenant(db, lead.tenant_id):
        raise HTTPException(status_code=404, detail="Tenant not found")
    return crud.create_lead(db, lead)


@app.get("/api/leads", response_model=List[schemas.Lead])
async def list_leads(
    skip: int = 0,
    limit: int = 100,
    tenant_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    return crud.get_leads(db, skip=skip, limit=limit, tenant_id=tenant_id)


@app.get("/api/leads/{lead_id}", response_model=schemas.Lead)
async def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = crud.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@app.put("/api/leads/{lead_id}", response_model=schemas.Lead)
async def update_lead(lead_id: int, lead_update: schemas.LeadUpdate, db: Session = Depends(get_db)):
    lead = crud.update_lead(db, lead_id, lead_update)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@app.delete("/api/leads/{lead_id}", status_code=204)
async def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    if not crud.delete_lead(db, lead_id):
        raise HTTPException(status_code=404, detail="Lead not found")


# AI Email Generation
@app.post("/api/ai/generate-email", response_model=schemas.EmailGenerationResponse)
async def generate_email(request: schemas.EmailGenerationRequest):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=503, detail="OpenAI API key not configured")

    try:
        company_info = f" at {request.company}" if request.company else ""
        prompt = f"Generate a {request.tone} email for {request.lead_name}{company_info} introducing our CRM solution. Return JSON with 'subject' and 'body' fields."

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a sales email writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )

        content = response.choices[0].message.content
        try:
            email_data = json.loads(content)
            return schemas.EmailGenerationResponse(**email_data)
        except json.JSONDecodeError:
            return schemas.EmailGenerationResponse(
                subject=f"Connecting with {request.lead_name}",
                body=content
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate email: {str(e)}")

