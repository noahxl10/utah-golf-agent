import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5000,
    allowedHosts: [
      'localhost',
      '.replit.dev',
      '10b7ea48-718e-4018-b4c6-704734d94440-00-1i3wtbxx6pimv.worf.replit.dev'
    ]
  }
});