"""
Seed script for RBAC: departments, roles, permissions, and role-permission mappings.

Usage:
    cd backend/
    python -m app.scripts.seed_rbac

Idempotent: safe to re-run. Uses INSERT ... ON CONFLICT DO NOTHING.
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
    {"name": "Administracion", "description": "Administracion general del sistema"},
    {"name": "Ventas", "description": "Departamento de ventas de polizas"},
    {"name": "Cobranza", "description": "Departamento de cobranza y recaudacion"},
    {"name": "Siniestros", "description": "Departamento de siniestros y ajuste"},
    {"name": "Recursos Humanos", "description": "Gestion de personal, vacaciones, quejas"},
]

ROLES = [
    {"name": "admin", "description": "Administrador con acceso total al sistema"},
    {"name": "gerente", "description": "Gerente de departamento. Acceso por departamento, no global"},
    {"name": "auxiliar", "description": "Auxiliar de oficina. Permisos configurables por admin"},
    {"name": "cobrador", "description": "Cobrador de campo. App movil: cobros, recibos, rutas"},
    {"name": "vendedor", "description": "Vendedor de campo. App movil: polizas, cotizaciones, renovaciones"},
    {"name": "ajustador", "description": "Ajustador de campo. App movil: siniestros, gruas, guardias"},
    {"name": "viewer", "description": "Solo lectura. Consulta sin modificar datos"},
]

# Permissions: module.action format
# Organized by module for clarity
PERMISSIONS = [
    # --- Polizas ---
    ("policies.create", "Crear polizas nuevas"),
    ("policies.read", "Ver todas las polizas"),
    ("policies.read_own", "Ver solo polizas propias (vendedor)"),
    ("policies.update", "Editar polizas existentes"),
    ("policies.delete", "Eliminar polizas"),
    ("policies.change_seller", "Cambiar vendedor asignado a poliza"),
    # --- Clientes ---
    ("clients.create", "Crear clientes nuevos"),
    ("clients.read", "Ver todos los clientes"),
    ("clients.read_assigned", "Ver solo clientes asignados"),
    ("clients.update", "Editar datos de clientes"),
    ("clients.delete", "Eliminar clientes"),
    # --- Vehiculos ---
    ("vehicles.create", "Registrar vehiculos nuevos"),
    ("vehicles.read", "Ver vehiculos"),
    ("vehicles.update", "Editar datos de vehiculos"),
    # --- Coberturas ---
    ("coverages.create", "Crear coberturas y precios"),
    ("coverages.read", "Ver tabla de coberturas y precios"),
    ("coverages.update", "Editar coberturas y precios"),
    # --- Pagos ---
    ("payments.create", "Registrar pagos"),
    ("payments.read", "Ver pagos"),
    ("payments.update", "Editar pagos (solo depto Cobranza)"),
    ("payments.reverse", "Revertir un pago aplicado"),
    # --- Propuestas de pago ---
    ("proposals.create", "Crear propuesta de cobro (cobrador campo)"),
    ("proposals.read", "Ver todas las propuestas"),
    ("proposals.read_own", "Ver solo propuestas propias"),
    ("proposals.approve", "Aprobar propuestas de pago"),
    ("proposals.reject", "Rechazar propuestas de pago"),
    # --- Cobranza / Tarjetas ---
    ("collections.create", "Crear avisos de visita y registros de cobranza"),
    ("collections.read", "Ver todas las tarjetas de cobranza"),
    ("collections.read_own_route", "Ver solo ruta de cobranza propia"),
    ("collections.assign", "Asignar tarjetas a cobradores"),
    ("collections.reassign", "Reasignar tarjetas entre cobradores"),
    # --- Recibos ---
    ("receipts.create_batch", "Crear lotes de recibos"),
    ("receipts.assign", "Asignar recibos a cobradores"),
    ("receipts.read", "Ver todos los recibos"),
    ("receipts.read_assigned", "Ver solo recibos asignados"),
    ("receipts.use", "Marcar recibo como usado"),
    ("receipts.cancel", "Cancelar o reportar extravio de recibo"),
    # --- Siniestros ---
    ("incidents.create", "Registrar siniestro nuevo"),
    ("incidents.read", "Ver todos los siniestros"),
    ("incidents.read_assigned", "Ver solo siniestros asignados"),
    ("incidents.update", "Actualizar siniestros"),
    ("incidents.close", "Cerrar un siniestro"),
    ("incidents.admin", "Gestionar guardias y turnos de ajustadores"),
    # --- Gruas ---
    ("tow_services.create", "Solicitar servicio de grua"),
    ("tow_services.read", "Ver todos los servicios de grua"),
    ("tow_services.read_assigned", "Ver solo servicios de grua asignados"),
    ("tow_services.update", "Actualizar servicio de grua"),
    ("tow_services.admin", "Gestionar proveedores de grua"),
    # --- Endosos ---
    ("endorsements.create", "Crear endoso"),
    ("endorsements.read", "Ver endosos"),
    ("endorsements.approve", "Aprobar endoso"),
    ("endorsements.reject", "Rechazar endoso"),
    ("endorsements.apply", "Aplicar endoso aprobado"),
    # --- Cancelaciones ---
    ("cancellations.create", "Crear cancelacion de poliza (C1-C5)"),
    ("cancellations.read", "Ver cancelaciones"),
    ("cancellations.undo", "Reactivar poliza cancelada"),
    # --- Renovaciones ---
    ("renewals.create", "Crear renovacion de poliza"),
    ("renewals.read", "Ver todas las renovaciones"),
    ("renewals.read_assigned", "Ver renovaciones asignadas (vendedor)"),
    # --- Promociones ---
    ("promotions.create", "Crear promociones"),
    ("promotions.read", "Ver promociones"),
    ("promotions.update", "Editar promociones"),
    ("promotions.apply", "Aplicar promocion a poliza"),
    # --- Empleados ---
    ("employees.create", "Crear empleados"),
    ("employees.read", "Ver empleados"),
    ("employees.update", "Editar datos de empleados"),
    ("employees.toggle_status", "Activar/desactivar empleados"),
    # --- Reportes ---
    ("reports.read", "Ver y descargar reportes"),
    ("reports.admin", "Reportes de comisiones y pagos del dia"),
    # --- Dashboard ---
    ("dashboard.view", "Ver dashboard general"),
    ("dashboard.collection", "Ver dashboard de cobranza"),
    # --- Notificaciones ---
    ("notifications.send", "Enviar notificaciones (WhatsApp/Telegram)"),
    ("notifications.read", "Ver historial de notificaciones"),
    # --- Administracion ---
    ("admin.access", "Acceder al panel de administracion"),
    ("admin.config", "Modificar configuracion del sistema"),
    ("admin.audit_log", "Ver log de auditoria"),
    # --- Guardias / Turnos ---
    ("shifts.read", "Ver turnos y guardias"),
    ("shifts.manage", "Gestionar turnos y guardias"),
]

# Role → list of permission names
# admin gets ALL permissions (handled in code via wildcard, but we also assign explicitly)
ROLE_PERMISSIONS: dict[str, list[str]] = {
    "admin": [p[0] for p in PERMISSIONS],  # ALL

    "gerente": [
        # Read everything in their department
        "policies.read", "clients.read", "vehicles.read", "coverages.read",
        "payments.read", "proposals.read", "collections.read",
        "receipts.read", "incidents.read", "tow_services.read",
        "endorsements.read", "cancellations.read", "renewals.read",
        "promotions.read", "notifications.read",
        # Manage employees in their department
        "employees.read", "employees.update",
        # Approve/reject
        "proposals.approve", "proposals.reject",
        "endorsements.approve", "endorsements.reject",
        "policies.update", "policies.change_seller",
        # Collections management
        "collections.assign", "collections.reassign",
        "receipts.assign",
        # Reports & dashboard
        "reports.read", "reports.admin",
        "dashboard.view", "dashboard.collection",
        # Shifts
        "shifts.read", "shifts.manage",
        # Incidents & tow admin
        "incidents.admin", "tow_services.admin",
        # Cancellations (create + approve undo)
        "cancellations.create",
    ],

    "auxiliar": [
        # Policies
        "policies.create", "policies.read",
        # Clients
        "clients.create", "clients.read", "clients.update",
        # Vehicles & coverages
        "vehicles.create", "vehicles.read", "vehicles.update",
        "coverages.read",
        # Payments (read only, Cobranza edits)
        "payments.read", "payments.create",
        # Receipts
        "receipts.read",
        # Endorsements
        "endorsements.create", "endorsements.read",
        # Renewals
        "renewals.read",
        # Promotions (read)
        "promotions.read",
        # Dashboard
        "dashboard.view",
        # Notifications (read)
        "notifications.read",
    ],

    "cobrador": [
        # Proposals (core function)
        "proposals.create", "proposals.read_own",
        # Receipts
        "receipts.read_assigned", "receipts.use",
        # Clients (assigned only)
        "clients.read_assigned",
        # Collections (own route + create visit notices)
        "collections.read_own_route", "collections.create",
        # Payments (read)
        "payments.read",
        # Dashboard
        "dashboard.view",
    ],

    "vendedor": [
        # Policies (core function)
        "policies.create", "policies.read_own",
        # Clients
        "clients.create", "clients.read",
        # Vehicles & coverages
        "vehicles.create", "vehicles.read", "vehicles.update",
        "coverages.read",
        # Renewals (assigned)
        "renewals.read_assigned",
        # Promotions (read, to inform clients)
        "promotions.read",
        # Dashboard
        "dashboard.view",
    ],

    "ajustador": [
        # Incidents (core function)
        "incidents.read", "incidents.read_assigned", "incidents.create",
        "incidents.update",
        # Tow services
        "tow_services.read", "tow_services.read_assigned", "tow_services.create",
        "tow_services.update",
        # Shifts
        "shifts.read",
        # Read basics
        "clients.read",
        "policies.read",
        # Dashboard
        "dashboard.view",
    ],

    "viewer": [
        # Read-only across most modules
        "policies.read", "clients.read", "vehicles.read", "coverages.read",
        "payments.read", "proposals.read", "collections.read",
        "receipts.read", "incidents.read", "tow_services.read",
        "endorsements.read", "cancellations.read", "renewals.read",
        "promotions.read", "notifications.read",
        "dashboard.view",
        "reports.read",
    ],
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
    logger.info("  %d permissions seeded (%d new)", len(mapping), len(PERMISSIONS))
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
