"""
Seed script for RBAC: departments, roles, permissions, and role-permission mappings.

Usage:
    cd backend/
    python -m app.scripts.seed_rbac

Idempotent: safe to re-run. Uses INSERT ... ON CONFLICT DO NOTHING.

Roles (4):
    admin    - Acceso total al sistema
    gerente  - Aprobaciones, reportes, supervision (scoped por departamento)
    oficina  - Ve todo, captura, aprueba polizas
    campo    - App movil, solo ve lo asignado, captura con aprobacion

Permissions (13): "todos ven, pocos editan"
    Todo lo que NO esta en esta lista es accesible para cualquier usuario autenticado.
    Restricciones por departamento se aplican en el middleware, no en la tabla role_permission.
"""

import asyncio
import logging
import sys

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.models.auth import Department, Permission, Role, RolePermission

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

settings = get_settings()

# ---------------------------------------------------------------------------
# DATA DEFINITIONS
# ---------------------------------------------------------------------------

DEPARTMENTS = [
    {"name": "Administracion", "description": "Administracion general, RH, gestion del sistema"},
    {"name": "Ventas", "description": "Venta de polizas y renovaciones"},
    {"name": "Cobranza", "description": "Cobranza, recaudacion, tarjetas y recibos"},
    {"name": "Siniestros", "description": "Atencion de siniestros, gruas y ajuste"},
]

ROLES = [
    {"name": "admin", "description": "Acceso total al sistema. Configuracion, usuarios, auditoria"},
    {
        "name": "gerente",
        "description": (
            "Gerente de departamento. Aprobaciones, reportes, supervision de personal. "
            "Permisos sensibles se aplican segun departamento en el middleware"
        ),
    },
    {
        "name": "oficina",
        "description": (
            "Personal de oficina. Ve todo, captura datos, aprueba polizas. "
            "Permisos de departamento especifico se aplican en el middleware"
        ),
    },
    {
        "name": "campo",
        "description": (
            "Personal de campo (app movil). Ve solo lo asignado, "
            "captura polizas y pagos que quedan pendientes de aprobacion"
        ),
    },
]

# Permissions: 13 total
# Format: (name, description)
# Department scoping is NOT in this table; it's enforced by the middleware.
# Comments note which departments the permission applies to.
PERMISSIONS = [
    # --- Admin-only (3) ---
    ("system.config", "Configurar parametros del sistema y backups"),
    ("users.manage", "Crear/editar usuarios, resetear passwords, asignar roles"),
    ("roles.manage", "Crear/editar roles y asignar permisos"),
    # --- Admin + Gerente (5) ---
    ("audit.view", "Ver bitacora de auditoria del personal"),
    ("employees.manage", "Alta, baja y edicion de empleados"),
    ("payments.approve", "Aprobar pagos capturados. Dept: gerente de ventas aprueba"),
    ("payments.modify", "Modificar pagos existentes. Dept: solo Cobranza"),
    ("cancellations.execute", "Cancelar polizas C1-C5. Dept: solo gerente Cobranza o admin"),
    # --- Admin + Gerente + Oficina (4) ---
    ("policies.approve", "Aprobar polizas capturadas por vendedor de campo"),
    ("endorsements.approve", "Aprobar endosos. Dept: solo Administracion"),
    ("promotions.manage", "Crear y editar promociones. Dept: solo Cobranza o superior"),
    ("receipts.batch", "Crear lotes de recibos y asignacion. Dept: solo personal Cobranza"),
    # --- Admin + Gerente only (1) ---
    ("cards.assign", "Asignar tarjetas de cobro a cobradores. Dept: gerente Cobranza"),
]

# Role → list of permission names
ROLE_PERMISSIONS: dict[str, list[str]] = {
    "admin": [p[0] for p in PERMISSIONS],  # ALL 13

    "gerente": [
        # Supervision
        "audit.view",
        "employees.manage",
        # Payments
        "payments.approve",
        "payments.modify",
        # Cancellations
        "cancellations.execute",
        # Policies
        "policies.approve",
        # Endorsements
        "endorsements.approve",
        # Promotions
        "promotions.manage",
        # Receipts
        "receipts.batch",
        # Cards
        "cards.assign",
    ],  # 10

    "oficina": [
        # Policies (auxiliar admin revisa y aprueba polizas del vendedor)
        "policies.approve",
        # Endorsements (solo depto Administracion, enforced in middleware)
        "endorsements.approve",
        # Promotions (solo depto Cobranza, enforced in middleware)
        "promotions.manage",
        # Receipts (solo personal Cobranza, enforced in middleware)
        "receipts.batch",
    ],  # 4

    "campo": [],  # 0 — solo ve lo asignado, captura con aprobacion
}


