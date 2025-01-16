from api.crud.users import get_all_users, create_user
from core.models import db_helper, User
import asyncio

from core.schemas.user import UserCreate


async def main():
    new_user_create = UserCreate(username="User1111 name")
    new_user: User = await db_helper.execute_with_session_scope(create_user, new_user_create)
    print(f"Created User ID: {new_user.id}, Username: {new_user.username}")

    users = await db_helper.execute_with_session(get_all_users)
    for user in users:
        print(f"User ID: {user.id}, Username: {user.username}")



if __name__ == "__main__":
    asyncio.run(main())
