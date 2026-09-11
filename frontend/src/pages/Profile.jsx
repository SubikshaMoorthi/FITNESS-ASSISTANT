import { useEffect, useState } from 'react';
import { useAppContext } from '../context/AppContext';
import { createProfile, getProfile, updateProfile } from '../services/api';
import TopHeader from '../components/TopHeader';

const defaultProfile = {
  name: '',
  age: 28,
  gender: 'Prefer not to say',
  height: 170,
  weight: 68,
  fitness_goal: 'General Fitness',
  fitness_level: 'Intermediate',
  workout_preference: 'Both',
  dietary_preference: 'No Preference',
  available_workout_minutes: 45,
};

export default function Profile() {
  const { profile, profileId, setProfile } = useAppContext();
  const [profileForm, setProfileForm] = useState(profile || defaultProfile);
  const [savedProfile, setSavedProfile] = useState(profile || defaultProfile);
  const [isEditing, setIsEditing] = useState(false);
  const [profileStatus, setProfileStatus] = useState({ type: '', message: '' });

  useEffect(() => {
    let active = true;

    async function loadProfile() {
      if (!profileId) return;

      try {
        const data = await getProfile();
        if (active) {
          const loadedProfile = {
            ...defaultProfile,
            ...data,
            available_workout_minutes: data.available_workout_minutes ?? profile?.available_workout_minutes ?? 45,
          };
          setProfileForm(loadedProfile);
          setSavedProfile(loadedProfile);
          setProfile(loadedProfile);
        }
      } catch (err) {
        if (active) {
          setProfileStatus({ type: 'error', message: err.message || 'Unable to load your profile.' });
        }
      }
    }

    loadProfile();
    return () => {
      active = false;
    };
  }, [profileId]);

  const handleProfileChange = (field, value) => {
    setProfileForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleProfileSubmit = async (event) => {
    event.preventDefault();
    setProfileStatus({ type: '', message: '' });

    try {
      const payload = {
        ...profileForm,
        height: Number(profileForm.height),
        weight: Number(profileForm.weight),
        age: Number(profileForm.age),
      };
      const data = profileId
        ? await updateProfile(profileId, payload)
        : await createProfile(payload);
      const savedProfile = { ...data, available_workout_minutes: Number(profileForm.available_workout_minutes) };

      setProfileStatus({
        type: 'success',
        message: 'Profile updated successfully ✓',
      });
      setProfile(savedProfile);
      setProfileForm(savedProfile);
      setSavedProfile(savedProfile);
      setIsEditing(false);
    } catch (err) {
      setProfileStatus({ type: 'error', message: err.message || 'Unable to save profile.' });
    }
  };

  const cancelEditing = () => {
    setProfileForm(savedProfile);
    setProfileStatus({ type: '', message: '' });
    setIsEditing(false);
  };

  return (
    <div className="page-card">
      <TopHeader eyebrow="Profile" title="My Profile" description="Save your details so your trainer can make better recommendations." />

      <section className="panel profile-section">
        {!isEditing ? (
          <div className="profile-readonly-grid">
            <div><span>Name</span><strong>{savedProfile.name || '--'}</strong></div>
            <div><span>Age</span><strong>{savedProfile.age || '--'}</strong></div>
            <div><span>Gender</span><strong>{savedProfile.gender || 'Prefer not to say'}</strong></div>
            <div><span>Height</span><strong>{savedProfile.height ? `${savedProfile.height} cm` : '--'}</strong></div>
            <div><span>Weight</span><strong>{savedProfile.weight ? `${savedProfile.weight} kg` : '--'}</strong></div>
            <div><span>BMI</span><strong>{savedProfile.bmi || '--'}</strong></div>
            <div><span>Fitness goal</span><strong>{savedProfile.fitness_goal || '--'}</strong></div>
            <div><span>Fitness level</span><strong>{savedProfile.fitness_level || '--'}</strong></div>
            <div><span>Workout preference</span><strong>{savedProfile.workout_preference || '--'}</strong></div>
            <div><span>Dietary preference</span><strong>{savedProfile.dietary_preference || '--'}</strong></div>
            <div><span>Available workout time</span><strong>{savedProfile.available_workout_minutes ?? '--'} minutes</strong></div>
            <button type="button" onClick={() => { setProfileStatus({ type: '', message: '' }); setIsEditing(true); }}>Edit Profile</button>
          </div>
        ) : (
        <form className="profile-form" onSubmit={handleProfileSubmit}>
          <div className="field-grid profile-grid">
            <label>
              Name
              <input
                type="text"
                required
                minLength="2"
                maxLength="100"
                value={profileForm.name}
                onChange={(e) => handleProfileChange('name', e.target.value)}
                placeholder="e.g. Sarah Johnson"
              />
            </label>

            <label>
              Age
              <input
                type="number"
                required
                min="10"
                max="120"
                value={profileForm.age}
                onChange={(e) => handleProfileChange('age', Number(e.target.value))}
              />
            </label>

            <label>
              Gender (optional)
              <select value={profileForm.gender} onChange={(e) => handleProfileChange('gender', e.target.value)}>
                <option value="Prefer not to say">Prefer not to say</option>
                <option value="Female">Female</option>
                <option value="Male">Male</option>
                <option value="Other">Other</option>
              </select>
            </label>

            <label>
              Height (cm)
              <input
                type="number"
                required
                min="50"
                max="250"
                value={profileForm.height}
                onChange={(e) => handleProfileChange('height', Number(e.target.value))}
              />
            </label>

            <label>
              Weight (kg)
              <input
                type="number"
                min="20"
                max="250"
                step="0.1"
                value={profileForm.weight}
                onChange={(e) => handleProfileChange('weight', Number(e.target.value))}
              />
            </label>

            <label>
              Fitness goal
              <select value={profileForm.fitness_goal} onChange={(e) => handleProfileChange('fitness_goal', e.target.value)}>
                <option value="Weight Loss">Weight Loss</option>
                <option value="Muscle Gain">Muscle Gain</option>
                <option value="General Fitness">General Fitness</option>
                <option value="Improve Endurance">Improve Endurance</option>
              </select>
            </label>

            <label>
              Fitness level
              <select value={profileForm.fitness_level} onChange={(e) => handleProfileChange('fitness_level', e.target.value)}>
                <option value="Beginner">Beginner</option>
                <option value="Intermediate">Intermediate</option>
                <option value="Advanced">Advanced</option>
              </select>
            </label>

            <label>
              Workout preference
              <select value={profileForm.workout_preference} onChange={(e) => handleProfileChange('workout_preference', e.target.value)}>
                <option value="Home">Home</option>
                <option value="Gym">Gym</option>
                <option value="Both">Both</option>
              </select>
            </label>

            <label>
              Dietary preference
              <select value={profileForm.dietary_preference} onChange={(e) => handleProfileChange('dietary_preference', e.target.value)}>
                <option value="Vegetarian">Vegetarian</option>
                <option value="Non-Vegetarian">Non-Vegetarian</option>
                <option value="Vegan">Vegan</option>
                <option value="No Preference">No Preference</option>
              </select>
            </label>

            <label>
              Available workout time (minutes)
              <input
                type="number"
                min="0"
                max="180"
                step="5"
                value={profileForm.available_workout_minutes}
                onChange={(e) => handleProfileChange('available_workout_minutes', Number(e.target.value))}
              />
            </label>
          </div>

          <div className="inline-actions">
            <button type="submit" className="profile-save-btn">Save Changes</button>
            <button type="button" className="secondary-btn" onClick={cancelEditing}>Cancel</button>
          </div>

          {profileStatus.message && (
            <p className={profileStatus.type === 'success' ? 'success-message' : 'error'}>
              {profileStatus.message}
            </p>
          )}
        </form>
        )}

        {!isEditing && profileStatus.message && (
          <p className={profileStatus.type === 'success' ? 'success-message' : 'error'}>
            {profileStatus.message}
          </p>
        )}
      </section>
    </div>
  );
}
