from sqlalchemy import select
from sqlalchemy.orm import Session

from second_brain_db.db.models import Note
from second_brain_db.utils.vector import cosine_similarity


class NoteRepository:
    def __init__(self, session: Session) -> None:
        """Initialize the NoteRepository with a SQLAlchemy session."""
        self.session = session

    def add(self, content: str, embedding: list[float] | None = None) -> Note:
        """Add a new note with the given content and optional embedding."""
        note = Note(content=content, embedding=embedding)
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

    def search_by_embedding(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        threshold: float | None = None,
    ) -> list[(Note, float)]:
        """
        Search for notes by semantic similarity using embeddings.

        Parameters
        ----------
        query_embedding : list[float]
            The embedding vector of the search query.
        top_k : int, optional
            Maximum number of results to return, by default 5.
        threshold : float, optional
            Minimum cosine similarity score to include a note in the results, by default None (no threshold).

        Returns
        -------
        list[(Note, float)]
            List of notes and their similarity scores ranked by cosine similarity (descending).
        """
        all_notes = self.get_all()

        # Filter notes that have embeddings
        notes_with_embeddings = [note for note in all_notes if note.embedding is not None]

        if not notes_with_embeddings:
            return []

        # Compute similarity scores
        similarities = [(note, cosine_similarity(query_embedding, note.embedding)) for note in notes_with_embeddings]

        # Filter by threshold if provided
        if threshold is not None:
            similarities = [item for item in similarities if item[1] >= threshold]

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top N results
        return similarities[:top_k]
