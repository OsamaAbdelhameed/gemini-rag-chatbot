from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select
from typing import List
import os
import shutil
from app.db.session import get_session
from app.models.models import Project, FileRecord, User, OrgMember
from app.api.deps import get_current_user
from app.core.encryption import decrypt_gemini_key
from app.services.gemini import upload_to_gemini, query_gemini_with_files
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    prompt: str
    secret: str  # User-provided secret for decryption

@router.post("/{project_id}/upload")
async def upload_file(
    project_id: int,
    secret: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Check permissions
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user is in org
    member = db.exec(
        select(OrgMember)
        .where(OrgMember.user_id == current_user.id)
        .where(OrgMember.org_id == project.org_id)
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Decrypt API Key
    api_key = decrypt_gemini_key(project.gemini_api_key_encrypted, secret)
    if not api_key:
        raise HTTPException(status_code=400, detail="Invalid secret or corrupted API key")
    
    # Save file temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        gemini_file = upload_to_gemini(api_key, temp_path, mime_type=file.content_type)
        
        # Save to DB
        file_record = FileRecord(
            project_id=project_id,
            filename=file.filename,
            gemini_file_id=gemini_file.name,
            mime_type=file.content_type or "application/octet-stream"
        )
        db.add(file_record)
        db.commit()
        db.refresh(file_record)
        return file_record
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/{project_id}/query")
async def chat_query(
    project_id: int,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Decrypt API Key
    api_key = decrypt_gemini_key(project.gemini_api_key_encrypted, request.secret)
    if not api_key:
        raise HTTPException(status_code=400, detail="Invalid secret or corrupted API key")
    
    # Get all files for this project
    files = db.exec(select(FileRecord).where(FileRecord.project_id == project_id)).all()
    file_ids = [f.gemini_file_id for f in files]
    
    if not file_ids:
        # Simple chat if no files
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(request.prompt)
        return {"response": response.text}
    
    try:
        response_text = query_gemini_with_files(api_key, request.prompt, file_ids)
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
