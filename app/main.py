from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from .routes import uploads, analysis, upload_analyze# type: ignore

app = FastAPI(
    title='Real Estate Analysis API',
    description='API for real estate analysis',
    version='1.0.0',
)

# Create router instance
router = APIRouter()

origins = [
    "http://localhost:3000",    # Your Next.js frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@router.get("/api/test")
async def testApi():
    return {"message": "successful api connection"}

# Include routers
app.include_router(router)  # Include the main router
app.include_router(uploads.router, prefix="/api/upload")
app.include_router(analysis.router, prefix="/api/analysis")
app.include_router(upload_analyze.router, prefix="/api/upload-analyze")
