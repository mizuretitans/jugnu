import { useRef, useState, type FormEvent, type KeyboardEvent } from 'react';
import { errorText } from '../api/client';

interface Props {
  label: string;
  maxLength: number;
  busy?: boolean;
  onSend: (text: string) => Promise<unknown>;
}

export function ChatForm({ label, maxLength, busy = false, onSend }: Props) {
  const [text, setText] = useState('');
  const [error, setError] = useState('');
  const [sending, setSending] = useState(false);
  const form = useRef<HTMLFormElement>(null);
  const blocked = busy || sending;

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const value = text.trim();
    if (!value || blocked) return;
    setError('');
    setSending(true);
    setText('');
    try {
      await onSend(value);
    } catch (problem) {
      setError(errorText(problem));
      setText((current) => current || value); // do not lose what they typed
    } finally {
      setSending(false);
    }
  };

  const onKeyDown = (event: KeyboardEvent) => {
    // isComposing: Enter also picks a word in Hindi/Bengali keyboards.
    if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {
      event.preventDefault();
      form.current?.requestSubmit();
    }
  };

  return (
    <form ref={form} onSubmit={submit}>
      <label>
        {label}
        <textarea
          value={text} required maxLength={maxLength} onKeyDown={onKeyDown}
          onChange={(event) => setText(event.target.value)}
        />
      </label>
      {error && <p className="error" role="alert">{error}</p>}
      <button disabled={blocked}>Send message</button>
    </form>
  );
}
