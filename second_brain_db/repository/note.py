from sqlalchemy import select
from sqlalchemy.orm import Session

from second_brain_db.db.models import Note


class NoteRepository:
    def __init__(self, session: Session) -> None:
        """Initialize the NoteRepository with a SQLAlchemy session."""
        self.session = session

    def add(self, content: str) -> Note:
        """Add a new note with the given content."""
        note = Note(content=content)
        self.session.add(note)
        self.session.commit()
        self.session.refresh(note)
        return note

    def get_all(self) -> list[Note]:
        """Get all notes."""
        stmt = select(Note).order_by(Note.created_at.desc())
        result = self.session.execute(stmt)
        return result.scalars().all()

    def search(self, query: str) -> list[Note]:
        """Search for notes containing the query string in their content."""
        stmt = select(Note).where(Note.content.ilike(f"%{query}%")).order_by(Note.created_at.desc()).limit(10)
        result = self.session.execute(stmt)
        return result.scalars().all()

    def get_one_or_none(self, note_id: int) -> Note | None:
        """Get a single note by its ID, or return None if it doesn't exist."""
        stmt = select(Note).where(Note.id == note_id)
        result = self.session.execute(stmt)
        return result.scalars().first()

    def delete(self, note_id: int) -> bool:
        """Delete a note by its ID. Returns True if the note was deleted, False if it didn't exist."""
        note = self.get_one_or_none(note_id)
        if not note:
            return False
        self.session.delete(note)
        self.session.commit()
        return True

    def search_by_content(self, query: str) -> list[Note]:
        """Search for notes that have content containing the given query string."""
        stmt = select(Note).where(Note.content.ilike(f"%{query}%")).order_by(Note.created_at.desc())
        result = self.session.execute(stmt)
        return result.scalars().all()
