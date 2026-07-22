import csv
import io
import uuid
from typing import Any

from openpyxl import Workbook
from fastapi.responses import StreamingResponse


def export_to_csv(rows: list[dict[str, Any]], filename: str) -> StreamingResponse:
    """Generic CSV export - takes a list of dicts (already-serialized
    records) and streams back a downloadable CSV file."""
    if not rows:
        output = io.StringIO()
        output.write("No records to export\n")
        output.seek(0)
    else:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}.csv"},
    )


def export_to_excel(rows: list[dict[str, Any]], filename: str) -> StreamingResponse:
    """Generic Excel (.xlsx) export - takes a list of dicts and streams
    back a downloadable Excel file."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Export"

    if rows:
        headers = list(rows[0].keys())
        ws.append(headers)
        for row in rows:
            ws.append([str(v) if v is not None else "" for v in row.values()])
    else:
        ws.append(["No records to export"])

    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}.xlsx"},
    )


def serialize_for_export(items: list, exclude_fields: set[str] = None) -> list[dict]:
    """Converts a list of SQLAlchemy model instances into plain dicts
    suitable for CSV/Excel export, converting UUIDs/dates to strings
    and dropping internal-only fields."""
    exclude_fields = exclude_fields or {"tenant_id", "is_deleted", "deleted_at"}
    rows = []
    for item in items:
        row = {}
        for column in item.__table__.columns:
            if column.name in exclude_fields:
                continue
            value = getattr(item, column.name)
            row[column.name] = str(value) if value is not None else ""
        rows.append(row)
    return rows