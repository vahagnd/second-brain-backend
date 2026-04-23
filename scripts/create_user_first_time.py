from second_brain_db.services import AuthService
from second_brain_db.repository.user import UserRepository
from second_brain_db.db.engine import session_maker

USERNAME = "admin"
PASSWORD = "Admin123"
ROLE = "admin"

with session_maker() as session:
    UserRepository(session).add(
        username=USERNAME,
        password_hash=AuthService.hash_password(PASSWORD),
        role=ROLE,
    )
