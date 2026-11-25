import { Link } from 'react-router';
import { errorText } from '../api/client';
import { useAccept, useDashboard } from '../api/hooks';
import type { Dashboard } from '../api/types';
import { useAuth } from '../auth/AuthContext';
import { BookingList } from '../components/BookingList';
import { HelperChat } from '../components/HelperChat';
import { MentorCard } from '../components/MentorCard';
import { Loading, Page, Problem } from '../components/Page';
import { RateForm } from '../components/RateForm';
import { Roadmap } from '../components/Roadmap';

function Requests({ data }: { data: Dashboard }) {
  const accept = useAccept();
  const isMentor = data.role === 'mentor';
  return (
    <div className="box">
      <h3>{isMentor ? 'Mentorship requests' : 'My mentors'}</h3>
      {data.requests.length === 0 && (
        <p>
          {isMentor
            ? 'Student requests will appear here.'
            : 'Choose a mentor and request guidance to get started.'}
        </p>
      )}
      {data.requests.map((r) => (
        <div className="resource" key={r.id}>
          <strong>{isMentor ? r.student.name : r.mentor.name}</strong>{' '}
          <span className="tag">{r.status === 'accepted' ? 'Accepted' : 'Pending'}</span>
          <div>
            {isMentor && r.status === 'pending' && (
              <button
                type="button" className="small" disabled={accept.isPending}
                onClick={() => accept.mutate(r.id)}
              >
                Accept request
              </button>
            )}
            {r.status === 'accepted' && (
              <Link className="link" to={`/messages/${r.id}`}>Open conversation</Link>
            )}
          </div>
        </div>
      ))}
      {accept.isError && <p className="error" role="alert">{errorText(accept.error)}</p>}
      {!isMentor && <Link className="link" to="/mentors">Explore mentors</Link>}
    </div>
  );
}

function GuideCta({ status }: { status: Dashboard['intake_status'] }) {
  return (
    <div className="box">
      <span className="tag">Career guide</span>
      <h3>{status === 'not_started' ? 'Start with your guide' : 'Continue your guide chat'}</h3>
      <p>A short chat about your interests and goals shapes your roadmap and mentor suggestions.</p>
      <Link className="btn" to="/guide">✧ &nbsp; Find my path</Link>
    </div>
  );
}

function RoadmapBox({ data }: { data: Dashboard }) {
  const isMentor = data.role === 'mentor';
  return (
    <div className="box">
      <span className="tag">{data.field_label ?? 'Explore'}</span>
      <h3>{isMentor ? 'Mentoring resources' : 'Your learning roadmap'}</h3>
      <Roadmap steps={data.roadmap} />
      {!isMentor && data.secondary_labels.length > 0 && (
        <p>Also worth exploring: {data.secondary_labels.join(', ')}</p>
      )}
      {!isMentor && <Link className="link" to="/guide">Open career guide</Link>}
    </div>
  );
}

const CommunityBox = () => (
  <div className="box">
    <h3>Community groups</h3>
    <p>Share a question or join a discussion with other students and mentors.</p>
    <Link className="link" to="/community">Open community</Link>
  </div>
);

function Suggestions({ data }: { data: Dashboard }) {
  if (data.suggested_mentors.length === 0) return null;
  const missing = data.field && data.field !== 'undecided' && !data.field_has_mentors;
  return (
    <section className="stack-top">
      <div className="sectionhead"><h2>Mentors for you</h2></div>
      {missing && (
        <p className="intro">
          There are no {data.field_label} mentors on Jugnu yet. These mentors can still help you explore.
        </p>
      )}
      <div className="grid">
        {data.suggested_mentors.map((m) => <MentorCard key={m.id} mentor={m} />)}
      </div>
    </section>
  );
}

export function DashboardPage() {
  const { user } = useAuth();
  const query = useDashboard();
  if (query.isPending) return <Loading />;
  if (!query.data) {
    return <Problem message={errorText(query.error)} onRetry={() => query.refetch()} />;
  }
  const data = query.data;
  const isMentor = data.role === 'mentor';
  const guideDone = data.intake_status === 'completed';

  return (
    <Page
      kicker={isMentor ? 'Mentor dashboard' : 'Student dashboard'}
      title={`Welcome, ${user?.name.split(' ')[0]}.`}
    >
      {data.mentor && !data.mentor.is_listed && (
        <p className="notice">
          Your profile is waiting for review. Students will see you once it is approved.
        </p>
      )}
      <div className="split columns">
        <div className="stack">
          <div className="box">
            <h3>Paid sessions</h3>
            <BookingList bookings={data.bookings} role={data.role} />
          </div>
          <Requests data={data} />
          {!isMentor && <RoadmapBox data={data} />}
          <CommunityBox />
        </div>
        <div className="stack">
          {data.mentor && <RateForm currentPaise={data.mentor.hourly_rate_paise} />}
          {isMentor && <RoadmapBox data={data} />}
          {!isMentor && (guideDone ? <HelperChat /> : <GuideCta status={data.intake_status} />)}
        </div>
      </div>
      {!isMentor && <Suggestions data={data} />}
    </Page>
  );
}
