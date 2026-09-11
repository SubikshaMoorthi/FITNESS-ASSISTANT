import TopHeader from '../components/TopHeader';
import WorkoutTracker from '../components/WorkoutTracker';

export default function Workout() {
  return <div className="page-card"><TopHeader eyebrow="Training" title="Today's workout" description="Move through your plan at a pace that feels right today." /><WorkoutTracker /></div>;
}
