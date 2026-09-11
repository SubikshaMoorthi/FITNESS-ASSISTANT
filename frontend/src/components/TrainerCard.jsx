const interventionLabels = {
  recovery_session: 'Recovery Session',
  light_workout: 'Light Workout',
  heavy_workout: 'Heavy Workout',
  walking_activity: 'Walking Activity',
  rest: 'Rest Day',
  nutrition_guidance: 'Nutrition Guidance',
  lifestyle_guidance: 'Lifestyle Guidance',
};

export function readinessLabel(level) {
  return level ? `You're ${level.toLowerCase()} ready today.` : 'Complete your Daily Check to see your readiness.';
}

export function interventionLabel(intervention) {
  return interventionLabels[intervention] || intervention?.replace(/_/g, ' ') || 'Personal plan';
}

export default function TrainerCard({ result }) {
  if (!result) {
    return <div className="empty-state">Complete a Daily Check and your trainer will prepare a plan for you.</div>;
  }

  return (
    <div className="trainer-insight">
      <div className="insight-icon">✦</div>
      <div>
        <p className="summary-label">Your trainer says</p>
        <h3>{readinessLabel(result.readiness_level)}</h3>
        <p>{result.reason}</p>
      </div>
    </div>
  );
}
