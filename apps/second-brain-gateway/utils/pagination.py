from second_brain_db.db.models import Note

SORT_KEY = {
    "id": lambda note: note.id,
    "content": lambda note: note.content,
    "created_at": lambda note: note.created_at,
    "updated_at": lambda note: note.updated_at,
    "search": lambda note: note.score if hasattr(note, "score") else 0,
}


def sort_and_paginate(items: list[Note], sort_by: str, order_by: str, page: int, limit: int) -> tuple[list[Note], int]:
    """Sort a list of ORM notes and return the requested page together with the total count.

    Parameters
    ----------
    items : list[Note]
        Full list of notes to sort and paginate.
    sort_by : str
        Column name to sort by. Allowed values: id, content, created_at, updated_at, search.
    order_by : str
        Sort direction: "asc" or "desc".
    page : int
        1-based page number.
    limit : int
        Number of items per page.

    Returns
    -------
    tuple[list[Note], int]
        Paginated list of notes and the total count before pagination.
    """
    key_fn = SORT_KEY.get(sort_by, SORT_KEY["id"])
    reverse = order_by == "desc"
    sorted_items = sorted(items, key=key_fn, reverse=reverse)
    total = len(sorted_items)
    offset = (page - 1) * limit
    return sorted_items[offset : offset + limit], total