# ---------------------------------------------------------------------------
# SEED LOGIC
# ---------------------------------------------------------------------------

async def seed_departments(session: AsyncSession) -> dict[str, int]:
    """Insert departments, return {name: id} mapping."""
    mapping = {}
    for dept in DEPARTMENTS:
        existing = await session.execute(
            select(Department).where(Department.name == dept["name"])
        )
        row = existing.scalar_one_or_none()
        if row:
            mapping[dept["name"]] = row.id
            logger.info("  Department '%s' already exists (id=%d)", dept["name"], row.id)
        else:
            obj = Department(**dept)
            session.add(obj)
            await session.flush()
            mapping[dept["name"]] = obj.id
            logger.info("  Department '%s' created (id=%d)", dept["name"], obj.id)
    return mapping


async def seed_roles(session: AsyncSession) -> dict[str, int]:
    """Insert roles, return {name: id} mapping."""
    mapping = {}
    for role in ROLES:
        existing = await session.execute(
            select(Role).where(Role.name == role["name"])
        )
        row = existing.scalar_one_or_none()
        if row:
            mapping[role["name"]] = row.id
            logger.info("  Role '%s' already exists (id=%d)", role["name"], row.id)
        else:
            obj = Role(**role)
            session.add(obj)
            await session.flush()
            mapping[role["name"]] = obj.id
            logger.info("  Role '%s' created (id=%d)", role["name"], obj.id)
    return mapping


async def seed_permissions(session: AsyncSession) -> dict[str, int]:
    """Insert permissions, return {name: id} mapping."""
    mapping = {}
    for perm_name, perm_desc in PERMISSIONS:
        existing = await session.execute(
            select(Permission).where(Permission.name == perm_name)
        )
        row = existing.scalar_one_or_none()
        if row:
            mapping[perm_name] = row.id
        else:
            obj = Permission(name=perm_name, description=perm_desc)
            session.add(obj)
            await session.flush()
            mapping[perm_name] = obj.id
    logger.info("  %d permissions seeded", len(mapping))
    return mapping


async def seed_role_permissions(
    session: AsyncSession,
    role_map: dict[str, int],
    perm_map: dict[str, int],
) -> None:
    """Insert role-permission mappings."""
    created = 0
    for role_name, perm_names in ROLE_PERMISSIONS.items():
        role_id = role_map[role_name]
        for perm_name in perm_names:
            perm_id = perm_map[perm_name]
            existing = await session.execute(
                select(RolePermission).where(
                    RolePermission.role_id == role_id,
                    RolePermission.permission_id == perm_id,
                )
            )
            if existing.scalar_one_or_none() is None:
                session.add(RolePermission(role_id=role_id, permission_id=perm_id))
                created += 1
    await session.flush()
    total = sum(len(v) for v in ROLE_PERMISSIONS.values())
    logger.info("  %d role-permission mappings (%d new)", total, created)


async def main() -> None:
    logger.info("=== Seed RBAC: departments, roles, permissions ===")

    engine = create_async_engine(settings.DATABASE_URL_DIRECT, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            logger.info("Seeding departments...")
            dept_map = await seed_departments(session)

            logger.info("Seeding roles...")
            role_map = await seed_roles(session)

            logger.info("Seeding permissions...")
            perm_map = await seed_permissions(session)

            logger.info("Seeding role-permission mappings...")
            await seed_role_permissions(session, role_map, perm_map)

        logger.info("=== RBAC seed completed ===")
        logger.info("  Departments: %d", len(dept_map))
        logger.info("  Roles: %d", len(role_map))
        logger.info("  Permissions: %d", len(perm_map))
        logger.info("  Mappings: %d", sum(len(v) for v in ROLE_PERMISSIONS.values()))

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
