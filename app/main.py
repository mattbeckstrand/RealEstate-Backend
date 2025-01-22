from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import uploads, analysis # type: ignore

app = FastAPI(
    title='Real Estate Analysis API',
    description='API for real estate analysis',
    version='1.0.0',
)

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

app.include_router(uploads.router, prefix="/api/uploads")
app.include_router(analysis.router, prefix="/api/analysis")
