# MySQL CURD Repository
from sqlalchemy.orm import Session
from models import document

def create_pdf(db: Session, uuid: str, name: str):
    db_pdf = document.PdfFile(uuid=uuid, name=name)
    db.add(db_pdf)
    db.commit()
    db.refresh(db_pdf)
    return db_pdf
