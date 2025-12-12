"""Routes for CV processing and ranking."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, status
from pydantic import BaseModel

from backend.services.cv_processor import CVProcessor
from backend.services.ranking_service import RankingService
from backend.models.database import get_job_by_id

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models
class RankingItem(BaseModel):
    id: int
    job_id: Optional[int] = None
    job_title: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    score: Optional[float] = None
    created_at: Optional[str] = None


class RankingResponse(BaseModel):
    success: bool
    data: List[RankingItem]


class CVProcessResponse(BaseModel):
    success: bool
    data: dict


@router.post("/process", response_model=CVProcessResponse)
async def process_cv(
    file: UploadFile = File(...),
    job_id: int = Form(...)
):
    """Process a CV file and score it against a job."""
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed"
            )
        
        # Verify job exists
        job = get_job_by_id(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        jd_text = job['description']
        
        # Read file bytes
        file_bytes = await file.read()
        
        # Process CV
        processor = CVProcessor()
        result = processor.process_cv(file_bytes, job_id, jd_text)
        
        return {
            "success": True,
            "data": {
                "candidate_info": result["info"],
                "scores": result["score_dict"],
                "reasons": result["reason_dict"],
                "total_score": result["total_score"]
            }
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error("Validation error processing CV: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error processing CV: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/ranking", response_model=RankingResponse)
async def get_ranking(job_id: Optional[int] = Query(None)):
    """Get CV ranking."""
    try:
        ranking = RankingService.get_ranking_dict(job_id)
        return {"success": True, "data": ranking}
    except Exception as e:
        logger.error("Error getting ranking: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
