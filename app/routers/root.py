from fastapi import APIRouter

router = APIRouter(
    tags=["Root"]
)

@router.get("/")
def root():
    return {
        "project": "Social Media Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

    
@router.get("/health")
def health():
    return {
        "status": "healthy"
    }