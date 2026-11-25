import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import type { Config } from '../api/types';

let client: SupabaseClient | null = null;

/** Null when the server has no Supabase project configured. Created once. */
export function getSupabase(config: Config): SupabaseClient | null {
  if (!config.supabase_url || !config.supabase_publishable_key) return null;
  client ??= createClient(config.supabase_url, config.supabase_publishable_key, {
    auth: { flowType: 'pkce', detectSessionInUrl: true, persistSession: true, autoRefreshToken: true },
  });
  return client;
}
