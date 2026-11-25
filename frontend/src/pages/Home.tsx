import { Link } from 'react-router';
import { useMentors } from '../api/hooks';
import { Doodle } from '../components/Doodle';
import { MentorCard } from '../components/MentorCard';
import { Eyebrow } from '../components/Page';
import { STEPS } from '../content/copy';

export function Home() {
  const mentors = useMentors().data ?? [];
  return (
    <div className="wrap">
      <section className="hero">
        <div>
          <Eyebrow>Student mentorship</Eyebrow>
          <h1>Find your path.<br /><em>With a mentor.</em></h1>
          <p>Discover a career that fits you and connect with a mentor who has walked that path.</p>
          <div className="actions">
            <Link className="btn" to="/guide">✧ &nbsp; Find my path</Link>
            <Link className="btn outline" to="/mentors">Explore mentors</Link>
          </div>
        </div>
        <img src="/landscape.svg" alt="A winding trail leads through green hills to a flag at the summit." />
      </section>
      <section className="how" id="how">
        <div className="sectionhead">
          <div><Eyebrow>How it works</Eyebrow><h2>Your journey in three steps.</h2></div>
        </div>
        <div className="grid steps">
          {STEPS.map(([title, text], i) => (
            <article className="card" key={title}>
              <Doodle index={i} />
              <span className="stepnum">Step 0{i + 1}</span>
              <h3>{title}</h3>
              <p>{text}</p>
            </article>
          ))}
        </div>
      </section>
      <section className="listing">
        <div className="sectionhead">
          <div><Eyebrow>Mentor directory</Eyebrow><h2>Explore mentors</h2></div>
          <Link className="link" to="/mentors">View all mentors</Link>
        </div>
        <div className="grid">
          {mentors.slice(0, 3).map((m) => <MentorCard key={m.id} mentor={m} />)}
        </div>
      </section>
    </div>
  );
}
