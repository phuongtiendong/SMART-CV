"""Routes for job management."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.models.database import (
    create_job,
    delete_job,
    get_all_jobs,
    get_job_by_id,
    update_job,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models
class JobCreate(BaseModel):
    title: str
    description: str


class JobUpdate(BaseModel):
    title: str
    description: str


class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    created_at: str
    updated_at: str


class SuccessResponse(BaseModel):
    success: bool
    data: Optional[JobResponse] = None
    message: Optional[str] = None
    error: Optional[str] = None


class JobsListResponse(BaseModel):
    success: bool
    data: List[JobResponse]


@router.get("", response_model=JobsListResponse)
async def list_jobs():
    """Get all jobs."""
    try:
        jobs = get_all_jobs()
        return {"success": True, "data": jobs}
    except Exception as e:
        logger.error("Error listing jobs: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{job_id}", response_model=SuccessResponse)
async def get_job(job_id: int):
    """Get a specific job by ID."""
    try:
        job = get_job_by_id(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        return {"success": True, "data": job}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting job %s: %s", job_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_job_route(job: JobCreate):
    """Create a new job."""
    try:
        title = job.title.strip()
        description = job.description.strip()
        
        if not title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title is required"
            )
        if not description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Description is required"
            )
        
        job_id = create_job(title, description)
        created_job = get_job_by_id(job_id)
        return {"success": True, "data": created_job}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating job: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{job_id}", response_model=SuccessResponse)
async def update_job_route(job_id: int, job: JobUpdate):
    """Update an existing job."""
    try:
        existing_job = get_job_by_id(job_id)
        if not existing_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        title = job.title.strip()
        description = job.description.strip()
        
        if not title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title is required"
            )
        if not description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Description is required"
            )
        
        success = update_job(job_id, title, description)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update job"
            )
        
        updated_job = get_job_by_id(job_id)
        return {"success": True, "data": updated_job}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating job %s: %s", job_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{job_id}", response_model=SuccessResponse)
async def delete_job_route(job_id: int):
    """Delete a job."""
    try:
        job = get_job_by_id(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        success = delete_job(job_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete job"
            )
        
        return {"success": True, "message": "Job deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting job %s: %s", job_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
