from __future__ import annotations

import re
from typing import Any

from ml.decision_engine import recommend_intervention


NUMBER = r'(\d+(?:\.\d+)?)'
READINESS_ORDER = {'Low': 1, 'Moderate': 2, 'High': 3}


def summarize_state(
    profile: dict[str, Any],
    daily: dict[str, Any],
    readiness_level: str,
    confidence: float,
    recommendation: dict[str, Any],
) -> dict[str, Any]:
    return {
        'sleep_hours': daily.get('sleep_hours'),
        'steps': daily.get('steps'),
        'active_minutes': daily.get('active_minutes'),
        'calories_burned': daily.get('calories_burned'),
        'fatigue_score': daily.get('fatigue_score'),
        'recovery_score': daily.get('recovery_score'),
        'workout_intensity': daily.get('workout_intensity'),
        'workout_frequency': profile.get('workout_frequency'),
        'available_workout_minutes': profile.get('available_workout_minutes'),
        'readiness_level': readiness_level,
        'confidence': round(confidence, 4),
        'intervention': recommendation['intervention'],
        'recommendation': recommendation['reason'],
    }


def expected_impact(
    change: str,
    current_state: str,
    future_state: str,
    current_intervention: str,
    future_intervention: str,
) -> dict[str, str]:
    current_rank = READINESS_ORDER.get(current_state, 0)
    future_rank = READINESS_ORDER.get(future_state, 0)

    if future_rank > current_rank:
        impact = 'positive'
        likely_change = f'Readiness may improve from {current_state} toward {future_state}.'
        practical = 'Try the change gradually and keep watching sleep, fatigue, recovery, and workout response.'
    elif future_rank < current_rank:
        impact = 'negative'
        likely_change = f'Readiness may drop from {current_state} toward {future_state}.'
        practical = 'Treat the change cautiously and consider a lighter plan if fatigue or soreness rises.'
    elif current_intervention != future_intervention:
        impact = 'neutral'
        likely_change = 'Readiness may stay similar, but the recommended training focus may change.'
        practical = 'Use the changed recommendation as a planning signal, not as a guaranteed outcome.'
    else:
        impact = 'neutral'
        likely_change = 'Readiness and recommendation may stay close to your current state.'
        practical = 'This change may still help comfort, consistency, or recovery even if the model output is similar.'

    return {
        'likely_change': likely_change,
        'why_it_may_change': (
            f'The scenario changes model inputs by {change}, so the readiness model and decision engine reassess '
            'training tolerance using the same rules as your Daily Check.'
        ),
        'impact_type': impact,
        'practical_recommendation': practical,
    }


