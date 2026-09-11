import { Link } from 'react-router-dom';
import TopHeader from '../components/TopHeader';
import TrainerCard, { interventionLabel } from '../components/TrainerCard';
import { useAppContext } from '../context/AppContext';

export default function Dashboard() {
  const { profile, latestResult, trainerPlan } = useAppContext();
  const readiness = latestResult?.readiness_level;
  const workout = trainerPlan?.workout;
  const meals = trainerPlan?.meals;

  return (
    <div className="page-card dashboard-page">
      <TopHeader eyebrow="Your space" title={`Good to see you${profile?.name ? `, ${profile.name}` : ''}.`} description="A clear view of how you are feeling and what to do next." />
      <div className="dashboard-hero">
        <div><p className="summary-label">Today's readiness</p><h2>{readiness || 'Not checked yet'}</h2><p>{latestResult ? 'Your plan adapts to your latest sleep, fatigue, and recovery check.' : 'Take your Daily Check to unlock a personal plan for today.'}</p></div>
        <div className={`readiness-ring ${readiness?.toLowerCase() || 'empty'}`}><strong>{latestResult?.score ?? '--'}</strong><span>score</span></div>
      </div>
      <TrainerCard result={latestResult} />
      <div className="dashboard-actions"><Link className="action-button" to="/workout">↗ <span>Start Workout</span></Link><Link className="action-button" to="/trainer">✦ <span>Ask Trainer</span></Link><Link className="action-button" to="/nutrition">◌ <span>View Meals</span></Link><Link className="action-button" to="/recovery">◒ <span>Check Recovery</span></Link></div>
      <div className="dashboard-overview-grid">
        <div className="overview-card"><p className="summary-label">Recommended action</p><h3>{latestResult ? interventionLabel(latestResult.intervention) : 'Waiting for your check-in'}</h3><p>{latestResult?.reason || 'Your trainer will explain the recommendation clearly.'}</p></div>
        <div className="overview-card"><p className="summary-label">Today's workout</p><h3>{workout?.workout_name || 'No workout yet'}</h3><p>{workout ? `${workout.estimated_total_minutes} minutes · ${workout.exercises.length} exercises` : 'Your workout appears after a Daily Check.'}</p></div>
        <div className="overview-card"><p className="summary-label">Meal focus</p><h3>{meals?.breakfast?.meal || 'Personal meal ideas'}</h3><p>{meals ? meals.breakfast.purpose : 'Breakfast, lunch, snack, and dinner suggestions will be ready here.'}</p></div>
        <div className="overview-card"><p className="summary-label">Progress</p><h3>Keep your rhythm</h3><p>Log your workout feedback to build a useful personal history.</p><Link className="text-link" to="/progress">View progress →</Link></div>
      </div>
    </div>
  );
}
