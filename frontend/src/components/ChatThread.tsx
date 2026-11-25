import { useEffect, useRef } from 'react';

export interface Bubble {
  key: string | number;
  name: string;
  text: string;
  mine?: boolean;
  pending?: boolean;
}

interface Props { bubbles: Bubble[]; empty?: string; typing?: boolean; label: string }

export function ChatThread({ bubbles, empty, typing, label }: Props) {
  const box = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (box.current) box.current.scrollTop = box.current.scrollHeight;
  }, [bubbles.length, typing]);

  return (
    <div className="messages scroll" ref={box} role="log" aria-label={label} tabIndex={0}>
      {bubbles.length === 0 && !typing && <p>{empty}</p>}
      {bubbles.map((b) => (
        <div key={b.key} className={`bubble${b.mine ? ' mine' : ''}${b.pending ? ' pending' : ''}`}>
          <b>{b.name}</b>{b.text}
        </div>
      ))}
      {typing && <div className="bubble pending">Typing…</div>}
    </div>
  );
}
