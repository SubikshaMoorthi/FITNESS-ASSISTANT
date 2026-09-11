import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: '⌂' },
  { to: '/trainer', label: 'AI Trainer', icon: '✦' },
  { to: '/workout', label: 'Workout', icon: '↗' },
  { to: '/nutrition', label: 'Nutrition', icon: '◌' },
  { to: '/recovery', label: 'Recovery', icon: '◒' },
  { to: '/daily-check', label: 'Daily Check', icon: '✓' },
  { to: '/progress', label: 'Progress', icon: '◔' },
  { to: '/history', label: 'History', icon: '↺' },
  { to: '/profile', label: 'Profile', icon: '○' },
  { to: '/settings', label: 'Settings', icon: '⚙' },
];

export default function Sidebar() {
  const { user, logout } = useAuth();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark">F</div>
        <div className="brand-name">Fitness Assistant</div>
      </div>

      <nav className="nav-list" aria-label="Main navigation">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <span aria-hidden="true">{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-account">
        <span>{user?.name || user?.email}</span>
        <button type="button" className="secondary-btn" onClick={logout}>Sign out</button>
      </div>
    </aside>
  );
}
