import { createContext, useContext, useMemo, useState } from 'react';

const TOKEN_KEY = 'fitness_assistant_access_token';
const USER_KEY = 'fitness_assistant_user';
const AuthContext = createContext(null);

function readUser() {
  try {
    const value = window.localStorage.getItem(USER_KEY);
    return value ? JSON.parse(value) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [token, setTokenState] = useState(() => window.localStorage.getItem(TOKEN_KEY));
  const [user, setUserState] = useState(readUser);

  const setAuth = (authResponse) => {
    window.localStorage.removeItem('fitness_assistant_profile_id');
    window.localStorage.removeItem('fitness_assistant_profile');
    window.localStorage.removeItem('fitness_assistant_latest_result');
    window.localStorage.removeItem('fitness_assistant_trainer_plan');
    setTokenState(authResponse.access_token);
    setUserState(authResponse.user);
    window.localStorage.setItem(TOKEN_KEY, authResponse.access_token);
    window.localStorage.setItem(USER_KEY, JSON.stringify(authResponse.user));
  };

  const logout = () => {
    setTokenState(null);
    setUserState(null);
    window.localStorage.removeItem(TOKEN_KEY);
    window.localStorage.removeItem(USER_KEY);
    window.localStorage.removeItem('fitness_assistant_profile_id');
    window.localStorage.removeItem('fitness_assistant_profile');
    window.localStorage.removeItem('fitness_assistant_latest_result');
    window.localStorage.removeItem('fitness_assistant_trainer_plan');
  };

  const value = useMemo(() => ({ token, user, isAuthenticated: Boolean(token), setAuth, logout }), [token, user]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth must be used inside AuthProvider');
  return value;
}
