"""
ETL Inicial - Migración de Empleados y Usuarios
Claudy ✨ — 2026-02-27

Este script realiza la migración inicial de Fer como administrador
y prepara el terreno para el resto del equipo.
"""

import os
import asyncio
import sys
from datetime import date
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from passlib.hash import argon2

# Configuración (Ajustada para ejecución directa en el VPS)
DATABASE_URL = "postgresql+asyncpg://protegrt:Pr0tegrt_2026!@localhost:5432/sistema_proteg"

async def run_etl():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    print("🚀 Iniciando ETL de Empleados...")

    async with async_session() as session:
        # 1. Crear el primer empleado (Fer)
        # Usamos SQL directo para evitar problemas de importación de modelos en este script aislado
        
        # Primero verificamos si ya existe
        result = await session.execute(text("SELECT id FROM employee WHERE email = 'fer@protegrt.com'"))
        employee_id = result.scalar()

        if not employee_id:
            print("👤 Creando registro de empleado para Fer...")
            result = await session.execute(text("""
                INSERT INTO employee (first_name, last_name, email, hire_date, status, created_at, updated_at)
                VALUES ('Fernando', 'López', 'fer@protegrt.com', '2018-02-17', 'active', NOW(), NOW())
                RETURNING id
            """))
            employee_id = result.scalar()
            print(f"✅ Empleado creado con ID: {employee_id}")
        else:
            print(f"ℹ️ El empleado Fer ya existe (ID: {employee_id})")

        # 2. Asignar Roles (Admin, Claims, Sales)
        roles = [
            ('admin', 'director'),
            ('claims', 'staff'),
            ('sales', 'staff')
        ]
        
        for dept, level in roles:
            result = await session.execute(text(
                "SELECT id FROM employee_role WHERE employee_id = :emp_id AND department = :dept"
            ), {"emp_id": employee_id, "dept": dept})
            
            if not result.scalar():
                print(f"🛡️ Asignando rol: {dept} ({level})...")
                await session.execute(text("""
                    INSERT INTO employee_role (employee_id, department, level, is_active, start_date, created_at, updated_at)
                    VALUES (:emp_id, :dept, :level, true, '2018-02-17', NOW(), NOW())
                """), {"emp_id": employee_id, "dept": dept, "level": level})

        # 3. Crear Perfiles Específicos
        # Perfil de Ajustador
        result = await session.execute(text(
            "SELECT er.id FROM employee_role er WHERE er.employee_id = :emp_id AND er.department = 'claims'"
        ), {"emp_id": employee_id})
        role_claims_id = result.scalar()

        result = await session.execute(text("SELECT id FROM adjuster_profile WHERE employee_role_id = :rid"), {"rid": role_claims_id})
        if not result.scalar():
            print("🚔 Creando perfil de Ajustador...")
            await session.execute(text("""
                INSERT INTO adjuster_profile (employee_role_id, code, created_at, updated_at)
                VALUES (:rid, 'M1', NOW(), NOW())
            """), {"rid": role_claims_id})

        # 4. Crear Usuario de Acceso (AppUser)
        result = await session.execute(text("SELECT id FROM app_user WHERE employee_id = :emp_id"), {"emp_id": employee_id})
        if not result.scalar():
            print("🔑 Creando usuario de acceso...")
            # Contraseña: Protegrt2026!
            pwd_hash = argon2.hash("Protegrt2026!")
            await session.execute(text("""
                INSERT INTO app_user (employee_id, username, password_hash, is_active, created_at, updated_at)
                VALUES (:emp_id, 'fer', :pwd, true, NOW(), NOW())
            """), {"emp_id": employee_id, "pwd": pwd_hash})
            print("✅ Usuario 'fer' creado con éxito. Contraseña: Protegrt2026!")

        # 5. Permisos de Liquidación (Fer puede pagar)
        result = await session.execute(text("SELECT id FROM settlement_permission WHERE employee_id = :emp_id"), {"emp_id": employee_id})
        if not result.scalar():
            print("💰 Asignando permisos de liquidación...")
            await session.execute(text("""
                INSERT INTO settlement_permission (employee_id, can_pay, created_at)
                VALUES (:emp_id, true, NOW())
            """), {"emp_id": employee_id})

        await session.commit()
        print("\n✨ ETL completado con éxito. ¡Ya puedes loguearte!")

if __name__ == "__main__":
    asyncio.run(run_etl())
