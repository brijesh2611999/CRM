import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.tenant import Tenant
from app.models.role import Role
from app.services.permission_service import seed_default_permissions

async def main():
    async with AsyncSessionLocal() as db:
        # Get all active tenants
        result = await db.execute(select(Tenant).where(Tenant.is_active == True))
        tenants = result.scalars().all()

        default_roles_info = [
            ("Sales Manager", "SALES_MANAGER", "Team"),
            ("Sales Executive", "SALES_EXECUTIVE", "Own"),
            ("Finance", "FINANCE", "All"),
            ("Customer Portal", "CUSTOMER_PORTAL", "Own"),
        ]

        for tenant in tenants:
            print(f"Checking tenant: {tenant.name}")
            # check which roles exist
            result = await db.execute(select(Role).where(Role.tenant_id == tenant.id))
            existing_roles = {r.code for r in result.scalars().all()}

            for r_name, r_code, r_scope in default_roles_info:
                if r_code not in existing_roles:
                    print(f"Seeding {r_code} for tenant {tenant.name}")
                    r = Role(
                        id=uuid.uuid4(),
                        tenant_id=tenant.id,
                        name=r_name,
                        code=r_code,
                        is_system_role=True,
                        is_active=True,
                        data_scope=r_scope,
                    )
                    db.add(r)
                    await db.flush()
                    await seed_default_permissions(db, tenant.id, r.id, r_code)
        
        await db.commit()
        print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
