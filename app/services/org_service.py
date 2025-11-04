from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from app.core.database import db
from app.models.org_model import Org, OrgCreate, OrgMember, OrgUpdate

_orgs = db.orgs
_members = db.org_members


async def list_orgs() -> Dict[str, List[Org] | int]:
    cursor = _orgs.find({}).sort("created_at", -1)
    items = [Org(**doc) async for doc in cursor]
    return {"items": [i.dict() for i in items], "total": len(items)}


async def get_org(org_id: str) -> Optional[Org]:
    doc = await _orgs.find_one({"id": org_id})
    return Org(**doc) if doc else None


async def create_org(payload: OrgCreate) -> Org:
    now = datetime.utcnow()
    org = Org(id=payload.id, name=payload.name, description=payload.description, created_at=now, updated_at=now)
    await _orgs.update_one({"id": org.id}, {"$set": org.dict()}, upsert=True)
    return org


async def update_org(org_id: str, payload: OrgUpdate) -> Optional[Org]:
    updates = {k: v for k, v in payload.dict().items() if v is not None}
    if not updates:
        return await get_org(org_id)
    updates["updated_at"] = datetime.utcnow()
    await _orgs.update_one({"id": org_id}, {"$set": updates})
    return await get_org(org_id)


async def delete_org(org_id: str) -> bool:
    res = await _orgs.delete_one({"id": org_id})
    await _members.delete_many({"org_id": org_id})
    return res.deleted_count > 0


async def list_members(org_id: str) -> List[OrgMember]:
    cursor = _members.find({"org_id": org_id})
    return [OrgMember(**doc) async for doc in cursor]


async def add_member(org_id: str, user_sub: str, roles: Optional[List[str]] = None) -> OrgMember:
    now = datetime.utcnow()
    member = OrgMember(org_id=org_id, user_sub=user_sub, roles=roles or [], created_at=now, updated_at=now)
    await _members.update_one(
        {"org_id": org_id, "user_sub": user_sub}, {"$set": member.dict()}, upsert=True
    )
    return member


async def remove_member(org_id: str, user_sub: str) -> bool:
    res = await _members.delete_one({"org_id": org_id, "user_sub": user_sub})
    return res.deleted_count > 0
