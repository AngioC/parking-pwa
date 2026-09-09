import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
      manifest: {
        name: 'Parking Disabili PWA',
        short_name: 'ParkDisabili',
        description: 'Mappa interattiva per posteggi disabili',
        theme_color: '#2563eb',
        background_color: '#ffffff',
        display: 'standalone', // Rende l'app a schermo intero (nasconde la barra del browser)
        icons: [
          // NOTA: Dovrai mettere queste icone nella cartella "public"
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
  ]
})