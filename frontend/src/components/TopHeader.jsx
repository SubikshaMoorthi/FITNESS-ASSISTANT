import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function TopHeader({ eyebrow, title, description }) {
  const { user } = useAuth();
  const initials = (user?.name || user?.email || 'U').slice(0, 1).toUpperCase();

  return (
    <header className="top-header">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        {description && <p className="top-description">{description}</p>}
      </div>
      <Link className="user-chip" to="/profile" aria-label="Open your profile">
        <span className="avatar">{initials}</span>
        <span>{user?.name || 'Your profile'}</span>
      </Link>
    </header>
  );
}
