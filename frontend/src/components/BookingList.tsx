import { Link } from 'react-router';
import { errorText } from '../api/client';
import { useConfirmBooking } from '../api/hooks';
import type { Booking, Role } from '../api/types';
import { money } from '../lib/money';

export function BookingList({ bookings, role }: { bookings: Booking[]; role: Role }) {
  const confirm = useConfirmBooking();
  if (bookings.length === 0) return <p>Your paid session bookings will appear here.</p>;
  return (
    <>
      {bookings.map((b) => (
        <article className="resource" key={b.id}>
          <strong>{role === 'mentor' ? b.student.name : b.mentor.name}</strong>
          <p>{b.topic}</p>
          <p>
            {b.minutes} minutes at {money(b.hourly_rate_paise)}/hour · {money(b.total_paise)} paid (test)
          </p>
          <span className="tag">
            {b.status === 'confirmed' ? 'Confirmed' : 'Awaiting mentor confirmation'}
          </span>
          <div>
            {role === 'mentor' && b.status === 'pending' && (
              <button
                type="button" className="small" disabled={confirm.isPending}
                onClick={() => confirm.mutate(b.id)}
              >
                Confirm session
              </button>
            )}
            {b.request_id && (
              <Link className="link" to={`/messages/${b.request_id}`}>Message about this session</Link>
            )}
          </div>
        </article>
      ))}
      {confirm.isError && <p className="error" role="alert">{errorText(confirm.error)}</p>}
    </>
  );
}
