import uvicorn
from fastapi import FastAPI
from src.routes.contacts import router as contacts_router
from src.routes.auth import router as auth_router


app = FastAPI()

app.include_router(contacts_router, prefix="/api")
app.include_router(auth_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
