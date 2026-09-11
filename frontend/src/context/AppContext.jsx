import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { getProfile } from '../services/api';

const PROFILE_ID_KEY = 'fitness_assistant_profile_id';
const PROFILE_KEY = 'fitness_assistant_profile';
const RESULT_KEY = 'fitness_assistant_latest_result';
const TRAINER_PLAN_KEY = 'fitness_assistant_trainer_plan';

const AppContext = createContext(null);

function readJson(key) {
  try {
    const value = window.localStorage.getItem(key);
    return value ? JSON.parse(value) : null;
  } catch {
    return null;
  }
}

export function AppProvider({ children }) {
  const [profile, setProfileState] = useState(() => readJson(PROFILE_KEY));
  const [profileId, setProfileIdState] = useState(() => window.localStorage.getItem(PROFILE_ID_KEY));
  const [latestResult, setLatestResultState] = useState(() => readJson(RESULT_KEY));
  const [trainerPlan, setTrainerPlanState] = useState(() => readJson(TRAINER_PLAN_KEY));

  useEffect(() => {
    let active = true;
    getProfile()
      .then((value) => {
        if (active) setProfile(value);
      })
      .catch(() => {
        // A new authenticated session may not have a profile in older databases.
      });
    return () => {
      active = false;
    };
  }, []);

  const setProfile = (value) => {
    setProfileState(value);
    setProfileIdState(String(value.id));
    window.localStorage.setItem(PROFILE_KEY, JSON.stringify(value));
    window.localStorage.setItem(PROFILE_ID_KEY, String(value.id));
  };

  const setLatestResult = (value) => {
    setLatestResultState(value);
    window.localStorage.setItem(RESULT_KEY, JSON.stringify(value));
  };

  const setTrainerPlan = (value) => {
    setTrainerPlanState(value);
    window.localStorage.setItem(TRAINER_PLAN_KEY, JSON.stringify(value));
  };

  const contextValue = useMemo(
    () => ({ profile, profileId, latestResult, trainerPlan, setProfile, setLatestResult, setTrainerPlan }),
    [profile, profileId, latestResult, trainerPlan]
  );

  return <AppContext.Provider value={contextValue}>{children}</AppContext.Provider>;
}

export function useAppContext() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used inside AppProvider');
  }
  return context;
}
