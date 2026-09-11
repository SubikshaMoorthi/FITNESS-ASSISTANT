import TopHeader from '../components/TopHeader';
import TrainerCard from '../components/TrainerCard';
import { useAppContext } from '../context/AppContext';

export default function Recovery() {
  const { latestResult } = useAppContext();
  return <div className="page-card"><TopHeader eyebrow="Recovery" title="Recover with intention" description="Your recovery plan is shaped by sleep, fatigue, and how ready you feel." /><TrainerCard result={latestResult} /><div className="recovery-grid"><div className="metric-card"><span>Sleep</span><strong>{latestResult ? 'From latest check' : '--'}</strong><small>Keep a consistent bedtime tonight.</small></div><div className="metric-card"><span>Fatigue</span><strong>{latestResult ? 'Monitored' : '--'}</strong><small>Choose a gentler pace when tired.</small></div><div className="metric-card"><span>Hydration</span><strong>Water nearby</strong><small>Drink regularly through the day.</small></div></div><section className="panel tips-panel"><h2>Today's recovery tips</h2><ul><li>Take a short walk or do gentle mobility.</li><li>Eat a balanced meal with protein and carbohydrates.</li><li>Use your energy level, not pressure, to guide intensity.</li></ul></section></div>;
}
