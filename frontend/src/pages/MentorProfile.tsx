import { Link, useNavigate, useParams } from 'react-router';
import { errorText } from '../api/client';
import { useDashboard, useMentor, useRequestMentor } from '../api/hooks';
import { useAuth } from '../auth/AuthContext';
import { Loading, Page, Problem } from '../components/Page';
import { money } from '../lib/money';
import { rememberNext } from '../lib/next';

export function MentorProfile() {
  const { id = '' } = useParams();
  const { user, status } = useAuth();
  const navigate = useNavigate();
  const query = useMentor(id);
  const dashboard = useDashboard(user?.role === 'student');
  const request = useRequestMentor();

  if (query.isPending) return <Loading />;
  if (query.isError) return <Problem message={errorText(query.error)} />;
  const mentor = query.data;
  const existing = dashboard.data?.requests.find((r) => r.mentor.id === id);

  const askMentor = async () => {
    if (!user) {
      rememberNext(`/mentors/${id}`);
      navigate(status === 'onboarding' ? '/welcome' : '/login');
      return;
    }
    await request.mutateAsync(id).then(() => navigate('/dashboard'), () => undefined);
  };

  return (
    <Page kicker="Mentor profile" title={mentor.name}>
      <div className="split">
        <div className="box">
          <span className="tag">{mentor.field_label}</span>
          <h3>Mentorship focus</h3>
          <p>{mentor.bio}</p>
          {user?.role !== 'mentor' && (existing ? (
            <Link className="btn" to="/dashboard">
              View request · {existing.status === 'accepted' ? 'Accepted' : 'Pending'}
            </Link>
          ) : (
            <button type="button" disabled={request.isPending} onClick={askMentor}>
              Request mentorship
            </button>
          ))}
          {request.isError && <p className="error" role="alert">{errorText(request.error)}</p>}
        </div>
        <div className="box">
          <h3>Book a teaching session</h3>
          <p className="price">{money(mentor.hourly_rate_paise)} / hour</p>
          {user?.role !== 'mentor' && (
            <Link className="btn" to={`/mentors/${id}/book`}>Book a session</Link>
          )}
          <p>
            Bring one question about {mentor.field_label.toLowerCase()} and a goal you would like to
            work towards.
          </p>
          <Link className="link" to="/mentors">Browse other mentors</Link>
        </div>
      </div>
    </Page>
  );
}
