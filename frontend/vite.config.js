import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Porta 5175 (a 5173 e do projeto de financas pessoais e a 5174 do clube) para os
// tres dev servers rodarem ao mesmo tempo.
export default defineConfig({
  plugins: [react()],
  server: { port: 5175 },
})
