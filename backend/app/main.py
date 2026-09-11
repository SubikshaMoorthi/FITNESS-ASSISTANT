from __future__ import annotations

import sys
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.auth import create_access_token, get_current_user, hash_password, verify_password
from backend.app.database import (
    DailyCheck,
    MealRecommendationRecord,
    ProgressHistory,
    RecommendationRecord,
    SessionLocal,
    User,
    UserProfile,
    WaterIntake,
    WorkoutFeedback,
    WorkoutPlanRecord,
    get_db,
)

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ml.decision_engine import recommend_intervention
from ml.models.readiness_model import load_readiness_model
from backend.app.nutrition import generate_meal_recommendations
from backend.app.workout_plan import generate_workout_plan
from backend.app.what_if import analyze_what_if

app = FastAPI(title='Intelligent Fitness Assistant API')
WATER_GOAL_ML = 2500

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


class RecommendationRequest(BaseModel):
    profile: dict[str, Any] = Field(default_factory=dict)
    daily_data: dict[str, Any] = Field(default_factory=dict)
    history: dict[str, Any] = Field(default_factory=dict)


class RecommendationResponse(BaseModel):
    readiness_level: str
    confidence: float
    intervention: str
    score: float
    main_factors: list[str]
    reason: str
    all_scores: dict[str, float]


class SignupRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict[str, Any]


class TrainerPlanRequest(BaseModel):
    profile: dict[str, Any] = Field(default_factory=dict)
    daily_data: dict[str, Any] = Field(default_factory=dict)
    recommendation: RecommendationResponse


class WhatIfRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)


class NutritionAlternativeRequest(BaseModel):
    meal_type: Literal['breakfast', 'lunch', 'snack', 'dinner']
    current_meal: str | None = Field(default=None, max_length=300)
    high_protein: bool = False


class WaterIntakeRequest(BaseModel):
    amount_ml: int = Field(..., ge=1, le=2000)


class WorkoutFeedbackRequest(BaseModel):
    workout_name: str = Field(..., min_length=1, max_length=120)
    readiness_level: str = Field(..., min_length=1, max_length=30)
    intervention: str = Field(..., min_length=1, max_length=50)
    completion_status: Literal['completed', 'partial', 'skipped']
    completion_percentage: float = Field(..., ge=0, le=100)
    difficulty: Literal['Easy', 'Moderate', 'Difficult', 'Very Difficult', 'Not rated']
    feedback: str | None = Field(default=None, max_length=1000)


class WorkoutFeedbackResponse(WorkoutFeedbackRequest):
    profile_id: int | None = None
    id: int
    created_at: datetime | None = None


class UserProfileCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    age: int = Field(..., ge=10, le=120)
    gender: str | None = Field(default=None, max_length=20)
    height: float = Field(..., gt=0)
    weight: float = Field(..., gt=0)
    fitness_goal: Literal['Weight Loss', 'Muscle Gain', 'General Fitness', 'Improve Endurance']
    fitness_level: Literal['Beginner', 'Intermediate', 'Advanced']
    workout_preference: Literal['Home', 'Gym', 'Both']
    dietary_preference: Literal['Vegetarian', 'Non-Vegetarian', 'Vegan', 'No Preference']
    available_workout_minutes: int = Field(default=45, ge=0, le=180)


class UserProfileUpdate(UserProfileCreate):
    pass


class UserProfileResponse(BaseModel):
    id: int
    name: str
    age: int
    gender: str | None
    height: float
    weight: float
    bmi: float
    fitness_goal: str
    fitness_level: str
    workout_preference: str
    dietary_preference: str
    available_workout_minutes: int
    created_at: datetime | None = None
    updated_at: datetime | None = None


def calculate_bmi(weight: float, height_cm: float) -> float:
    height_m = height_cm / 100.0
    if height_m <= 0:
        raise ValueError('Height must be greater than zero.')
    return round(weight / (height_m * height_m), 2)


