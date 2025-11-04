from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Org(BaseModel):
    id: str = Field(description="Stable organization identifier (slug or UUID)")
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OrgCreate(BaseModel):
    id: str
    name: str
    description: Optional[str] = None


class OrgUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class OrgMember(BaseModel):
    org_id: str
    user_sub: str = Field(description="OIDC subject (Auth0 sub)")
    roles: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
