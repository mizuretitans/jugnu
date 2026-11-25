import { Link } from 'react-router';
import type { Mentor } from '../api/types';
import { money } from '../lib/money';

const initials = (name: string) =>
  name.split(/\s+/).map((part) => part[0] ?? '').join('').slice(0, 2).toUpperCase();

export const MentorCard = ({ mentor }: { mentor: Mentor }) => (
  <article className="card">
    <div className="row">
      <span className="avatar">{initials(mentor.name)}</span>
      <span className="tag">{mentor.field_label}</span>
    </div>
    <h3>{mentor.name}</h3>
    <p>{mentor.bio}</p>
    <p className="price">{money(mentor.hourly_rate_paise)} / hour</p>
    <Link className="link" to={`/mentors/${mentor.id}`}>Meet mentor</Link>
  </article>
);
