# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

  - Added authenticated user feedback endpoints
    <details>
    Detailed description: `POST /users/feedback` accepts `text`, requires bearer authentication, stores feedback with the current user's ID, and returns the created feedback with timestamps. `GET /admin/feedback` requires an admin bearer token and returns all feedback ordered by newest first with a total count. `DELETE /admin/feedback/{feedback_id}` requires an admin bearer token, deletes feedback by ID, returns `204 No Content` on success, and returns `404 Not Found` when the feedback item does not exist. Feedback is stored in a dedicated `feedback` table with `ON DELETE CASCADE` ownership through `users.id`.
    </details>

  - Added public signup and authenticated password change endpoints
    <details>
    Detailed description: `POST /auth/signup` accepts `username` and `password`, rejects duplicate usernames with `409 Conflict`, hashes the password, creates a regular `user` role account, and returns user details without a password hash. `PATCH /users/me/password` accepts `current_password` and `new_password`, requires bearer authentication, returns `401 Unauthorized` when the current password is invalid, hashes the new password, updates the authenticated user's password, revokes all refresh tokens for that user, and returns user details without a password hash.
    </details>

---

## [0.1.0] - 2026-05-03

> Changelog not maintained prior to this release.

---

[0.1.0]: https://github.com/vahagnd/second-brain-backend/releases/tag/v0.1.0
[Unreleased]: https://github.com/vahagnd/second-brain-backend/compare/v0.1.0...develop
