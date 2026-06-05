from sqlmodel import create_engine, Session, SQLModel
from app.core.config import settings

engine = create_engine(settings.get_database_url, echo=True)

def init_db():
    from app.models.models import User, Organization, OrgMember, Project, FileRecord
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
