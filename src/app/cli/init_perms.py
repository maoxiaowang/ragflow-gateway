import asyncio
from pathlib import Path

import yaml
from sqlalchemy.future import select

from app.core.db import async_session
from app.core.settings import settings
from app.models import Role, Permission
from app.models.iam import auth_role_permissions

PERMISSIONS_YAML = Path(settings.config_dir) / "permissions.yaml"


async def init_group_perms():
    async with async_session() as session:
        async with session.begin():
            with open(PERMISSIONS_YAML, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            for role_name, info in data["roles"].items():
                # --- role ---
                role = await session.scalar(
                    select(Role).where(Role.name == role_name)
                )
                if not role:
                    role = Role(name=role_name)
                    session.add(role)
                    await session.flush()

                # --- 当前 role 已有关联的权限名 ---
                existing_perm_names = set(
                    await session.scalars(
                        select(Permission.name)
                        .join(auth_role_permissions)
                        .where(auth_role_permissions.c.role_id == role.id)
                    )
                )

                for perm_name in info.get("permissions", []):
                    perm = await session.scalar(
                        select(Permission).where(Permission.name == perm_name)
                    )
                    if not perm:
                        perm = Permission(name=perm_name)
                        session.add(perm)
                        await session.flush()

                    if perm_name not in existing_perm_names:
                        await session.execute(
                            auth_role_permissions.insert().values(
                                role_id=role.id,
                                permission_id=perm.id,
                            )
                        )
                        existing_perm_names.add(perm_name)


def main():
    asyncio.run(init_group_perms())


if __name__ == "__main__":
    main()
