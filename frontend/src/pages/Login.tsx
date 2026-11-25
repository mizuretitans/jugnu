import { useState } from 'react';
import { Navigate } from 'react-router';
import { errorText } from '../api/client';
import type { DemoAccount } from '../api/types';
import { useAuth } from '../auth/AuthContext';
import { AfterLogin } from './AuthCallback';
import { Eyebrow, Loading, Problem } from '../components/Page';

const DEMOS: [DemoAccount, string][] = [
  ['student', 'New student'],
  ['student_almost', 'Student finishing the guide'],
  ['student_done', 'Student with dashboard'],
  ['mentor', 'Mentor'],
];

export function Login() {
  const auth = useAuth();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  if (auth.status === 'loading') return <Loading />;
  if (auth.status === 'error') return <Problem onRetry={auth.retry} />;
  if (auth.status === 'onboarding') return <Navigate to="/welcome" replace />;
  if (auth.status === 'active') return <AfterLogin />;

  const run = async (action: () => Promise<void>) => {
    setError('');
    setBusy(true);
    try {
      await action();
    } catch (problem) {
      setError(errorText(problem));
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="wrap page split auth">
      <div>
        <Eyebrow>Jugnu community</Eyebrow>
        <h1>Welcome to Jugnu.</h1>
        <p className="intro">A little guidance for the path ahead.</p>
        <img className="art" src="/landscape.svg" alt="" />
      </div>
      <div className="box">
        <h2>Log in</h2>
        <p>New here? Continue with Google and we will create your account.</p>
        {auth.googleAvailable ? (
          <button
            type="button" className="outline google" disabled={busy}
            onClick={() => run(auth.loginWithGoogle)}
          >
            <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true">
              <path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9.1 3.6l6.8-6.8C35.8 2.4 30.3 0 24 0 14.6 0 6.5 5.4 2.6 13.2l7.9 6.2C12.4 13.7 17.7 9.5 24 9.5z" />
              <path fill="#4285F4" d="M47 24.6c0-1.6-.2-3.1-.4-4.6H24v9h12.9c-.6 3-2.3 5.5-4.8 7.2l7.7 6C44.4 38 47 31.8 47 24.6z" />
              <path fill="#FBBC05" d="M10.5 28.6A14.5 14.5 0 0 1 9.8 24c0-1.6.3-3.1.7-4.6l-7.9-6.2A24 24 0 0 0 0 24c0 3.9.9 7.5 2.6 10.8z" />
              <path fill="#34A853" d="M24 48c6.5 0 11.9-2.1 15.8-5.8l-7.7-6c-2.1 1.4-4.9 2.3-8.1 2.3-6.3 0-11.6-4.2-13.5-9.9l-7.9 6.2C6.5 42.6 14.6 48 24 48z" />
            </svg>
            Continue with Google
          </button>
        ) : (
          <p className="notice">Google login is not set up on this server yet.</p>
        )}
        {error && <p className="error" role="alert">{error}</p>}
        {auth.demoAvailable && (
          <>
            <hr />
            <p>Try a demo workspace</p>
            <div className="actions">
              {DEMOS.map(([account, label]) => (
                <button
                  key={account} type="button" className="small outline" disabled={busy}
                  onClick={() => run(() => auth.loginDemo(account))}
                >
                  {label}
                </button>
              ))}
            </div>
          </>
        )}
      </div>
    </section>
  );
}
