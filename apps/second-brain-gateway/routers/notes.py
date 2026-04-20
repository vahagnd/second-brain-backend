import math
from typing import Annotated, Literal

from dependencies.embedding import EmbeddingServiceDependency
from dependencies.repositories import NoteRepositoryDependency
from fastapi import APIRouter, HTTPException, Query, status
from models.note import Note, NoteCreate, NoteCreatedResponse, NoteListResponse, NoteWithScore
from settings import pagination_settings, similarity_search_settings
from utils.pagination import sort_and_paginate

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_note(
    note_create: NoteCreate, notes_repo: NoteRepositoryDependency, embedding_service: EmbeddingServiceDependency
) -> NoteCreatedResponse:
    """Create a new note in db."""
    # Generate embedding from note content
    embedding = embedding_service.embed(note_create.content)

    # Check for semantic duplicates before creating the note
    duplicates = notes_repo.search_by_embedding(
        query_embedding=embedding,
        top_k=similarity_search_settings.top_k,
        threshold=similarity_search_settings.threshold,
    )

    if duplicates:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Very similar notes already exist.",
                "similar_notes": [
                    {
                        "id": note.id,
                        "content": note.content,
                        "score": score,
                    }
                    for note, score in duplicates
                ],
            },
        )

    # Add note with embedding
    note = notes_repo.add(note_create.content, embedding=embedding)

    return NoteCreatedResponse(id=note.id, content=note_create.content, created=True)


@router.get("", status_code=status.HTTP_200_OK)
def list_notes(  # noqa: PLR0913
    notes_repo: NoteRepositoryDependency,
    embedding_service: EmbeddingServiceDependency,
    search: str | None = None,
    search_type: Literal["like", "semantic"] = "semantic",
    top_k: Annotated[int, Query(gt=0, description="Only used with semantic search.")] = 5,
    sort_by: Literal["id", "content", "created_at", "updated_at"] = "id",
    order_by: Literal["asc", "desc"] = "desc",
    page: Annotated[int, Query(gt=0, description="Page number (1-based).")] = 1,
    limit: Annotated[int, Query(gt=0, description="Number of items per page.")] = pagination_settings.limit,
) -> NoteListResponse:
    """List notes with sorting and pagination.

    If a search query is provided, uses semantic or LIKE search.
    Sorting and pagination are applied to all result sets.
    """
    if search:
        if search_type == "semantic":
            search_embedding = embedding_service.embed(search)
            similarities = notes_repo.search_by_embedding(search_embedding, top_k=top_k)
            # Extract notes, sort, paginate, then re-attach scores
            notes = [note for note, _ in similarities]
            scores = {note.id: score for note, score in similarities}
            page_notes, total = sort_and_paginate(notes, "search", order_by, page, limit)
            pages = math.ceil(total / limit) if limit else 1
            return NoteListResponse(
                total=total,
                search_type="semantic",
                page=page,
                limit=limit,
                pages=pages,
                items=[NoteWithScore(id=note.id, content=note.content, score=scores[note.id]) for note in page_notes],
            )

        # LIKE search
        all_notes = notes_repo.search_by_content(search)
        page_notes, total = sort_and_paginate(all_notes, sort_by, order_by, page, limit)
        pages = math.ceil(total / limit) if limit else 1
        return NoteListResponse(
            total=total,
            search_type="like",
            page=page,
            limit=limit,
            pages=pages,
            items=[
                Note(id=note.id, content=note.content, created_at=note.created_at, updated_at=note.updated_at)
                for note in page_notes
            ],
        )

    # No search — return all notes
    all_notes = notes_repo.get_all()
    page_notes, total = sort_and_paginate(all_notes, sort_by, order_by, page, limit)
    pages = math.ceil(total / limit) if limit else 1
    return NoteListResponse(
        total=total,
        page=page,
        limit=limit,
        pages=pages,
        items=[
            Note(id=note.id, content=note.content, created_at=note.created_at, updated_at=note.updated_at)
            for note in page_notes
        ],
    )


@router.get("/{note_id}", status_code=status.HTTP_200_OK)
def get_note(note_id: int, notes_repo: NoteRepositoryDependency) -> Note | None:
    """Get a single note by its ID."""
    note = notes_repo.get_one_or_none(note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return Note(id=note.id, content=note.content, created_at=note.created_at, updated_at=note.updated_at)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, notes_repo: NoteRepositoryDependency) -> None:
    """Delete a note by its ID."""
    deleted = notes_repo.delete(note_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
