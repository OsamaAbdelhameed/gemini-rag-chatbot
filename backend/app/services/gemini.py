import google.generativeai as genai
from typing import List, Optional
import os

def upload_to_gemini(api_key: str, file_path: str, mime_type: Optional[str] = None):
    genai.configure(api_key=api_key)
    file = genai.upload_file(file_path, mime_type=mime_type)
    return file

def query_gemini_with_files(api_key: str, prompt: str, file_ids: List[str]):
    genai.configure(api_key=api_key)
    
    # Retrieve file objects
    files = [genai.get_file(name=fid) for fid in file_ids]
    
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    
    # Combine files and prompt
    content = []
    for f in files:
        content.append(f)
    content.append(prompt)
    
    response = model.generate_content(content)
    return response.text

def delete_gemini_file(api_key: str, file_id: str):
    genai.configure(api_key=api_key)
    genai.delete_file(file_id)
