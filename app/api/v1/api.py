from fastapi import APIRouter

from app.api.v1.endpoints import (
    analysis,
    auth,
    comments,
    metrics,
    situations,
    topics,
    users,
)

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(topics.router, prefix="/topics", tags=["Topics"])
router.include_router(situations.router, prefix="/situations", tags=["Situations"])
router.include_router(comments.router, prefix="/comments", tags=["Comments"])
router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
router.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
