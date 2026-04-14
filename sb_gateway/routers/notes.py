from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query, status

from sb_gateway.dependencies.embedding import EmbeddingServiceDependency
from sb_gateway.dependencies.repositories import NoteRepositoryDependency
from sb_gateway.models.note import Note, NoteCreate, NoteCreatedResponse, NoteListResponse, NoteWithScore

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_note(
    note_create: NoteCreate, notes_repo: NoteRepositoryDependency, embedding_service: EmbeddingServiceDependency
) -> NoteCreatedResponse:
    """Create a new note in db."""
    if notes_repo.search_by_content(note_create.content):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Note with content '{note_create.content}' already exists"
        )

    # Generate embedding from note content
    embedding = embedding_service.embed(note_create.content)

    # Add note with embedding
    note = notes_repo.add(note_create.content, embedding=embedding)

    return NoteCreatedResponse(id=note.id, content=note_create.content, created=True)


@router.get("", status_code=status.HTTP_200_OK)
def list_notes(
    notes_repo: NoteRepositoryDependency,
    embedding_service: EmbeddingServiceDependency,
    search: str | None = None,
    search_type: Literal["like", "semantic"] = "semantic",
    top_k: Annotated[int, Query(gt=0, description="Only used with semantic search.")] = 5,
) -> NoteListResponse:
    """List all notes ordered by newest first.

    If search query is provided, uses semantic search via embeddings.
    Otherwise, returns all notes ordered by creation date.
    """
    if search:
        if search_type == "semantic":
            # Convert search query to embedding and use semantic search
            search_embedding = embedding_service.embed(search)
            similarities = notes_repo.search_by_embedding(search_embedding, top_k=top_k)
            return NoteListResponse(
                total=len(similarities),
                search_type="semantic",
                items=[(NoteWithScore(id=note.id, content=note.content, score=score)) for note, score in similarities],
            )
        # Use LIKE search
        note_orm = notes_repo.search_by_content(search)
    else:
        # Return all notes
        note_orm = notes_repo.get_all()
    total = len(note_orm)

    note_list = [Note(id=note.id, content=note.content) for note in note_orm]
    return NoteListResponse(total=total, items=note_list)


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
