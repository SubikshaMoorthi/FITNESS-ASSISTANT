import unittest

from ml.decision_engine import recommend_intervention


class DecisionEngineTests(unittest.TestCase):
    def test_recovery_selected_when_low_readiness_and_high_fatigue(self):
        profile = {
            'goal': 'muscle_gain',
            'fitness_level': 'Intermediate',
            'constraints': ['no_joint_pain'],
            'available_workout_minutes': 45,
        }
        daily_data = {
            'sleep_hours': 5.2,
            'fatigue_score': 8,
            'workout_intensity': 9,
            'steps': 4500,
            'activity_level': 'low',
        }
        history = {
            'adherence_rate': 0.4,
            'previous_session_rating': 2,
            'recent_workout_load': 9,
        }

        result = recommend_intervention(profile, daily_data, history, 'Low')
        self.assertEqual(result['intervention'], 'recovery_session')
        self.assertGreater(result['score'], 0)

    def test_heavy_workout_selected_when_readiness_is_high(self):
        profile = {
            'goal': 'muscle_gain',
            'fitness_level': 'Intermediate',
            'constraints': [],
            'available_workout_minutes': 60,
        }
        daily_data = {
            'sleep_hours': 8.2,
            'fatigue_score': 2,
            'workout_intensity': 5,
            'steps': 9500,
            'activity_level': 'moderate',
        }
        history = {
            'adherence_rate': 0.8,
            'previous_session_rating': 4,
            'recent_workout_load': 5,
        }

        result = recommend_intervention(profile, daily_data, history, 'High')
        self.assertEqual(result['intervention'], 'heavy_workout')


if __name__ == '__main__':
    unittest.main()
