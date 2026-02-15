"""Business logic for the Receipts module."""

from __future__ import annotations

from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payments import Receipt
from app.modules.receipts.repository import ReceiptRepository
from app.modules.receipts.schemas import (
    ReceiptAssign,
    ReceiptBatchCreate,
    ReceiptVerify,
)


class ReceiptService:
    def __init__(self, session: AsyncSession):
        self.repo = ReceiptRepository(session)

    # ── Listing ───────────────────────────────────────────────────────

    async def list_receipts(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        status_filter: str | None = None,
        collector_id: int | None = None,
        policy_id: int | None = None,
    ) -> dict:
        receipts, total = await self.repo.list_receipts(
            skip=skip,
            limit=limit,
            status=status_filter,
            collector_id=collector_id,
            policy_id=policy_id,
        )
        return {"items": receipts, "total": total, "skip": skip, "limit": limit}

    async def get_receipt(self, receipt_id: int) -> Receipt:
        receipt = await self.repo.get_by_id(receipt_id)
        if receipt is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recibo no encontrado",
            )
        return receipt

    async def get_by_number(self, receipt_number: str) -> Receipt:
        receipt = await self.repo.get_by_number(receipt_number.upper())
        if receipt is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recibo no encontrado",
            )
        return receipt

    async def get_by_collector(self, collector_id: int) -> list[Receipt]:
        return await self.repo.get_by_collector(collector_id)

    # ── Batch Creation ────────────────────────────────────────────────

    async def create_batch(self, data: ReceiptBatchCreate) -> dict:
        # Generate receipt numbers: prefix + zero-padded 4-digit number
        numbers = [
            f"{data.prefix}{i:04d}" for i in range(data.start, data.end + 1)
        ]

        # Skip duplicates
        existing = await self.repo.existing_receipt_numbers(numbers)
        new_numbers = [n for n in numbers if n not in existing]

        if not new_numbers:
            return {
                "created": 0,
                "skipped": len(numbers),
                "receipt_numbers": [],
            }

        receipts = [Receipt(receipt_number=n) for n in new_numbers]
        await self.repo.create_many(receipts)

        return {
            "created": len(new_numbers),
            "skipped": len(existing),
            "receipt_numbers": new_numbers,
        }

    # ── Assignment ────────────────────────────────────────────────────

    async def assign_receipts(self, data: ReceiptAssign) -> dict:
        # Validate collector exists and is active cobrador
        collector = await self.repo.get_collector(data.collector_id)
        if collector is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cobrador no encontrado o inactivo",
            )

        # Only assign receipts with status 'unassigned'
        receipts = await self.repo.get_receipts_by_ids(
            data.receipt_ids, status_filter="unassigned"
        )
        if not receipts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ninguno de los recibos indicados esta disponible para asignar",
            )

        # Respect receipt_limit
        active_count = await self.repo.count_active_receipts_for_collector(
            data.collector_id
        )
        available_slots = collector.receipt_limit - active_count

        if available_slots <= 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El cobrador ya tiene {active_count} recibos activos "
                f"(limite: {collector.receipt_limit})",
            )

        truncated = 0
        if len(receipts) > available_slots:
            truncated = len(receipts) - available_slots
            receipts = receipts[:available_slots]

        today = date.today()
        for receipt in receipts:
            receipt.collector_id = data.collector_id
            receipt.assignment_date = today
            receipt.status = "assigned"

        await self.repo.update(receipts[0])  # flush all dirty objects

        message = None
        if truncated > 0:
            message = (
                f"Se asignaron {len(receipts)} recibos. "
                f"{truncated} recibos fueron omitidos por limite del cobrador "
                f"({collector.receipt_limit})"
            )

        return {
            "assigned": len(receipts),
            "truncated": truncated,
            "message": message,
        }

    # ── Verification ──────────────────────────────────────────────────

    async def verify_receipt(self, data: ReceiptVerify) -> dict:
        receipt = await self.repo.get_by_number(data.receipt_number)
        if receipt is None:
            return {
                "valid": False,
                "receipt": None,
                "skipped_receipts": [],
                "warning": f"Recibo {data.receipt_number} no existe",
            }

        # Must belong to the indicated collector
        if receipt.collector_id != data.collector_id:
            return {
                "valid": False,
                "receipt": receipt,
                "skipped_receipts": [],
                "warning": "El recibo no esta asignado a este cobrador",
            }

        # Check status
        r_status = receipt.status
        if hasattr(r_status, "value"):
            r_status = r_status.value

        if r_status == "used" and receipt.policy_id == data.policy_id and receipt.payment_id == data.payment_id:
            return {
                "valid": True,
                "receipt": receipt,
                "skipped_receipts": [],
                "warning": "Recibo ya fue usado para este mismo pago",
            }

        if r_status != "assigned":
            return {
                "valid": False,
                "receipt": receipt,
                "skipped_receipts": [],
                "warning": f"Status invalido: {r_status}. Se requiere 'assigned'",
            }

        # Mark as used
        receipt.status = "used"
        receipt.policy_id = data.policy_id
        receipt.payment_id = data.payment_id
        receipt.usage_date = date.today()

        # Cancel any loss schedule for this receipt
        await self.repo.cancel_loss_schedule(data.receipt_number)

        await self.repo.update(receipt)

        # Detect skipped receipts
        skipped = await self.repo.get_skipped_receipts(
            data.collector_id, data.receipt_number
        )

        warning = None
        if skipped:
            warning = (
                f"Se detectaron {len(skipped)} recibos sin usar antes de este"
            )

        return {
            "valid": True,
            "receipt": receipt,
            "skipped_receipts": skipped,
            "warning": warning,
        }

    # ── Cancel ────────────────────────────────────────────────────────

    async def cancel_receipt(self, receipt_id: int) -> Receipt:
        receipt = await self.get_receipt(receipt_id)

        r_status = receipt.status
        if hasattr(r_status, "value"):
            r_status = r_status.value

        if r_status in ("assigned", "unassigned"):
            receipt.status = "cancelled_undelivered"
        elif r_status in ("used", "delivered"):
            receipt.status = "cancelled"
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"No se puede cancelar un recibo con status '{r_status}'",
            )

        return await self.repo.update(receipt)

    # ── Mark Lost ─────────────────────────────────────────────────────

    async def mark_lost(self, receipt_id: int) -> Receipt:
        receipt = await self.get_receipt(receipt_id)

        r_status = receipt.status
        if hasattr(r_status, "value"):
            r_status = r_status.value

        if r_status != "assigned":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Solo se pueden marcar como extraviados recibos con status 'assigned'",
            )

        receipt.status = "lost"
        return await self.repo.update(receipt)
