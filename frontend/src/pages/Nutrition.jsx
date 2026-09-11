import TopHeader from '../components/TopHeader';
import { useAppContext } from '../context/AppContext';

export default function Nutrition() {
  const { trainerPlan } = useAppContext();
  const meals = trainerPlan?.meals || {};
  return <div className="page-card"><TopHeader eyebrow="Nutrition coach" title="Eat for your day" description="Simple meal ideas matched to your goal, preference, and readiness." />{trainerPlan ? <><div className="meal-grid">{Object.entries(meals).map(([name, meal]) => <article className="meal-card" key={name}><span className="meal-icon">{name === 'breakfast' ? '☀' : name === 'lunch' ? '◐' : name === 'snack' ? '✦' : '☾'}</span><p className="summary-label">{name}</p><h2>{meal.meal}</h2><p>{meal.purpose}</p><div className="meal-actions"><button type="button" className="secondary-btn">Suggest another</button><button type="button" className="secondary-btn">High protein</button></div></article>)}</div></> : <div className="empty-state">Complete a Daily Check to unlock meal recommendations.</div>}</div>;
}
