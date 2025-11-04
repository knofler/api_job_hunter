from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, Query, status

from app.api.dependencies import AdminDependency
from app.models.org_model import Org, OrgCreate, OrgMember, OrgUpdate
from app.services import org_service

router = APIRouter(prefix="/api/admin/orgs", tags=["admin-orgs"], dependencies=[AdminDependency])


@router.get("")
async def list_orgs() -> dict:
    return await org_service.list_orgs()


@router.post("")
async def create_org(payload: OrgCreate) -> Org:
    return await org_service.create_org(payload)


@router.get("/{org_id}")
async def get_org(org_id: str = Path(...)) -> Org:
    org = await org_service.get_org(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Org not found")
    return org


@router.put("/{org_id}")
async def update_org(org_id: str, payload: OrgUpdate) -> Org:
    org = await org_service.update_org(org_id, payload)
    if not org:
        raise HTTPException(status_code=404, detail="Org not found")
    return org


@router.delete("/{org_id}")
async def delete_org(org_id: str) -> dict:
    ok = await org_service.delete_org(org_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Org not found")
    return {"deleted": True}


@router.get("/{org_id}/members")
async def list_members(org_id: str) -> List[OrgMember]:
    return await org_service.list_members(org_id)


@router.post("/{org_id}/members")
async def add_member(org_id: str, user_sub: str = Query(...), roles: Optional[List[str]] = Query(default=None)) -> OrgMember:
    return await org_service.add_member(org_id, user_sub, roles)


@router.delete("/{org_id}/members/{user_sub}")
async def remove_member(org_id: str, user_sub: str) -> dict:
    ok = await org_service.remove_member(org_id, user_sub)
    if not ok:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"deleted": True}
