import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from src.api.auth.router import router as auth_router
from src.core.elasticsearch.es_servise import elastic_service
from src.core.redis.redis_service import redis_service
from src.api.documents.router import router as documents_router
from src.api.search.router import router as search_router
from src.api.ws.router import router as ws_router
from src.core.db.database import engine, init_models
from src.core.rabbitmq.client import rabbitmq_client
from src.core.rabbitmq.to_back import start_consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_models()
    await elastic_service.init_index()
    await rabbitmq_client.connect()
    await start_consumer()
    try:
        yield
    finally:
        await engine.dispose()
        await redis_service.client.aclose()
        await rabbitmq_client.close()


app = FastAPI(
    title="summer_practice",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(search_router)
app.include_router(ws_router)

Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


@app.get("/")
async def ping() -> dict[str, str]:
    return {"ping": "pong"}


def main() -> None:
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()