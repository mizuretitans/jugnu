import { useState, type FormEvent } from 'react';
import { useNavigate, useParams } from 'react-router';
import { ApiError, errorText } from '../api/client';
import { useBook, useMentor } from '../api/hooks';
import { Loading, Page, Problem } from '../components/Page';
import { DURATIONS, money, priceFor } from '../lib/money';

export function Book() {
  const { id = '' } = useParams();
  const navigate = useNavigate();
  const query = useMentor(id);
  const book = useBook();
  const [minutes, setMinutes] = useState(60);
  const [topic, setTopic] = useState('');
  // One key per checkout: pressing Pay twice, or retrying after a lost connection, books once.
  const [key, setKey] = useState(() => crypto.randomUUID());

  if (query.isPending) return <Loading />;
  if (query.isError) return <Problem message={errorText(query.error)} />;
  const mentor = query.data;
  const rate = mentor.hourly_rate_paise;

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await book.mutateAsync({
        idempotency_key: key, mentor_id: id, minutes, topic: topic.trim(), expected_rate_paise: rate,
      });
      navigate('/dashboard');
    } catch (problem) {
      if (problem instanceof ApiError && problem.status === 409) setKey(crypto.randomUUID());
    }
  };

  return (
    <Page kicker="Session booking" title={`Book with ${mentor.name}`}>
      <form className="box narrow" onSubmit={submit}>
        <span className="tag">Test checkout</span>
        <h3>One-to-one teaching session</h3>
        <p>{money(rate)} per hour</p>
        <label>
          Session length
          <select value={minutes} onChange={(event) => setMinutes(Number(event.target.value))}>
            {DURATIONS.map((n) => <option key={n} value={n}>{n} minutes</option>)}
          </select>
        </label>
        <label>
          What would you like to learn?
          <textarea
            required maxLength={300} value={topic} onChange={(event) => setTopic(event.target.value)}
          />
        </label>
        <div className="bill-total">
          Session total <strong aria-live="polite">{money(priceFor(rate, minutes))}</strong>
        </div>
        <p>
          This demo simulates payment. Your mentor can confirm the session, then you can agree on a
          time in messages.
        </p>
        {book.isError && <p className="error" role="alert">{errorText(book.error)}</p>}
        <button disabled={book.isPending || !topic.trim()}>Pay with test funds</button>
      </form>
    </Page>
  );
}
