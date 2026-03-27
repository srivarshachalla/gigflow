from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth as auth_router
from app.routers import projects as projects_router
from app.routers import tasks as tasks_router

app = FastAPI(
    title="GigFlow API",
    description="Freelance project and time tracking API",
    version = "1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(projects_router.router)
app.include_router(tasks_router.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "GigFlow is running"}
