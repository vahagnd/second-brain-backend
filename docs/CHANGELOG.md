# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

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
