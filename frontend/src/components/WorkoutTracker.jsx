import { useState } from 'react';
import { useAppContext } from '../context/AppContext';
import { saveWorkoutFeedback } from '../services/api';

export default function WorkoutTracker({ compact = false }) {
  const { profileId, latestResult, trainerPlan } = useAppContext();
  const exercises = trainerPlan?.workout?.exercises || [];
  const [started, setStarted] = useState(false);
  const [active, setActive] = useState(0);
  const [completed, setCompleted] = useState([]);
  const [difficulty, setDifficulty] = useState('Not rated');
  const [status, setStatus] = useState('completed');
  const [message, setMessage] = useState('');
  const percentage = exercises.length ? Math.round(completed.length / exercises.length * 100) : 0;

  if (!trainerPlan?.workout) return <div className="empty-state">Your workout will appear after your Daily Check.</div>;

  const exercise = exercises[active];
  const advance = (action) => {
    if (action === 'completed') setCompleted((items) => items.includes(active) ? items : [...items, active]);
    if (action === 'difficult') setDifficulty('Difficult');
    setActive((index) => Math.min(index + 1, exercises.length - 1));
  };

  const submit = async (event) => {
    event.preventDefault();
    setMessage('');
    try {
      await saveWorkoutFeedback({
        workout_name: trainerPlan.workout.workout_name,
        readiness_level: latestResult.readiness_level,
        intervention: latestResult.intervention,
        completion_status: status,
        completion_percentage: status === 'skipped' ? 0 : percentage,
        difficulty,
        feedback: 'Feedback submitted from the workout page.',
      });
      setMessage('Saved. Your trainer will use this feedback in your progress history.');
    } catch (error) {
      setMessage(error.message);
    }
  };

  return (
    <div className={`workout-tracker ${compact ? 'compact' : ''}`}>
      <div className="workout-title-row">
        <div>
          <p className="summary-label">Today's session</p>
          <h2>{trainerPlan.workout.workout_name}</h2>
        </div>
        <span className="time-pill">{trainerPlan.workout.estimated_total_minutes} min</span>
      </div>
      <p>{trainerPlan.workout.trainer_guidance}</p>
      {!started ? (
        <button type="button" onClick={() => setStarted(true)}>Start workout</button>
      ) : (
        <div className="exercise-focus">
          <p className="summary-label">Exercise {active + 1} of {exercises.length}</p>
          <h3>{exercise.name}</h3>
          <p className="exercise-prescription">{exercise.sets} sets · {exercise.repetitions} · {exercise.rest_seconds}s rest</p>
          <p>{exercise.guidance}</p>
          <div className="inline-actions">
            <button type="button" onClick={() => advance('completed')}>Complete</button>
            <button type="button" className="secondary-btn" onClick={() => advance('difficult')}>Difficult</button>
            <button type="button" className="secondary-btn" onClick={() => advance('skipped')}>Skip</button>
            <button type="button" className="secondary-btn" onClick={() => advance('next')}>Next</button>
          </div>
          <div className="progress-track"><span style={{ width: `${percentage}%` }} /></div>
          <p className="summary-label">{percentage}% complete</p>
        </div>
      )}
      {!compact && (
        <form className="feedback-form" onSubmit={submit}>
          <h3>How did it feel?</h3>
          <div className="field-grid compact-grid">
            <label>Workout status<select value={status} onChange={(event) => setStatus(event.target.value)}><option value="completed">Completed</option><option value="partial">Partially completed</option><option value="skipped">Skipped</option></select></label>
            <label>Difficulty<select value={difficulty} onChange={(event) => setDifficulty(event.target.value)}><option>Not rated</option><option>Easy</option><option>Moderate</option><option>Difficult</option><option>Very Difficult</option></select></label>
          </div>
          <button type="submit">Save feedback</button>
          {message && <p className={message.startsWith('Saved') ? 'success-message' : 'error'}>{message}</p>}
        </form>
      )}
    </div>
  );
}
