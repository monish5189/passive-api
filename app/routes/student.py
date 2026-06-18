from fastapi import APIRouter
import math

router = APIRouter(
    prefix="/api/v2/student",
    tags=["Student V2"]
)

@router.get("/attendance")
async def attendance(
    total_classes: int,
    attended_classes: int,
    required_percentage: float = 75
):
    current = (attended_classes / total_classes) * 100

    needed = 0

    if current < required_percentage:
        num = (
            required_percentage * total_classes
            - 100 * attended_classes
        )

        den = 100 - required_percentage

        needed = math.ceil(num / den)

    return {
        "current_percentage": round(current, 2),
        "required_percentage": required_percentage,
        "classes_needed": max(0, needed)
    }

@router.get("/cgpa")
async def cgpa(
    total_grade_points: float,
    total_credits: float
):
    return {
        "cgpa": round(
            total_grade_points / total_credits,
            2
        )
    }

@router.get("/percentage")
async def percentage(
    obtained_marks: float,
    total_marks: float
):
    return {
        "percentage": round(
            (obtained_marks / total_marks) * 100,
            2
        )
    }

@router.get("/exam-countdown")
async def exam_countdown(
    days_remaining: int
):
    return {
        "days_remaining": days_remaining,
        "weeks_remaining": round(
            days_remaining / 7,
            2
        )
    }
