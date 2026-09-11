import { useState } from 'react';
import { useAppContext } from '../context/AppContext';
import { getRecommendation, getTrainerPlan } from '../services/api';
import TopHeader from '../components/TopHeader';

const fatigueOptions = [
  { label: 'Very Fresh (1–2)', value: 2 },
  { label: 'Slightly Tired (3–4)', value: 4 },
  { label: 'Moderate (5–6)', value: 6 },
  { label: 'Very Tired (7–8)', value: 8 },
  { label: 'Extremely Tired (9–10)', value: 10 },
];

const workoutOptions = [
  { label: 'Very Light (1–2)', value: 2 },
  { label: 'Light (3–4)', value: 4 },
  { label: 'Moderate (5–6)', value: 6 },
  { label: 'Hard (7–8)', value: 8 },
  { label: 'Very Hard (9–10)', value: 10 },
];

const recoveryOptions = [
  { label: 'Poor', value: 25, description: 'I still feel worn down' },
  { label: 'Okay', value: 50, description: 'I am getting there' },
  { label: 'Good', value: 75, description: 'I feel ready' },
  { label: 'Excellent', value: 100, description: 'I feel fully refreshed' },
];

const sessionFeelingOptions = [
  { label: 'Very Poor', value: 1 },
  { label: 'Poor', value: 2 },
  { label: 'Okay', value: 3 },
  { label: 'Good', value: 4 },
  { label: 'Excellent', value: 5 },
];

const initialForm = {
  goal: 'muscle_gain',
  fitness_level: 'Intermediate',
  sleep_hours: 5.2,
  fatigue: 8,
  recent_workout: 8,
  session_feeling: 2,
  recovery: 35,
  steps: 4500,
  available_workout_minutes: 45,
};

const friendlyInterventionMap = {
  recovery_session: 'Recovery day',
  light_workout: 'Gentle workout',
  heavy_workout: 'Strength workout',
  walking_activity: 'Walk and move',
  rest: 'Rest day',
  nutrition_guidance: 'Nutrition focus',
  lifestyle_guidance: 'Lifestyle reset',
};

const friendlyFactorMap = {
  sleep_hours: 'Sleep',
  fatigue_score: 'How tired you feel',
  recovery_score: 'How recovered you feel',
  steps: 'Daily movement',
  previous_session_rating: 'How your recent workouts felt',
  previous_workout_intensity: 'Last workout intensity',
  available_workout_minutes: 'Time available for exercise',
  workout_intensity: 'Recent workout intensity',
  goal: 'Your goal',
  fitness_level: 'Fitness level',
};

function buildBackendPayload(formData) {
  const adherenceRate = Math.min(0.95, Math.max(0.2, 0.35 + formData.session_feeling * 0.12));

  return {
    profile: {
      goal: formData.goal,
      fitness_level: formData.fitness_level,
      constraints: ['no_joint_pain'],
      available_workout_minutes: Number(formData.available_workout_minutes),
    },
    daily_data: {
      sleep_hours: Number(formData.sleep_hours),
      fatigue_score: Number(formData.fatigue),
      workout_intensity: Number(formData.recent_workout),
      steps: Number(formData.steps),
      active_minutes: Number(formData.available_workout_minutes),
      calories_burned: 1800,
      recovery_score: Number(formData.recovery),
    },
    history: {
      adherence_rate: adherenceRate,
      previous_session_rating: Number(formData.session_feeling),
      recent_workout_load: Number(formData.recent_workout),
    },
  };
}

function buildProfilePayload(profile, formData) {
  const goalMap = {
    'Weight Loss': 'fat_loss',
    'Muscle Gain': 'muscle_gain',
    'General Fitness': 'general_health',
    'Improve Endurance': 'endurance',
  };

  return {
    age: Number(profile?.age || 30),
    bmi: Number(profile?.bmi || 25),
    fitness_level: profile?.fitness_level || formData.fitness_level,
    goal: goalMap[profile?.fitness_goal] || formData.goal,
    fitness_goal: profile?.fitness_goal || formData.goal,
    dietary_preference: profile?.dietary_preference || 'No Preference',
    available_workout_minutes: Number(profile?.available_workout_minutes || formData.available_workout_minutes),
  };
}

function formatFactor(factor) {
  return friendlyFactorMap[factor] || factor.replace(/_/g, ' ');
}

