import { useState, type FormEvent } from 'react';
import { Navigate } from 'react-router';
import { errorText } from '../api/client';
import { useConfig } from '../api/hooks';
import type { Role } from '../api/types';
import { useAuth } from '../auth/AuthContext';
import { Loading, Page, Problem } from '../components/Page';
import { AfterLogin } from './AuthCallback';

function OnboardingForm() {
  const { suggestedName, finishOnboarding } = useAuth();
  const config = useConfig().data;
  const [role, setRole] = useState<Role>('student');
  const [name, setName] = useState(suggestedName);
  const [field, setField] = useState('');
  const [bio, setBio] = useState('');
  const [rate, setRate] = useState('500');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');
    setBusy(true);
    try {
      await finishOnboarding({
        role,
        name,
        ...(role === 'mentor' ? { field, bio, hourly_rate_rupees: Number(rate) } : {}),
      });
    } catch (problem) {
      setError(errorText(problem));
      setBusy(false);
    }
  };

  return (
    <form className="box narrow" onSubmit={submit}>
      <label>
        Your name
        <input
          required maxLength={60} autoComplete="name" value={name}
          onChange={(event) => setName(event.target.value)}
        />
      </label>
      <label>
        Account type
        <select value={role} onChange={(event) => setRole(event.target.value as Role)}>
          <option value="student">Student</option>
          <option value="mentor">Mentor</option>
        </select>
      </label>
      <p>You cannot change the account type later.</p>
      {role === 'mentor' && (
        <>
          <label>
            Career field
            <select required value={field} onChange={(event) => setField(event.target.value)}>
              <option value="" disabled>Choose a field</option>
              {config?.mentor_fields.map((f) => <option key={f.key} value={f.key}>{f.label}</option>)}
            </select>
          </label>
          <label>
            How can you help students?
            <textarea
              required minLength={10} maxLength={500} value={bio}
              onChange={(event) => setBio(event.target.value)}
            />
          </label>
          <label>
            Hourly rate (₹)
            <input
              type="number" required min={1} max={100000} step={1} value={rate}
              onChange={(event) => setRate(event.target.value)}
            />
          </label>
          <p className="notice">New mentors are reviewed before students can see them.</p>
        </>
      )}
      {error && <p className="error" role="alert">{error}</p>}
      <button disabled={busy}>Create account</button>
    </form>
  );
}

export function Welcome() {
  const { status, retry } = useAuth();
  if (status === 'loading') return <Loading />;
  if (status === 'error') return <Problem onRetry={retry} />;
  if (status === 'guest') return <Navigate to="/login" replace />;
  if (status === 'active') return <AfterLogin />;
  return (
    <Page kicker="Welcome" title="Tell us who you are.">
      <OnboardingForm />
    </Page>
  );
}
