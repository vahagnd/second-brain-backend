# Changelog

All notable changes to this project will be documented in this file.

---

## [Unreleased]

### Added — Gateway: sorting and pagination for `GET /notes`

The `GET /notes` endpoint now supports **sorting** and **pagination** for all result sets (no-search, LIKE search, and semantic search).

#### New query parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `sort_by` | `"id"` \| `"content"` \| `"created_at"` \| `"updated_at"` | `"id"` | Field to sort results by. Has no effect on semantic search (results are always ordered by relevance score). |
| `order_by` | `"asc"` \| `"desc"` | `"desc"` | Sort direction. Has no effect on semantic search. |
| `page` | `integer` (> 0) | `1` | 1-based page number. |
| `limit` | `integer` (> 0) | `10` | Number of items per page. Overridable via `PAGINATION_LIMIT` env variable. |

#### Updated response fields (`NoteListResponse`)

Three new fields are now included in every `GET /notes` response:

| Field | Type | Description |
|---|---|---|
| `page` | `integer` | Current page number (1-based) |
| `limit` | `integer` | Number of items per page |
| `pages` | `integer` | Total number of pages (`ceil(total / limit)`) |

#### New configuration

A new `PaginationSettings` class (env prefix `PAGINATION_`) was added to `apps/second-brain-gateway/settings.py`:

| Env Variable | Default | Description |
|---|---|---|
| `PAGINATION_LIMIT` | `10` | Default page size for `GET /notes` |

#### New utility

`apps/second-brain-gateway/utils/pagination.py` — `sort_and_paginate()` helper that sorts a list of ORM `Note` objects by a given field and returns the requested page together with the total count.
