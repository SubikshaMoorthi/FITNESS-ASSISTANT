const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  let response;
  const token = window.localStorage.getItem('fitness_assistant_access_token');

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(options.headers || {}),
      },
    });
  } catch {
    throw new Error('Unable to connect to the recommendation service. Please try again.');
  }

  let data = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    throw new Error(data?.detail || 'The recommendation service returned an error.');
  }

  return data;
}

export function signup(payload) {
  return request('/auth/signup', { method: 'POST', body: JSON.stringify(payload) });
}

export function login(payload) {
  return request('/auth/login', { method: 'POST', body: JSON.stringify(payload) });
}

export function getProfile() {
  return request('/profile');
}

export function createProfile(profile) {
  return request('/profile', {
    method: 'POST',
    body: JSON.stringify(profile),
  });
}

export function updateProfile(profileId, profile) {
  return request(`/profile/${profileId}`, {
    method: 'PUT',
    body: JSON.stringify(profile),
  });
}

export function getRecommendation(payload) {
  return request('/recommendation', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getTrainerPlan(payload) {
  return request('/trainer-plan', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function saveWorkoutFeedback(payload) {
  return request('/workout-feedback', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getHistory() {
  return request('/history');
}

export function getProgressSummary() {
  return request('/progress-summary');
}

export function runWhatIf(question) {
  return request('/what-if', {
    method: 'POST',
    body: JSON.stringify({ question }),
  });
}
