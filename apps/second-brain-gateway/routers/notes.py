from typing import Annotated, Literal

from dependencies.auth import CurrentUserDependency
from dependencies.embedding import EmbeddingServiceDependency
from dependencies.repositories import NoteRepositoryDependency
from fastapi import APIRouter, HTTPException, Query, status
from models.note import (
    Note,
    NoteCreate,
    NoteCreatedResponse,
    NoteListDuplicateResponse,
    NoteListResponse,
    NoteWithScore,
)
from settings import similarity_search_settings

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_note(
    current_user: CurrentUserDependency,
    notes_repo: NoteRepositoryDependency,
    embedding_service: EmbeddingServiceDependency,
    note_create: NoteCreate,
) -> NoteCreatedResponse:
    """Create a new note in db."""
    # Generate embedding from note content
    embedding = embedding_service.embed(note_create.content)

    user_id = current_user.id
    # Check for semantic duplicates before creating the note
    duplicates = notes_repo.search_by_embedding(
        user_id=user_id,
        query_embedding=embedding,
        top_k=similarity_search_settings.top_k,
        threshold=similarity_search_settings.threshold,
    )

    if duplicates:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=NoteListDuplicateResponse(
                message="One or more similar notes already exist.",
                similar_notes=[
                    NoteWithScore(id=note.id, content=note.content, score=score) for note, score in duplicates
                ],
            ).model_dump(),
        )

    # Add note with embedding
    note = notes_repo.add(note_create.content, embedding=embedding)

    return NoteCreatedResponse(id=note.id, content=note_create.content, created=True)


@router.get("", status_code=status.HTTP_200_OK)
def list_notes(  # noqa: PLR0913
    current_user: CurrentUserDependency,
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
    user_id = current_user.id
    if search:
        if search_type == "semantic":
            # Convert search query to embedding and use semantic search
            search_embedding = embedding_service.embed(search)
            similarities = notes_repo.search_by_embedding(
                user_id=user_id,
                query_embedding=search_embedding,
                top_k=top_k,
            )
            return NoteListResponse(
                total=len(similarities),
                search_type="semantic",
                items=[(NoteWithScore(id=note.id, content=note.content, score=score)) for note, score in similarities],
            )
        # Use LIKE search
        note_orm = notes_repo.search_by_content(user_id=user_id, query=search)
    else:
        # Return all notes
        note_orm = notes_repo.get_all(user_id=user_id)
    total = len(note_orm)

    note_list = [Note(id=note.id, content=note.content) for note in note_orm]
    return NoteListResponse(total=total, items=note_list)


@router.get("/{note_id}", status_code=status.HTTP_200_OK)
def get_note(
    current_user: CurrentUserDependency,
    notes_repo: NoteRepositoryDependency,
    note_id: int,
) -> Note | None:
    """Get a single note by its ID."""
    user_id = current_user.id
    note = notes_repo.get_one_or_none(user_id=user_id, note_id=note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return Note(id=note.id, content=note.content, created_at=note.created_at.isoformat())


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    current_user: CurrentUserDependency,
    notes_repo: NoteRepositoryDependency,
    note_id: int,
) -> None:
    """Delete a note by its ID."""
    user_id = current_user.id
    deleted = notes_repo.delete(user_id=user_id, note_id=note_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
