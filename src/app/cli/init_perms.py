import asyncio
import logging
from pathlib import Path

import yaml
from sqlalchemy import delete
from sqlalchemy.future import select

from app.core.db import async_session
from app.core.settings import settings
from app.models import Role, Permission
from app.models.iam import auth_role_permissions

PERMISSIONS_YAML = Path(settings.config_dir) / "permissions.yaml"

logger = logging.getLogger("init_group_perms")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


async def init_group_perms():
    async with async_session() as session:
        async with session.begin():
            # Load permissions YAML
            logger.info(f"Loading permissions from {PERMISSIONS_YAML}")
            with open(PERMISSIONS_YAML, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            for role_name, info in data["roles"].items():
                display_name = info.get("display_name", "")
                yaml_perms = set(info.get("permissions", []))

                # --- Role ---
                role = await session.scalar(select(Role).where(Role.name == role_name))
                if not role:
                    # Create new role
                    role = Role(name=role_name, display_name=display_name)
                    session.add(role)
                    await session.flush()
                    logger.info(f"Created role '{role_name}' with display_name '{display_name}'")
                else:
                    # Update display_name if changed
                    if role.display_name != display_name:
                        role.display_name = display_name
                        session.add(role)
                        logger.info(f"Updated role '{role_name}' display_name to '{display_name}'")

                # --- Permissions ---
                perms_in_db = {
                    p.name: p
                    for p in await session.scalars(
                        select(Permission).where(Permission.name.in_(yaml_perms))
                    )
                }

                # Add missing permissions
                for perm_name in yaml_perms:
                    perm = perms_in_db.get(perm_name)
                    if not perm:
                        perm = Permission(name=perm_name)
                        session.add(perm)
                        await session.flush()
                        perms_in_db[perm_name] = perm
                        logger.info(f"Created permission '{perm_name}'")

                # --- Current role's associated permissions ---
                current_perm_ids = set(
                    await session.scalars(
                        select(auth_role_permissions.c.permission_id)
                        .where(auth_role_permissions.c.role_id == role.id)  # type: ignore
                    )
                )

                # --- Remove associations not in YAML ---
                perms_to_remove = current_perm_ids - {p.id for p in perms_in_db.values() if p.name in yaml_perms}
                if perms_to_remove:
                    await session.execute(
                        delete(auth_role_permissions)
                        .where(auth_role_permissions.c.role_id == role.id)  # type: ignore
                        .where(auth_role_permissions.c.permission_id.in_(perms_to_remove))
                    )
                    logger.info(f"Removed {len(perms_to_remove)} permissions from role '{role_name}'")

                # --- Add new associations from YAML ---
                added_count = 0
                for perm in perms_in_db.values():
                    if perm.id not in current_perm_ids and perm.name in yaml_perms:
                        await session.execute(
                            auth_role_permissions.insert().values(
                                role_id=role.id,
                                permission_id=perm.id,
                            )
                        )
                        added_count += 1
                if added_count:
                    logger.info(f"Added {added_count} permissions to role '{role_name}'")

        logger.info(f"Roles and permissions initialized successfully.")


def main():
    asyncio.run(init_group_perms())


if __name__ == "__main__":
    main()
