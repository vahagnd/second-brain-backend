from fastapi import APIRouter, HTTPException, status

from sb_gateway.dependencies.repositories import NoteRepositoryDependency
from sb_gateway.models.note import Note, NoteCreate, NoteCreatedResponse

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_note(note_create: NoteCreate, notes_repo: NoteRepositoryDependency) -> NoteCreatedResponse:
    """Create a new note in db."""
    note = notes_repo.add(note_create.content)

    existing_note = False  # TODO: Implement check for existing note with same content, cosine similarity, etc.
    if existing_note:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Note with content '{note_create.content}' already exists"
        )

    return NoteCreatedResponse(id=note.id, content=note_create.content, created=True)


@router.get("", status_code=status.HTTP_200_OK)
def list_notes(notes_repo: NoteRepositoryDependency, search: str | None) -> list[Note]:
    """List all notes ordered by newest first."""
    note_orm = notes_repo.search_by_content(search) if search else notes_repo.get_all()
    note_list = [Note(id=note.id, content=note.content, created_at=note.created_at.isoformat()) for note in note_orm]
    return note_list


@router.get("/{note_id}", status_code=status.HTTP_200_OK)
def get_note(note_id: int, notes_repo: NoteRepositoryDependency) -> Note | None:
    """Get a single note by its ID."""
    note = notes_repo.get_one_or_none(note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return Note(id=note.id, content=note.content, created_at=note.created_at.isoformat())


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, notes_repo: NoteRepositoryDependency) -> None:
    """Delete a note by its ID."""
    deleted = notes_repo.delete(note_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
