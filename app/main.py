import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from .routes import router
from .init_db import init_db

app = FastAPI()

static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:8000",
        "http://koodilahnat.com",
        "https://koodilahnat.com",
        "http://172.105.84.210",
        "http://koodilahnat.com:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    try:
        await init_db()
    except Exception as e:
        print(f"Error initializing database: {e}")


@app.get("/")
async def root():
    return {"message": "Welcome to Pretty Interesting Sky Samples API"}