export default function DailyCheck() {
  const { profile, setLatestResult, setTrainerPlan } = useAppContext();
  const [formData, setFormData] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');

    try {
      const formPayload = buildBackendPayload(formData);
      const data = await getRecommendation({
        ...formPayload,
        profile: buildProfilePayload(profile, formData),
      });

      setResult(data);
      setLatestResult(data);
      const trainerPlan = await getTrainerPlan({
        profile: buildProfilePayload(profile, formData),
        daily_data: formPayload.daily_data,
        recommendation: data,
      });
      setTrainerPlan(trainerPlan);
    } catch (err) {
      setError(err.message || 'Unable to analyze your current fitness condition.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-card">
      <TopHeader eyebrow="Daily check-in" title="Check your readiness" description="Answer a few quick questions to choose the best plan for today." />
      <header className="page-header compact-note">
        {!profile && <p className="placeholder">You can complete My Profile first for more personalized results.</p>}
      </header>

      <section className="layout">
        <form className="panel" onSubmit={handleSubmit}>
          <div className="field-grid">
            <label>
              Your goal
              <select value={formData.goal} onChange={(e) => handleChange('goal', e.target.value)}>
                <option value="muscle_gain">Build strength</option>
                <option value="fat_loss">Lose weight</option>
                <option value="general_health">Feel healthier</option>
                <option value="endurance">Build stamina</option>
              </select>
            </label>

            <label>
              Your fitness level
              <select value={formData.fitness_level} onChange={(e) => handleChange('fitness_level', e.target.value)}>
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
              </select>
            </label>

            <label>
              How many hours did you sleep last night?
              <input
                type="number"
                min="0"
                max="16"
                step="0.1"
                value={formData.sleep_hours}
                onChange={(e) => handleChange('sleep_hours', Number(e.target.value))}
              />
            </label>

            <label>
              How tired do you feel today?
              <select value={formData.fatigue} onChange={(e) => handleChange('fatigue', Number(e.target.value))}>
                {fatigueOptions.map((option) => (
                  <option key={option.label} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>

            <label>
              How intense was your most recent workout?
              <select value={formData.recent_workout} onChange={(e) => handleChange('recent_workout', Number(e.target.value))}>
                {workoutOptions.map((option) => (
                  <option key={option.label} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>

            <label>
              How do you feel after your recent workouts?
              <select value={formData.session_feeling} onChange={(e) => handleChange('session_feeling', Number(e.target.value))}>
                {sessionFeelingOptions.map((option) => (
                  <option key={option.label} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>

            <label>
              How well recovered do you feel today?
              <select value={formData.recovery} onChange={(e) => handleChange('recovery', Number(e.target.value))}>
                {recoveryOptions.map((option) => (
                  <option key={option.label} value={option.value}>
                    {option.label} - {option.description}
                  </option>
                ))}
              </select>
            </label>

            <label>
              How many steps have you completed today?
              <input
                type="number"
                min="0"
                step="100"
                value={formData.steps}
                onChange={(e) => handleChange('steps', Number(e.target.value))}
              />
            </label>

            <label>
              How much time can you exercise today?
              <input
                type="number"
                min="0"
                max="180"
                step="5"
                value={formData.available_workout_minutes}
                onChange={(e) => handleChange('available_workout_minutes', Number(e.target.value))}
              />
            </label>
          </div>

          <button type="submit" disabled={loading}>
            {loading ? 'Checking...' : 'Get my plan'}
          </button>
          {error && <p className="error">{error}</p>}
        </form>

        <aside className="panel result-panel">
          <h2>Your plan</h2>

          {result ? (
            <>
              <div className="badge-row">
                <span className="badge">Readiness: {result.readiness_level}</span>
                <span className="badge secondary">Confidence: {result.confidence}</span>
              </div>

              <div className="result-card">
                <h3>{friendlyInterventionMap[result.intervention] || result.intervention.replace(/_/g, ' ')}</h3>
                <p className="score">Readiness score: {result.score}</p>
                <p>{result.reason}</p>
              </div>

              <div>
                <h4>What matters most</h4>
                <ul>
                  {result.main_factors.map((factor) => (
                    <li key={factor}>{formatFactor(factor)}</li>
                  ))}
                </ul>
              </div>
            </>
          ) : (
            <p className="placeholder">Answer a few quick questions to get your personalized plan for today.</p>
          )}
        </aside>
      </section>
    </div>
  );
}
