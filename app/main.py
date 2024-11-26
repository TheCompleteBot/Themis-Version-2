# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import router as api_router
from app.middleware import LoggingMiddleware
from app.core.rate_limit import limiter
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse
from starlette.requests import Request
from pathlib import Path

app = FastAPI(
    title="Themis Contract Generation API",
    description="API for generating legal contracts using Themis LLM",
    version="1.0.0",
)

# CORS Middleware Configuration
origins = [
    "http://localhost:5500",  # Frontend server (replace with your frontend origin)
    "http://127.0.0.1:5500",
    "http://localhost:3000",   # Next.js default port
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True, 
    allow_methods=["*"],    
    allow_headers=["*"],    
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)

# Configure rate limiter
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded."}
    )

# Define the path to the 'generated_contracts' directory
BASE_DIR = Path(__file__).resolve().parent
GENERATED_CONTRACTS_DIR = BASE_DIR.parent / "generated_contracts"

# Ensure the 'generated_contracts' directory exists
if not GENERATED_CONTRACTS_DIR.exists():
    GENERATED_CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)

# Mount the 'generated_contracts' directory to serve static files
app.mount(
    "/generated_contracts",
    StaticFiles(directory=str(GENERATED_CONTRACTS_DIR)),
    name="generated_contracts"
)

app.include_router(api_router, prefix="/api/v1")

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to Themis Contract Generation API"}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}
