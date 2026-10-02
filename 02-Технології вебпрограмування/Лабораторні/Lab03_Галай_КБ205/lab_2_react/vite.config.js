import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

// Плагін @tailwindcss/vite сам сканує файли проєкту й генерує CSS.
// У Tailwind v4 не потрібні ні tailwind.config.js, ні postcss.config.js.
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
})
