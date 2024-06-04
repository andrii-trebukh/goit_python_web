import uvicorn
import redis.asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from src.routes.contacts import router as contacts_router
from src.routes.auth import router as auth_router
from src.routes.users import router as users_router
from src.conf.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    The lifespan function is a coroutine that runs before and after the server starts.
    It's used to initialize any resources that need to be available for the entire lifetime of the application.
    In this case, we're using it to initialize our Redis connection pool.
    
    :param app: FastAPI: Pass the fastapi instance to the lifespan function
    :return: A context manager, which is used to manage the lifetime of a resource
    :doc-author: Trelent
    """
    r = await redis.asyncio.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0,
        encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(r)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(contacts_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix='/api')

origins = [ 
    "http://localhost:3000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
