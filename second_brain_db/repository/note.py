from sqlalchemy.orm import Session
from sqlalchemy import select
from second_brain_db.db.models import Note


class NoteRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, content: str) -> Note:
        note = Note(content=content)
        self.session.add(note)
        self.session.commit()
        self.session.refresh(note)
        return note

    def get_all(self) -> list[Note]:
        stmt = select(Note).order_by(Note.created_at.desc())
        result = self.session.execute(stmt)
        return result.scalars().all()

    def search(self, query: str) -> list[Note]:
        stmt = (
            select(Note)
            .where(Note.content.ilike(f"%{query}%"))
            .order_by(Note.created_at.desc())
            .limit(10)
        )
        result = self.session.execute(stmt)
        return result.scalars().all()
