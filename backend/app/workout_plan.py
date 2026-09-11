from __future__ import annotations

from typing import Any


def _exercise(name: str, sets: int, repetitions: str, rest_seconds: int, guidance: str) -> dict[str, Any]:
    return {
        'name': name,
        'sets': sets,
        'repetitions': repetitions,
        'rest_seconds': rest_seconds,
        'guidance': guidance,
    }


def generate_workout_plan(
    readiness_level: str,
    intervention: str,
    fitness_level: str,
    fitness_goal: str,
    available_minutes: int,
) -> dict[str, Any]:
    """Create a predictable workout plan from the ML state and profile context."""
    readiness = readiness_level.lower()
    level = fitness_level.lower()
    goal = fitness_goal.lower()
    duration = max(10, min(int(available_minutes or 30), 120))

    if intervention in {'recovery_session', 'rest'} or readiness == 'low':
        exercises = [
            _exercise('Easy walk', 1, '10 minutes', 0, 'Keep the pace conversational and relaxed.'),
            _exercise('Hip and shoulder mobility', 2, '30 seconds', 20, 'Move gently through a comfortable range.'),
            _exercise('Box breathing', 3, '5 slow breaths', 20, 'Breathe slowly to help your body settle.'),
        ]
        name = 'Recovery and Mobility Session'
        guidance = 'Today is about restoring energy. Stop if movement increases pain or dizziness.'
    elif intervention == 'heavy_workout' and readiness == 'high':
        main_reps = '6-8' if level == 'advanced' else '8-10'
        exercises = [
            _exercise('Squats', 4, main_reps, 90, 'Brace your core and keep your knees tracking over your toes.'),
            _exercise('Push-ups', 4, main_reps, 75, 'Use an incline or knees if needed to keep good form.'),
            _exercise('Reverse lunges', 3, '8 each side', 75, 'Step back softly and keep your front foot stable.'),
            _exercise('Plank', 3, '30-45 seconds', 60, 'Keep your body in one straight line.'),
        ]
        name = 'Strength and Performance Session'
        guidance = 'Your readiness supports a stronger session. Leave one or two good repetitions in reserve.'
    else:
        exercises = [
            _exercise('Bodyweight squats', 3, '10', 60, 'Move with control and keep your chest lifted.'),
            _exercise('Incline push-ups', 3, '8-10', 60, 'Choose a surface that lets you maintain steady form.'),
            _exercise('Alternating lunges', 2, '8 each side', 60, 'Use a shorter range if your balance needs attention.'),
            _exercise('Front plank', 3, '20-30 seconds', 45, 'Stop before your lower back begins to sag.'),
        ]
        name = 'Light Full-Body Session'
        guidance = 'Keep the effort controlled and focus on consistency over intensity.'

    if 'endurance' in goal:
        name = 'Steady Endurance Session' if readiness != 'low' else name
    elif 'weight loss' in goal:
        guidance += ' Keep moving continuously at a comfortable pace where possible.'

    return {
        'workout_name': name,
        'exercises': exercises,
        'estimated_total_minutes': duration,
        'trainer_guidance': guidance,
        'readiness_level': readiness_level,
        'intervention': intervention,
    }
