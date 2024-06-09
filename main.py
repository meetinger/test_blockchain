import uvicorn

from core.settings import settings

# запуск uvicorn
if __name__ == "__main__":
    uvicorn.run(
        "core.app:app",
        host='0.0.0.0',
        port=settings.HTTP_PORT,
        root_path=settings.ROOT_PATH or '',
        reload=False,
    )
