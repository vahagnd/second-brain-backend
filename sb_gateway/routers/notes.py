from fastapi import APIRouter, HTTPException, status
from sb_gateway.dependencies.repositories import NoteRepositoryDependency
from sb_gateway.models.note import NoteCreatedResponse, NoteCreate
from sb_gateway.models import NoteCreate

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_note(
    note_create: NoteCreate,
    notes_repo: NoteRepositoryDependency,
    ) -> NoteCreatedResponse:
    """Create a new note in db"""
    notes_repo.add(note_create.content)

    existing_note = False # TODO: Implement check for existing note with same content
    if existing_note:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Note with content '{note_create.content}' already exists")
    
    return NoteCreatedResponse(
        content=note_create.content,
        created=True,
    ) # TODO return the created note with id and created_at fields populated from db


@router.get("", status_code=status.HTTP_200_OK)
def list_notes(notes_repo: NoteRepositoryDependency):
    """List all notes ordered by newest first."""
    return notes_repo.get_all()
