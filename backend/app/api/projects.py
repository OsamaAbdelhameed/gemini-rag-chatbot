from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.db.session import get_session
from app.models.models import Project, Organization, OrgMember, User
from app.api.deps import get_current_user
from pydantic import BaseModel

router = APIRouter()

class ProjectCreate(BaseModel):
    name: str
    org_id: int
    project_type: str = "rag_chatbot"
    gemini_api_key_encrypted: str = None

@router.post("/", response_model=Project)
def create_project(project_in: ProjectCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    # Check if user is member of the org
    member = db.exec(
        select(OrgMember)
        .where(OrgMember.user_id == current_user.id)
        .where(OrgMember.org_id == project_in.org_id)
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="You are not a member of this organization")
    
    new_project = Project(
        name=project_in.name,
        org_id=project_in.org_id,
        project_type=project_in.project_type,
        gemini_api_key_encrypted=project_in.gemini_api_key_encrypted
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@router.get("/{org_id}", response_model=List[Project])
def list_projects(org_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    # Check membership
    member = db.exec(
        select(OrgMember)
        .where(OrgMember.user_id == current_user.id)
        .where(OrgMember.org_id == org_id)
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    projects = db.exec(select(Project).where(Project.org_id == org_id)).all()
    return projects
