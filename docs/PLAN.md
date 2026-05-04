# Plan: Add Self-Service Password Update and Public Signup Endpoints

## Scope

Add two Gateway API capabilities:

- Authenticated users can update their own password.
- New users can sign up from scratch without admin credentials.

This plan is documentation only. Implementation should be done in a later task.

## Current Context

- The project currently exposes a single Gateway service from `apps/second-brain-gateway`.
- The public API base path is `/api/v1`.
- Existing relevant endpoints:
  - `POST /auth/login`
  - `POST /auth/refresh`
  - `POST /auth/logout`
  - `GET /users/me`
  - `PATCH /users/me`
  - `POST /admin/users`
  - `PATCH /admin/users/{user_id}/password`
- Existing admin user creation already hashes passwords with `AuthService.hash_password(...)` and writes users through `UserRepository.add(...)`.
- Existing admin password update already uses `UserUpdatePassword` and `UserRepository.update_password(...)`.
- Existing refresh token invalidation uses `RefreshTokenRepository.revoke_all_for_user(...)`.

## Proposed API Contract

### 1. Public Signup

- Endpoint: `POST /auth/signup`
- Auth: none
- Request body:

```json
{
  "username": "string",
  "password": "string"
}
```

- Response `201 Created`:

```json
{
  "id": 1,
  "username": "string",
  "role": "user"
}
```

- Error responses:
  - `409 Conflict`: username already exists
  - `422 Unprocessable Entity`: invalid request body

Decision: public signup must always create role `user`. Do not accept `role` from the public request body.

### 2. Current User Password Update

- Endpoint: `PATCH /users/me/password`
- Auth: bearer access token
- Request body:

```json
{
  "current_password": "string",
  "new_password": "string"
}
```

- Response `200 OK`:

```json
{
  "id": 1,
  "username": "string",
  "role": "string"
}
```

- Error responses:
  - `401 Unauthorized`: missing, invalid, expired, or revoked access token
  - `403 Forbidden`: current password is incorrect
  - `422 Unprocessable Entity`: invalid request body

Decision: after a successful password update, revoke all refresh tokens for the current user so old refresh tokens cannot mint new access tokens. The current access token can remain valid until expiry unless a later security requirement says to blacklist it too.

## Implementation Steps

1. Add request models.
   - Add a public signup request model in `apps/second-brain-gateway/models/auth.py`.
   - Add a self-service password update request model in `apps/second-brain-gateway/models/user.py`.
   - Use `ConfigDict(extra="forbid")`, matching existing request models.

2. Add `POST /auth/signup`.
   - Implement in `apps/second-brain-gateway/routers/auth.py`.
   - Check `user_repo.get_one_or_none_by_username(...)`.
   - Return `409 Conflict` with a clear duplicate-username detail when username exists.
   - Hash the password with `AuthService.hash_password(...)`.
   - Create the user with `UserRepository.add(username, password_hash, role="user")`.
   - Return `UserDetail`.

3. Add `PATCH /users/me/password`.
   - Implement in `apps/second-brain-gateway/routers/users.py`.
   - Reuse `CurrentUserDependency`, `UserRepositoryDependency`, and `RefreshTokenRepositoryDependency`.
   - Verify `current_password` with `AuthService.verify_password(...)`.
   - Return `403 Forbidden` when the current password does not match.
   - Hash `new_password` with `AuthService.hash_password(...)`.
   - Update via `user_repo.update_password(current_user.id, password_hash)`.
   - Revoke all refresh tokens for the user after the password update.
   - Return `UserDetail`.

4. Keep repository changes minimal.
   - `UserRepository.add(...)`, `UserRepository.update_password(...)`, and `RefreshTokenRepository.revoke_all_for_user(...)` already exist.
   - Do not add database migrations unless implementation reveals a schema requirement.

5. Update API analytics documentation.
   - Update `docs/analytics/API_ANALYTICS.md` after implementation.
   - Endpoint total should increase from 17 to 19.
   - Add the two new endpoint descriptions and update statistics tables.

6. Update changelog.
   - Add the feature entry to `docs/CHANGELOG.md` after implementation, as required by project rules.

## Test Plan

Follow `docs/DEV_RULES.md`:

- Put all tests under `/tests`.
- Use `pytest`.
- Do not use test classes.
- Keep tests independent and clean up created users.
- Add or extend case files under `tests/cases/`.

Recommended E2E coverage:

1. Signup success.
   - `POST /auth/signup` creates a user with role `user`.
   - Cleanup with existing admin delete-user endpoint.

2. Signup duplicate username.
   - First signup succeeds.
   - Second signup with same username returns `409`.
   - Cleanup created user.

3. Signup rejects role injection.
   - Request with an unexpected `role` field returns `422`.

4. Login after signup.
   - Signup succeeds.
   - `POST /auth/login` with the new credentials succeeds.
   - Cleanup created user.

5. Own password update success.
   - Create or sign up a dedicated user.
   - Login as that user.
   - `PATCH /users/me/password` with the current password succeeds.
   - Login with old password fails.
   - Login with new password succeeds.
   - Cleanup created user.

6. Own password update with wrong current password.
   - Authenticated request returns `403`.
   - Existing password remains valid.

7. Own password update without auth.
   - Request returns `401`.

8. Refresh token behavior after own password update.
   - Login and keep the refresh token.
   - Update own password.
   - `POST /auth/refresh` with the old refresh token returns `401`.

## Security Notes

- Do not log plaintext passwords.
- Do not return password hashes.
- Keep public signup restricted to role `user`.
- Prefer generic auth failure details where useful, but keep response codes aligned with the existing API style.
- Consider password length and complexity validation as a follow-up if product requirements define it.

## Open Decisions

- Whether public signup should return only `UserDetail` or immediately return login tokens. This plan chooses `UserDetail` to match `POST /admin/users` and avoid changing token issuance behavior.
- Whether a successful password change should also blacklist the currently used access token. This plan revokes refresh tokens only, matching the existing token-revocation primitives without forcing immediate logout.
- Whether password strength rules should be introduced now or separately.
