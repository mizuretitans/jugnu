import { useAskHelper, useConfig, useHelper } from '../api/hooks';
import { CHAT_NOTICE, SUPPORT_NOTICE } from '../content/copy';
import { ChatForm } from './ChatForm';
import { ChatThread, type Bubble } from './ChatThread';

export function HelperChat() {
  const config = useConfig().data;
  const helper = useHelper(true);
  const ask = useAskHelper();
  if (!config) return null;

  const bubbles: Bubble[] = (helper.data?.messages ?? []).map((m, i) => ({
    key: i,
    name: m.role === 'user' ? 'You' : 'Guide',
    text: m.content,
    mine: m.role === 'user',
  }));
  if (ask.isPending) {
    bubbles.push({ key: 'pending', name: 'You', text: ask.variables, mine: true, pending: true });
  }

  return (
    <div className="box">
      <span className="tag">{config.ai_mode === 'demo' ? 'Demo guide' : 'AI guide'}</span>
      <h3>Ask your guide</h3>
      {config.ai_available ? (
        <>
          <ChatThread
            label="Chat with your guide" bubbles={bubbles} typing={ask.isPending}
            empty="Ask about your roadmap, your next step, or what to discuss with a mentor."
          />
          <ChatForm label="Your message" maxLength={2000} onSend={(text) => ask.mutateAsync(text)} />
          <div className="notice stack-top">
            <p>{CHAT_NOTICE[config.ai_mode]}</p>
            <p>{SUPPORT_NOTICE}</p>
          </div>
        </>
      ) : (
        <p>The AI guide is not set up on this server yet.</p>
      )}
    </div>
  );
}
