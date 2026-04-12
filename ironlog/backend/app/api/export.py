from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import csv
import json
import io
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.workout import WorkoutSession, WorkoutExercise, Set
from app.models.exercise import Exercise

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/csv")
async def export_csv(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export all workout data as CSV"""
    
    # Fetch all sessions with exercises and sets
    result = await db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.user_id == current_user.id)
        .order_by(WorkoutSession.started_at.desc())
    )
    sessions = result.scalars().all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Session Date',
        'Session Name',
        'Exercise',
        'Set Number',
        'Weight (kg)',
        'Reps',
        'RPE',
        'RIR',
        'Set Type',
        'Is PR',
        'Notes'
    ])
    
    # Write data
    for session in sessions:
        session_date = session.started_at.strftime('%Y-%m-%d %H:%M:%S')
        session_name = session.session_name or 'Workout'
        
        # Fetch exercises for this session
        exercises_result = await db.execute(
            select(WorkoutExercise)
            .where(WorkoutExercise.session_id == session.id)
            .order_by(WorkoutExercise.exercise_order)
        )
        exercises = exercises_result.scalars().all()
        
        for workout_exercise in exercises:
            # Get exercise name
            exercise_result = await db.execute(
                select(Exercise).where(Exercise.id == workout_exercise.exercise_id)
            )
            exercise = exercise_result.scalar_one_or_none()
            exercise_name = exercise.display_name if exercise else 'Unknown'
            
            # Fetch sets
            sets_result = await db.execute(
                select(Set)
                .where(Set.workout_exercise_id == workout_exercise.id)
                .order_by(Set.set_order)
            )
            sets = sets_result.scalars().all()
            
            for set_data in sets:
                writer.writerow([
                    session_date,
                    session_name,
                    exercise_name,
                    set_data.set_order,
                    set_data.weight_kg,
                    set_data.reps,
                    set_data.rpe or '',
                    set_data.rir or '',
                    set_data.set_type,
                    'Yes' if set_data.is_pr else 'No',
                    workout_exercise.notes or ''
                ])
    
    # Prepare response
    output.seek(0)
    filename = f"ironlog_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/json")
async def export_json(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export all workout data as JSON"""
    
    # Fetch all sessions
    result = await db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.user_id == current_user.id)
        .order_by(WorkoutSession.started_at.desc())
    )
    sessions = result.scalars().all()
    
    export_data = {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
        },
        "export_date": datetime.now().isoformat(),
        "sessions": []
    }
    
    for session in sessions:
        session_data = {
            "id": session.id,
            "started_at": session.started_at.isoformat(),
            "finished_at": session.finished_at.isoformat() if session.finished_at else None,
            "session_name": session.session_name,
            "notes": session.notes,
            "bodyweight_kg": session.bodyweight_kg,
            "exercises": []
        }
        
        # Fetch exercises
        exercises_result = await db.execute(
            select(WorkoutExercise)
            .where(WorkoutExercise.session_id == session.id)
            .order_by(WorkoutExercise.exercise_order)
        )
        exercises = exercises_result.scalars().all()
        
        for workout_exercise in exercises:
            # Get exercise details
            exercise_result = await db.execute(
                select(Exercise).where(Exercise.id == workout_exercise.exercise_id)
            )
            exercise = exercise_result.scalar_one_or_none()
            
            exercise_data = {
                "exercise_id": workout_exercise.exercise_id,
                "exercise_name": exercise.display_name if exercise else 'Unknown',
                "exercise_order": workout_exercise.exercise_order,
                "notes": workout_exercise.notes,
                "sets": []
            }
            
            # Fetch sets
            sets_result = await db.execute(
                select(Set)
                .where(Set.workout_exercise_id == workout_exercise.id)
                .order_by(Set.set_order)
            )
            sets = sets_result.scalars().all()
            
            for set_data in sets:
                exercise_data["sets"].append({
                    "set_order": set_data.set_order,
                    "set_type": set_data.set_type,
                    "weight_kg": set_data.weight_kg,
                    "reps": set_data.reps,
                    "rpe": set_data.rpe,
                    "rir": set_data.rir,
                    "is_pr": set_data.is_pr,
                    "logged_at": set_data.logged_at.isoformat() if set_data.logged_at else None
                })
            
            session_data["exercises"].append(exercise_data)
        
        export_data["sessions"].append(session_data)
    
    # Prepare response
    json_str = json.dumps(export_data, indent=2)
    filename = f"ironlog_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    return StreamingResponse(
        iter([json_str]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
