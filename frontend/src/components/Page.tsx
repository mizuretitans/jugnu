import type { ReactNode } from 'react';
import { Link } from 'react-router';

export const Eyebrow = ({ children }: { children: ReactNode }) => (
  <div className="eyebrow">{children}</div>
);

interface PageProps { kicker: string; title: ReactNode; intro?: string; children?: ReactNode }

export function Page({ kicker, title, intro, children }: PageProps) {
  return (
    <section className="page wrap">
      <Eyebrow>{kicker}</Eyebrow>
      <h1>{title}</h1>
      {intro && <p className="intro">{intro}</p>}
      {children}
    </section>
  );
}

export const Loading = () => (
  <section className="page wrap"><p className="loading" role="status">Loading…</p></section>
);

export function Problem({ message, onRetry }: { message?: string; onRetry?: () => void }) {
  return (
    <Page kicker="Jugnu" title="Something went wrong.">
      <p className="intro" role="alert">{message ?? 'Could not reach Jugnu. Please try again.'}</p>
      <div className="actions">
        {onRetry && <button type="button" onClick={onRetry}>Try again</button>}
        <Link className="btn outline" to="/">Go to home</Link>
      </div>
    </Page>
  );
}

export const NotFound = () => (
  <Page kicker="Jugnu" title="Page not found.">
    <div className="actions"><Link className="btn" to="/">Go to home</Link></div>
  </Page>
);
