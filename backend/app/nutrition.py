from __future__ import annotations

from typing import Any


MEAL_TYPES = {'breakfast', 'lunch', 'snack', 'dinner'}


def _preference_foods(dietary_preference: str) -> dict[str, str]:
    if 'vegan' in dietary_preference:
        return {
            'breakfast_protein': 'soy yogurt, tofu, beans, or chickpeas',
            'plate_protein': 'tofu, tempeh, or bean curry',
            'lean_protein': 'tofu or tempeh',
            'snack_protein': 'soy yogurt or roasted chickpeas',
        }

    if 'vegetarian' in dietary_preference and 'non' not in dietary_preference:
        return {
            'breakfast_protein': 'Greek yogurt, tofu, lentils, or paneer',
            'plate_protein': 'tofu or lentil curry',
            'lean_protein': 'paneer, tofu, or lentils',
            'snack_protein': 'Greek yogurt, paneer, or roasted lentils',
        }

    return {
        'breakfast_protein': 'Greek yogurt, eggs, or a lean protein',
        'plate_protein': 'fish, chicken, eggs, or beans',
        'lean_protein': 'chicken, fish, eggs, or beans',
        'snack_protein': 'Greek yogurt, eggs, cottage cheese, or tuna',
    }


def _meal_bank(
    dietary_preference: str,
    goal: str,
    purpose: str,
    snack: str,
    snack_purpose: str,
) -> dict[str, list[dict[str, str]]]:
    foods = _preference_foods(dietary_preference)
    high_protein_note = 'Keeps protein prominent while staying compatible with your stated preference.'

    return {
        'breakfast': [
            {
                'meal': f'Oats with fruit and {foods["breakfast_protein"]}',
                'purpose': f'Provides carbohydrates and protein; {purpose}.',
                'tags': ['balanced'],
            },
            {
                'meal': f'Whole-grain toast with {foods["lean_protein"]} and fruit',
                'purpose': 'Gives a steady breakfast with protein, fiber, and training fuel.',
                'tags': ['balanced'],
            },
            {
                'meal': f'High-protein breakfast bowl with {foods["lean_protein"]}, vegetables, and grains',
                'purpose': high_protein_note,
                'tags': ['high_protein'],
            },
            {
                'meal': f'Protein smoothie with fruit, oats, and {foods["snack_protein"]}',
                'purpose': 'Useful when you want a quicker higher-protein breakfast.',
                'tags': ['high_protein'],
            },
        ],
        'lunch': [
            {
                'meal': f'Whole grains, vegetables, and {foods["plate_protein"]}',
                'purpose': 'Builds a balanced plate with sustained energy and recovery nutrients.',
                'tags': ['balanced'],
            },
            {
                'meal': f'Rice or quinoa bowl with vegetables and {foods["lean_protein"]}',
                'purpose': 'Keeps lunch easy to adjust for appetite and activity level.',
                'tags': ['balanced'],
            },
            {
                'meal': f'High-protein lunch plate with extra {foods["lean_protein"]} and vegetables',
                'purpose': high_protein_note,
                'tags': ['high_protein'],
            },
            {
                'meal': f'Protein-rich wrap with {foods["lean_protein"]}, greens, and a side of fruit',
                'purpose': 'Adds a compact higher-protein lunch without making the meal heavy.',
                'tags': ['high_protein'],
            },
        ],
        'snack': [
            {
                'meal': snack,
                'purpose': snack_purpose,
                'tags': ['balanced'],
            },
            {
                'meal': 'Fruit with a small handful of nuts or seeds',
                'purpose': 'Adds a simple snack with fiber and fats for fullness.',
                'tags': ['balanced'],
            },
            {
                'meal': f'{foods["snack_protein"]} with fruit',
                'purpose': high_protein_note,
                'tags': ['high_protein'],
            },
            {
                'meal': f'Protein snack plate with {foods["snack_protein"]} and raw vegetables',
                'purpose': 'Raises protein while keeping the snack practical.',
                'tags': ['high_protein'],
            },
        ],
        'dinner': [
            {
                'meal': f'Roasted vegetables, potatoes or rice, and {foods["plate_protein"]}',
                'purpose': 'Supports a satisfying evening meal and next-day recovery.',
                'tags': ['balanced'],
            },
            {
                'meal': f'Vegetable stir-fry with noodles or rice and {foods["lean_protein"]}',
                'purpose': 'Balances carbohydrates and protein after the day.',
                'tags': ['balanced'],
            },
            {
                'meal': f'High-protein dinner bowl with {foods["lean_protein"]}, vegetables, and rice',
                'purpose': high_protein_note,
                'tags': ['high_protein'],
            },
            {
                'meal': f'Protein-forward curry with {foods["lean_protein"]}, vegetables, and whole grains',
                'purpose': 'Keeps dinner recovery-focused without implying a guaranteed outcome.',
                'tags': ['high_protein'],
            },
        ],
    }


def _select_meal(options: list[dict[str, str]], avoid_meal: str | None = None) -> dict[str, str]:
    normalized_avoid = (avoid_meal or '').strip().lower()
    for option in options:
        if option['meal'].strip().lower() != normalized_avoid:
            return {'meal': option['meal'], 'purpose': option['purpose']}
    first = options[0]
    return {'meal': first['meal'], 'purpose': first['purpose']}


def generate_meal_recommendations(
    profile: dict[str, Any],
    daily_data: dict[str, Any],
    readiness_level: str,
    intervention: str,
    meal_type: str | None = None,
    high_protein: bool = False,
    avoid_meal: str | None = None,
) -> dict[str, dict[str, str]]:
    """Return general fitness nutrition guidance, not medical dietary advice."""
    dietary_preference = (profile.get('dietary_preference') or 'No Preference').lower()
    goal = (profile.get('fitness_goal') or profile.get('goal') or 'General Fitness').lower()
    low_readiness = readiness_level.lower() == 'low' or intervention in {'recovery_session', 'rest'}
    purpose = 'supports recovery and steady energy' if low_readiness else 'supports training energy and recovery'

    if 'weight loss' in goal or 'fat loss' in goal:
        snack = 'Fruit with a portion of nuts'
        snack_purpose = 'Provides a filling snack with fiber and healthy fats.'
    else:
        snack = 'Fruit with yogurt or a protein-rich alternative'
        snack_purpose = 'Adds convenient carbohydrates and protein around activity.'

    meal_bank = _meal_bank(dietary_preference, goal, purpose, snack, snack_purpose)

    if meal_type:
        normalized_type = meal_type.lower()
        if normalized_type not in MEAL_TYPES:
            raise ValueError('Meal type must be breakfast, lunch, snack, or dinner.')
        options = meal_bank[normalized_type]
        if high_protein:
            options = [meal for meal in options if 'high_protein' in meal['tags']]
        return {normalized_type: _select_meal(options, avoid_meal)}

    return {
        name: _select_meal([meal for meal in options if 'balanced' in meal['tags']])
        for name, options in meal_bank.items()
    }
