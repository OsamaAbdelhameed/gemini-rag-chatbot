from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.models.models import Organization, OrgMember, User
from app.api.deps import get_current_user
from pydantic import BaseModel

router = APIRouter()

class OrgCreate(BaseModel):
    name: str
    slug: str

class MemberAdd(BaseModel):
    email: str
    role: str = "member"

@router.post("/", response_model=Organization)
def create_org(org_in: OrgCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    # Check if slug exists
    org = db.exec(select(Organization).where(Organization.slug == org_in.slug)).first()
    if org:
        raise HTTPException(status_code=400, detail="Organization with this slug already exists")
    
    new_org = Organization(name=org_in.name, slug=org_in.slug, owner_id=current_user.id)
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    
    # Add creator as admin
    member = OrgMember(user_id=current_user.id, org_id=new_org.id, role="admin")
    db.add(member)
    db.commit()
    
    return new_org

@router.get("/", response_model=List[Organization])
def list_orgs(current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    orgs = db.exec(
        select(Organization)
        .join(OrgMember)
        .where(OrgMember.user_id == current_user.id)
    ).all()
    return orgs

@router.post("/{org_id}/members", response_model=OrgMember)
def add_member(org_id: int, member_in: MemberAdd, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    # Check if current user is admin of the org
    member = db.exec(
        select(OrgMember)
        .where(OrgMember.user_id == current_user.id)
        .where(OrgMember.org_id == org_id)
        .where(OrgMember.role == "admin")
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Only admins can add members")
    
    # Check if user exists
    user = db.exec(select(User).where(User.email == member_in.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already a member
    existing_member = db.exec(
        select(OrgMember)
        .where(OrgMember.user_id == user.id)
        .where(OrgMember.org_id == org_id)
    ).first()
    if existing_member:
        raise HTTPException(status_code=400, detail="User is already a member")
    
    new_member = OrgMember(user_id=user.id, org_id=org_id, role=member_in.role)
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

@router.get("/{org_id}/members", response_model=List[dict])
def list_members(org_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    # Check if member
    member = db.exec(
        select(OrgMember)
        .where(OrgMember.user_id == current_user.id)
        .where(OrgMember.org_id == org_id)
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    results = db.exec(
        select(User.email, User.full_name, OrgMember.role)
        .join(OrgMember)
        .where(OrgMember.org_id == org_id)
    ).all()
    
    return [{"email": r[0], "full_name": r[1], "role": r[2]} for r in results]
