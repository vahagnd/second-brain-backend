import math
from typing import Annotated, Literal

from dependencies.embedding import EmbeddingServiceDependency
from dependencies.repositories import NoteRepositoryDependency
from dependencies.user import CurrentUserDependency
from fastapi import APIRouter, HTTPException, Query, status
from models.note import (
    Note,
    NoteCreate,
    NoteListDuplicateResponse,
    NoteListResponse,
    NoteWithScore,
)
from settings import pagination_settings, similarity_search_settings
from utils.pagination import sort_and_paginate

router = APIRouter(
    prefix="/notes",
    tags=["notes"],
    responses={
        401: {"description": "Unauthenticated"},
        403: {"description": "Forbidden - insufficient permissions"},
    },
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "A similar note already exists", "model": NoteListDuplicateResponse}},
)
def create_note(
    current_user: CurrentUserDependency,
    notes_repo: NoteRepositoryDependency,
    embedding_service: EmbeddingServiceDependency,
    note_create: NoteCreate,
) -> Note:
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
                message="One or more similar notes already exist",
                similar_notes=[
                    NoteWithScore(
                        id=note.id,
                        content=note.content,
                        created_at=note.created_at,
                        updated_at=note.updated_at,
                        score=score,
                        user_id=note.user_id,
                    )
                    for note, score in duplicates
                ],
            ).model_dump(mode="json"),
        )

    # Add note with embedding
    note = notes_repo.add(user_id=current_user.id, content=note_create.content, embedding=embedding)

    return Note(
        id=note.id,
        content=note.content,
        created_at=note.created_at,
        updated_at=note.updated_at,
        user_id=note.user_id,
    )


@router.get("", status_code=status.HTTP_200_OK)
def list_notes(  # noqa: PLR0913
    current_user: CurrentUserDependency,
    notes_repo: NoteRepositoryDependency,
    embedding_service: EmbeddingServiceDependency,
    search: str | None = None,
    search_type: Literal["like", "semantic"] = "semantic",
    top_k: Annotated[
        int,
        Query(gt=0, description="Only used with semantic search."),
    ] = similarity_search_settings.top_k,
    sort_by: Literal["id", "content", "created_at", "updated_at"] = "id",
    order_by: Literal["asc", "desc"] = "desc",
    page: Annotated[int, Query(gt=0, description="Page number (1-based).")] = 1,
    limit: Annotated[int, Query(gt=0, description="Number of items per page.")] = pagination_settings.limit,
) -> NoteListResponse:
    """List notes with sorting and pagination.

    If a search query is provided, uses semantic or LIKE search.
    Sorting and pagination are applied to all result sets.
    """
    # Admin users can see all notes, regular users can only see their own notes
    user_id = None if current_user.role == "admin" else current_user.id

    if search:
        # Semantic search with embeddings
        if search_type == "semantic":
            search_embedding = embedding_service.embed(search)
            similarities = notes_repo.search_by_embedding(
                user_id=user_id,
                query_embedding=search_embedding,
                top_k=top_k,
            )
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
                items=[
                    NoteWithScore(
                        id=note.id,
                        content=note.content,
                        score=scores[note.id],
                        created_at=note.created_at,
                        updated_at=note.updated_at,
                        user_id=note.user_id,
                    )
                    for note in page_notes
                ],
            )
        # LIKE search
        all_notes = notes_repo.search_by_content(user_id=user_id, query=search)
        page_notes, total = sort_and_paginate(all_notes, sort_by, order_by, page, limit)
        pages = math.ceil(total / limit) if limit else 1
        return NoteListResponse(
            total=total,
            search_type="like",
            page=page,
            limit=limit,
            pages=pages,
            items=[
                Note(
                    id=note.id,
                    content=note.content,
                    created_at=note.created_at,
                    updated_at=note.updated_at,
                    user_id=note.user_id,
                )
                for note in page_notes
            ],
        )

    # No search — return all notes
    all_notes = notes_repo.get_all(user_id=user_id)
    page_notes, total = sort_and_paginate(all_notes, sort_by, order_by, page, limit)
    pages = math.ceil(total / limit) if limit else 1
    return NoteListResponse(
        total=total,
        page=page,
        limit=limit,
        pages=pages,
        items=[
            Note(
                id=note.id,
                content=note.content,
                created_at=note.created_at,
                updated_at=note.updated_at,
                user_id=note.user_id,
            )
            for note in page_notes
        ],
    )


@router.get(
    "/{note_id}",
    status_code=status.HTTP_200_OK,
    responses={404: {"description": "Note not found"}},
)
def get_note(
    current_user: CurrentUserDependency,
    notes_repo: NoteRepositoryDependency,
    note_id: int,
) -> Note | None:
    """Get a single note by its ID."""
    # Admin users can see all notes, regular users can only see their own notes
    user_id = None if current_user.role == "admin" else current_user.id
    note = notes_repo.get_one_or_none(user_id=user_id, note_id=note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return Note(
        id=note.id,
        content=note.content,
        created_at=note.created_at,
        updated_at=note.updated_at,
        user_id=note.user_id,
    )


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Note not found"}},
)
def delete_note(
    current_user: CurrentUserDependency,
    notes_repo: NoteRepositoryDependency,
    note_id: int,
) -> None:
    """Delete a note by its ID."""
    # Admin users can delete any note, regular users can only delete their own notes
    user_id = None if current_user.role == "admin" else current_user.id
    deleted = notes_repo.delete(user_id=user_id, note_id=note_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
