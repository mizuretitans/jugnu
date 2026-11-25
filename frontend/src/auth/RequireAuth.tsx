import type { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router';
import type { Role } from '../api/types';
import { Loading, Problem } from '../components/Page';
import { rememberNext } from '../lib/next';
import { useAuth } from './AuthContext';

/** Convenience only. The server checks every request itself. */
export function RequireAuth({ role, children }: { role?: Role; children: ReactNode }) {
  const { status, user, retry } = useAuth();
  const location = useLocation();

  if (status === 'loading') return <Loading />;
  if (status === 'error') return <Problem onRetry={retry} />;
  if (status === 'guest') {
    rememberNext(location.pathname);
    return <Navigate to="/login" replace />;
  }
  if (status === 'onboarding') {
    rememberNext(location.pathname);
    return <Navigate to="/welcome" replace />;
  }
  if (role && user?.role !== role) return <Navigate to="/dashboard" replace />;
  return children;
}
