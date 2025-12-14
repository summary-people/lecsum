# MySQL CRUD Repository
from sqlalchemy.orm import Session
from app.models.document import PdfFile

def create_pdf(
    db: Session,
    uuid: str,
    name: str,
    summary: str,
    keywords: str | None = None,
):
    pdf = PdfFile(
        uuid=uuid,
        name=name,
        summary=summary,
        keywords=keywords,
    )
    db.add(pdf)
    db.commit()
    db.refresh(pdf)
    return pdf

# PDF 정보 조회 (UUID 찾기용)
def get_pdf_by_id(db: Session, pdf_id: int):
    return db.query(PdfFile).filter(PdfFile.id == pdf_id).first()

def list_documents(db: Session, limit: int = 10, offset: int = 0):
    return (
        db.query(PdfFile)
        .order_by(PdfFile.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

def get_document_by_uuid(db: Session, uuid: str):
    return (
        db.query(PdfFile)
        .filter(PdfFile.uuid == uuid)
        .first()
    )