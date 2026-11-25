import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router';
import { errorText } from '../api/client';
import {
  useConfig, useDashboard, useIntake, useRestartIntake, useSendIntake, useStartIntake,
} from '../api/hooks';
import { ChatForm } from '../components/ChatForm';
import { ChatThread, type Bubble } from '../components/ChatThread';
import { Loading, Page, Problem } from '../components/Page';
import { CHAT_NOTICE, PRIVACY_NOTICE, SUPPORT_NOTICE } from '../content/copy';

const REDIRECT_MS = 5_000;

function Finished() {
  const dashboard = useDashboard().data;
  const restart = useRestartIntake();
  const retake = () => {
    if (window.confirm('Retaking the guide deletes your current answers and both guide chats. Continue?')) {
      restart.mutate();
    }
  };
  return (
    <Page kicker="Your career guide" title="Your suggested path">
      <div className="box narrow">
        <span className="tag">Based on your conversation</span>
        <h2>{dashboard?.field_label ?? '…'}</h2>
        <p>
          This is a direction to explore, not a final decision.
          {dashboard?.secondary_labels.length ? ` You could also look at: ${dashboard.secondary_labels.join(', ')}.` : ''}
        </p>
        {restart.isError && <p className="error" role="alert">{errorText(restart.error)}</p>}
        <div className="actions">
          <Link className="btn" to="/dashboard">Go to my dashboard</Link>
          <button type="button" className="outline" disabled={restart.isPending} onClick={retake}>
            Retake guide
          </button>
        </div>
      </div>
    </Page>
  );
}

export function Guide() {
  const navigate = useNavigate();
  const config = useConfig().data;
  const intake = useIntake();
  const start = useStartIntake();
  const send = useSendIntake();
  const [justFinished, setJustFinished] = useState(false);
  const [turnError, setTurnError] = useState('');
  const [returning, setReturning] = useState(false);
  const checkedReturn = useRef(false);

  const status = intake.data?.status;
  const available = config?.ai_available ?? false;

  const { mutate: startChat } = start;
  useEffect(() => {
    if (status === 'not_started' && available) startChat();
  }, [status, available, startChat]);

  // Decide once, on the first load, whether this is a returning student.
  useEffect(() => {
    if (!intake.data || checkedReturn.current) return;
    checkedReturn.current = true;
    setReturning(intake.data.messages.some((m) => m.role === 'user'));
  }, [intake.data]);

  useEffect(() => {
    if (!justFinished) return;
    const timer = setTimeout(() => navigate('/dashboard'), REDIRECT_MS);
    return () => clearTimeout(timer);
  }, [justFinished, navigate]);

  if (intake.isError) {
    return <Problem message={errorText(intake.error)} onRetry={() => intake.refetch()} />;
  }
  if (!config || !intake.data) return <Loading />;
  if (status === 'completed' && !justFinished && !send.isPending) return <Finished />;
  if (!available) {
    return (
      <Page kicker="Career guide" title="Let’s find your direction.">
        <div className="box narrow">
          <p>The AI guide is not set up on this server yet. You can still explore mentors.</p>
          <div className="actions"><Link className="btn" to="/mentors">Explore mentors</Link></div>
        </div>
      </Page>
    );
  }

  const sendText = async (text: string) => {
    setTurnError('');
    setReturning(false);
    const turn = await send.mutateAsync(text);
    if (turn.done) setJustFinished(true);
    else if (turn.error) setTurnError(turn.reply);
  };

  const messages = intake.data.messages;
  const last = messages.at(-1);
  const bubbles: Bubble[] = messages.map((m, i) => ({
    key: i,
    name: m.role === 'user' ? 'You' : 'Guide',
    text: m.content,
    mine: m.role === 'user',
  }));
  const working = send.isPending || intake.data.busy;
  const alreadyShown = last?.role === 'user' && last.content === send.variables;
  if (send.isPending && !alreadyShown) {
    bubbles.push({ key: 'pending', name: 'You', text: send.variables, mine: true, pending: true });
  }

  return (
    <Page kicker="Career guide" title="Let’s find your direction.">
      <div className="box narrow">
        <span className="tag">{config.ai_mode === 'demo' ? 'Demo guide' : 'AI guide'}</span>
        {returning && <p><strong>Welcome back!</strong> Let’s continue where we left off.</p>}
        <ChatThread label="Career guide chat" bubbles={bubbles} typing={working} />
        {start.isError && (
          <p className="error" role="alert">
            {errorText(start.error)}{' '}
            <button type="button" className="small" onClick={() => startChat()}>Try again</button>
          </p>
        )}
        {justFinished ? (
          <div className="actions"><Link className="btn" to="/dashboard">Go to my dashboard</Link></div>
        ) : (
          <>
            {intake.data.can_retry && !working && last && (
              <div role="alert">
                <p className="error">{turnError || 'Your last message did not get a reply.'}</p>
                <button
                  type="button" className="small outline"
                  onClick={() => void sendText(last.content).catch((e: unknown) => setTurnError(errorText(e)))}
                >
                  Try again
                </button>
              </div>
            )}
            <ChatForm label="Your message" maxLength={2000} busy={working} onSend={sendText} />
          </>
        )}
        <div className="notice stack-top">
          <p>{CHAT_NOTICE[config.ai_mode]}</p>
          <p>{PRIVACY_NOTICE}</p>
          <p>{SUPPORT_NOTICE}</p>
        </div>
      </div>
    </Page>
  );
}
