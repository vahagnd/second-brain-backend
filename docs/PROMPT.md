Generate a plan in file PLAN.md on adding user authoziation to project.

Currently as you can see I added user table, with used_id being foreign key in notes table.
Also added admin endpoints for getting all users, adding, deleting, getting user by id.

You need to add propert authorization and authentication system.

Endpoints that need to be added - auth and users:
- auth - login, logout, no refresh for now.
- users - get info about current user with get users/me, update with patch users/me

Also add new admin endpoints for updating user by id and changing password of user by id.

Dont generate any code, only detailed plan in PLAN.md, that you can use in the future to generate code.
