// Where to go after login. Kept in sessionStorage so it survives the Google redirect.
const KEY = 'jugnu.next';

/** Only paths inside this app, so a crafted value cannot send people to another site. */
const isLocalPath = (path: string) => /^\/(?![/\\])/.test(path) && !path.includes('\\');

export function rememberNext(path: string): void {
  if (isLocalPath(path)) sessionStorage.setItem(KEY, path);
}

/** Reading and clearing are separate because React may run effects twice in development. */
export function peekNext(): string {
  const path = sessionStorage.getItem(KEY);
  return path && isLocalPath(path) ? path : '/dashboard';
}

export const clearNext = () => sessionStorage.removeItem(KEY);
