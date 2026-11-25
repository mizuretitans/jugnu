import { useState } from 'react';
import { errorText } from '../api/client';
import { useMentors } from '../api/hooks';
import { MentorCard } from '../components/MentorCard';
import { Loading, Page, Problem } from '../components/Page';

const ALL = 'All paths';

export function Mentors() {
  const query = useMentors();
  const [filter, setFilter] = useState(ALL);
  const [search, setSearch] = useState('');
  if (query.isPending) return <Loading />;
  if (query.isError) return <Problem message={errorText(query.error)} onRetry={() => query.refetch()} />;

  const labels = [...new Set(query.data.map((m) => m.field_label))];
  const needle = search.trim().toLowerCase();
  const shown = query.data.filter(
    (m) =>
      (filter === ALL || m.field_label === filter) &&
      `${m.name} ${m.field_label} ${m.bio}`.toLowerCase().includes(needle),
  );

  return (
    <Page kicker="Mentor directory" title="Explore mentors" intro="Meet the mentors on Jugnu.">
      <label>
        <span className="sr">Search mentors</span>
        <input
          className="search" type="search" placeholder="Search by name or career path"
          value={search} onChange={(event) => setSearch(event.target.value)}
        />
      </label>
      <div className="chips">
        {[ALL, ...labels].map((label) => (
          <button
            key={label} type="button" className={filter === label ? 'active' : ''}
            aria-pressed={filter === label} onClick={() => setFilter(label)}
          >
            {label}
          </button>
        ))}
      </div>
      <div className="grid">
        {shown.length ? shown.map((m) => <MentorCard key={m.id} mentor={m} />)
          : <p>No mentors match your search.</p>}
      </div>
    </Page>
  );
}