def map_profile_to_response(profile: UserProfile) -> UserProfileResponse:
    return UserProfileResponse(
        id=profile.id,
        name=profile.name,
        age=profile.age,
        gender=profile.gender,
        height=profile.height,
        weight=profile.weight,
        bmi=profile.bmi,
        fitness_goal=profile.fitness_goal,
        fitness_level=profile.fitness_level,
        workout_preference=profile.workout_preference,
        dietary_preference=profile.dietary_preference,
        available_workout_minutes=profile.available_workout_minutes,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


def map_feedback_to_response(feedback: WorkoutFeedback) -> WorkoutFeedbackResponse:
    return WorkoutFeedbackResponse(
        id=feedback.id,
        profile_id=feedback.profile_id,
        workout_name=feedback.workout_name,
        readiness_level=feedback.readiness_level,
        intervention=feedback.intervention,
        completion_status=feedback.completion_status,
        completion_percentage=feedback.completion_percentage,
        difficulty=feedback.difficulty,
        feedback=feedback.feedback,
        created_at=feedback.created_at,
    )


def build_profile_data(profile_record: UserProfile, stored_payload: dict[str, Any] | None = None) -> dict[str, Any]:
    stored_payload = stored_payload or {}
    stored_profile = stored_payload.get('profile', {})
    return {
        'age': profile_record.age,
        'bmi': profile_record.bmi,
        'fitness_level': profile_record.fitness_level,
        'fitness_goal': profile_record.fitness_goal,
        'goal': stored_profile.get('goal', 'general_health'),
        'available_workout_minutes': profile_record.available_workout_minutes,
        'dietary_preference': profile_record.dietary_preference,
    }


def build_water_summary(db: Session, user_id: int, target_date: date | None = None) -> dict[str, Any]:
    target_date = target_date or date.today()
    entries = (
        db.query(WaterIntake)
        .filter(WaterIntake.user_id == user_id, WaterIntake.intake_date == target_date)
        .order_by(WaterIntake.created_at.desc(), WaterIntake.id.desc())
        .all()
    )
    total_ml = sum(entry.amount_ml for entry in entries)
    remaining_ml = max(WATER_GOAL_ML - total_ml, 0)
    percentage = round(min(total_ml / WATER_GOAL_ML * 100, 100), 1) if WATER_GOAL_ML else 0
    return {
        'date': target_date,
        'goal_ml': WATER_GOAL_ML,
        'total_ml': total_ml,
        'remaining_ml': remaining_ml,
        'percentage': percentage,
        'entries': [
            {
                'id': entry.id,
                'amount_ml': entry.amount_ml,
                'created_at': entry.created_at,
            }
            for entry in entries
        ],
    }


def build_water_history(db: Session, user_id: int, days: int) -> list[dict[str, Any]]:
    today = date.today()
    start_date = today - timedelta(days=days - 1)
    entries = (
        db.query(WaterIntake)
        .filter(WaterIntake.user_id == user_id, WaterIntake.intake_date >= start_date)
        .all()
    )
    totals: dict[date, int] = {}
    for entry in entries:
        totals[entry.intake_date] = totals.get(entry.intake_date, 0) + entry.amount_ml

    return [
        {
            'date': start_date + timedelta(days=index),
            'total_ml': totals.get(start_date + timedelta(days=index), 0),
            'goal_ml': WATER_GOAL_ML,
            'percentage': round(min(totals.get(start_date + timedelta(days=index), 0) / WATER_GOAL_ML * 100, 100), 1),
        }
        for index in range(days)
    ]


def as_date(value: datetime | date | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    return value


def readiness_points(recommendations: list[RecommendationRecord]) -> list[dict[str, Any]]:
    points = []
    for item in reversed(recommendations):
        result = item.result or {}
        points.append(
            {
                'readiness_level': result.get('readiness_level'),
                'score': result.get('score'),
                'confidence': result.get('confidence'),
                'intervention': result.get('intervention'),
                'created_at': item.created_at,
                'date': as_date(item.created_at),
            }
        )
    return points


@lru_cache(maxsize=1)
def get_readiness_model():
    return load_readiness_model()


def build_feature_row(profile: dict[str, Any], daily_data: dict[str, Any], history: dict[str, Any]) -> dict[str, Any]:
    return {
        'age': profile.get('age', 30),
        'bmi': profile.get('bmi', 25.0),
        'sleep_hours': daily_data.get('sleep_hours', 7.0),
        'steps': daily_data.get('steps', 8000),
        'active_minutes': daily_data.get('active_minutes', 30),
        'calories_burned': daily_data.get('calories_burned', 2200),
        'workout_frequency': profile.get('workout_frequency', 2),
        'workout_intensity': daily_data.get('workout_intensity', 5),
        'previous_workout_intensity': history.get('recent_workout_load', daily_data.get('workout_intensity', 5)),
        'fatigue_score': daily_data.get('fatigue_score', 3),
        'recovery_score': daily_data.get('recovery_score', 60),
        'fitness_level': profile.get('fitness_level', 'Intermediate'),
        'goal': profile.get('goal', 'general_health'),
        'adherence_rate': history.get('adherence_rate', 0.7),
        'available_workout_minutes': profile.get('available_workout_minutes', 45),
    }


def build_user_history(db: Session, user_id: int, supplied: dict[str, Any]) -> dict[str, Any]:
    """Use authenticated stored feedback as history instead of trusting client user IDs."""
    history = dict(supplied)
    feedback = (
        db.query(WorkoutFeedback)
        .filter(WorkoutFeedback.user_id == user_id)
        .order_by(WorkoutFeedback.created_at.desc())
        .limit(20)
        .all()
    )
    if not feedback:
        return history

    completed = sum(item.completion_status == 'completed' for item in feedback)
    history['adherence_rate'] = completed / len(feedback)
    difficulty_rating = {'Easy': 2, 'Moderate': 5, 'Difficult': 7, 'Very Difficult': 9, 'Not rated': 5}
    history['previous_session_rating'] = max(1, 6 - round(difficulty_rating.get(feedback[0].difficulty, 5) / 2))
    return history


def predict_readiness_level(profile: dict[str, Any], daily_data: dict[str, Any], history: dict[str, Any]) -> tuple[str, float]:
    pipeline, label_encoder = get_readiness_model()
    row = pd.DataFrame([build_feature_row(profile, daily_data, history)])

    predicted_index = pipeline.predict(row)[0]
    predicted_label = label_encoder.inverse_transform([predicted_index])[0]
    probabilities = pipeline.predict_proba(row)[0]
    confidence = float(max(probabilities))
    return predicted_label, confidence


@app.get('/')
def root():
    return {
        'project': 'Intelligent Personalized Fitness and Health Assistant',
        'status': 'initialized',
        'phase': 'Model and decision engine integrated',
    }


@app.get('/health')
def health_check():
    return {'status': 'ok'}


@app.post('/auth/signup', response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='An account with this email already exists')

    user = User(name=payload.name.strip(), email=email, password_hash=hash_password(payload.password))
    db.add(user)
    db.flush()
    default_profile = UserProfile(
        user_id=user.id,
        name=user.name,
        age=28,
        gender='Prefer not to say',
        height=170,
        weight=68,
        bmi=round(68 / (1.70 * 1.70), 2),
        fitness_goal='General Fitness',
        fitness_level='Beginner',
        workout_preference='Both',
        dietary_preference='No Preference',
        available_workout_minutes=45,
    )
    db.add(default_profile)
    db.commit()
    db.refresh(user)
    return {
        'access_token': create_access_token(user),
        'token_type': 'bearer',
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
    }


@app.post('/auth/login', response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')

    return {
        'access_token': create_access_token(user),
        'token_type': 'bearer',
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
    }


@app.get('/auth/me')
def current_user(user: User = Depends(get_current_user)):
    return {'id': user.id, 'name': user.name, 'email': user.email}


@app.post('/profile', response_model=UserProfileResponse)
def create_profile(
    profile: UserProfileCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        bmi_value = calculate_bmi(profile.weight, profile.height)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    db_profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if db_profile is None:
        db_profile = UserProfile(user_id=user.id)
        db.add(db_profile)

    db_profile.name = profile.name.strip()
    db_profile.age = profile.age
    db_profile.gender = profile.gender.strip() if profile.gender else None
    db_profile.height = float(profile.height)
    db_profile.weight = float(profile.weight)
    db_profile.bmi = bmi_value
    db_profile.fitness_goal = profile.fitness_goal
    db_profile.fitness_level = profile.fitness_level
    db_profile.workout_preference = profile.workout_preference
    db_profile.dietary_preference = profile.dietary_preference
    db_profile.available_workout_minutes = profile.available_workout_minutes
    db.commit()
    db.refresh(db_profile)
    return map_profile_to_response(db_profile)


@app.get('/profile', response_model=UserProfileResponse)
def get_current_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail='Profile not found')
    return map_profile_to_response(profile)


@app.get('/profile/{profile_id}', response_model=UserProfileResponse)
def get_profile(profile_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = db.query(UserProfile).filter(UserProfile.id == profile_id, UserProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail='Profile not found')
    return map_profile_to_response(profile)


@app.put('/profile/{profile_id}', response_model=UserProfileResponse)
def update_profile(
    profile_id: int,
    profile: UserProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    existing_profile = db.query(UserProfile).filter(UserProfile.id == profile_id, UserProfile.user_id == user.id).first()
    if not existing_profile:
        raise HTTPException(status_code=404, detail='Profile not found')

    try:
        bmi_value = calculate_bmi(profile.weight, profile.height)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    existing_profile.name = profile.name.strip()
    existing_profile.age = profile.age
    existing_profile.gender = profile.gender.strip() if profile.gender else None
    existing_profile.height = float(profile.height)
    existing_profile.weight = float(profile.weight)
    existing_profile.bmi = bmi_value
    existing_profile.fitness_goal = profile.fitness_goal
    existing_profile.fitness_level = profile.fitness_level
    existing_profile.workout_preference = profile.workout_preference
    existing_profile.dietary_preference = profile.dietary_preference
    existing_profile.available_workout_minutes = profile.available_workout_minutes
    existing_profile.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(existing_profile)
    return map_profile_to_response(existing_profile)


@app.post('/predict-readiness', response_model=dict[str, Any])
def predict_readiness(payload: RecommendationRequest, user: User = Depends(get_current_user)):
    readiness_level, confidence = predict_readiness_level(payload.profile, payload.daily_data, payload.history)
    return {
        'readiness_level': readiness_level,
        'confidence': round(confidence, 4),
    }


@app.post('/recommendation', response_model=RecommendationResponse)
def get_recommendation(
    payload: RecommendationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    effective_history = build_user_history(db, user.id, payload.history)
    effective_payload = payload.model_copy(update={'history': effective_history})
    readiness_level, confidence = predict_readiness_level(payload.profile, payload.daily_data, effective_history)
    recommendation = recommend_intervention(
        payload.profile,
        payload.daily_data,
        effective_history,
        readiness_level,
    )

    response = RecommendationResponse(
        readiness_level=readiness_level,
        confidence=round(confidence, 4),
        intervention=recommendation['intervention'],
        score=recommendation['score'],
        main_factors=recommendation['main_factors'],
        reason=recommendation['reason'],
        all_scores=recommendation['all_scores'],
    )
    today = date.today()
    daily_check = (
        db.query(DailyCheck)
        .filter(DailyCheck.user_id == user.id, DailyCheck.check_date == today)
        .first()
    )
    if daily_check is None:
        daily_check = DailyCheck(user_id=user.id, check_date=today, payload=effective_payload.model_dump())
        db.add(daily_check)
    else:
        daily_check.payload = effective_payload.model_dump()
    db.add(RecommendationRecord(user_id=user.id, payload=effective_payload.model_dump(), result=response.model_dump()))
    db.commit()
    return response


@app.post('/trainer-plan')
def get_trainer_plan(
    payload: TrainerPlanRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    recommendation = payload.recommendation
    workout = generate_workout_plan(
        recommendation.readiness_level,
        recommendation.intervention,
        payload.profile.get('fitness_level', 'Intermediate'),
        payload.profile.get('fitness_goal', payload.profile.get('goal', 'General Fitness')),
        payload.profile.get('available_workout_minutes', 45),
    )
    meals = generate_meal_recommendations(
        payload.profile,
        payload.daily_data,
        recommendation.readiness_level,
        recommendation.intervention,
    )
    response = {
        'trainer_message': (
            f"Based on your sleep, fatigue, and recovery today, your body is "
            f"{recommendation.readiness_level.lower()} ready for exercise. "
            f"Let's focus on a {recommendation.intervention.replace('_', ' ')}."
        ),
        'workout': workout,
        'meals': meals,
    }
    db.add(WorkoutPlanRecord(user_id=user.id, plan=workout))
    db.add(MealRecommendationRecord(user_id=user.id, meals=meals))
    db.commit()
    return response


@app.post('/nutrition/alternative')
def get_nutrition_alternative(
    payload: NutritionAlternativeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    profile_record = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if profile_record is None:
        raise HTTPException(status_code=404, detail='Create your profile before generating meal alternatives')

    latest_check = (
        db.query(DailyCheck)
        .filter(DailyCheck.user_id == user.id)
        .order_by(DailyCheck.created_at.desc())
        .first()
    )
    latest_recommendation = (
        db.query(RecommendationRecord)
        .filter(RecommendationRecord.user_id == user.id)
        .order_by(RecommendationRecord.created_at.desc())
        .first()
    )
    if latest_check is None or latest_recommendation is None:
        raise HTTPException(status_code=400, detail='Complete a Daily Check before generating meal alternatives')

    stored_payload = latest_check.payload or {}
    result = latest_recommendation.result or {}
    profile_data = build_profile_data(profile_record, stored_payload)
    daily_data = stored_payload.get('daily_data', {})
    readiness_level = result.get('readiness_level', 'Moderate')
    intervention = result.get('intervention', 'nutrition_guidance')

    alternative = generate_meal_recommendations(
        profile_data,
        daily_data,
        readiness_level,
        intervention,
        meal_type=payload.meal_type,
        high_protein=payload.high_protein,
        avoid_meal=payload.current_meal,
    )[payload.meal_type]

    latest_meals = (
        db.query(MealRecommendationRecord)
        .filter(MealRecommendationRecord.user_id == user.id)
        .order_by(MealRecommendationRecord.created_at.desc())
        .first()
    )
    updated_meals = dict(latest_meals.meals) if latest_meals and latest_meals.meals else {}
    if not updated_meals:
        updated_meals = generate_meal_recommendations(profile_data, daily_data, readiness_level, intervention)
    updated_meals[payload.meal_type] = alternative
    db.add(MealRecommendationRecord(user_id=user.id, meals=updated_meals))
    db.commit()

    return {
        'meal_type': payload.meal_type,
        'meal': alternative,
        'meals': updated_meals,
    }


@app.post('/what-if')
def what_if_analysis(
    payload: WhatIfRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    profile_record = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if profile_record is None:
        raise HTTPException(status_code=404, detail='Create your profile before running a What-If analysis')

    latest_check = (
        db.query(DailyCheck)
        .filter(DailyCheck.user_id == user.id)
        .order_by(DailyCheck.created_at.desc())
        .first()
    )
    if latest_check is None:
        raise HTTPException(status_code=400, detail='Complete a Daily Check before running a What-If analysis')

    stored_payload = latest_check.payload or {}
    profile_data = build_profile_data(profile_record, stored_payload)
    daily_data = stored_payload.get('daily_data', {})
    history = stored_payload.get('history', {})
    try:
        return analyze_what_if(payload.question, profile_data, daily_data, history, predict_readiness_level)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.post('/workout-feedback', response_model=WorkoutFeedbackResponse)
def save_workout_feedback(
    payload: WorkoutFeedbackRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    feedback = WorkoutFeedback(**payload.model_dump(), user_id=user.id, profile_id=profile.id if profile else None)
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return map_feedback_to_response(feedback)


@app.get('/workout-feedback', response_model=list[WorkoutFeedbackResponse])
def list_workout_feedback(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    feedback = (
        db.query(WorkoutFeedback)
        .filter(WorkoutFeedback.user_id == user.id)
        .order_by(WorkoutFeedback.created_at.desc())
        .all()
    )
    return [map_feedback_to_response(item) for item in feedback]


@app.get('/water/today')
def get_today_water(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return build_water_summary(db, user.id)


@app.post('/water/intake')
def add_water_intake(
    payload: WaterIntakeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    entry = WaterIntake(user_id=user.id, intake_date=date.today(), amount_ml=payload.amount_ml)
    db.add(entry)
    db.commit()
    return build_water_summary(db, user.id)


@app.delete('/water/intake/last')
def undo_last_water_intake(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    latest_entry = (
        db.query(WaterIntake)
        .filter(WaterIntake.user_id == user.id, WaterIntake.intake_date == date.today())
        .order_by(WaterIntake.created_at.desc(), WaterIntake.id.desc())
        .first()
    )
    if latest_entry is None:
        raise HTTPException(status_code=404, detail='No water entry found for today')

    db.delete(latest_entry)
    db.commit()
    return build_water_summary(db, user.id)


@app.get('/water/history')
def get_water_history(
    days: int = Query(default=14, ge=1, le=90),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return {'days': build_water_history(db, user.id, days)}


@app.get('/history')
def get_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Return the current user's recent activity across the trainer modules."""
    checks = db.query(DailyCheck).filter(DailyCheck.user_id == user.id).order_by(DailyCheck.created_at.desc()).limit(20).all()
    recommendations = db.query(RecommendationRecord).filter(RecommendationRecord.user_id == user.id).order_by(RecommendationRecord.created_at.desc()).limit(20).all()
    plans = db.query(WorkoutPlanRecord).filter(WorkoutPlanRecord.user_id == user.id).order_by(WorkoutPlanRecord.created_at.desc()).limit(20).all()
    meals = db.query(MealRecommendationRecord).filter(MealRecommendationRecord.user_id == user.id).order_by(MealRecommendationRecord.created_at.desc()).limit(20).all()
    feedback = db.query(WorkoutFeedback).filter(WorkoutFeedback.user_id == user.id).order_by(WorkoutFeedback.created_at.desc()).limit(20).all()
    water_entries = db.query(WaterIntake).filter(WaterIntake.user_id == user.id).order_by(WaterIntake.created_at.desc()).limit(20).all()

    return {
        'daily_checks': [
            {'id': item.id, 'check_date': item.check_date, 'payload': item.payload, 'created_at': item.created_at}
            for item in checks
        ],
        'recommendations': [{'id': item.id, 'result': item.result, 'created_at': item.created_at} for item in recommendations],
        'workout_plans': [{'id': item.id, 'plan': item.plan, 'created_at': item.created_at} for item in plans],
        'meal_recommendations': [{'id': item.id, 'meals': item.meals, 'created_at': item.created_at} for item in meals],
        'workout_feedback': [map_feedback_to_response(item).model_dump() for item in feedback],
        'water_intake': [
            {
                'id': item.id,
                'intake_date': item.intake_date,
                'amount_ml': item.amount_ml,
                'created_at': item.created_at,
            }
            for item in water_entries
        ],
    }


@app.get('/progress-summary')
def get_progress_summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    feedback = db.query(WorkoutFeedback).filter(WorkoutFeedback.user_id == user.id).order_by(WorkoutFeedback.created_at.desc()).limit(50).all()
    recommendations = db.query(RecommendationRecord).filter(RecommendationRecord.user_id == user.id).order_by(RecommendationRecord.created_at.desc()).limit(50).all()
    checks = db.query(DailyCheck).filter(DailyCheck.user_id == user.id).order_by(DailyCheck.check_date.desc()).limit(30).all()
    completed = [item for item in feedback if item.completion_status == 'completed']
    average_completion = round(sum(item.completion_percentage for item in feedback) / len(feedback), 1) if feedback else 0
    adherence = round(len(completed) / len(feedback) * 100, 1) if feedback else 0
    readiness_history = readiness_points(recommendations)
    latest_readiness_score = readiness_history[-1]['score'] if readiness_history else None
    readiness_delta = None
    if len(readiness_history) >= 2:
        first_score = readiness_history[0].get('score')
        last_score = readiness_history[-1].get('score')
        if first_score is not None and last_score is not None:
            readiness_delta = round(float(last_score) - float(first_score), 1)

    water_history = build_water_history(db, user.id, 14)
    water_by_date = {item['date']: item for item in water_history}
    feedback_by_date: dict[date, list[WorkoutFeedback]] = {}
    for item in feedback:
        item_date = as_date(item.created_at)
        if item_date is not None:
            feedback_by_date.setdefault(item_date, []).append(item)
    check_dates = {item.check_date for item in checks}
    readiness_by_date: dict[date, dict[str, Any]] = {}
    for point in readiness_history:
        point_date = point.get('date')
        if point_date is not None:
            readiness_by_date[point_date] = point

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    weekly_summary = []
    for index in range(7):
        day = week_start + timedelta(days=index)
        daily_feedback = feedback_by_date.get(day, [])
        completed_count = sum(item.completion_status == 'completed' for item in daily_feedback)
        weekly_summary.append(
            {
                'date': day,
                'day': day.strftime('%a'),
                'daily_check_completed': day in check_dates,
                'workouts_logged': len(daily_feedback),
                'completed_workouts': completed_count,
                'average_completion': round(
                    sum(item.completion_percentage for item in daily_feedback) / len(daily_feedback),
                    1,
                ) if daily_feedback else 0,
                'water_ml': water_by_date.get(day, {}).get('total_ml', 0),
                'readiness_score': readiness_by_date.get(day, {}).get('score'),
                'readiness_level': readiness_by_date.get(day, {}).get('readiness_level'),
            }
        )

    water_days = sum(1 for item in water_history if item['total_ml'] > 0)
    achievements = []
    if len(completed) >= 5:
        achievements.append(f'{len(completed)} workouts completed')
    if feedback and adherence >= 80:
        achievements.append('80%+ workout adherence')
    if readiness_delta is not None and readiness_delta >= 5:
        achievements.append('Improved readiness trend')
    if water_days >= 3:
        achievements.append(f'Water logged on {water_days} recent days')

    latest_water_entries = (
        db.query(WaterIntake)
        .filter(WaterIntake.user_id == user.id)
        .order_by(WaterIntake.created_at.desc())
        .limit(5)
        .all()
    )
    recent_activity: list[dict[str, Any]] = []
    recent_activity.extend(
        {
            'type': 'readiness',
            'title': f"{(item.result or {}).get('readiness_level', 'Readiness')} readiness",
            'detail': ((item.result or {}).get('intervention') or 'recommendation').replace('_', ' '),
            'created_at': item.created_at,
        }
        for item in recommendations[:5]
    )
    recent_activity.extend(
        {
            'type': 'workout',
            'title': item.workout_name,
            'detail': f'{item.completion_status} at {item.completion_percentage:g}%',
            'created_at': item.created_at,
        }
        for item in feedback[:5]
    )
    recent_activity.extend(
        {
            'type': 'daily_check',
            'title': 'Daily Check completed',
            'detail': f'{item.check_date}',
            'created_at': item.created_at,
        }
        for item in checks[:5]
    )
    recent_activity.extend(
        {
            'type': 'water',
            'title': 'Water logged',
            'detail': f'{item.amount_ml} ml',
            'created_at': item.created_at,
        }
        for item in latest_water_entries
    )
    recent_activity = sorted(
        recent_activity,
        key=lambda item: item.get('created_at') or datetime.min,
        reverse=True,
    )[:8]

    return {
        'workouts_logged': len(feedback),
        'completed_workouts': len(completed),
        'average_completion': average_completion,
        'adherence_percentage': adherence,
        'daily_checks_completed': len(checks),
        'latest_readiness_score': latest_readiness_score,
        'latest_readiness_level': readiness_history[-1]['readiness_level'] if readiness_history else None,
        'readiness_delta': readiness_delta,
        'readiness_history': readiness_history,
        'workout_performance': [
            {
                'id': item.id,
                'workout_name': item.workout_name,
                'completion_status': item.completion_status,
                'completion_percentage': item.completion_percentage,
                'difficulty': item.difficulty,
                'created_at': item.created_at,
                'date': as_date(item.created_at),
            }
            for item in reversed(feedback[:10])
        ],
        'weekly_summary': weekly_summary,
        'water_history': water_history,
        'achievements': achievements,
        'recent_activity': recent_activity,
        'feedback': [map_feedback_to_response(item).model_dump() for item in feedback],
    }
