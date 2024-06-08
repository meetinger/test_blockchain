from fastapi import FastAPI

from src.api.router import base_router

app = FastAPI(title="Bitcoin Blockchain Explorer")

app.include_router(base_router)
