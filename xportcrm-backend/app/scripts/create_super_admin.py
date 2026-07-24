"""One-time script to create the first Super Admin account.
Run manually: python -m app.scripts.create_super_admin
"""
import asyncio
import uuid

from app.db.session import AsyncSessionLocal
from app.core.security import hash_password
from app.models.super_admin import SuperAdmin


async def main():
    email = input("Super Admin email: ")
    full_name = input("Full name: ")
    password = input("Password: ")

    async with AsyncSessionLocal() as db:
        admin = SuperAdmin(
            id=uuid.uuid4(),
            full_name=full_name,
            email=email,
            hashed_password=hash_password(password),
            is_active=True,
        )
        db.add(admin)
        await db.commit()
        print(f"Super Admin created: {email}")


if __name__ == "__main__":
    asyncio.run(main())