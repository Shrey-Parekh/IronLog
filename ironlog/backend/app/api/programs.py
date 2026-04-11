"""Programs API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.program import TrainingProgram, ProgramDay
from app.schemas.program import (
    GenerateSplitRequest,
    GenerateSplitResponse,
    TrainingProgramResponse,
)
from app.ml.split_optimizer import SplitOptimizer
from sqlalchemy import select
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/programs", tags=["programs"])


@router.post("/generate", response_model=GenerateSplitResponse)
async def generate_split(
    request: GenerateSplitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a training split based on user preferences."""
    optimizer = SplitOptimizer(db)
    
    # Generate the split
    split_data = await optimizer.generate_split(
        user_id=str(current_user.id),
        days_per_week=request.days_per_week,
        goal=request.goal,
        experience_level=request.experience_level,
    )
    
    # Create program in database
    program = TrainingProgram(
        user_id=current_user.id,
        name=f"{split_data['split_type'].replace('_', ' ').title()} - {request.days_per_week} days/week",
        days_per_week=request.days_per_week,
        is_active=False,  # User must explicitly activate
    )
    db.add(program)
    await db.flush()
    
    # Create program days
    for day_data in split_data["days"]:
        program_day = ProgramDay(
            program_id=program.id,
            day_number=day_data["day_number"],
            day_name=day_data["day_name"],
            target_muscle_groups=day_data["target_muscle_groups"],
        )
        db.add(program_day)
    
    await db.commit()
    await db.refresh(program)
    
    # Load days
    query = (
        select(TrainingProgram)
        .where(TrainingProgram.id == program.id)
        .options(selectinload(TrainingProgram.days))
    )
    result = await db.execute(query)
    program = result.scalar_one()
    
    # Calculate estimated volume per muscle
    estimated_volume = {}
    for day in split_data["days"]:
        for mg_id in day.get("target_muscle_groups", []):
            estimated_volume[str(mg_id)] = estimated_volume.get(str(mg_id), 0) + 3  # Estimate 3 sets per muscle per day
    
    return GenerateSplitResponse(
        program=TrainingProgramResponse.model_validate(program),
        rationale=split_data["rationale"],
        estimated_volume_per_muscle=estimated_volume,
    )


@router.get("", response_model=list[TrainingProgramResponse])
async def list_programs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all programs for the current user."""
    query = (
        select(TrainingProgram)
        .where(TrainingProgram.user_id == current_user.id)
        .options(selectinload(TrainingProgram.days))
        .order_by(TrainingProgram.created_at.desc())
    )
    result = await db.execute(query)
    programs = result.scalars().all()
    return [TrainingProgramResponse.model_validate(p) for p in programs]


@router.get("/{program_id}", response_model=TrainingProgramResponse)
async def get_program(
    program_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific program."""
    query = (
        select(TrainingProgram)
        .where(
            TrainingProgram.id == program_id,
            TrainingProgram.user_id == current_user.id,
        )
        .options(selectinload(TrainingProgram.days))
    )
    result = await db.execute(query)
    program = result.scalar_one_or_none()
    
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    return TrainingProgramResponse.model_validate(program)


@router.post("/{program_id}/activate")
async def activate_program(
    program_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Activate a program (deactivates all others)."""
    # Deactivate all programs
    query = select(TrainingProgram).where(TrainingProgram.user_id == current_user.id)
    result = await db.execute(query)
    programs = result.scalars().all()
    
    for program in programs:
        program.is_active = False
    
    # Activate the selected program
    query = select(TrainingProgram).where(
        TrainingProgram.id == program_id,
        TrainingProgram.user_id == current_user.id,
    )
    result = await db.execute(query)
    program = result.scalar_one_or_none()
    
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    program.is_active = True
    await db.commit()
    
    return {"message": "Program activated"}


@router.delete("/{program_id}")
async def delete_program(
    program_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a program."""
    query = select(TrainingProgram).where(
        TrainingProgram.id == program_id,
        TrainingProgram.user_id == current_user.id,
    )
    result = await db.execute(query)
    program = result.scalar_one_or_none()
    
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    await db.delete(program)
    await db.commit()
    
    return {"message": "Program deleted"}
