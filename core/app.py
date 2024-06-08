from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.router import base_router
from src.service.blockchair.parser import blockchair_parser


@asynccontextmanager
async def lifespan(_app: FastAPI):
    downloader_process = blockchair_parser.start_downloader_process()
    yield
    downloader_process.terminate()

app = FastAPI(title="Bitcoin Blockchain Explorer")

app.include_router(base_router)
