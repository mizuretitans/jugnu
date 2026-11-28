import { useMemo, useState } from 'react';
import { errorText } from '../api/client';
import { useAskCareerExplorer, useCareerPaths, useConfig } from '../api/hooks';
import type { CareerPath, ChatMessage } from '../api/types';
import { ChatForm } from '../components/ChatForm';
import { ChatThread, type Bubble } from '../components/ChatThread';
import { Loading, Page, Problem } from '../components/Page';
import { SUPPORT_NOTICE } from '../content/copy';
import './CareerExplorer.css';

const FILTERS = [
  { key: 'all', label: 'All paths' },
  { key: 'pcb', label: 'Biology / medical' },
  { key: 'pcm', label: 'Maths / non-medical' },
  { key: 'commerce', label: 'Commerce' },
  { key: 'humanities', label: 'Arts / humanities' },
  { key: 'vocational', label: 'Vocational' },
  { key: 'any', label: 'Across streams' },
] as const;

const WELCOME =
  'Ask about the study route, entrance requirements, everyday work, work-life balance, useful skills, or related careers. I’ll flag details that can change and point you to official sources.';

export function CareerExplorer() {
  const pathsQuery = useCareerPaths();
  const configQuery = useConfig();
  const ask = useAskCareerExplorer();
  const [stream, setStream] = useState<(typeof FILTERS)[number]['key']>('all');
  const [search, setSearch] = useState('');
  const [selectedId, setSelectedId] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const paths = pathsQuery.data ?? [];
  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase();
    return paths.filter((path) => {
      const matchesStream = stream === 'all'
        || path.streams.includes(stream)
        || (stream !== 'any' && path.streams.includes('any'));
      const matchesSearch = !query
        || `${path.title} ${path.category} ${path.overview}`.toLowerCase().includes(query);
      return matchesStream && matchesSearch;
    });
  }, [paths, search, stream]);

  const selected = paths.find((path) => path.id === selectedId) ?? null;
  const choose = (path: CareerPath) => {
    setSelectedId(path.id);
    setMessages([]);
    ask.reset();
  };

  const send = async (text: string) => {
    if (!selected) return;
    const history = messages.slice(-12);
    const result = await ask.mutateAsync({ career_id: selected.id, history, text });
    const exchange: ChatMessage[] = [
      { role: 'user', content: text },
      { role: 'assistant', content: result.reply },
    ];
    setMessages((current) => [...current, ...exchange].slice(-24));
  };

  if (pathsQuery.isPending || configQuery.isPending) return <Loading />;
  if (pathsQuery.isError) {
    return <Problem message={errorText(pathsQuery.error)} onRetry={() => void pathsQuery.refetch()} />;
  }
  if (configQuery.isError || !configQuery.data) {
    return <Problem message={errorText(configQuery.error)} onRetry={() => void configQuery.refetch()} />;
  }

  const config = configQuery.data;
  const bubbles: Bubble[] = selected
    ? [
        { key: 'welcome', name: 'Guide', text: WELCOME },
        ...messages.map((message, index) => ({
          key: index,
          name: message.role === 'user' ? 'You' : 'Guide',
          text: message.content,
          mine: message.role === 'user',
        })),
      ]
    : [];
  if (ask.isPending && ask.variables) {
    bubbles.push({ key: 'pending-user', name: 'You', text: ask.variables.text, mine: true, pending: true });
  }

  return (
    <Page
      kicker="Career explorer"
      title="Explore your options after Class 12."
      intro="Browse paths across school streams, get a quick overview, then ask follow-up questions about the work and study route."
    >
      <div className="career-explorer-layout">
        <section className="box career-list" aria-label="Career paths">
          <label className="career-search">
            Find a career
            <input
              className="search"
              value={search}
              maxLength={100}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Try doctor, design, finance…"
            />
          </label>
          <div className="chips career-filters" aria-label="Filter by stream">
            {FILTERS.map((filter) => (
              <button
                key={filter.key}
                type="button"
                className={stream === filter.key ? 'active' : ''}
                aria-pressed={stream === filter.key}
                onClick={() => setStream(filter.key)}
              >
                {filter.label}
              </button>
            ))}
          </div>
          <p className="minor">{filtered.length} paths to explore</p>
          <div className="career-options">
            {filtered.map((path) => (
              <button
                key={path.id}
                type="button"
                className={`career-option${selectedId === path.id ? ' selected' : ''}`}
                aria-pressed={selectedId === path.id}
                onClick={() => choose(path)}
              >
                <span className="tag">{path.category}</span>
                <strong>{path.title}</strong>
                <span className="career-route-preview">{path.route}</span>
              </button>
            ))}
            {filtered.length === 0 && <p>No matching paths. Try another search or stream.</p>}
          </div>
        </section>

        <div className="stack career-detail">
          {selected ? (
            <>
              <section className="box">
                <span className="tag">Quick overview</span>
                <h2 className="career-title">{selected.title}</h2>
                <p className="career-overview">{selected.overview}</p>
                <h3>Typical study route</h3>
                <p>{selected.route}</p>
                <p className="minor">This is a starting point. Eligibility and admission rules can vary by college, state and year.</p>
              </section>

              <section className="box career-chat">
                <span className="tag">{config.ai_mode === 'demo' ? 'Demo guide' : 'AI guide'}</span>
                <h3>Ask about {selected.title}</h3>
                {config.ai_available ? (
                  <>
                    <ChatThread label={`Questions about ${selected.title}`} bubbles={bubbles} typing={ask.isPending} />
                    <ChatForm label="Your question" maxLength={2000} busy={ask.isPending} onSend={send} />
                    <div className="notice stack-top">
                      <p>{config.ai_mode === 'demo'
                        ? 'This is a scripted demo. This chat stays in your current browser tab and is not saved to Jugnu.'
                        : 'AI replies may be incomplete. Your question and recent chat are sent to the configured AI provider; this chat is not saved to Jugnu. Please do not share private details.'}</p>
                      <p>{SUPPORT_NOTICE}</p>
                    </div>
                  </>
                ) : (
                  <p>The career chat is not set up on this server yet. You can still browse the path overviews.</p>
                )}
              </section>
            </>
          ) : (
            <section className="box career-empty">
              <span className="tag">Choose a path</span>
              <h2>What would you like to explore?</h2>
              <p>Select a career to see its quick overview and open a chat about the route, skills, daily work and more.</p>
            </section>
          )}
        </div>
      </div>
    </Page>
  );
}
