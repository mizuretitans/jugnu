import { useEffect } from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router';
import { useAuth } from '../auth/AuthContext';

function Account() {
  const { status, logout } = useAuth();
  const navigate = useNavigate();
  if (status === 'loading') return null;
  if (status === 'guest' || status === 'error') {
    return (
      <>
        <Link className="link" to="/login">Log in</Link>
        <Link className="btn small" to="/login">Get started</Link>
      </>
    );
  }
  const leave = async () => {
    navigate('/');
    await logout();
  };
  return (
    <>
      <Link className="link" to={status === 'onboarding' ? '/welcome' : '/dashboard'}>
        {status === 'onboarding' ? 'Finish sign up' : 'Dashboard'}
      </Link>
      <button type="button" className="outline small" onClick={leave}>Log out</button>
    </>
  );
}

export function Layout() {
  const { pathname, hash } = useLocation();
  useEffect(() => {
    const target = hash ? document.getElementById(hash.slice(1)) : null;
    if (target) target.scrollIntoView();
    else window.scrollTo({ top: 0, behavior: 'instant' });
  }, [pathname, hash]);

  return (
    <>
      <header>
        <Link to="/" className="brand" aria-label="Jugnu home">
          <span className="mark">✳</span>Jugnu<span className="branddot">.</span>
        </Link>
        <nav>
          <Link to="/#how">How it works</Link>
          <Link to="/mentors">Explore mentors</Link>
          <Link to="/community">Community</Link>
        </nav>
        <div className="account"><Account /></div>
      </header>
      <main id="app"><Outlet /></main>
      <footer>
        <Link className="brand" to="/">Jugnu.</Link>
        <span>Student &amp; mentor community</span>
        <Link to="/mentors">Explore mentors</Link>
      </footer>
    </>
  );
}
