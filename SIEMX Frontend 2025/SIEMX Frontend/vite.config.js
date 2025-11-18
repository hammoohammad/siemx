import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const target = env.VITE_BACKEND_HTTP_URL || 'http://127.0.0.1:5000';
  return {
    plugins: [react()],
    server: {
      port: 3000,
      open: true,
      proxy: {
        '/api': {
          target,
          changeOrigin: true,
          secure: false,
        },
        // optional ws proxy if your backend exposes a ws endpoint like /ws
        '/ws': {
          target: target.replace('http', 'ws'),
          ws: true,
          changeOrigin: true,
          secure: false,
        },
      },
    },
  };
});
