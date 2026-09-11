from __future__ import annotations

import numpy as np
import pandas as pd


def generate_sample_dataset(rows: int = 250, output_path: str = 'data/raw/fitness_dataset.csv') -> pd.DataFrame:
    rng = np.random.default_rng(42)
    goals = ["muscle_gain", "fat_loss", "general_health", "endurance"]
    levels = ["Beginner", "Intermediate", "Advanced"]

    records = []
    for _ in range(rows):
        age = int(rng.integers(18, 55))
        bmi = round(float(rng.normal(25, 4)), 2)
        sleep = round(float(rng.normal(7, 1.3)), 2)
        steps = int(rng.integers(4000, 15000))
        active = int(rng.integers(20, 90))
        calories = int(rng.integers(1800, 3500))
        workout_freq = int(rng.integers(1, 6))
        workout_intensity = int(rng.integers(3, 9))
        prev_intensity = int(rng.integers(2, 9))
        fatigue = int(rng.integers(1, 9))
        recovery = int(rng.integers(20, 90))
        goal = rng.choice(goals)
        level = rng.choice(levels)
        adherence = round(float(rng.uniform(0.45, 0.98)), 2)
        avail = int(rng.integers(20, 90))

        if sleep < 6 or fatigue >= 7 or prev_intensity >= 8 or recovery <= 30:
            readiness = "Low"
        elif sleep >= 7.5 and fatigue <= 4 and recovery >= 60 and prev_intensity <= 6:
            readiness = "High"
        else:
            readiness = "Moderate"

        records.append({
            'age': age,
            'bmi': bmi,
            'sleep_hours': sleep,
            'steps': steps,
            'active_minutes': active,
            'calories_burned': calories,
            'workout_frequency': workout_freq,
            'workout_intensity': workout_intensity,
            'previous_workout_intensity': prev_intensity,
            'fatigue_score': fatigue,
            'recovery_score': recovery,
            'fitness_level': level,
            'goal': goal,
            'adherence_rate': adherence,
            'available_workout_minutes': avail,
            'readiness_level': readiness,
        })

    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    return df


if __name__ == '__main__':
    generate_sample_dataset()
    print('Generated data/raw/fitness_dataset.csv')
