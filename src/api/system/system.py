from fastapi import APIRouter, BackgroundTasks, status
from starlette.responses import JSONResponse

from src.service.blockchair.parser import blockchair_parser

system_router = APIRouter(prefix="/system", tags=["system"])


@system_router.post("/force-download-dump")
async def get_system_status(background_tasks: BackgroundTasks):
    def _worker():
        blockchair_parser.force_download_and_insert_to_db()

    background_tasks.add_task(_worker)
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={"status": "Pending"})