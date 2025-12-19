# MySQL CRUD Repository
from sqlalchemy.orm import Session

from app.models.document import DocumentFile

def create_document(
    db: Session,
    uuid: str,
    name: str,
    summary: str,
    keywords: str | None = None,
):
    document = DocumentFile(
        uuid=uuid,
        name=name,
        summary=summary,
        keywords=keywords,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

# 문서 정보 조회
def get_document_by_id(db: Session, document_id: int):
    return db.query(DocumentFile).filter(DocumentFile.id == document_id).first()

def list_documents(db: Session, limit: int = 10, offset: int = 0):
    return (
        db.query(DocumentFile)
        .order_by(DocumentFile.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

def get_document_by_uuid(db: Session, uuid: str):
    return (
        db.query(DocumentFile)
        .filter(DocumentFile.uuid == uuid)
        .first()
    )