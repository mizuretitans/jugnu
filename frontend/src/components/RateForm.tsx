import { useState, type FormEvent } from 'react';
import { errorText } from '../api/client';
import { useUpdateRate } from '../api/hooks';

export function RateForm({ currentPaise }: { currentPaise: number }) {
  const [rupees, setRupees] = useState(String(currentPaise / 100));
  const update = useUpdateRate();
  const submit = (event: FormEvent) => {
    event.preventDefault();
    update.mutate(Number(rupees));
  };
  return (
    <form className="box" onSubmit={submit}>
      <h3>Your teaching rate</h3>
      <label>
        Hourly rate (₹)
        <input
          type="number" required min={1} max={100000} step={1} value={rupees}
          onChange={(event) => setRupees(event.target.value)}
        />
      </label>
      <button className="small" disabled={update.isPending}>Save hourly rate</button>
      <p role="status">
        {update.isSuccess && 'Rate saved for new bookings.'}
        {update.isError && <span className="error">{errorText(update.error)}</span>}
      </p>
    </form>
  );
}
