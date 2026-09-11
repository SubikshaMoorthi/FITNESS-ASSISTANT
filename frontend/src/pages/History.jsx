import { useEffect, useState } from 'react';
import TopHeader from '../components/TopHeader';
import { getHistory } from '../services/api';

export default function History() {
  const [history, setHistory] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => { getHistory().then(setHistory).catch((err) => setError(err.message)); }, []);
  const items = history?.recommendations || [];
  return <div className="page-card"><TopHeader eyebrow="Your records" title="History" description="A private timeline of your checks, plans, and feedback." />{error && <p className="error">{error}</p>}{!history && !error && <div className="empty-state">Loading your history...</div>}{history && !items.length && <div className="empty-state">Your history will fill up after your first Daily Check.</div>}{items.length > 0 && <div className="history-list">{items.map((item) => <article className="history-item" key={item.id}><div><span className="history-dot" /><div><p className="summary-label">{new Date(item.created_at).toLocaleString()}</p><h3>{item.result.readiness_level} readiness · {item.result.intervention?.replace(/_/g, ' ')}</h3><p>{item.result.reason}</p></div></div><strong>{item.result.score}</strong></article>)}</div>}</div>;
}
