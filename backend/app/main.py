from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import init_db
from app.api import auth, orgs, projects, chat

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(orgs.router, prefix=f"{settings.API_V1_STR}/orgs", tags=["orgs"])
app.include_router(projects.router, prefix=f"{settings.API_V1_STR}/projects", tags=["projects"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])

@app.on_event("startup")
def on_startup():
    # init_db() # This will fail if Postgres is not running, so we'll wrap it or run manually
    try:
        init_db()
    except Exception as e:
        print(f"Error initializing DB: {e}")

@app.get("/")
def root():
    return {"message": "Gemini RAG Chatbot API is running"}
