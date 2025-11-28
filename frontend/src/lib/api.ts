import { supabase } from './supabase';

export async function apiFetch(
  path: string,
  init: RequestInit = {}
): Promise<Response> {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;

  const headers = new Headers(init.headers);
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  return fetch(`${import.meta.env.VITE_BACKEND_URI}${path}`, {
    ...init,
    headers,
  });
}