def parse_scenario(question: str, current_profile: dict[str, Any], current_daily: dict[str, Any]) -> tuple[str, dict[str, Any], str]:
    text = question.lower()
    profile = dict(current_profile)
    daily = dict(current_daily)
    change = 'a small improvement in your current routine'

    match = re.search(r'(?:sleep|sleep for|sleeping)\s*(?:an?\s*)?(?:additional|more)?\s*(?:of\s*)?([0-9]+(?:\.\d+)?)\s*hour', text)
    if match:
        amount = float(match.group(1))
        daily['sleep_hours'] = float(daily.get('sleep_hours', 7)) + amount
        change = f'sleeping {amount:g} more hour' + ('s' if amount != 1 else '')
    elif re.search(r'sleep.*more|more.*sleep', text):
        daily['sleep_hours'] = float(daily.get('sleep_hours', 7)) + 1
        change = 'sleeping 1 more hour'
    else:
        match = re.search(r'(?:steps|step count).*?(?:to|of)\s*([0-9][0-9,]*)', text)
        if match:
            daily['steps'] = int(match.group(1).replace(',', ''))
            change = f'increasing steps to {daily["steps"]:,}'
        elif re.search(r'(?:steps|walking).*more', text):
            daily['steps'] = int(daily.get('steps', 8000)) + 2000
            change = 'adding around 2,000 steps'
        else:
            match = re.search(r'(?:workout|train|training).*?(?:(?:to|for)\s*)?([0-9]+)\s*days?', text)
            if match:
                profile['workout_frequency'] = int(match.group(1))
                change = f'training {match.group(1)} days per week'
            elif re.search(r'train more|workout more|increase.*workout', text):
                profile['workout_frequency'] = int(profile.get('workout_frequency', 2)) + 1
                change = 'adding one training day per week'
            elif re.search(r'(?:rest|take).*(?:more|another)', text):
                daily['recovery_score'] = min(100, float(daily.get('recovery_score', 60)) + 10)
                daily['fatigue_score'] = max(1, float(daily.get('fatigue_score', 5)) - 1)
                change = 'taking one additional rest day'
            else:
                match = re.search(r'(?:workout|session).*?(?:for|to)\s*([0-9]+)\s*minutes?', text)
                if match:
                    profile['available_workout_minutes'] = int(match.group(1))
                    daily['active_minutes'] = int(match.group(1))
                    change = f'using a {match.group(1)} minute workout'
                elif re.search(r'(?:reduce|lower|decrease).*intensity|intensity.*(?:reduce|lower|decrease)', text):
                    daily['workout_intensity'] = max(1, float(daily.get('workout_intensity', 5)) - 2)
                    daily['previous_workout_intensity'] = daily['workout_intensity']
                    change = 'reducing workout intensity by about two points'
                elif re.search(r'(?:increase|higher).*intensity|intensity.*increase', text):
                    daily['workout_intensity'] = min(10, float(daily.get('workout_intensity', 5)) + 2)
                    daily['previous_workout_intensity'] = daily['workout_intensity']
                    change = 'increasing workout intensity by about two points'
                elif re.search(r'(?:reduce|lower|decrease).*calorie', text):
                    daily['calories_burned'] = max(1200, float(daily.get('calories_burned', 2200)) - 250)
                    change = 'reducing daily calorie intake by roughly 250 calories'
                elif re.search(r'(?:more protein|increase protein)', text):
                    daily['recovery_score'] = min(100, float(daily.get('recovery_score', 60)) + 5)
                    change = 'adding a protein serving to meals'
                elif re.search(r'(?:recovery|hydration|water).*improve|drink more', text):
                    daily['recovery_score'] = min(100, float(daily.get('recovery_score', 60)) + 10)
                    change = 'improving hydration and recovery habits'
                elif re.search(r'skip.*workout', text):
                    daily['recovery_score'] = min(100, float(daily.get('recovery_score', 60)) + 5)
                    daily['fatigue_score'] = max(1, float(daily.get('fatigue_score', 5)) - 1)
                    change = 'skipping today\'s workout'
                else:
                    raise ValueError('Try asking about sleep, steps, workout frequency, duration, intensity, calories, protein, rest, recovery, or hydration.')
    return change, {'profile': profile, 'daily_data': daily}, text


def analyze_what_if(
    question: str,
    profile: dict[str, Any],
    daily_data: dict[str, Any],
    history: dict[str, Any],
    predict_readiness,
) -> dict[str, Any]:
    current_profile = dict(profile)
    current_daily = dict(daily_data)
    change, scenario, _ = parse_scenario(question, current_profile, current_daily)
    scenario_history = dict(history)
    if 'previous_workout_intensity' in scenario['daily_data']:
        scenario_history['recent_workout_load'] = scenario['daily_data']['previous_workout_intensity']
    current_state, current_confidence = predict_readiness(current_profile, current_daily, history)
    future_state, future_confidence = predict_readiness(scenario['profile'], scenario['daily_data'], scenario_history)
    current_recommendation = recommend_intervention(current_profile, current_daily, history, current_state)
    future_recommendation = recommend_intervention(scenario['profile'], scenario['daily_data'], scenario_history, future_state)
    impact = expected_impact(
        change,
        current_state,
        future_state,
        current_recommendation['intervention'],
        future_recommendation['intervention'],
    )

    if future_state == current_state:
        expected = 'The readiness level may stay similar, but the change could still improve comfort, consistency, or recovery capacity.'
    else:
        expected = f'Readiness may move from {current_state} toward {future_state}; this is an estimate based on the current model and scenario inputs.'

    return {
        'title': 'What-If Analysis',
        'question': question,
        'current': summarize_state(current_profile, current_daily, current_state, current_confidence, current_recommendation),
        'scenario': {
            'change': change,
            **summarize_state(scenario['profile'], scenario['daily_data'], future_state, future_confidence, future_recommendation),
        },
        'expected_change': expected,
        'expected_impact': impact,
        'meaning': f'Based on your current data and goal, {change} could affect training tolerance and recovery. It is an estimate, not a guaranteed physiological outcome.',
        'recommended_action': future_recommendation['reason'],
    }
