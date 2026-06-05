from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    is_active: bool = True

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    
    # Relationships
    memberships: List["OrgMember"] = Relationship(back_populates="user")

class OrganizationBase(SQLModel):
    name: str
    slug: str = Field(unique=True, index=True)

class Organization(OrganizationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    
    # Relationships
    members: List["OrgMember"] = Relationship(back_populates="organization")
    projects: List["Project"] = Relationship(back_populates="organization")

class OrgMember(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    org_id: int = Field(foreign_key="organization.id", primary_key=True)
    role: str = "member"  # admin, member
    
    # Relationships
    user: User = Relationship(back_populates="memberships")
    organization: Organization = Relationship(back_populates="members")

class ProjectBase(SQLModel):
    name: str
    project_type: str = "rag_chatbot"

class Project(ProjectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    org_id: int = Field(foreign_key="organization.id")
    gemini_api_key_encrypted: Optional[str] = None  # Encrypted key from frontend
    
    # Relationships
    organization: Organization = Relationship(back_populates="projects")
    files: List["FileRecord"] = Relationship(back_populates="project")

class FileRecordBase(SQLModel):
    filename: str
    gemini_file_id: str
    mime_type: str

class FileRecord(FileRecordBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    project: Project = Relationship(back_populates="files")
