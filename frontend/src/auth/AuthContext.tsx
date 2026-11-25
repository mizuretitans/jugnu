import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createContext, useCallback, useContext, useEffect, useMemo, useRef, useState,
  type ReactNode,
} from 'react';
import { connectAuth, get, post } from '../api/client';
import { useConfig } from '../api/hooks';
import type { DemoAccount, Me, Onboarding, User } from '../api/types';
import { getSupabase } from './supabase';

// Demo tokens live in sessionStorage, so each tab can be a different demo user.
const DEMO_KEY = 'jugnu.demo-token';

const PRIVATE_KEYS = new Set<unknown>(['dashboard', 'conversation', 'brief', 'intake', 'helper']);

type Status = 'loading' | 'guest' | 'onboarding' | 'active' | 'error';

interface Auth {
  status: Status;
  user: User | null;
  suggestedName: string;
  googleAvailable: boolean;
  demoAvailable: boolean;
  retry: () => void;
  loginWithGoogle: () => Promise<void>;
  loginDemo: (account: DemoAccount) => Promise<void>;
  finishOnboarding: (data: Onboarding) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<Auth | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const configQuery = useConfig();
  const config = configQuery.data;
  const supabase = useMemo(() => (config ? getSupabase(config) : null), [config]);

  const [demoToken, setDemoToken] = useState(() => sessionStorage.getItem(DEMO_KEY));
  // undefined = Supabase has not told us yet
  const [googleUserId, setGoogleUserId] = useState<string | null | undefined>(undefined);

  useEffect(() => {
    if (!config) return;
    if (!supabase) {
      setGoogleUserId(null);
      return;
    }
    // The first event arrives after any ?code= in the URL has been exchanged.
    const { data } = supabase.auth.onAuthStateChange((_event, session) => {
      setGoogleUserId(session?.user.id ?? null);
    });
    return () => data.subscription.unsubscribe();
  }, [config, supabase]);

  const identity = demoToken ? `demo:${demoToken}` : googleUserId ? `google:${googleUserId}` : null;

  const logout = useCallback(async () => {
    if (sessionStorage.getItem(DEMO_KEY)) {
      sessionStorage.removeItem(DEMO_KEY);
      setDemoToken(null);
    } else {
      await supabase?.auth.signOut({ scope: 'local' });
    }
  }, [supabase]);

  // Connected during render so it is in place before any child query runs.
  const connected = useRef<unknown>(null);
  if (connected.current !== logout) {
    connected.current = logout;
    connectAuth(
      async () => {
        const demo = sessionStorage.getItem(DEMO_KEY);
        if (demo) return demo;
        if (!supabase) return null;
        const { data } = await supabase.auth.getSession();
        return data.session?.access_token ?? null;
      },
      () => void logout(),
    );
  }

  // Never show one person's cached data to the next person in this tab.
  const lastIdentity = useRef(identity);
  useEffect(() => {
    if (lastIdentity.current === identity) return;
    lastIdentity.current = identity;
    queryClient.removeQueries({
      predicate: ({ queryKey }) =>
        PRIVATE_KEYS.has(queryKey[0]) || (queryKey[0] === 'me' && queryKey[1] !== identity),
    });
  }, [identity, queryClient]);

  const me = useQuery({
    queryKey: ['me', identity],
    queryFn: () => get<Me>('/me'),
    enabled: identity !== null,
    staleTime: Infinity,
  });

  let status: Status = 'loading';
  if (configQuery.isError) status = 'error';
  else if (config && (demoToken || googleUserId !== undefined)) {
    if (!identity) status = 'guest';
    else if (me.data) status = me.data.status === 'active' ? 'active' : 'onboarding';
    else if (me.isError) status = 'error';
  }

  const value: Auth = {
    status,
    user: status === 'active' ? (me.data?.user ?? null) : null,
    suggestedName: me.data?.suggested_name ?? '',
    googleAvailable: supabase !== null,
    demoAvailable: config?.demo_login ?? false,
    retry: () => {
      if (configQuery.isError) void configQuery.refetch();
      if (me.isError) void me.refetch();
    },
    loginWithGoogle: async () => {
      if (!supabase) return;
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: { redirectTo: `${window.location.origin}/auth/callback` },
      });
      if (error) throw error;
    },
    loginDemo: async (account) => {
      const { access_token } = await post<{ access_token: string }>('/auth/demo', { account });
      sessionStorage.setItem(DEMO_KEY, access_token);
      setDemoToken(access_token);
    },
    finishOnboarding: async (data) => {
      const result = await post<Me>('/me/onboarding', data);
      queryClient.setQueryData(['me', identity], result);
    },
    logout,
  };

  return <AuthContext value={value}>{children}</AuthContext>;
}

export function useAuth(): Auth {
  const auth = useContext(AuthContext);
  if (!auth) throw new Error('useAuth must be used inside AuthProvider');
  return auth;
}
