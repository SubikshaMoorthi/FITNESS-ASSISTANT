import TopHeader from '../components/TopHeader';
import { useAuth } from '../context/AuthContext';

export default function Settings() {
  const { logout } = useAuth();
  return <div className="page-card"><TopHeader eyebrow="Preferences" title="Settings" description="Keep your account and trainer experience under your control." /><section className="settings-list"><div className="setting-row"><div><h3>Account privacy</h3><p>Your records are scoped to your authenticated account.</p></div><span className="status-pill">Protected</span></div><div className="setting-row"><div><h3>Trainer style</h3><p>Guidance is based on your profile and latest Daily Check.</p></div><span className="status-pill">Personal</span></div><div className="setting-row"><div><h3>Sign out</h3><p>End this session on the current device.</p></div><button type="button" className="secondary-btn" onClick={logout}>Sign out</button></div></section></div>;
}
