from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.services.report_service import build_report

router = APIRouter()


@router.post("/generate")
def generate_report(payload: dict):
    report_format = str(payload.get("format", "PDF")).upper()
    try:
        content, media_type, filename = build_report(
            payload.get("records", []),
            report_format,
            payload.get("dataset_name", "dataset"),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
