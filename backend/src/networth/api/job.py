from fastapi import APIRouter, HTTPException
from typing import List
import ksuid

from networth.models.job import Job

router = APIRouter()


@router.post("/jobs/", response_model=Job)
async def create_job(job: JobCreate):
    # Generate a new KSUID for the job
    job_id = str(ksuid.ksuid())

    # Create the job with the generated ID
    return Job(
        id=job_id, name=job.name, start_date=job.start_date, end_date=job.end_date
    )


@router.get("/jobs/{job_id}", response_model=Job)
async def read_job(job_id: str):
    # Add your database query logic here
    # For now, raising a not found error
    raise HTTPException(status_code=404, detail="Job not found")


@router.get("/jobs/", response_model=List[Job])
async def list_jobs():
    # Add your database query logic here
    # For now, returning an empty list
    return []


@router.put("/jobs/{job_id}", response_model=Job)
async def update_job(job_id: str, job: JobCreate):
    # Add your database update logic here
    # For now, raising a not found error
    raise HTTPException(status_code=404, detail="Job not found")


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    # Add your database deletion logic here
    # For now, raising a not found error
    raise HTTPException(status_code=404, detail="Job not found")
