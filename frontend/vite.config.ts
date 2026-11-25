import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// The browser always calls /api on its own origin. In development Vite forwards it
// to FastAPI; later a Docker web server (for example nginx) does the same job.
const apiTarget = process.env.API_TARGET ?? 'http://127.0.0.1:8000';

export default defineConfig({
  plugins: [react()],
  server: {
    // Fixed: this origin is registered with Google and Supabase.
    port: 5173,
    strictPort: true,
    proxy: { '/api': apiTarget },
  },
});
