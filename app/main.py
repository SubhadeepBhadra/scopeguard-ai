import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .seed_data import seed_database
from .routers import auth_router, projects_router, scope_router, billing_router, analytics_router

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema & seed demo dataset
    Base.metadata.create_all(bind=engine)
    try:
        seed_database()
    except Exception as e:
        print(f"Warning during seed: {e}")
    yield

app = FastAPI(
    title="ScopeGuard AI - Client Scope Creep & Change Order Engine",
    description="Production-grade AI SaaS application empowering agencies and freelancers to detect scope creep, generate diplomatic client responses, and issue legally enforceable change orders.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Graceful Error Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = str(exc)
    print(f"[Application Error] Path: {request.url.path} | Error: {error_msg}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "An unexpected error occurred while processing your request. Please try again or contact support.",
            "detail": error_msg if os.getenv("ENVIRONMENT") == "development" else "Internal server error."
        }
    )

# Include Routers
app.include_router(auth_router.router)
app.include_router(projects_router.router)
app.include_router(scope_router.router)
app.include_router(billing_router.router)
app.include_router(analytics_router.router)

# Mount Static Files
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "ScopeGuard AI Core",
        "version": "1.0.0",
        "architecture": "production-ready"
    }

@app.get("/", include_in_schema=False)
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "ScopeGuard AI API is operational. Static frontend not yet compiled."}
