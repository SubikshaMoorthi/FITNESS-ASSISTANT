from __future__ import annotations

from typing import Any


INTERVENTIONS = [
    'heavy_workout',
    'light_workout',
    'recovery_session',
    'walking_activity',
    'rest',
    'nutrition_guidance',
    'lifestyle_guidance',
]


def score_intervention(
    intervention: str,
    profile: dict[str, Any],
    daily_data: dict[str, Any],
    history: dict[str, Any],
    predicted_state: str,
) -> tuple[float, list[str]]:
    """Return the suitability score and the main reasons for the intervention."""
    score = 0.0
    reasons: list[str] = []

    goal = (profile.get('goal') or '').lower()
    fitness_level = (profile.get('fitness_level') or '').lower()
    constraints = profile.get('constraints') or []
    available_minutes = profile.get('available_workout_minutes', 0)
    sleep_hours = float(daily_data.get('sleep_hours', 0) or 0)
    fatigue = float(daily_data.get('fatigue_score', 0) or 0)
    workout_intensity = float(daily_data.get('workout_intensity', 0) or 0)
    activity_level = (daily_data.get('activity_level') or '').lower()
    adherence = float(history.get('adherence_rate', 0.5) or 0.5)
    previous_rating = float(history.get('previous_session_rating', 3) or 3)
    recent_load = float(history.get('recent_workout_load', 0) or 0)

    if goal in {'muscle_gain', 'strength', 'hypertrophy'}:
        score += 14
    elif goal in {'fat_loss', 'weight_loss'}:
        score += 10
    elif goal in {'general_health', 'endurance'}:
        score += 8

    if predicted_state == 'High':
        score += 18
        reasons.append('readiness is high')
        if intervention == 'heavy_workout':
            score += 25
            reasons.append('high readiness supports a demanding session')
        elif intervention == 'recovery_session':
            score -= 10
            reasons.append('recovery is not ideal when readiness is high')
    elif predicted_state == 'Moderate':
        score += 10
        reasons.append('readiness is moderate')
    else:
        score -= 12
        reasons.append('readiness is low')
        if intervention == 'recovery_session':
            score += 35
            reasons.append('low readiness strongly favors recovery')
        elif intervention == 'rest':
            score += 18
            reasons.append('low readiness supports a deliberate rest day')
        elif intervention == 'walking_activity':
            score += 12
            reasons.append('low readiness still benefits from light movement')
        else:
            score -= 18
            reasons.append('hard training is less appropriate under low readiness')

    if sleep_hours >= 7.5:
        score += 10
        reasons.append('sleep is sufficient')
    elif sleep_hours < 6:
        score -= 18
        reasons.append('sleep is limited')

    if fatigue >= 7:
        score -= 16
        reasons.append('fatigue is high')
    elif fatigue <= 3:
        score += 8
        reasons.append('fatigue is low')

    if workout_intensity >= 8 and predicted_state != 'High':
        score -= 14
        reasons.append('recent workout load is heavy')
    elif workout_intensity <= 5:
        score += 6
        reasons.append('workout demand is manageable')

    if adherence < 0.5:
        score -= 8
        reasons.append('adherence is low')
    elif adherence > 0.75:
        score += 8
        reasons.append('adherence history is strong')

    if previous_rating <= 2:
        score -= 8
        reasons.append('user rated recent sessions poorly')

    if recent_load >= 8:
        score -= 10
        reasons.append('recent training load is high')

    if constraints:
        score -= 12
        reasons.append('user constraints reduce options')

    if available_minutes < 20:
        score -= 8
        reasons.append('available time is limited')

    if activity_level in {'low', 'sedentary'}:
        score += 4
        reasons.append('daily movement is low')

    if intervention == 'heavy_workout':
        if predicted_state == 'High' and sleep_hours >= 7.5 and fatigue <= 4:
            score += 48
            reasons.append('strong readiness supports a heavy session')
        elif predicted_state == 'Moderate':
            score += 20
            reasons.append('moderate readiness can support a strong but controlled session')
        else:
            score -= 24
            reasons.append('heavy workout is unsafe for current readiness')

    if intervention == 'light_workout':
        if predicted_state in {'Moderate', 'High'}:
            score += 22
            reasons.append('light workout fits current capacity')
        elif predicted_state == 'Low':
            score += 18
            reasons.append('light movement is safer than a hard session')
        else:
            score -= 6

    if intervention == 'recovery_session':
        if predicted_state == 'Low':
            score += 62
            reasons.append('recovery is the safest intervention')
        elif predicted_state == 'Moderate' and (sleep_hours < 6 or fatigue >= 7):
            score += 28
            reasons.append('recovery is justified by reduced recovery capacity')
        elif predicted_state == 'High':
            score -= 8
            reasons.append('recovery is less necessary when readiness is strong')

        if sleep_hours < 6 or fatigue >= 7:
            score += 14
            reasons.append('active recovery preserves training quality while reducing strain')

    if intervention == 'walking_activity':
        if activity_level in {'low', 'sedentary'} or predicted_state == 'Moderate':
            score += 20
            reasons.append('walking supports active recovery without excessive strain')
        elif predicted_state == 'Low':
            score += 12
            reasons.append('gentle movement helps maintain momentum while reducing strain')
        else:
            score -= 4

    if intervention == 'rest':
        if predicted_state == 'Low' and (sleep_hours < 6 or fatigue >= 7):
            score += 32
            reasons.append('rest is medically consistent with current fatigue')
            if goal in {'muscle_gain', 'strength', 'hypertrophy'} and fatigue >= 7:
                score -= 10
                reasons.append('full rest is less ideal than structured recovery when performance goals are still important')
        elif predicted_state == 'Moderate':
            score += 8
            reasons.append('rest is reasonable if fatigue is elevated')
        else:
            score -= 10

    if intervention == 'nutrition_guidance':
        if goal in {'fat_loss', 'general_health'} or sleep_hours < 6:
            score += 8
            reasons.append('nutrition support improves recovery and consistency')
        else:
            score += 2

    if intervention == 'lifestyle_guidance':
        if sleep_hours < 6 or adherence < 0.6:
            score += 8
            reasons.append('lifestyle structure is needed for better consistency')
        else:
            score -= 2

    if fitness_level == 'beginner' and intervention == 'heavy_workout':
        score -= 10
        reasons.append('beginner load should be managed carefully')

    if duration_penalty := (available_minutes < 30 and intervention == 'heavy_workout'):
        score -= 10
        reasons.append('session duration is too short for a heavy workout')

    return round(score, 2), reasons


def recommend_intervention(
    profile: dict[str, Any],
    daily_data: dict[str, Any],
    history: dict[str, Any],
    predicted_state: str,
) -> dict[str, Any]:
    """Select the best intervention from a transparent candidate set."""
    candidate_scores: list[tuple[str, float, list[str]]] = []

    for intervention in INTERVENTIONS:
        score, reasons = score_intervention(intervention, profile, daily_data, history, predicted_state)
        candidate_scores.append((intervention, score, reasons))

    best_intervention, best_score, best_reasons = max(candidate_scores, key=lambda item: item[1])

    return {
        'intervention': best_intervention,
        'score': best_score,
        'main_factors': best_reasons,
        'reason': (
            f"{best_intervention.replace('_', ' ')} was selected because the system judged the current readiness and "
            f"context to be most compatible with this intervention."
        ),
        'all_scores': {name: round(score, 2) for name, score, _ in candidate_scores},
    }
