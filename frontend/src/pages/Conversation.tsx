import { Link, useParams } from 'react-router';
import { errorText } from '../api/client';
import { useConversation, useSendMessage, useStudentBrief } from '../api/hooks';
import { useAuth } from '../auth/AuthContext';
import { ChatForm } from '../components/ChatForm';
import { ChatThread } from '../components/ChatThread';
import { Loading, Page, Problem } from '../components/Page';

function Brief({ requestId }: { requestId: string }) {
  const brief = useStudentBrief(requestId, true).data;
  if (!brief) return null;
  const rows: [string, string][] = [
    ['Summary', brief.summary],
    ['Goals', brief.goals],
    ['Help wanted', brief.guidance_needed],
    ['Interests', brief.interests.join(', ')],
    ['Strengths', brief.strengths.join(', ')],
    ['Suggested focus', brief.mentor_focus],
  ];
  return (
    <div className="box narrow stack-top">
      <span className="tag">{brief.field_label ?? 'Student brief'}</span>
      <h3>About this student</h3>
      {brief.needs_human_followup && (
        <p className="flag">
          This student may need extra support. Please check in with care and tell the Jugnu team.
        </p>
      )}
      {rows.filter(([, value]) => value).map(([label, value]) => (
        <p key={label}><strong>{label}:</strong> {value}</p>
      ))}
      <p className="minor">Written by AI from the student’s guide chat. It may contain mistakes.</p>
    </div>
  );
}

export function ConversationPage() {
  const { requestId = '' } = useParams();
  const { user } = useAuth();
  const query = useConversation(requestId);
  const send = useSendMessage(requestId);
  if (query.isPending) return <Loading />;
  if (!query.data) return <Problem message={errorText(query.error)} />;
  const { request, messages } = query.data;
  const isMentor = user?.role === 'mentor';

  return (
    <Page kicker="Mentor conversation" title={isMentor ? request.student.name : request.mentor.name}>
      <div className="box narrow">
        <ChatThread
          label="Conversation"
          bubbles={messages.map((m) => ({ key: m.id, name: m.sender_name, text: m.body, mine: m.mine }))}
          empty="Start the conversation with a question or an introduction."
        />
        <ChatForm label="Your message" maxLength={1500} onSend={(body) => send.mutateAsync(body)} />
        <p><Link className="link" to="/dashboard">Back to dashboard</Link></p>
      </div>
      {isMentor && <Brief requestId={requestId} />}
    </Page>
  );
}
