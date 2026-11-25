import { useEffect, useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router';
import { useAuth } from '../auth/AuthContext';
import { Loading, Page, Problem } from '../components/Page';
import { clearNext, peekNext } from '../lib/next';

/** Sends a logged-in person to the page they originally wanted. */
export function AfterLogin() {
  const navigate = useNavigate();
  const [next] = useState(peekNext);
  useEffect(() => {
    clearNext();
    navigate(next, { replace: true });
  }, [navigate, next]);
  return <Loading />;
}

/** Google sends people back here; supabase-js exchanges the ?code= for a session. */
export function AuthCallback() {
  const { status, retry } = useAuth();
  if (status === 'loading') return <Loading />;
  if (status === 'error') return <Problem onRetry={retry} />;
  if (status === 'active') return <AfterLogin />;
  if (status === 'onboarding') return <Navigate to="/welcome" replace />;
  return (
    <Page kicker="Log in" title="Login did not finish.">
      <p className="intro" role="alert">Google login was cancelled or expired. Please try again.</p>
      <div className="actions"><Link className="btn" to="/login">Back to login</Link></div>
    </Page>
  );
}
