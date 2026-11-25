import { Link, useParams } from 'react-router';
import { errorText } from '../api/client';
import { useConfig, useCreatePost, usePosts } from '../api/hooks';
import { useAuth } from '../auth/AuthContext';
import { ChatForm } from '../components/ChatForm';
import { ChatThread } from '../components/ChatThread';
import { Loading, NotFound, Page } from '../components/Page';
import { rememberNext } from '../lib/next';

function Group({ field, label }: { field: string; label: string }) {
  const { user } = useAuth();
  const posts = usePosts(field);
  const create = useCreatePost(field);
  const bubbles = (posts.data ?? []).map((p) => ({
    key: p.id,
    name: p.author_role === 'mentor' ? `${p.author_name} · Mentor` : p.author_name,
    text: p.body,
  }));
  return (
    <div className="box">
      <h3>{label}</h3>
      {posts.isError ? <p className="error" role="alert">{errorText(posts.error)}</p> : (
        <ChatThread
          label={`${label} discussion`} bubbles={bubbles}
          empty={posts.isPending ? 'Loading…' : 'Start the conversation with a question or an introduction.'}
        />
      )}
      {user ? (
        <ChatForm label="Your message" maxLength={1500} onSend={(body) => create.mutateAsync(body)} />
      ) : (
        <Link className="btn" to="/login" onClick={() => rememberNext(`/community/${field}`)}>
          Log in to join the discussion
        </Link>
      )}
    </div>
  );
}

export function Community() {
  const { field = 'civil_services' } = useParams();
  const config = useConfig().data;
  if (!config) return <Loading />;
  const current = config.community_fields.find((f) => f.key === field);
  if (!current) return <NotFound />;
  return (
    <Page kicker="Community" title="Group discussions">
      <div className="chips">
        {config.community_fields.map((f) => (
          <Link key={f.key} to={`/community/${f.key}`} className={`btn chip${f.key === field ? ' active' : ''}`}>
            {f.label}
          </Link>
        ))}
      </div>
      <Group key={field} field={field} label={current.label} />
    </Page>
  );
}
