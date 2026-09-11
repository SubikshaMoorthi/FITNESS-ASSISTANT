import { Navigate, Outlet, Route, Routes } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import ProtectedRoute from './components/ProtectedRoute';
import { AppProvider } from './context/AppContext';
import { AuthProvider } from './context/AuthContext';
import DailyCheck from './pages/DailyCheck';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Progress from './pages/Progress';
import Trainer from './pages/Trainer';
import Workout from './pages/Workout';
import Nutrition from './pages/Nutrition';
import Recovery from './pages/Recovery';
import History from './pages/History';
import Settings from './pages/Settings';
import Login from './pages/Login';
import Signup from './pages/Signup';

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppProviderLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/trainer" element={<Trainer />} />
            <Route path="/workout" element={<Workout />} />
            <Route path="/nutrition" element={<Nutrition />} />
            <Route path="/recovery" element={<Recovery />} />
            <Route path="/daily-check" element={<DailyCheck />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/progress" element={<Progress />} />
            <Route path="/history" element={<History />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}

function AppProviderLayout() {
  return (
    <AppProvider>
      <div className="app-layout">
        <Sidebar />
        <main className="page-shell"><Outlet /></main>
      </div>
    </AppProvider>
  );
}
