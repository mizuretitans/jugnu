export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
  ) {
    super(message);
  }
}

type TokenSource = () => Promise<string | null>;

let getToken: TokenSource = async () => null;
let onUnauthorized: () => void = () => {};

/** AuthContext tells the client where tokens come from. */
export function connectAuth(source: TokenSource, unauthorized: () => void): void {
  getToken = source;
  onUnauthorized = unauthorized;
}

function toError(status: number, body: unknown): ApiError {
  const detail = (body as { detail?: unknown } | null)?.detail;
  if (Array.isArray(detail)) {
    // Pydantic validation error
    const message = (detail[0] as { msg?: string } | undefined)?.msg ?? 'Please check your input.';
    return new ApiError(status, 'validation', message.replace(/^Value error, /, ''));
  }
  if (detail && typeof detail === 'object') {
    const { code, message } = detail as { code?: string; message?: string };
    return new ApiError(status, code ?? 'error', message ?? 'Something went wrong.');
  }
  return new ApiError(status, 'error', 'Something went wrong. Please try again.');
}

export async function api<T>(method: string, path: string, body?: unknown): Promise<T> {
  const token = await getToken();
  const headers: Record<string, string> = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  if (body !== undefined) headers['Content-Type'] = 'application/json';

  let response: Response;
  try {
    response = await fetch(`/api${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(0, 'network', 'Could not reach Jugnu. Check your connection.');
  }
  if (response.status === 204) return undefined as T;
  const data: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    if (response.status === 401 && token) onUnauthorized();
    throw toError(response.status, data);
  }
  return data as T;
}

export const get = <T>(path: string) => api<T>('GET', path);
export const post = <T>(path: string, body?: unknown) => api<T>('POST', path, body);
export const patch = <T>(path: string, body: unknown) => api<T>('PATCH', path, body);
export const del = (path: string) => api<void>('DELETE', path);

export function errorText(error: unknown): string {
  return error instanceof Error ? error.message : 'Something went wrong.';
}
